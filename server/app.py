import tornado.web  # for handlers
import tornado.ioloop  # for listening to port
import logging

from caduceus.dag import MercuriDag

from server.views import CaduceusHandler
from server.views.dag import DagInfoHandler
from server.views.node import NodeHandler, NodeContainerHandler
from server.views.edge import EdgeHandler
from server.views.connector import ConnectorHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self):
        # setting up a dag as an attribute of this class
        # all base classes can modify it
        self.dag = MercuriDag()
        self.handlers = [
            (r"/", CaduceusHandler),
            (r"/nodes/([^/\s]+)/status", NodeContainerHandler),
            (r"/nodes(?:/([^/\s]+))?", NodeHandler),
            (r"/edges(?:/([^/\s]+))?", EdgeHandler),
            (r"/connector(?:/([^/\s]+))?", ConnectorHandler),
            (r"/dag", DagInfoHandler),
        ]
        super().__init__(self.handlers, debug=True)


if __name__ == "__main__":
    app = Application()

    app.listen(8888)
    logging.info("Running on port 8888")
    tornado.ioloop.IOLoop.current().start()
