import networkx as nx
import logging
from typing import List, Dict
from uuid import uuid4

from networkx.algorithms.dag import ancestors

from mercury.node import MercuryNode
from mercury.edge import MercuryEdge

logger = logging.getLogger(__name__)


class MercuryDag:

    def __init__(self, id=None):
        if id is not None:
            self.id = id
        else:
            self.id = uuid4().hex
        self._nxdag = nx.DiGraph()
        self._state: str = None

    @property
    def nodes(self) -> List[MercuryNode]:
        return list(self._nxdag.nodes)

    @property
    def edges(self) -> list:
        return [_[2]["object"] for _ in self._nxdag.edges(data=True)]

    def add_node(self, node: MercuryNode) -> None:

        def is_port_in_use(port):
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0

        while is_port_in_use(node.jupyter_port):
            node.jupyter_port += 1
        logger.info(f"Starting container and mapping to port {node.jupyter_port}")

        self._nxdag.add_node(node, id=node.id)

    def remove_node(self, node: MercuryNode) -> None:
        self._nxdag.remove_node(node)

    def add_edge(self, edge: MercuryEdge) -> None:
        # not the most elegant, to do: change
        assert edge.source_node
        assert edge.dest_node

        self._nxdag.add_edge(edge.source_node, edge.dest_node, object=edge)

    def remove_edge(self, edge: MercuryEdge) -> None:
        assert edge.source_node
        assert edge.dest_node
        self._nxdag.remove_edge(edge.source_node, edge.dest_node)

    def get_node(self, id: str) -> MercuryNode:
        node_search = [_ for _ in self._nxdag.nodes if _.id == id]
        assert len(node_search) < 2
        if len(node_search) == 1:
            return node_search[0]

    def get_edge(self, id: str) -> MercuryEdge:
        edge_search = [_ for _ in self.edges if _.id == id]
        assert len(edge_search) < 2
        if len(edge_search) == 1:
            return edge_search[0]

    def get_edge_from_nodes(
        self, source_node_id: str, destination_node_id: str
    ) -> MercuryEdge:
        edge_search = [
            _
            for _ in self.edges
            if _.source_node.id == source_node_id
            and _.dest_node.id == destination_node_id
        ]
        assert len(edge_search) < 3
        if len(edge_search) == 1:
            return edge_search[0]

    def get_valid_connections_for_nodes(self) -> Dict[MercuryNode, List[MercuryNode]]:
        all_nodes = set(self._nxdag.nodes)
        valid_edges_per_nodes = {}
        for node in self._nxdag.nodes:
            impossible_descendants = ancestors(self._nxdag, node)
            impossible_descendants.add(node)
            possible_descendants = all_nodes.difference(impossible_descendants)
            valid_edges_per_nodes[node] = (
                list(possible_descendants) if possible_descendants is not None else []
            )

        return valid_edges_per_nodes

    def get_node_edges(self, node_id: str) -> List[MercuryEdge]:
        edge_search = [
            _
            for _ in self.edges
            if _.source_node.id == node_id or _.dest_node.id == node_id
        ]
        return edge_search

    def get_node_input_edges(self, node_id: str) -> List[MercuryEdge]:
        edge_search = [_ for _ in self.edges if _.dest_node.id == node_id]
        return edge_search

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, workflow_state: str) -> None:
        self._state = workflow_state

    async def run_dag(self, n_max_parallel: int = 2):

        nodes_executed = []
        # use brute force to find a node ready for execution
        node_to_execute = True
        while node_to_execute:
            node_to_execute = False
            for node in self._nxdag.nodes:
                if node.id in nodes_executed:
                    continue

                if not node.input:
                    logger.info("executing node with no inputs")
                    node_to_execute = node
                    break

                input_edges = self.get_node_input_edges(node.id)
                if all(
                    [
                        input_edge.source_node.id in nodes_executed
                        for input_edge in input_edges
                    ]
                ):
                    node_to_execute = node
                    break

            if node_to_execute:
                logger.info(f"Executing node: {node_to_execute.id}")

                node_to_execute.run()
                import asyncio

                node_to_execute.mercury_container.notebook_exec_exit_code = -1
                while True:
                    # await here to send kernel status message, and receive stop signals
                    await asyncio.sleep(1)
                    logger.info(f"dag state : {self._state}")
                    if self._state == "stop":
                        logger.info(
                            "Stopping workflow run. Sending stop signal to running node"
                        )
                        node_stop_exit_code, _ = node_to_execute.stop()
                        logger.info(f"Node stop exit code: {node_stop_exit_code}")

                    if node_to_execute.mercury_container.notebook_exec_exit_code != -1:
                        break

                if node_to_execute.mercury_container.notebook_exec_exit_code == 1:
                    logger.info(
                        "Notebook did not execute successfully or was stopped in the middle.\
                        Stopping workflow execution"
                    )
                    return 1

                assert node_to_execute.mercury_container.notebook_exec_exit_code == 0
                logger.info("Notebook executed successfully")
                nodes_executed.append(node_to_execute.id)

        logger.info(f"{len(nodes_executed)} nodes executed successfully")
        logger.info("Workflow execution successful")
        return 0
