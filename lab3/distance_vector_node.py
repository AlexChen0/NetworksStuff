from simulator.node import Node
import json
import copy


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # we want to store this node's DV, direct neighbors DV, link costs to direct neighbors
        # distance vectors should store shortest-path/next-hop for every destination from this node

        # we're storing each distance vector as a dictionary, where each node keys to a [cost, [path]], and "sequence number" keys to the sequence number
        # path will include beginning and ending node
        self.my_DV = {}
        self.my_DV[self.id] = [0, [self.id, self.id]]
        self.my_DV["sequence number"] = 1
        # neighbors is a dictionary of distance vectors of neighboring nodes, where each neighboring node's ID keys to a distance vector ()
        self.neighbors = {}

        # store link costs as dictionary keying neighboring node to cost
        self.link_costs = {}

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # advertisements have a format of: "node": self.id, "DV": distance vector

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        delete = False
        if latency == -1:
            self.my_DV[str(neighbor)][0] = float('inf')
            self.link_costs.pop(neighbor)
            self.neighbors.pop(str(neighbor))
            delete = True
        else:
            self.link_costs[neighbor] = latency

        # latency = -1 if delete a link
        # store link costs
        # neighbor not in my DV
        if str(neighbor) not in self.my_DV:
            # if changed, send to neighbors
            self.my_DV[str(neighbor)] = [latency, [self.id, neighbor]]
            # send my DV to neighbors and pass to neighbors
            self.my_DV["sequence number"] += 1
            advertisement = {"node": self.id, "DV": self.my_DV}
            self.send_to_neighbors(json.dumps(advertisement))
            return

        # checking if the changed latency is actually relevant
        if not delete and latency > self.my_DV[str(neighbor)][0] and self.my_DV[str(neighbor)][1] != [self.id, int(neighbor)]:
            return

        changed = 0
        # Update each node
        for node in self.my_DV.keys():
            if node == self.id or node == "sequence number":
                continue
            # min cost keeps track of shortest cost so far
            # min path keeps track of path from shortest cost
            prev_cost = self.my_DV[str(node)][0]
            min_path = self.my_DV[str(node)][1][:]
            min_cost = float('inf')

            # Check if direct cost is smaller if it exists
            if int(node) in self.link_costs:
                if self.link_costs[int(node)] < min_cost:
                    min_cost = self.link_costs[int(node)]
                    min_path = [self.id, int(node)]

            for neigh_bor in self.neighbors.keys():
                # This DV wont help us
                if neigh_bor == node:  # or (delete and neigh_bor == neighbor):
                    continue

                neighbor_dv = self.neighbors[neigh_bor]
                if node not in neighbor_dv:
                    continue
                neighbor_cost = neighbor_dv[node][0]
                my_total_cost = neighbor_cost + self.link_costs[int(neigh_bor)]
                # If true we found a shorter path
                if my_total_cost < min_cost:
                    # MY PATH to Neighbor plus neighbors path
                    path = neighbor_dv[node][1]
                    # NO LOOPS
                    if self.id not in path:
                        # print('double pass')
                        min_cost = my_total_cost
                        min_path = path[:]
                        min_path.insert(0, self.id)

                if prev_cost != min_cost:
                    changed = 1

            self.my_DV[str(node)][0] = min_cost
            self.my_DV[str(node)][1] = min_path

        # Send update to neighbors if a change was made to the DV
        if changed == 1 or delete:
            self.my_DV["sequence number"] += 1
            advertisement = {"node": self.id, "DV": self.my_DV}
            self.send_to_neighbors(json.dumps(advertisement))

        # Fill in this function
    def process_incoming_routing_message(self, m: json):
        new_DV = json.loads(m)
        new_node = new_DV["node"]
        changed = 0
        addedNode = 0
        if str(new_node) not in self.neighbors:
            self.neighbors[str(new_node)] = new_DV["DV"]
            #     for node in new_DV["DV"]:
            #         self.neighbors[node] = new_DV["DV"][node]
            addedNode = 1
        # update self.neighbors if the incoming DV has a higher sequence number
        if new_DV["DV"]["sequence number"] > self.neighbors[str(new_node)]["sequence number"]:
            # deepcopy might not be necessary, idk
            self.neighbors[str(new_node)] = new_DV["DV"]
        elif addedNode == 1:
            pass
        else:
            return
        # ADD ANY NEW KEYS
        my_node_keys = self.my_DV.keys()
        neighbor_new_keys = self.neighbors[str(new_node)].keys()

        for neighbor_node in neighbor_new_keys:
            if neighbor_node not in my_node_keys and neighbor_node != str(self.id):
                n_cost = self.neighbors[str(new_node)][neighbor_node][0]
                n_path = self.neighbors[str(new_node)][neighbor_node][1][:]

                total_cost = n_cost + self.link_costs[new_node]
                n_path.insert(0, self.id)
                self.my_DV[str(neighbor_node)] = [total_cost, n_path]
                changed = 1

        # Update each node
        for node in my_node_keys:
            if node == self.id or node == "sequence number":
                continue
            # min cost keeps track of shortest cost so far
            # min path keeps track of path from shortest cost

            # BE CAREFUL OF THIS
            prev_cost = self.my_DV[str(node)][0]
            min_cost = float('inf')
            min_path = self.my_DV[str(node)][1][:]

            if int(node) in self.link_costs:
                if self.link_costs[int(node)] < min_cost:
                    min_cost = self.link_costs[int(node)]
                    min_path = [self.id, int(node)]
                    # changed = 1

            for neighbor in self.neighbors.keys():
                # This DV wont help us
                if neighbor == node:
                    continue
                neighbor_dv = self.neighbors[neighbor]
                if str(node) not in neighbor_dv:
                    continue

                neighbor_cost = neighbor_dv[str(node)][0]
                my_total_cost = neighbor_cost + self.link_costs[int(neighbor)]
                # If true we found a shorter path
                if my_total_cost < min_cost:
                    # MY PATH to Neighbor plus neighbors path
                    path = neighbor_dv[str(node)][1]
                    # NO LOOPS
                    if self.id not in path:
                        min_cost = my_total_cost
                        min_path = path[:]
                        min_path.insert(0, self.id)
                        # changed = 1

            self.my_DV[str(node)][0] = min_cost
            self.my_DV[str(node)][1] = min_path

            if prev_cost != min_cost:
                changed = 1

        if changed == 1:
            # constructing advertisement
            self.my_DV["sequence number"] += 1
            advertisement = advertisement = {"node": self.id, "DV": self.my_DV}
            self.send_to_neighbors(json.dumps(advertisement))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # use DVs to get the next hop
        if str(destination) in self.my_DV:
            return self.my_DV[str(destination)][1][1]
        else:
            return -1
