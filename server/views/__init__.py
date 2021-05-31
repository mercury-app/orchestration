import tornado.web
import logging
from typing import List
import json

logger = logging.getLogger(__name__)


class MercuryHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.method in ["POST", "PATCH"]:
            assert (
                self.request.headers.get("Content-Type") == "application/vnd.api+json"
            )
            assert self.request.headers.get("Accept") == "application/vnd.api+json"

            data = json.loads(self.request.body)
            assert "data" in data.keys()
            assert isinstance(data["data"], dict)
            assert "type" in data["data"]

            if self.request == "PATCH":
                assert "id" in data.keys()

        elif self.request.method in ["GET"]:
            assert self.request.headers.get("Accept") == "application/vnd.api+json"

    def get(self):
        self.write("Welcome to Mercury")
