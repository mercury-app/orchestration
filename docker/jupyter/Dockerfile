# original source - https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile

ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

USER root

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install -yq --no-install-recommends \
    vim

# allow mercuri which runs on port 5000 to embed jupyter notebook
RUN echo 'c.NotebookApp.tornado_settings = { \
    "headers": { \
    "Content-Security-Policy": "frame-ancestors 'self' http://localhost:5000", \
    "Access-Control-Allow-Origin": "http://locahost:5000", \
    } \
    }' >> /home/jovyan/.jupyter/jupyter_notebook_config.py

# create an empty untitled.ipynb 
RUN mkdir work/scripts/
COPY create_notebook.py ./create_notebook.py
RUN python3 create_notebook.py work/scripts/Untitled.ipynb

RUN ls work/scripts/
# remove all token based access to notebooks
CMD ["jupyter", "notebook", "--allow-root", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]



# Switch back to jovyan to avoid accidental container runs as root
# USER $NB_UID
