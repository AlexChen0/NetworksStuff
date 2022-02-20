from simulator.node import Node
import json


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        # dictionary of links (edges), where each edge key (frozenset) keys to an array with latency (int) and seq # (starts at 1)
        self.edges = {}

        # neighbors is an array containing the ID of every node in graph in no real order
        self.neighbors = [self.id]

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
            if neighbor not in self.neighbors:
                self.neighbors.append(neighbor)
                # key list and val list for making json objects
                # json gives me data science pipeline ptsd hehe Bill dont delete this comment they need to know
                key_list = list(self.edges.keys())
                val_list = list(self.edges.values())
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
                    message = {"nodes": nodes,
                                     "latency": self.edges[edge][0],
                                     "sequence number": self.edges[edge][1]}
                    self.send_to_neighbor(neighbor, json.dumps(message))
        # create routing message
        message = {"nodes": [self.id, neighbor],
                         "latency": latency,
                         "sequence number": self.edges[link][1]}
        self.send_to_neighbors(json.dumps(message))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # get message and un-json it
        edge = json.loads(m)
        nodes = frozenset([edge["nodes"][0], edge["nodes"][1]])

        # update neighbors
        if edge["nodes"][0] not in self.neighbors:
            self.neighbors.append(edge["nodes"][0])
        if edge["nodes"][1] not in self.neighbors:
            self.neighbors.append(edge["nodes"][1])

        # update edges based on message
        if nodes not in self.edges:
            self.edges[nodes] = [edge["latency"], edge["sequence number"]]
            self.send_to_neighbors(m)

        # seq num update
        # so THIS is what seq num is for
        if self.edges[nodes][1] < edge["sequence number"]:
            self.edges[nodes] = [edge["latency"], edge["sequence number"]]
            self.send_to_neighbors(m)
        else:
            message = {"nodes": edge["nodes"],
                             "latency": self.edges[nodes][0],
                             "sequence number": self.edges[nodes][1]}
            self.send_to_neighbor(edge["nodes"][0], json.dumps(message))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # djikstra time
        self.neighbors.sort()
        num_nodes = len(self.neighbors)

        # create index / id matrices because sometimes the IDs get higher than number of IDS
        indexToID = {}
        idToIndex = {}
        index = 0
        for node in self.neighbors:
            idToIndex[node] = index
            indexToID[index] = node
            index += 1

        # create and fill distance matrix
        dist = [float("inf")] * num_nodes
        dist[idToIndex[self.id]] = 0

        # create path matrix (array that contains array of ints to keep track of shortest path to each node)
        paths = [None] * num_nodes
        for x in range(num_nodes):
            paths[x] = [idToIndex[self.id]]

        shortPathSet = [False] * num_nodes

        while False in shortPathSet:
            min = float("inf")
            for x in range(num_nodes):
                if dist[x] < min and shortPathSet[x] is False:
                    min = dist[x]
                    min_index = x

            # if still inf, then no path to it
            if min == float("inf"):
                return -1
            # check if visiting desired node. If so, return second element in path (first one after self)
            if indexToID[min_index] == destination:
                if len(paths[min_index]) == 1:
                    return indexToID[min_index]
                else:
                    return indexToID[paths[min_index][1]]

            shortPathSet[min_index] = True

            for y in range(num_nodes):
                # if edge exists, that edge is not -1, y has not been visited, and the distance to y is greater than distance to (min + edge connecting min to y), update
                edgeToCheck = frozenset([indexToID[y], indexToID[min_index]])
                if edgeToCheck in self.edges:
                    if shortPathSet[y] is False and self.edges[edgeToCheck][0] > -1 and dist[y] > dist[min_index] + self.edges[edgeToCheck][0]:
                        dist[y] = dist[min_index] + self.edges[edgeToCheck][0]
                        paths[y] = paths[min_index][:]
                        paths[y].append(y)
        return -1
