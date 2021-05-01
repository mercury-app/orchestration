import tornado.web
import logging

logger = logging.getLogger(__name__)


class CaduceusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to Caduceus")