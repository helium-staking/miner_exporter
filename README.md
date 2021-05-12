# miner_exporter

Prometheus exporter for the [Helium miner (validator)](https://github.com/helium/miner). Using prometheus_client, this code exposes metrics from the helium miner to a prometheus compatible server.

This is only the exporter, which still requires a **prometheus server** for data and **grafana** for the dashboard. Prometheus and Grafana servers can run on an external machine, the same machine as the miner, or possibly using a cloud service.

Note [port 9825 is the 'reserved' port for this specific exporter](https://github.com/prometheus/prometheus/wiki/Default-port-allocations). Feel free to use whatever you like, of course, but you won't be able to dial 9VAL on your phone.

## Running via Docker

Using the docker file, you can run this with Docker or docker-compose! Both of these expose Prometheus on 9825, feel free to choose your own port. The images are hosted on [GHCR](https://github.com/users/tedder/packages/container/package/miner_exporter).

### Docker client

```
docker run -p 9825:9825 -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/helium-staking/miner_exporter:latest
```

### Docker-Compose

Using your existing docker-compose file, add the section for the exporter (below). When you're done, run `docker-compose up -d` as usual. That's it!

```
version: "3"
services:
  validator:
    image: quay.io/team-helium/validator:latest-val-amd64
    container_name: validator
...
  miner_exporter:
    image: ghcr.io/tedder/miner_exporter:latest
    container_name: miner_exporter
    volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    ports:
    - "9825:9825"
```

## Running locally

On the miner machine:

install python3

```
pip install prometheus_client psutil docker
```

Details on the libraries:

- [client_python](https://github.com/prometheus/client_python)
- [psutil](https://github.com/giampaolo/psutil)
- [docker](https://pypi.org/project/docker/)
