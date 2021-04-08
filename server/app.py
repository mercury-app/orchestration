import tornado.web  # for handlers
import tornado.ioloop  # for listening to port
import logging

from caduceus.dag import MercuriDag
from caduceus.node import MercuriNode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from server.views import (
    CaduceusHandler,
    NodeHandler,
    NodeContainerHandler,
    DagInfo,
    EdgeHandler,
)


class Application(tornado.web.Application):
    def __init__(self):
        # setting up a dag as an attribute of this class
        # all base classes can modify it
        self.dag = MercuriDag()
        handlers = [
            (r"/", CaduceusHandler),
            (r"/nodes/([^/]+)?/trigger", NodeContainerHandler),
            (r"/nodes/([^/]+)?", NodeHandler),
            (r"/edges/([^/]+)?", EdgeHandler),
            (r"/dag", DagInfo),
        ]
        super().__init__(handlers, debug=True)


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    logging.info("running on port 8888")
    tornado.ioloop.IOLoop.current().start()
