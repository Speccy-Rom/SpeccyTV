from django.contrib import admin

from .models import FilmWork, Genre, Person, File


class PersonInLineAdmin(admin.TabularInline):
    model = FilmWork.persons.through
    extra = 0


class GenreInLineAdmin(admin.TabularInline):
    model = FilmWork.genres.through
    extra = 0


class FileInLineAdmin(admin.TabularInline):
    model = FilmWork.files.through
    extra = 0


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating')
    list_filter = ('type',)
    fields = ('title', 'type', 'description', 'creation_date', 'rating', 'certificate', 'file_path')
    inlines = (PersonInLineAdmin, GenreInLineAdmin, FileInLineAdmin)
    search_fields = ('title', 'description', 'type', 'genres', 'files')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    fields = ('full_name', 'birth_date')
    inlines = (PersonInLineAdmin,)
    search_fields = ('full_name', 'birth_date')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    fields = ('name', 'description')
    inlines = (GenreInLineAdmin,)
    search_fields = ('name', 'description')


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'file_path',
        'video_width',
        'video_height',
        'video_fps',
        'video_codec',
        'audio_codec',
        'audio_channels',
    )
    list_filter = (
        'file_format',
        'video_codec',
        'video_width',
        'video_height',
        'video_fps',
        'audio_codec',
        'audio_sample_rate',
        'audio_channels',
    )
    inlines = (FileInLineAdmin,)
    search_fields = (
        'id',
        'file_path',
        'file_format',
        'video_width',
        'video_height',
        'video_fps',
        'video_codec',
        'audio_codec',
        'audio_channels',
    )
