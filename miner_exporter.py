#!/usr/bin/env python3

# external packages
import prometheus_client
import psutil

# internal packages
import time
import subprocess
import docker
import sys
import os

# time to sleep between scrapes
UPDATE_PERIOD = int(os.environ.get('UPDATE_PERIOD', 30))
VALIDATOR_CONTAINER_NAME = os.environ.get('VALIDATOR_CONTAINER_NAME', 'validator')

# prometheus exporter types Gauge,Counter,Summary,Histogram,Info and Enum
SYSTEM_USAGE = prometheus_client.Gauge('system_usage',
                                       'Hold current system resource usage',
                                       ['resource_type'])
VAL = prometheus_client.Gauge('validator_height',
                              'Height of the blockchain',
                              ['resource_type'])

INCON = prometheus_client.Gauge('validator_inconsensus',
                              'Is validator currently in consensus group',
                              ['resource_type'])
BLOCKAGE = prometheus_client.Gauge('validator_block_age',
                              'Age of the current block',
                             ['resource_type'])
PENALTY = prometheus_client.Gauge('validator_hbbft_penalty',
                              'HBBFT Penalty metrit from perf ',
                             ['resource_type'])

def stats():
  dc = docker.DockerClient()
  docker_container = dc.containers.get(VALIDATOR_CONTAINER_NAME)

  # collect total cpu and memory usage. Might want to consider just the docker
  # container with something like cadvisor instead
  SYSTEM_USAGE.labels('CPU').set(psutil.cpu_percent())
  SYSTEM_USAGE.labels('Memory').set(psutil.virtual_memory()[2])

  # grab the local blockchain height
  out = docker_container.exec_run('miner info height')
  print(out.output)
  VAL.labels('Height').set(out.output.split()[1])

  # need to fix this. hotspot name really should only be queried once
  out = docker_container.exec_run('miner info name')
  print(out.output)
  hotspot_name = out.output.rstrip(b"\n")
  hotspot_name_str = hotspot_name.decode('utf-8')

  # check if currently in consensus group
  out = docker_container.exec_run('miner info in_consensus')
  print(out.output)
  incon = 0
  if out.output.rstrip(b"\n") == 'true':
    incon=1
  INCON.labels(hotspot_name_str).set(incon)

  # collect current block age
  out = docker_container.exec_run('miner info block_age')
  BLOCKAGE.labels('BlockAge').set(out.output)

  # parse the hbbft performance table for the penalty field
  out = docker_container.exec_run('miner hbbft perf')
  print(out.output)
  results = out.output.split(b"\n")
  for line in results:
    if hotspot_name in line:
      results = line.split()[12]
      PENALTY.labels('Penalty').set(results)


if __name__ == '__main__':
  prometheus_client.start_http_server(8000)
  while True:
    stats()

    # sleep 30 seconds
    time.sleep(UPDATE_PERIOD)

