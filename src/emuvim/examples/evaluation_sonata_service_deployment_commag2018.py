"""
Copyright (c) 2018 Paderborn University
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the Paderborn University
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
"""

import logging
import argparse
import subprocess
import time
import pandas as pd
from mininet.log import setLogLevel
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint
from mininet.node import RemoteController
import os

logging.basicConfig(level=logging.INFO)

class Topology1(object):

    def __init__(self, args):
        self.args = args
        self.results = {
            "time_emulator_boot": 0,
            "time_service_onboard": 0,
            "time_service_instantiate": 0,
            "time_total": 0,
            "mode": args.mode,
            "pops": args.topology,
            "service": args.service,
            "repetition_id": args.r_id
        }

    def create(self):
        self.net = DCNetwork(controller=RemoteController, monitor=False, enable_learning=False)
        self.dc1 = self.net.addDatacenter("dc1")
        # add the command line interface endpoint to each DC (REST API)
        #self.rapi1 = RestApiEndpoint("0.0.0.0", 5001)
        #self.rapi1.connectDCNetwork(self.net)
        #self.rapi1.connectDatacenter(self.dc1)
        #self.rapi1.start()
        # add the SONATA dummy gatekeeper to each DC
        self.sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=False, eval_args=self.args)
        self.sdkg1.connectDatacenter(self.dc1)
        self.sdkg1.start()

    def start(self):
        self.net.start()

    def cli(self):
        self.net.CLI()

    def stop(self):
        self.net.stop()

    def timer_start(self, name):
        self.results[name] = time.time()
        print("timer start {}@{}".format(name, self.results[name]))

    def timer_stop(self, name):
        self.results[name] = time.time() - self.results[name]
        print("timer stop {} = {}".format(name, self.results[name]))


class Topology2(Topology1):

    def create(self):
        self.net = DCNetwork(controller=RemoteController, monitor=False, enable_learning=False)
        self.dc1 = self.net.addDatacenter("dc1")
        self.dc2 = self.net.addDatacenter("dc2")
        self.net.addLink("dc1", "dc2")
        # add the SONATA dummy gatekeeper to each DC
        self.sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=False, eval_args=self.args)
        self.sdkg1.connectDatacenter(self.dc1)
        self.sdkg1.connectDatacenter(self.dc2)
        self.sdkg1.start()


class SonataClient(object):

    def __init__(self, args, endpoint="127.0.0.1:5000"):
        self.args = args
        self.endpoint = endpoint

    def on_board(self, pkg_path):
        cmd = ("curl -i -X POST -F package=@{} http://{}/packages"
               .format(pkg_path, self.endpoint))
        print("On-boarding cmd: {}".format(cmd))         
        subprocess.call(cmd,
                        shell=True)

    def instantiate(self):
        cmd = ("curl -i -X POST http://%r/instantiations -d '{}'" % self.endpoint)
        print("Instantiate cmd: {}".format(cmd))         
        subprocess.call(cmd,
                        shell=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Emulator platform evaluation topology")

    parser.add_argument(
        "-m",
        "--mode",
        help="Mode: docker|vm, default=docker",
        required=False,
        default="docker",
        dest="mode")

    parser.add_argument(
        "-t",
        "--topology",
        help="Topology: 1|2, default=1",
        required=False,
        default="1",
        dest="topology")

    parser.add_argument(
        "-r",
        "--repetitions",
         help="Number of repetitions, default=1",
        required=False,
        default="1",
        dest="repetitions")

    parser.add_argument(
        "-s",
        "--service",
         help="Service to be used (path to *.son)",
        required=False,
        default="examples/sonata_pkgs/eu.sonata-nfv.vfoward-2-1-test.0.2.1-docker.son",
        dest="service")

    parser.add_argument(
        "--cli",
        help="Boot to CLI.",
        required=False,
        default=False,
        dest="cli",
        action="store_true")

    parser.add_argument(
        "-o",
        "--output",
         help="Output path for CSV, default=results.csv",
        required=False,
        default="results.csv",
        dest="output")

    return parser.parse_args()


def run_experiments(args):
    results = list()
    for i in range(0, int(args.repetitions)):
        args.r_id = i
        c = SonataClient(args)
        # start topology
        if int(args.topology) == 2:
            topo = Topology2(args)
        else:
            topo = Topology1(args)
        topo.timer_start("time_total")
        topo.timer_start("time_emulator_boot")
        topo.create()
        topo.start()
        topo.timer_stop("time_emulator_boot")
        topo.timer_start("time_service_onboard")
        # on_board_service
        c.on_board(args.service)
        topo.timer_stop("time_service_onboard")
        # start service
        topo.timer_start("time_service_instantiate")
        c.instantiate()
        topo.timer_stop("time_service_instantiate")
        topo.timer_stop("time_total")
        # wait for service
        if args.cli:
            topo.cli()
        else:
            time.sleep(3)
        # stop service/topology
        topo.stop()
        # force cleanup?
        time.sleep(1)
        subprocess.call("mn -c", shell=True)
        time.sleep(1)
        # result
        results.append(topo.results)
        print("### Result: {}".format(topo.results))
    return results
        
    

def main():
    setLogLevel('info')
    args = parse_args()
    print("Args: {}".format(args))
    results = run_experiments(args)
    df = pd.DataFrame(results)
    print(df)
    # store results in CSV
    df.to_csv(args.output)
    print("Wrote results to {}".format(args.output))

    


if __name__ == '__main__':
    main()
