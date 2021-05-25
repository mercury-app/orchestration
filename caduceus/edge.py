import logging
from typing import Tuple
from uuid import uuid4

from caduceus.node import MercuriNode


class MercuriEdge:
    def __init__(
        self,
        source_node: MercuriNode = None,
        dest_node: MercuriNode = None,
        source_dest_connect: list = [],
    ):

        self.id = uuid4().hex
        self._source_node = source_node
        self._dest_node = dest_node

        # the connections between source output set and destination input set have to
        # be one-one (injective) but not necessarily onto(surjective)
        self._source_dest_connect = source_dest_connect

    @property
    def source_node(self) -> MercuriNode:
        return self._source_node

    @source_node.setter
    def source_node(self, node: MercuriNode):
        self._source_node = node

    @property
    def dest_node(self) -> MercuriNode:
        return self._dest_node

    @dest_node.setter
    def dest_node(self, node: MercuriNode):
        self._dest_node = node

    @property
    def source_dest_connect(self) -> list:
        return self._source_dest_connect

    @source_dest_connect.setter
    def source_dest_connect(self, source_dest_map: list):
        assert self._source_node.output
        assert self._dest_node.input

        assert isinstance(source_dest_map, list)

        for source_dest_pair in source_dest_map:
            assert "input" in source_dest_pair and "output" in source_dest_pair
            if source_dest_pair["input"] not in self._source_node.output.keys():
                raise Exception("source output is not an output of the source node")
            if source_dest_pair["output"] not in self._dest_node.input.keys():
                raise Exception(
                    "destination input is not an input of the destination node"
                )

        self._source_dest_connect = source_dest_map
