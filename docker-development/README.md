# Wave app development in Docker container

If you either don't want to install python on your machine or just want to have the dev env same for everyone, Docker is the right tool for the job.

Wave is no different from other web frameworks which means you can even reuse your existing docker / docker-compose files.

## Prerequisites

* Docker installed - <https://www.docker.com/>

## Installation

Linux / MacOS:

```sh
git clone https://github.com/h2oai/wave-apps.git
cd wave-apps/docker-development
docker build . -t wave_local_dev
docker run -p 10101:10101 -v $(pwd)/src:/app/src wave_local_dev:latest
```

TODO: Windows

## Features

Once the above steps are done, you should see the sample app at <http://localhost:10101> in your browser. What's more, any changes within the `src` directory should be picked up and reflected as well.

More info: [Docker docs](https://docs.docker.com/)
