import logging
from typing import Tuple
from uuid import uuid4
import os

from mercury.node import MercuryNode
from mercury.constants import BASE_DOCKER_BIND_VOLUME


class MercuryEdge:
    def __init__(
        self,
        source_node: MercuryNode = None,
        dest_node: MercuryNode = None,
        source_dest_connect: list = None,
    ):

        self.id = uuid4().hex
        self._source_node = source_node
        self._dest_node = dest_node
        self._json_path = f"{BASE_DOCKER_BIND_VOLUME}/{self.id}.json"

        with open(self._json_path) as f:
            io = json.load(f)

        self._json_inputs = io.keys().tolist()

        # the connections between source output set and destination input set have to
        # be one-one (injective) but not necessarily onto(surjective)
        self._source_dest_connect = (
            [] if source_dest_connect is None else source_dest_connect
        )

    @property
    def source_node(self) -> MercuryNode:
        return self._source_node

    @source_node.setter
    def source_node(self, node: MercuryNode):
        self._source_node = node

    @property
    def dest_node(self) -> MercuryNode:
        return self._dest_node

    @dest_node.setter
    def dest_node(self, node: MercuryNode):
        self._dest_node = node

    @property
    def source_dest_connect(self) -> list:
        return self._source_dest_connect

    @property
    def json_inputs(self) -> list:
        return self._json_inputs

    def get_input_code_snippet(self) -> str:
        if not os.path.exists(self._json_path):
            raise Exception(f"json for edge {self.id} doesn't exist")

        with open(self._json_path) as f:
            io = json.load(f)

        code_lines = []

        for k, v in io.items():
            code_line = f"{k} = {v}"
            code_lines.append(code_line)

        code = "\n".join(code_lines)
        return code
