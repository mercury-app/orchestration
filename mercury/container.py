import docker
import logging

logger = logging.getLogger(__name__)


class MercuryContainer:
    def __init__(self, container: docker.models.containers.Container):
        self._container: docker.models.containers.Container = container
        self._container_id: str = container.id
        self._container_state: dict = None
        self._kernel_state: str = None

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

    @property
    def kernel_state(self) -> str:
        return self._kernel_state

    @kernel_state.setter
    def kernel_state(self, kernel_state: str) -> str:
        self._kernel_state = kernel_state

    def commit(
        self,
        build_img_name: str = None,
        build_img_tag: str = "latest",
    ):
        logger.info(
            f"Committing the container to image {build_img_name}:{build_img_tag}"
        )
        if build_img_name is None:
            build_img_name = self._docker_img_name
        logging.info(f"Building new docker image: {build_img_name}:{build_img_tag}")
        if self._container is None:
            logger.error("This node does not have an attached container")

        assert self.container_state["Running"]
        self._container.commit(repository=build_img_name, tag=build_img_tag)

    def execute_code(self, code: str) -> tuple:
        logger.info("Executing code in docker container")
        logger.info(code)

        cmd = f"python3 -m container.cli execute-code --code '{code}'"
        logger.info(f"Docker exec command: {cmd}")
        exit_code, container_output = self._container.exec_run(cmd)

        if exit_code != 0:
            logger.warning("code did not run successfully in kernel")
            print(container_output)

        return exit_code, container_output

    def write_variables_to_json(
        self, source_outputs: list, dest_inputs: list, json_fp: str
    ) -> tuple:
        logger.info("Writing variables from docker environment")

        source_outputs_list = "|".join(source_outputs)
        dest_inputs_list = "|".join(dest_inputs)
        cmd = f"python3 -m container.cli write-kernel-variables-to-json --source_outputs '{source_outputs_list}' --dest_inputs '{dest_inputs_list}'  --json '{json_fp}'"
        logger.info(f"Docker exec command: {cmd}")

        exit_code, container_output = self._container.exec_run(cmd)

        if exit_code != 0:
            logger.warning("code did not run successfully in kernel")
            print(container_output)

        return exit_code, container_output
