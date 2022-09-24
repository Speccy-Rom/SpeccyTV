from http import HTTPStatus

DONE_ACTION = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
CREATE_ACTION = HTTPStatus.CREATED
EXISTS_ACTION = HTTPStatus.CONFLICT

aspect_size = {
    "144p": "256x144",
    "240p": "426x240",
    "360p": "640x360",
    "480p": "854x480",
    "720p": "1280x720",
    "1080p": "1920x1080"
}
