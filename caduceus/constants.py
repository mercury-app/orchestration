import os

DOCKER_COMMON_VOLUME = os.path.abspath("caduceus/experimentation/common_volume")
BASE_DOCKER_IMAGE_NAME = "caduceus-base"
BASE_DOCKER_BIND_VOLUME = "/usr/src/app"
DEFAULT_DOCKER_VOL_MODE = "rw"
