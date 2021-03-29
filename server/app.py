import tornado.web  # for handlers
import tornado.ioloop  # for listening to port

from caduceus.dag import MercuriDag
from caduceus.node import MercuriNode

from server.views import CaduceusHandler, AddNode, DagInfo


class Application(tornado.web.Application):
    def __init__(self):
        # setting up a dag as an attribute of this class
        # all base classes can modify it
        self.dag = MercuriDag()
        handlers = [
            (r"/", CaduceusHandler),
            (r"/add_node", AddNode),
            (r"/dag_info", DagInfo),
        ]
        super().__init__(handlers)


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
