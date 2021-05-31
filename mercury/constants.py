import os

DOCKER_COMMON_VOLUME = os.path.abspath("mercury/experimentation/common_volume")
BASE_DOCKER_IMAGE_NAME = "jupyter-mercury"
BASE_DOCKER_BIND_VOLUME = "/usr/src/app"
DEFAULT_DOCKER_VOL_MODE = "rw"
