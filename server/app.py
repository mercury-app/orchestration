import tornado.web  # for handlers
import tornado.ioloop  # for listening to port
import logging
from apispec import APISpec
from apispec_webframeworks.tornado import TornadoPlugin
import swagger_ui

from caduceus.dag import MercuriDag
from server.swagger import generate_swagger_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SWAGGER_API_OUTPUT_FILE = "./swagger.json"

from server.views import (
    CaduceusHandler,
    NodeHandler,
    NodeContainerHandler,
    DagInfo,
    EdgeHandler,
)

spec = APISpec(
    title="Caduceus API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(description="Documentation for Caduceus"),
    plugins=[TornadoPlugin()],
    servers=[
        {
            "url": "http://localhost:8888/",
            "description": "Local environment",
        },
    ],
)


class Application(tornado.web.Application):
    def __init__(self):
        # setting up a dag as an attribute of this class
        # all base classes can modify it
        self.dag = MercuriDag()
        self.handlers = [
            (r"/", CaduceusHandler),
            (r"/nodes/([^/]+)/status", NodeContainerHandler),
            (r"/nodes/([^/]+)?", NodeHandler),
            (r"/edges/([^/]+)?", EdgeHandler),
            (r"/dag", DagInfo),
        ]
        super().__init__(self.handlers, debug=True)


if __name__ == "__main__":
    app = Application()
    # Generate a fresh Swagger file
    generate_swagger_file(handlers=app.handlers, file_location=SWAGGER_API_OUTPUT_FILE)

    # Start the Swagger UI. Automatically generated swagger.json can also
    # be served using a separate Swagger-service.
    swagger_ui.tornado_api_doc(
        app,
        config_path=SWAGGER_API_OUTPUT_FILE,
        url_prefix="/swagger/spec.html",
        title="Caduceus API",
    )

    app.listen(8888)
    logging.info("running on port 8888")
    tornado.ioloop.IOLoop.current().start()
