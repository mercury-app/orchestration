import docker
import logging

logger = logging.getLogger(__name__)


class CaduceusContainer:
    def __init__(self, container: docker.models.containers.Container):
        self._container: docker.models.containers.Container = container
        self._container_id: str = container.id
        self._container_state: dict = None

    @property
    def container(self) -> docker.models.containers.Container:
        return self._container

    @container.deleter
    def container(self):
        self._container.remove()
        self._container = None
        self._container_state = None
        self._container_id = None

    @property
    def container_state(self) -> dict:
        if self._container is None:
            self._container_state = None
            return self._container_state
        self._container.reload()
        self._container_state = self._container.attrs["State"]
        return self._container_state

    @property
    def container_id(self) -> str:
        return self._container_id

    def commit(
        self,
        build_img_name: str = None,
        build_img_tag: str = "latest",
    ):
        if build_img_name is None:
            build_img_name = self._docker_img_name
        logging.info(
            f"Building new docker image: {self._docker_img_name}:{build_img_tag}"
        )
        if self._container is None:
            logger.error("This node does not have an attached container")

        assert self.container_state["Running"]
        self.container.commit(repository=build_img_name, tag=build_img_tag)
