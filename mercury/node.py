import logging
from uuid import uuid4
import copy


from mercury.docker_client import docker_cl
from mercury.constants import (
    DEFAULT_DOCKER_VOL_MODE,
    DOCKER_COMMON_VOLUME,
    BASE_DOCKER_IMAGE_NAME,
    BASE_DOCKER_BIND_VOLUME,
)
from mercury.container import MercuryContainer

logger = logging.getLogger(__name__)


class MercuryNode:
    def __init__(
        self,
        input: list = None,
        output: list = None,
        docker_volume: str = None,  # TODO: make a default docker volume
        docker_img_name: str = None,
    ):
        self.id = uuid4().hex
        self._input = input
        self._output = output

        self._docker_img_name = copy.copy(self.id)
        self._docker_volume = docker_volume
        self._docker_img_tag = "0"

        # Here, the container is itself changing on every execution
        self._mercury_container: MercuryContainer = None
        self._jupyter_port: int = 8880

    def __str__(self) -> str:
        return self.id

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
        container_run = docker_cl.containers.run(
            BASE_DOCKER_IMAGE_NAME,
            environment=self._input,
            volumes={
                DOCKER_COMMON_VOLUME: {
                    "bind": BASE_DOCKER_BIND_VOLUME,
                    "mode": DEFAULT_DOCKER_VOL_MODE,
                }
            },
            detach=True,
            ports={"8888/tcp": self._jupyter_port},
        )
        self._mercury_container = MercuryContainer(container_run)
        logger.info(f"Initialised container {self._mercury_container.container_id}")

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
    def run(self) -> str:
        """Run the node end to end.

        Returns
        -------
        str
            [description]
        """
        logger.info("Running container")

        if not self._mercury_container:
            self.initialise_container()
        assert self._mercury_container.container_state["Running"]

        logger.info(f"Running in container {self._mercury_container.container_id}")
        exit_code, output = self._mercury_container.container.exec_run(
            "echo 'dasdasds'"
        )
        return exit_code, output
