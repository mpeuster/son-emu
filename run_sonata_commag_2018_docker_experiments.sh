#!/bin/bash

set -x
set -e

sudo python examples/evaluation_sonata_service_deployment_commag2018.py -t 1 -s examples/sonata_pkgs/eu.sonata-nfv.vfoward-2-1-test.0.2.1-docker.son -o result_docker_1pop_2vnf.csv -r 10

sudo python examples/evaluation_sonata_service_deployment_commag2018.py -t 2 -s examples/sonata_pkgs/eu.sonata-nfv.vfoward-2-1-test.0.2.1-docker.son -o result_docker_2pop_2vnf.csv -r 10

sudo python examples/evaluation_sonata_service_deployment_commag2018.py -t 1 -s examples/sonata_pkgs/eu.sonata-nfv.vfoward-8-1-test.0.8.1-docker.son -o result_docker_1pop_8vnf.csv -r 10

sudo python examples/evaluation_sonata_service_deployment_commag2018.py -t 2 -s examples/sonata_pkgs/eu.sonata-nfv.vfoward-8-1-test.0.8.1-docker.son -o result_docker_2pop_8vnf.csv -r 10
