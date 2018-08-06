"""
Copyright (c) 2018 Manuel Peuster and Paderborn University
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
"""
import logging
import argparse
import networkx as nx
import numpy as np

logging.basicConfig(level=logging.DEBUG)
# setLogLevel('info')  # set Mininet loglevel
LOG = logging.getLogger("rnd_topo")


class RandomGraphTopology(object):
    """
    NetworkX Random Graph Generator
    https://networkx.github.io/documentation/stable/reference/
    generators.html?highlight=generate#module-networkx.generators.random_graphs
    """

    def __init__(self, args):
        self.args = args
        LOG.info("Initialized RandomGraphTopology: {}"
                 .format(self.args))
        all_fkt = list()
        self.G = self.generate_G()
        


    def generate_G(self):
        """
        Generate random graph with args.vertices and args. edges.
        Ref: https://networkx.github.io/documentation/stable/_modules/networkx/generators/random_graphs.html#dense_gnm_random_graph
        """
        G = nx.generators.random_graphs.dense_gnm_random_graph(
            int(self.args.vertices),
            int(self.args.edges))
        LOG.info("Generated G = (V, E) = ({}, {})"
                 .format(len(G.nodes()), len(G.edges())))
        return G


def parse_args():
    parser = argparse.ArgumentParser(
        description="Random Graph Topology Generator")

    parser.add_argument(
        "-V",
        "--vertices",
        help="No. of vertices",
        required=False,
        default=5,
        dest="vertices")

    parser.add_argument(
        "-E",
        "--edges",
        help="No. of edges",
        required=False,
        default=5,
        dest="edges")

    return parser.parse_args()

def main():
    args = parse_args()
    args.r_id = 0
    t = RandomGraphTopology(args)
    # t.cli()
    # t.stop_topology()
    #print(t.results)

if __name__ == '__main__':
    main()
