from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from app import app
