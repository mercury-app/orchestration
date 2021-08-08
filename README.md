# Mercury Orchestration

This repository contains all the code for the service that orchestrates the
execution of workflows and underlying notebooks.

### Usage

#### Install dependencies and activate virtual environment

Install poetry - https://python-poetry.org/docs/basic-usage/

```sh
cd orchestration
poetry install
poetry shell
```

#### Start the server

```sh
python3 -m server.app
```

Go to localhost:8888

### Contributing

If you install a new dependency or update an existing dependency, commit the `poetry.lock` file as well.

### Build the docker image for Mercury in the container repository 
https://github.com/mercury-app/container#build-docker-image


### API documentation

Docs in Postman
https://documenter.getpostman.com/view/2281095/TzK16F5A

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/7adb5e7a82f5292336d7)
