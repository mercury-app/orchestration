import tornado.web  # for handlers
import tornado.ioloop  # for listening to port
import logging

from mercury.docker_client import docker_cl

from server.views import MercuryHandler
from server.views.workflow import WorkflowHandler
from server.views.node import (
    NodeHandler,
    NodeImageHandler,
    NodeNotebookHandler,
    KernelInfoHandler,
)
from server.views.connector import ConnectorHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self):
        # setting up a dag as an attribute of this class
        # all base classes can modify it
        self.workflows = {}
        self.handlers = [
            (r"/", MercuryHandler),
            (r"/workflows/([^/\s]+)/nodes/([^/\s]+)/notebook", NodeNotebookHandler),
            (r"/workflows/([^/\s]+)/nodes/([^/\s]+)/ws", KernelInfoHandler),
            (r"/workflows/([^/\s]+)/nodes/([^/\s]+)/image", NodeImageHandler),
            (r"/workflows/([^/\s]+)/nodes(?:/([^/\s]+))?", NodeHandler),
            (r"/workflows/([^/\s]+)/connectors(?:/([^/\s]+))?", ConnectorHandler),
            (r"/workflows(?:/([^/\s]+))?", WorkflowHandler),
        ]
        super().__init__(self.handlers, debug=True)


if __name__ == "__main__":
    # kill all running mercury containers
    logger.info("Killing already running containers...")
    [
        _.kill()
        for _ in docker_cl.containers.list()
        if "jupyter-mercury:latest" in _.image.tags
    ]

    app = Application()

    app.listen(8888)
    logging.info("Running on port 8888")
    tornado.ioloop.IOLoop.current().start()
