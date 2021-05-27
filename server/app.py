import tornado.web  # for handlers
import tornado.ioloop  # for listening to port
import logging

from caduceus.dag import MercuriDag
from caduceus.docker_client import docker_cl

from server.views import CaduceusHandler
from server.views.workflow import WorkflowHandler
from server.views.node import NodeHandler, NodeContainerHandler
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
            (r"/connectors(?:/([^/\s]+))?", ConnectorHandler),
            (r"/workflows", WorkflowHandler),
        ]
        super().__init__(self.handlers, debug=True)


if __name__ == "__main__":
    # kill all running caduceus containers
    logger.info("Killing already running containers")
    [
        _.kill()
        for _ in docker_cl.containers.list()
        if _.image.tags[0] == "jupyter-caduceus:latest"
    ]

    app = Application()

    app.listen(8888)
    logging.info("Running on port 8888")
    tornado.ioloop.IOLoop.current().start()
