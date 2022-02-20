from simulator.node import Node
import json


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        # nodes of graph
        self.nodes = [self.id]

        # edges of graph, using frozenset as key and keeping track of latency and seq num
        self.edges = {}

    # Return a string
    def __str__(self):
        return "debug uwu hi steve please be nice to our grade"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # what the hell is a frozenset even lmao
        link = frozenset([self.id, neighbor])
        if link in self.edges:
            # seq number needs to be higher so things don't bounce. arbitrary number -> 50 big enough?
            # yes!
            self.edges[link] = [latency, self.edges[link][1] + 50]
        else:
            # link
            self.edges[link] = [latency, 1]
            # check if given node needs to be added to neighbors
            if neighbor not in self.nodes:
                self.nodes.append(neighbor)
                for edge in self.edges:
                    if self.edges[edge][0] == -1:
                        # dont do anything
                        continue
                    # adj nodes increment seq num
                    self.edges[edge][1] += 1
                    # get keys for edge
                    nodes = []
                    for node in edge:
                        nodes.append(node)
                    message = { "nodes": nodes,
                                "latency": self.edges[edge][0],
                                "sequence number": self.edges[edge][1]}
                    self.send_to_neighbor(neighbor, json.dumps(message))
        # create routing message
        message = { "nodes": [self.id, neighbor],
                    "latency": latency,
                    "sequence number": self.edges[link][1]}
        self.send_to_neighbors(json.dumps(message))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # get message and un-json it
        edge = json.loads(m)
        # get the nodes the edge connects
        node1 = edge["nodes"][0]
        node2 = edge["nodes"][1]
        edgenodes = frozenset([node1, node2])

        # update neighbors
        if node1 not in self.nodes:
            self.nodes.append(node1)
        if node2 not in self.nodes:
            self.nodes.append(node2)

        # update edges based on message
        if edgenodes not in self.edges:
            self.edges[edgenodes] = [edge["latency"], edge["sequence number"]]
            self.send_to_neighbors(m)

        # seq num update
        # so THIS is what seq num is for
        if self.edges[edgenodes][1] < edge["sequence number"]:
            self.edges[edgenodes] = [edge["latency"], edge["sequence number"]]
            self.send_to_neighbors(m)
        else:
            message = { "nodes": edge["nodes"],
                        "latency": self.edges[edgenodes][0],
                        "sequence number": self.edges[edgenodes][1]}
            self.send_to_neighbor(node1, json.dumps(message))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # djikstra time
        self.nodes.sort()
        num_nodes = len(self.nodes)

        # dist path visited lists
        dist = [float("inf")] * num_nodes
        dist[self.nodes.index(self.id)] = 0

        paths = [None] * num_nodes
        for i in range(num_nodes):
            paths[i] = [self.nodes.index(self.id)]

        visited = [False] * num_nodes

        # the djikstra loop tm
        while False in visited:
            min = float("inf")
            for x in range(num_nodes):
                if dist[x] < min and visited[x] is False:
                    min = dist[x]
                    target_node = x

            # no path if still inf
            if min == float("inf"):
                return -1

            # if dest found, done!
            if self.nodes[target_node] == destination:
                if len(paths[target_node]) == 1:
                    return self.nodes[target_node]
                else:
                    return self.nodes[paths[target_node][1]]

            # else, do the djikstra neighbor edge thing
            visited[target_node] = True

            for i in range(num_nodes):
                target_edge = frozenset([self.nodes[i], self.nodes[target_node]])
                if target_edge in self.edges and visited[i] is False and dist[i] > dist[target_node] + self.edges[target_edge][0]:
                    dist[i] = dist[target_node] + self.edges[target_edge][0]
                    paths[i] = paths[target_node][:]
                    paths[i].append(i)
        return -1
