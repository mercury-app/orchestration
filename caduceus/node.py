import logging
from uuid import uuid4

from caduceus.docker_client import docker_cl
from caduceus.constants import (
    DEFAULT_DOCKER_VOL_MODE,
    DOCKER_COMMON_VOLUME,
    BASE_DOCKER_IMAGE_NAME,
    BASE_DOCKER_BIND_VOLUME,
)
from caduceus.container import CaduceusContainer

logger = logging.getLogger(__name__)


class MercuriNode:
    def __init__(
        self,
        input: dict = None,
        output: dict = None,
        docker_volume: str = None,  # TODO: make a default docker volume
        docker_img_name: str = None,
    ):
        self.id = uuid4().hex
        self._input = input
        self._output = output

        self._docker_img_name = docker_img_name
        self._docker_volume = docker_volume

        # Here, the container is itself changing on every execution
        self._caduceus_container: CaduceusContainer = None

    def __str__(self) -> str:
        return self.id

    @property
    def caduceus_container(self) -> CaduceusContainer:
        return self._caduceus_container

    @property
    def input(self) -> dict:
        return self._input

    @input.setter
    def input(self, input_fields: dict) -> None:
        self._input = input_fields

    @property
    def output(self) -> dict:
        return self._output

    @output.setter
    def output(self, output_fields: dict) -> None:
        self._output = output_fields

    @property
    def docker_img_name(self) -> str:
        return self._docker_img_name

    @docker_img_name.setter
    def docker_img_name(self, img_name: str) -> None:
        self._docker_img_name = img_name

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
        )
        self._caduceus_container = CaduceusContainer(container_run)
        logger.info(f"Initialised container {self._caduceus_container.container_id}")

    def commit(
        self,
        build_img_name: str = None,
        build_img_tag: str = "latest",
    ) -> str:
        self._caduceus_container.commit(repository=build_img_name, tag=build_img_tag)

    def get_run_log(self) -> str:
        pass

    # trigger can either start a new container if a container is not
    # running for the node, or reuse the running container for running
    # the workflow in the notebook.
    def trigger(self) -> str:

        if self._caduceus_container:
            if self._caduceus_container.container_state["Running"]:
                logging.info(
                    f"Running in container {self._caduceus_container.container_id}"
                )
                exit_code, output = self._caduceus_container.container.exec_run(
                    "echo 'dasdasds'"
                )
                logger.info(exit_code, output)
                return output

        else:
            self.initialise_container()
            exit_code, output = self._caduceus_container.container.exec_run(
                "echo 'dasdasds'"
            )
            logging.info(
                f"Running in container {self._caduceus_container.container_id}"
            )
            logger.info(exit_code, output)
            return output
