## Running on a local computer

This app can be run inside a docker container. You can build your own
container, or download one from the git repo.

### Build a docker container

A docker container can be built from either
`docker/Dockerfile` or `docker/Dockerfile-dev`.

When running locally, I use `Dockerfile-dev`, and I mount the directory
with my github repo to the working directory `/app/dev`.  That way,
code on my laptop is used by the streamlit app, so its easy to modify
the code and see the resulting change.

The build command should be something like:

`docker build -f docker/Dockerfile-dev -t peviewer:v1 .`

### Running for development

If using the Dockerfile-dev build, I run the container with these settings:

Bind mounts:  source: `/path/to/gitrepo/`   destination: `/app/dev`

Ports:  `8500:8501`


### Or, use a pre-built docker container

Pre-built docker containers with everything installed are available here:
https://github.com/jkanner/pe-viewer/pkgs/container/pe-viewer

Each container corresponds to a commit into the github repo.




