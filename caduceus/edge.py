import logging
from typing import Tuple
from uuid import uuid4

from caduceus.node import MercuriNode


class MercuriEdge:
    def __init__(
        self,
        source_node: MercuriNode = None,
        dest_node: MercuriNode = None,
        source_dest_connect: list = None,
    ):

        self.id = uuid4().hex
        self._source_node = source_node
        self._dest_node = dest_node

        # the connections between source output set and destination input set have to
        # be one-one (injective) but not necessarily onto(surjective)
        self._source_dest_connect = (
            [] if source_dest_connect is None else source_dest_connect
        )

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
