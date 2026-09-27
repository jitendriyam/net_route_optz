class GraphBuilder:
    def build(self, nodes, edges) -> dict:
        """Build {node_name: [(neighbor_name, latency), ...]} from nodes and edges."""
        graph = {name: [] for name in sorted(nodes)}
        for source, destination, latency in sorted(edges):
            graph[source].append((destination, latency))
        return graph
