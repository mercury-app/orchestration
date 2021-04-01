import logging
import docker
from uuid import uuid4

from caduceus.docker_client import docker_cl
from caduceus.constants import DEFAULT_DOCKER_VOL_MODE, DOCKER_COMMON_VOLUME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MercuriNode:
    def __init__(
        self,
        input: dict,
        output: dict = None,
        docker_volume: str = None,  # TODO: make a default docker volume
        docker_img_name: str = None,
    ):
        self.id = uuid4().hex
        self._input = input
        self._output = output

        self._docker_img_name = docker_img_name
        self._docker_volume = docker_volume

        # following attributes is for container instance from docker-py
        # and a dict for container-properties
        # Here, the container is itself changing on every execution
        # might flesh this out later
        self._container: docker.models.containers.Container = None
        self._container_state: dict = None

    def __str__(self) -> str:
        return self._docker_img_name

    @property
    def container(self) -> docker.models.containers.Container:
        return self._container

    @container.deleter
    def container(self):
        self._container.remove()
        self._container = None
        self._container_state = None

    @property
    def container_state(self) -> dict:
        if self._container is None:
            self._container_state = None
            return self._container_state
        self._container.reload()
        self._container_state = self._container.attrs["State"]
        return self._container_state

    @container_state.deleter
    def exit_code(self):
        self._container_state = None

    @property
    def input(self) -> dict:
        return self._input

    @input.setter
    def input(self, input_fields: dict) -> None:
        self._input = input_fields

    @property
    def docker_img_name(self) -> str:
        return self._docker_img_name

    @docker_img_name.setter
    def docker_img_name(self, img_name: str) -> None:
        self._docker_img_name = img_name

    def trigger(self) -> str:
        logging.info(f"Running {self._docker_img_name}")
        self._container = docker_cl.containers.run(
            self._docker_img_name,
            environment=self._input,
            volumes={
                DOCKER_COMMON_VOLUME: {
                    "bind": self._docker_volume,
                    "mode": DEFAULT_DOCKER_VOL_MODE,
                }
            },
            detach=True,
        )
        # TODO setter container id
        return self._container.id

    def build(
        self,
        build_img_name: str = None,
        build_img_tag: str = "latest",
    ) -> str:
        if build_img_name is None:
            build_img_name = self._docker_img_name
        logging.info(
            f"Building new docker image: {self._docker_img_name}:{build_img_tag}"
        )
        if self._container is None:
            logger.error("This node does not have an attached container")

        assert self.container_state["Running"]
        self.container.commit(repository=build_img_name, tag=build_img_tag)

    def get_run_log(self) -> str:
        pass
