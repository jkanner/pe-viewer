## Running on a local computer

The easiest way to run this app locally is with **Docker Compose** from the root of the repository (where `docker-compose.yml` lives).

### Build images to run locally for development and production

```shell
docker compose build
```

This will build the images for the development and production servers.
To start the servers, run:

```shell
docker compose up
```

or start them from the Docker Desktop GUI.

`docker compose up` starts **two** services built from the same image (`docker/Dockerfile`):

| Service         | Purpose | URL                    |
|----------------|---------|------------------------|
| **peviewer-dev** | Development: your repo’s `streamlit-app.py` is bind-mounted into the container, so edits on disk show up in the app. | http://localhost:8502 |
| **peviewer-prod** | Production-like: no bind mounts; the app is what will be copied into the image at build time, similar to a deployed container. | http://localhost:8501 |

You can open both in the browser at the same time.

Typical workflow:

1. `docker compose build` (first time, or after dependency or Dockerfile changes)
2. `docker compose up`
3. Use **8502** while working on `streamlit-app.py`; use **8501** to review.

To start a single service: `docker compose up peviewer-dev` or `docker compose up peviewer-prod`.

### Manual image build (optional)

If you are not using Compose, you can still build the image yourself, for example:

```
docker build -f docker/Dockerfile -p 8501:8501 -t peviewer:local .
```

### Pre-built images

Pre-built images tied to repo commits are published here:

https://github.com/jkanner/pe-viewer/pkgs/container/pe-viewer

Pull and run those images if you prefer not to build locally.
