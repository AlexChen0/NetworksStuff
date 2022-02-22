from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        # store DV as dictionary, w latency and path
        self.distance_vector = {}
        self.distance_vector[str(self.id)] = [0, [self.id, self.id]]
        #seqnum
        self.seqnum = 1
        # store neighbors as well [distance vector (), seqnum]
        self.neighbors = {}

        # store link costs as dictionary keying neighboring node to cost
        self.link_costs = {}

    # Return a string
    def __str__(self):
        return "A few dozen lines eh is a few 40 to ya (or are we just bad lol)"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # we wanna keep track of if something was changed or deleted
        delete = False
        changed = False
        neighbor = str(neighbor)
        if latency == -1:
            self.distance_vector[neighbor][0] = float('inf')
            self.link_costs.pop(neighbor)
            self.neighbors.pop(neighbor)
            delete = True
        else:
            self.link_costs[neighbor] = latency

        # neighbor not in dv
        if neighbor not in self.distance_vector:
            #  send message to neighbors
            self.distance_vector[neighbor] = [latency, [self.id, int(neighbor)]]
            self.seqnum += 1
            message = {"node": self.id,
                        "DV": self.distance_vector,
                        "seqnum": self.seqnum}
            self.send_to_neighbors(json.dumps(message))
            return

        # latency and seqnum checks
        if not delete and latency > self.distance_vector[neighbor][0] and self.distance_vector[neighbor][1] != [self.id, int(neighbor)]:
            return

        # update
        for node in self.distance_vector.keys():
            # keep track of costs and paths
            if int(node) != self.id:
                prev_cost = self.distance_vector[node][0]
                min_path = self.distance_vector[node][1][:]
                min_cost = float('inf')

                # update if better cost is found
                if node in self.link_costs and self.link_costs[node] < min_cost:
                    min_cost = self.link_costs[node]
                    min_path = [self.id, int(node)]

                for neighbor_id in self.neighbors.keys():
                    if node != neighbor_id:
                        neighbor_dv = self.neighbors[neighbor_id][0]
                        if node not in neighbor_dv:
                            continue
                        neighbor_cost = neighbor_dv[node][0]
                        total_cost = neighbor_cost + self.link_costs[neighbor_id]
                        if total_cost < min_cost:
                            # new path found
                            path = neighbor_dv[node][1]
                            if self.id not in path:
                                # check no loop
                                min_cost = total_cost
                                min_path = path[:]
                                min_path.insert(0, self.id)
                        if prev_cost != min_cost:
                            changed = True
                self.distance_vector[node][0] = min_cost
                self.distance_vector[node][1] = min_path

        # send update
        if changed or delete:
            self.seqnum += 1
            message = {"node": self.id, "DV": self.distance_vector, "seqnum": self.seqnum}
            self.send_to_neighbors(json.dumps(message))


    # Fill in this function
    def process_incoming_routing_message(self, m):
        new_DV = json.loads(m)
        new_node = str(new_DV["node"])
        changed = False
        addedNode = False
        if new_node not in self.neighbors:
            self.neighbors[new_node] = [new_DV["DV"], new_DV["seqnum"]]
            addedNode = True
        # seqnum check for update
        if new_DV["seqnum"] > self.neighbors[new_node][1]:
            self.neighbors[new_node] = [new_DV["DV"], new_DV["seqnum"]]
        elif addedNode:
            pass
        else:
            return
        # key update
        node_keys = self.distance_vector.keys()
        neighbor_keys = self.neighbors[new_node][0].keys()

        for node in neighbor_keys:
            if node not in node_keys and node != str(self.id):
                n_cost = self.neighbors[new_node][0][node][0]
                n_path = self.neighbors[new_node][0][node][1][:]

                total_cost = n_cost + self.link_costs[new_node]
                n_path.insert(0, self.id)
                self.distance_vector[node] = [total_cost, n_path]
                changed = True

        #basically same logic as L66 loop
        for node in node_keys:
            node = str(node)
            if int(node) != self.id:
                prev_cost = self.distance_vector[node][0]
                min_cost = float('inf')
                min_path = self.distance_vector[node][1][:]

                if node in self.link_costs:
                    if self.link_costs[node] < min_cost:
                        min_cost = self.link_costs[node]
                        min_path = [self.id, int(node)]

                for neighbor in self.neighbors.keys():
                    if neighbor != node:
                        neighbor_dv = self.neighbors[neighbor][0]
                        if node not in neighbor_dv:
                            continue
                        if neighbor not in self.link_costs:
                            continue
                        neighbor_cost = neighbor_dv[node][0]
                        my_total_cost = neighbor_cost + self.link_costs[neighbor]
                        if my_total_cost < min_cost:
                            # new path found
                            path = neighbor_dv[node][1]
                            if self.id not in path:
                                # check no loop
                                min_cost = my_total_cost
                                min_path = path[:]
                                min_path.insert(0, self.id)
                if prev_cost != min_cost:
                    changed = True
                self.distance_vector[node][0] = min_cost
                self.distance_vector[node][1] = min_path

        # send update
        if changed:
            self.seqnum += 1
            message = {"node": self.id, "DV": self.distance_vector, "seqnum": self.seqnum}
            self.send_to_neighbors(json.dumps(message))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # stored in dv already, so no need to do further calculation
        # for the record, djikstra was more fun to implement
        if str(destination) in self.distance_vector:
            return self.distance_vector[str(destination)][1][1]
        else:
            return -1
