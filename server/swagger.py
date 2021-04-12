import json
from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec_webframeworks.tornado import TornadoPlugin


def generate_swagger_file(handlers, file_location):
    """Automatically generates Swagger spec file based on RequestHandler
    docstrings and saves it to the specified file_location.
    """

    # Starting to generate Swagger spec file. All the relevant
    # information can be found from here https://apispec.readthedocs.io/
    spec = APISpec(
        title="Caduceus API",
        version="0.0.1",
        openapi_version="3.0.2",
        info=dict(description="Documentation for the Caduceus API"),
        plugins=[TornadoPlugin()],
        servers=[
            {
                "url": "http://localhost:8888/",
                "description": "Local environment",
            },
        ],
    )
    # Looping through all the handlers and trying to register them.
    # Handlers without docstring will raise errors. That's why we
    # are catching them silently.
    for handler in handlers:
        try:
            spec.path(urlspec=handler)
        except APISpecError:
            pass

    # Write the Swagger file into specified location.
    with open(file_location, "w", encoding="utf-8") as file:
        json.dump(spec.to_dict(), file, ensure_ascii=False, indent=4)