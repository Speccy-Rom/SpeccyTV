import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """
    Function to serialize Python data types into a JSON formatted string using orjson.

    Args:
        v: The Python data to be serialized.
        default: The function to call for types not serializable by default.

    Returns:
        A JSON formatted string.
    """
    return orjson.dumps(v, default=default).decode()


class CustomBaseModel(BaseModel):
    """
    A custom base model class that extends the BaseModel class from Pydantic.

    This class overrides the methods used for loading and dumping JSON data with orjson for performance benefits.

    Attributes:
        Config: A nested class used to configure the behavior of the model.
    """
    class Config:
        """
        A nested class used to configure the behavior of the model.

        Attributes:
            json_loads: The function used to parse JSON data into Python data types.
            json_dumps: The function used to serialize Python data types into a JSON formatted string.
        """
        json_loads = orjson.loads
        json_dumps = orjson_dumps
