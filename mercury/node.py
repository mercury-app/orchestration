import copy
import logging
import os

from networkx.algorithms.coloring.greedy_coloring import strategy_largest_first
from server.views import workflow
from uuid import uuid4


from mercury.docker_client import docker_cl
from mercury.constants import (
    DEFAULT_DOCKER_VOL_MODE,
    BASE_DOCKER_IMAGE_NAME,
    BASE_DOCKER_HOME,
    BASE_DOCKER_WORK_DIR,
)
from mercury.container import MercuryContainer

logger = logging.getLogger(__name__)


class MercuryNode:
    def __init__(
        self,
        name: str,
        id: str = None,
        input: list = None,
        output: list = None,
        docker_img_name: str = None,
        docker_img_tag: str = None,
        docker_volume: str = None,  # TODO: make a default docker volume
        container_id: str = None,
        workflow_id: str = None,
    ):
        self._name = name

        self.id = id if id is not None else uuid4().hex
        self._input = input
        self._output = output

        self._docker_img_name = (
            docker_img_name if docker_img_name is not None else copy.copy(self.id)
        )
        self._docker_img_tag = docker_img_tag if docker_img_tag is not None else "0"
        self._docker_volume = docker_volume

        if container_id is not None:
            self._mercury_container = MercuryContainer.find(container_id)
        else:
            self._mercury_container: MercuryContainer = None

        self._notebook_dir = ""
        self._jupyter_port = 8880
        self._workflow_id = workflow_id

    def __str__(self) -> str:
        return self.id

    @property
    def name(self) -> str:
        return self._name

    @property
    def notebook_dir(self) -> str:
        return self._notebook_dir

    @notebook_dir.setter
    def notebook_dir(self, dir: str):
        self._notebook_dir = dir

    @property
    def mercury_container(self) -> MercuryContainer:
        return self._mercury_container

    @property
    def input(self) -> list:
        return self._input

    @input.setter
    def input(self, input_fields: list) -> None:
        self._input = input_fields

    @property
    def output(self) -> list:
        return self._output

    @output.setter
    def output(self, output_fields: list) -> None:
        self._output = output_fields

    @property
    def docker_img_name(self) -> str:
        return self._docker_img_name

    @property
    def docker_img_tag(self) -> str:
        return self._docker_img_tag

    @property
    def jupyter_port(self) -> int:
        return self._jupyter_port

    @jupyter_port.setter
    def jupyter_port(self, port: int) -> int:
        self._jupyter_port = port

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, id: str):
        self._workflow_id = id

    def initialise_container(self):
        """This should start the jupyter notebook inside the docker container

        Parameters
        ----------
        container : [type]
            [description]

        Returns
        -------
        str
            container id of the running container
        """
        logger.info(f"AAAaaaa  {self._workflow_id}")
        container_run = docker_cl.containers.run(
            BASE_DOCKER_IMAGE_NAME,
            environment={"MERCURY_NODE": self.id, "WORKFLOW_ID": self._workflow_id},
            volumes={
                f"{self._notebook_dir}": {
                    "bind": f"{BASE_DOCKER_HOME}/{BASE_DOCKER_WORK_DIR}",
                    "mode": DEFAULT_DOCKER_VOL_MODE,
                }
            },
            detach=True,
            ports={"8888/tcp": self._jupyter_port},
        )
        self._mercury_container = MercuryContainer(container_run)
        exit_code, output = self._mercury_container.container.exec_run(
            f"python3 -m container.cli create-notebook --name={BASE_DOCKER_WORK_DIR}/{self._name}.ipynb"
        )
        print(exit_code, output)

        logger.info(f"Initialized container {self._mercury_container.container_id}")

    def restart_container(self):
        self._mercury_container.container.restart()

    def commit(self) -> str:
        self._docker_img_tag = str(int(self._docker_img_tag) + 1)
        self._mercury_container.commit(
            build_img_name=self._docker_img_name, build_img_tag=self._docker_img_tag
        )

    def get_run_log(self) -> str:
        pass

    # run can either start a new container if a container is not
    # running for the node, or reuse the running container for running
    # the workflow in the notebook.
    def run(self) -> None:
        """Run the node end to end.

        Returns
        -------
        str
            [description]
        """
        logger.info("Running notebook in container")

        if not self._mercury_container:
            self.initialise_container()
        assert self._mercury_container.container_state["Running"]

        logger.info(f"Running in container {self._mercury_container.container_id}")
        cmd = "python3 -m container.cli run-notebook --notebook_path='work/scripts/Untitled.ipynb'"
        # detached state could be used for running multiple containers together in workflow run
        self._mercury_container.container.exec_run(cmd, detach=True)

    def stop(self) -> str:
        logger.info("stopping notebook in container")
        logger.info(
            f"stopping process {self._mercury_container.notebook_exec_pid} in container"
        )

        assert self._mercury_container._notebook_exec_pid

        cmd = f"kill {self._mercury_container._notebook_exec_pid}"
        exit_code, output = self._mercury_container.container.exec_run(
            cmd, detach=False
        )
        self._mercury_container.notebook_exec_exit_code = 1
        return exit_code, output

    def execute_code(self, code) -> tuple:
        return self._mercury_container.execute_code(code)

    def write_output_to_json(
        self, source_outputs: list, dest_inputs: list, json_fp: str
    ) -> tuple:
        return self._mercury_container.write_variables_to_json(
            source_outputs, dest_inputs, json_fp
        )

    def cleanup_before_deletion(self):
        self.mercury_container.container.kill()

        notebook_file_path = f"{self._notebook_dir}/{self._name}.ipynb"
        if os.path.isfile(notebook_file_path):
            os.remove(notebook_file_path)
