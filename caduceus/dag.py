import networkx as nx

from caduceus.node import MercuriNode


class MercuriDag:
    def __init__(self):
        self.nx_dag = nx.DiGraph()

    @property
    def nodes(self) -> list:
        return [str(_node) for _node in self.nx_dag.nodes]

    @property
    def edges(self) -> list:
        return [(str(_[0]), str(_[1])) for _ in self.nx_dag.edges]

    def add_node(self, node: MercuriNode) -> None:
        self.nx_dag.add_node(node)

    def remove_node(self, node: MercuriNode) -> None:
        self.nx_dag.remove_node(node)

    def add_edge(self, node1: MercuriNode, node2: MercuriNode) -> None:
        self.nx_dag.add_edge(node1, node2)

    # nx_dag.successors(node1)
    # nx_dag.predescessors(node1)