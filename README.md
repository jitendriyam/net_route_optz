# Network Route Optimization API

FastAPI API for a directed network with positive edge latencies. The API finds
minimum-latency paths with Dijkstra's algorithm and stores every successful
calculation as an independent route-history snapshot.

## API contract

All application endpoints intentionally use the requested unversioned paths.
Request validation errors are returned by FastAPI as HTTP `422` responses.

### Nodes

#### `POST /nodes`

Create a node.

Request:

```json
{"name": "ServerA"}
```

Response `201`:

```json
{"id": 1, "name": "ServerA"}
```

Node names are unique. Duplicate names return `409 Conflict`.

#### `GET /nodes`

Return all nodes as a complete list.

#### `DELETE /nodes/{id}`

Delete a node. Incoming and outgoing edges are deleted by PostgreSQL foreign-key
cascade behavior. A missing node returns `404 Not Found`.

### Edges

#### `POST /edges`

Create a directed edge between two existing nodes.

Request:

```json
{"source": "ServerA", "destination": "ServerB", "latency": 12.5}
```

Response `201`:

```json
{"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5}
```

The source and destination must exist, latency must be finite and greater than
zero, and duplicate directed edges are not allowed. Violations return `404` for
missing nodes, `409` for duplicate edges, or `422` for invalid request data.

Edges are directed: `ServerA -> ServerB` and `ServerB -> ServerA` are independent
edges. Positive self-loops are allowed.

#### `GET /edges`

Return all directed edges as a complete list.

#### `DELETE /edges/{id}`

Delete an edge. A missing edge returns `404 Not Found`.

### Shortest route

#### `POST /routes/shortest`

Validate both nodes, load the current graph, build an adjacency list, run
Dijkstra's algorithm, store the successful result in route history, and return
the result.

Request:

```json
{"source": "ServerA", "destination": "ServerD"}
```

Response `200`:

```json
{
  "total_latency": 23.4,
  "path": ["ServerA", "ServerB", "ServerD"]
}
```

Missing nodes and unreachable destinations return `404 Not Found`. Only a
successful route calculation creates a history record.

### Route history

#### `GET /routes/history`

Return successful route calculations, newest first. Optional query parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| `source` | string | Filter by source node name |
| `destination` | string | Filter by destination node name |
| `limit` | integer | Newest results; default `100`, maximum `1000` |
| `date_from` | datetime | Inclusive lower bound for `created_at` |
| `date_to` | datetime | Inclusive upper bound for `created_at` |

Example: `GET /routes/history?source=ServerA&limit=20`

History stores source and destination names, total latency, and the full path at
calculation time. It has no foreign keys to the network, so deleting nodes or
edges and changing the topology do not modify old snapshots.

The endpoint currently returns complete filtered lists with a limit; it is not
cursor- or page-based pagination. If data volume grows, add documented
pagination with a stable sort order while preserving this contract where
possible.

### Test data utilities

These endpoints create and remove a deterministic sample network for manual API
testing. They are intended for local development and should be protected or
disabled before exposing the service publicly.

#### `POST /test-data`

Create `TestA`, `TestB`, `TestC`, and `TestD`, plus sample edges. A second
attempt returns `409 Conflict`.

#### `DELETE /test-data`

Delete the sample nodes and their cascaded edges. Existing route-history
snapshots remain available.

### Health

#### `GET /api/v1/health`

Return `{"status": "ok"}` when the application process is running.

## Decisions and error behavior

- Names are trimmed, case-sensitive, and must contain 1–255 characters.
- Edge weights must be finite and greater than zero. Latency units are
  caller-defined but must be consistent throughout the graph.
- Edges are directed; the reverse edge is independent.
- Positive self-loops are allowed.
- Missing nodes, missing deletion targets, and unreachable destinations return
  `404 Not Found`.
- Duplicate node names and directed edges return `409 Conflict`.
- Invalid request data returns `422 Unprocessable Entity`.
- Database failures return a sanitized `503 Service Unavailable` response.
- Unexpected failures return a sanitized `500 Internal Server Error` response;
  internal exception details are written to server logs, not exposed to clients.
- Only successful route calculations create history snapshots.

## Logging

The API logs every request with its HTTP method, path, response status, and
execution duration. Domain errors are logged at warning level, while database
and unexpected errors include tracebacks at error level.

Set `LOG_LEVEL` to control application verbosity. The default and Docker Compose
value is `INFO`.

## Architecture

`app/api/nodes.py`, `app/api/edges.py`, `app/api/routes.py`, and
`app/api/test_data.py` contain the HTTP handlers. `app/main.py` registers the
routers, request-logging middleware, and exception handlers.

The API layer validates HTTP input and calls `app/services`. Services enforce
business rules, coordinate repositories, and own transaction commits.
Repositories perform database access only, using SQLAlchemy models from
`app/models`. API schemas are separate in `app/schemas`. See the detailed
[database model documentation](app/models/README.md) for table structure,
constraints, indexes, relationships, and route-history snapshot behavior.

`RouteService` validates requested nodes, asks `GraphBuilder` to create an
adjacency list, runs the configured shortest-path engine, stores the result, and
returns the response. `ShortestPathAlgorithm` is the plain-Python base contract;
`Dijkstra` is the current and default implementation. A future implementation
can inherit the base class and implement:

```python
find_path(graph, source, destination)
```

The engine returns a dictionary containing `path` and `total_latency`, or `None`
when no route exists. It can be supplied with
`RouteService(session, algorithm=MyAlgorithm())`. The `app/graph` package has no
FastAPI or SQLAlchemy dependency.

## Database and migrations

PostgreSQL enforces node-name uniqueness, directed-edge uniqueness, positive
latency, foreign keys, and deletion cascades. Route history intentionally stores
independent JSON path snapshots.

The Docker app runs migrations automatically before starting Uvicorn:

```text
alembic upgrade head
```

To run migrations locally, set `DATABASE_URL` and use:

```powershell
uv run alembic upgrade head
```

The initial migration is in `alembic/versions/0001_create_network_tables.py`.
The model-to-schema details are documented in
[app/models/README.md](app/models/README.md).

## Run with Docker

Docker Desktop must be running. From the project root, start the API and
PostgreSQL with one command:

```powershell
docker compose up --build
```

The services are exposed at:

- API: <http://localhost:8003>
- Swagger UI: <http://localhost:8003/docs>
- ReDoc: <http://localhost:8003/redoc>
- PostgreSQL: `localhost:5432`

Stop the services with:

```powershell
docker compose down
```

The database is stored in the `postgres_data` Docker volume. To remove the
database volume as well, use `docker compose down -v`.


## Local development

Install dependencies and run the API with `uv`:

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

Run the test suite and lint checks:

```powershell
uv run pytest
uv run ruff check .
```

For local non-Docker execution, set:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/network_route_optimization
```
