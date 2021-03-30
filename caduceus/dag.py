import networkx as nx
from typing import List

from caduceus.node import MercuriNode


class MercuriDag:
    def __init__(self):
        self._nxdag = nx.DiGraph()

    @property
    def nodes(self) -> List[MercuriNode]:
        return list(self._nxdag.nodes)

    @property
    def edges(self) -> list:
        return [(str(_[0]), str(_[1])) for _ in self._nxdag.edges]

    def add_node(self, node: MercuriNode) -> None:
        self._nxdag.add_node(node, id=node.id)

    def remove_node(self, node: MercuriNode) -> None:
        self._nxdag.remove_node(node)

    def add_edge(self, node1: MercuriNode, node2: MercuriNode) -> None:
        self._nxdag.add_edge(node1, node2)

    def get_node(self, id: str) -> MercuriNode:
        node_search = [_ for _ in self._nxdag.nodes if _.id == id]
        assert len(node_search) < 2
        if len(node_search) == 1:
            return node_search[0]

    # _nxdag.successors(node1)
    # _nxdag.predescessors(node1)