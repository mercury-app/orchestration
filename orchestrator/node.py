from orchestrator.docker_client import docker_cl
from orchestrator.constants import DEFAULT_DOCKER_VOL_MODE, DOCKER_COMMON_VOLUME

import logging

logging.basicConfig(level=logging.INFO)


class MercuriNode:
    def __init__(
        self,
        input: dict,
        output: dict = None,
        docker_volume: str = None,
        docker_img_name: str = None,
    ):
        self._input = input
        self._output = output
        self._run_status = None
        self._docker_img_name = docker_img_name
        self._docker_volume = docker_volume

    def trigger(self) -> str:
        logging.info(f"Running {self._docker_img_name}")
        container = docker_cl.containers.run(
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
        return container.id

    def get_run_log(self) -> str:
        pass
