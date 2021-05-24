import networkx as nx
import logging
from typing import List
from uuid import uuid4

from caduceus.node import MercuriNode
from caduceus.edge import MercuriEdge

logger = logging.getLogger(__name__)


class MercuriDag:
    def __init__(self):
        self.id = uuid4().hex
        self._nxdag = nx.DiGraph()

    @property
    def nodes(self) -> List[MercuriNode]:
        return list(self._nxdag.nodes)

    @property
    def edges(self) -> list:
        return [_[2]["object"] for _ in self._nxdag.edges(data=True)]

    def add_node(self, node: MercuriNode) -> None:

        if len(self._nxdag.nodes) > 0:
            used_ports = [_.jupyter_port for _ in self._nxdag.nodes]
            print(used_ports)
            port = max(used_ports) + 1
            logger.info(f"Starting new container and mapping to port {port}")
            node.jupyter_port = port
        self._nxdag.add_node(node, id=node.id)

    def remove_node(self, node: MercuriNode) -> None:
        self._nxdag.remove_node(node)

    def add_edge(self, edge: MercuriEdge) -> None:
        # not the most elegant, to do: change
        assert edge.source_node
        assert edge.dest_node

        self._nxdag.add_edge(edge.source_node, edge.dest_node, object=edge)

    def remove_edge(self, edge: MercuriEdge) -> None:
        assert edge.source_node
        assert edge.dest_node
        self._nxdag.remove_edge(edge.source_node, edge.dest_node)

    def get_node(self, id: str) -> MercuriNode:
        node_search = [_ for _ in self._nxdag.nodes if _.id == id]
        assert len(node_search) < 2
        if len(node_search) == 1:
            return node_search[0]

    def get_edge(self, id: str) -> MercuriEdge:
        edge_search = [_ for _ in self.edges if _.id == id]
        assert len(edge_search) < 2
        if len(edge_search) == 1:
            return edge_search[0]

    def get_edge_from_nodes(
        self, source_node_id: str, detination_node_id: str
    ) -> MercuriEdge:
        edge_search = [
            _
            for _ in self.edges
            if _.source_node.id == source_node_id
            and _.dest_node.id == detination_node_id
        ]
        assert len(edge_search) < 3
        if len(edge_search) == 1:
            return edge_search[0]

    # _nxdag.successors(node1)
    # _nxdag.predescessors(node1)
