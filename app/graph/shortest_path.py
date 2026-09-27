from heapq import heappop, heappush
from math import inf


class ShortestPathAlgorithm:
    """Common contract for shortest-path engines, independent of HTTP and the database."""

    def find_path(self, graph: dict, source: str, destination: str):
        """Return {path, total_latency}, or None when no route exists."""
        raise NotImplementedError("Shortest-path engines must implement find_path")


class Dijkstra(ShortestPathAlgorithm):
    """Find a shortest path in a graph with finite, positive edge weights."""

    def find_path(self, graph: dict, source: str, destination: str):
        """Return a dictionary with path and total_latency, or None if unreachable."""
        if source not in graph or destination not in graph:
            return None
        if source == destination:
            return {"path": [source], "total_latency": 0}

        distances = {node: inf for node in graph}
        previous = {}
        distances[source] = 0
        queue = [(0, source)]

        while queue:
            current_distance, current = heappop(queue)
            if current_distance != distances[current]:
                continue
            if current == destination:
                break

            for neighbor, latency in graph.get(current, []):
                distance = current_distance + latency
                if distance < distances.get(neighbor, inf):
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heappush(queue, (distance, neighbor))

        if distances[destination] == inf:
            return None

        path = []
        current = destination
        while current != source:
            path.append(current)
            current = previous[current]
        path.append(source)
        path.reverse()
        return {"path": path, "total_latency": distances[destination]}
    
