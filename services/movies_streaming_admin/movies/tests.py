from movies.serializers import FileSerializer
from rest_framework.exceptions import ValidationError
import pytest

from rest_framework.test import APIClient
from rest_framework import status
from mixer.backend.django import mixer
from movies.models import File


from services.movies_streaming_admin.movies.serializers import FilmWorkSerializer


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_data, expected",
    [
        # Happy path tests
        (
            {"name": "test_file.mp4", "path": "/path/to/file.mp4"},
            "test_file.mp4",
        ),  # ID: HP-1
        (
            {"name": "sample_movie.avi", "path": "/movies/sample_movie.avi"},
            "sample_movie.avi",
        ),  # ID: HP-2
        # Edge cases
        ({"name": "", "path": "/path/to/empty_name.mp4"}, ValidationError),  # ID: EC-1
        (
            {"name": " " * 5, "path": "/path/to/whitespace.mp4"},
            ValidationError,
        ),  # ID: EC-2
        # Error cases
        (
            {"name": None, "path": "/path/to/none_name.mp4"},
            ValidationError,
        ),  # ID: ERR-1
        ({"path": "/path/to/no_name.mp4"}, ValidationError),  # ID: ERR-2
    ],
)
def test_file_serializer(file_data, expected):
    # Arrange
    # sourcery skip: no-conditionals-in-tests
    if not isinstance(expected, type) or not issubclass(expected, Exception):
        file = File(**file_data)
        file.full_clean()  # Validate model instance to ensure it's correct

    # Act
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            FileSerializer(data=file_data).is_valid(raise_exception=True)
    else:
        serializer = FileSerializer(file)
        is_valid = serializer.is_valid()

    # Assert
    if not isinstance(expected, type) or not issubclass(expected, Exception):
        assert is_valid, serializer.errors
        assert serializer.data['name'] == expected
    # No assert needed for the error cases as the exception is the expected outcome


# Assuming FilmWork model has fields like id, title, creation_date, rating etc.
# You will need to adjust the fields and values according to your actual model.


@pytest.mark.django_db
@pytest.mark.parametrize(
    "film_work_data, expected",
    [
        # Happy path tests
        pytest.param(
            {'title': 'Test Film', 'creation_date': '2021-01-01', 'rating': 5},
            {'title': 'Test Film', 'creation_date': '2021-01-01', 'rating': 5},
            id='happy-path-valid-data',
        ),
        # Add more happy path cases with different realistic values
        # Edge cases
        pytest.param(
            {'title': '', 'creation_date': '2021-01-01', 'rating': 5},
            ValidationError,
            id='edge-case-empty-title',
        ),
        # Add more edge cases with different values
        # Error cases
        pytest.param(
            {'title': 'Test Film', 'creation_date': 'invalid-date', 'rating': 5},
            ValidationError,
            id='error-case-invalid-date',
        ),
        # Add more error cases with different invalid values
    ],
)
def test_film_work_serializer(film_work_data, expected):
    # Arrange
    serializer = FilmWorkSerializer(data=film_work_data)

    # Act
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            serializer.is_valid(raise_exception=True)
    else:
        assert serializer.is_valid(), serializer.errors
        assert serializer.save()

    # Assert
    if not isinstance(expected, type):
        assert serializer.data == expected


@pytest.mark.django_db
class TestFileViewSet:
    client = APIClient()

    @pytest.mark.parametrize(
        "file_data, expected_status_code",
        [
            # Happy path tests
            (
                {"name": "test_file_1.txt", "file": "dummy_content_1"},
                status.HTTP_201_CREATED,
                "test_id_01",
            ),
            (
                {"name": "test_file_2.txt", "file": "dummy_content_2"},
                status.HTTP_201_CREATED,
                "test_id_02",
            ),
            # Edge case tests
            (
                {"name": "", "file": "dummy_content"},
                status.HTTP_400_BAD_REQUEST,
                "test_id_03",
            ),
            # Error case tests
            ({"name": "test_file_3.txt"}, status.HTTP_400_BAD_REQUEST, "test_id_04"),
            ({"file": "dummy_content_3"}, status.HTTP_400_BAD_REQUEST, "test_id_05"),
        ],
        ids=["test_id_01", "test_id_02", "test_id_03", "test_id_04", "test_id_05"],
    )
    def test_create_file(self, file_data, expected_status_code):
        # Act
        response = self.client.post('/files/', file_data)

        # Assert
        assert response.status_code == expected_status_code
        if expected_status_code == status.HTTP_201_CREATED:
            assert File.objects.filter(name=file_data["name"]).exists()

    @pytest.mark.parametrize(
        "file_setup, update_data, expected_status_code",
        [
            # Happy path test
            (
                {"name": "test_file_4.txt", "file": "dummy_content_4"},
                {"name": "updated_test_file_4.txt"},
                status.HTTP_200_OK,
                "test_id_06",
            ),
            # Edge case test
            (
                {"name": "test_file_5.txt", "file": "dummy_content_5"},
                {"name": ""},
                status.HTTP_400_BAD_REQUEST,
                "test_id_07",
            ),
            # Error case test
            (
                {"name": "test_file_6.txt", "file": "dummy_content_6"},
                {"non_existing_field": "value"},
                status.HTTP_400_BAD_REQUEST,
                "test_id_08",
            ),
        ],
        ids=["test_id_06", "test_id_07", "test_id_08"],
    )
    def test_update_file(self, file_setup, update_data, expected_status_code):
        # Arrange
        file = mixer.blend(File, **file_setup)

        # Act
        response = self.client.put(
            f'/files/{file.pk}/', update_data, content_type='application/json'
        )

        # Assert
        assert response.status_code == expected_status_code
        if expected_status_code == status.HTTP_200_OK:
            file.refresh_from_db()
            assert file.name == update_data["name"]

    @pytest.mark.parametrize(
        "file_setup, expected_status_code",
        [
            # Happy path test
            (
                {"name": "test_file_7.txt", "file": "dummy_content_7"},
                status.HTTP_204_NO_CONTENT,
                "test_id_09",
            ),
            # Error case test
            ({}, status.HTTP_404_NOT_FOUND, "test_id_10"),
        ],
        ids=["test_id_09", "test_id_10"],
    )
    def test_delete_file(self, file_setup, expected_status_code):
        # Arrange
        file = mixer.blend(File, **file_setup) if file_setup else None
        file_pk = file.pk if file else 99999  # Assuming 99999 is an unlikely pk

        # Act
        response = self.client.delete(f'/files/{file_pk}/')

        # Assert
        assert response.status_code == expected_status_code
        if expected_status_code == status.HTTP_204_NO_CONTENT:
            assert not File.objects.filter(pk=file_pk).exists()
