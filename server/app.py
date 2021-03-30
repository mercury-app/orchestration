import tornado.web  # for handlers
import tornado.ioloop  # for listening to port

from caduceus.dag import MercuriDag
from caduceus.node import MercuriNode

from server.views import CaduceusHandler, NodeHandler, DagInfo


class Application(tornado.web.Application):
    def __init__(self):
        # setting up a dag as an attribute of this class
        # all base classes can modify it
        self.dag = MercuriDag()
        handlers = [
            (r"/", CaduceusHandler),
            (r"/nodes/([^/]+)?", NodeHandler),
            (r"/dag", DagInfo),
        ]
        super().__init__(handlers, debug=True)


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
