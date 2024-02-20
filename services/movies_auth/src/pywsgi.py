from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa: E402
from app import app  # noqa: E402


http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()
