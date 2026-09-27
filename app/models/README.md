# Database model

The API stores network topology in `nodes` and `edges`, and stores completed route
calculations in `route_history`. The SQLAlchemy classes are in `network.py`; the initial
PostgreSQL schema is created by `alembic/versions/0001_create_network_tables.py`.

```text
nodes.id ──< edges.source_id
         └─< edges.destination_id

route_history    independent snapshot; no foreign keys to nodes or edges
```

## Nodes

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | Integer primary key | Stable identifier for a node. |
| `name` | String, maximum 255 characters | Name used in API requests and graph calculations. Required and unique. |
| `created_at` | Timestamp with time zone | Time the row was inserted. |

The API trims names and rejects empty or overlong values before inserting. The database
constraint `uq_nodes_name` is the final protection against duplicate names, including
concurrent requests. PostgreSQL creates a unique B-tree index for this constraint. The
repository's exact-name lookup (`WHERE name = ...`) can use that index, so a second
index on `name` is unnecessary. Name matching is case-sensitive.

## Edges

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | Integer primary key | Stable identifier for an edge. |
| `source_id` | Integer foreign key to `nodes.id` | Starting node of the directed edge. Required. |
| `destination_id` | Integer foreign key to `nodes.id` | Ending node of the directed edge. Required. |
| `latency` | Floating-point number | Positive weight used by the shortest-path algorithm. |
| `created_at` | Timestamp with time zone | Time the row was inserted. |

An edge from A to B does not imply an edge from B to A. The unique constraint
`uq_edges_source_destination` prevents a second edge with the same ordered pair.
The check constraint `ck_edges_positive_latency` enforces `latency > 0` in PostgreSQL;
the API also rejects non-finite latency values. Positive self-loops are allowed.

Both foreign keys use `ON DELETE CASCADE`. Deleting a node removes edges where it is
either the source or the destination. PostgreSQL does not create indexes on referencing
foreign-key columns automatically, so the index choices matter:

| Index | Helps with |
| --- | --- |
| Unique index from `uq_edges_source_destination` on `(source_id, destination_id)` | Duplicate-edge checks, lookups by the full pair, and lookups or cascades by `source_id` because it is the first indexed column. |
| `ix_edges_destination_id` on `destination_id` | Lookups or cascades by destination alone, such as incoming edges of a deleted node. |

An additional index on `source_id` alone would duplicate the useful leading part of
the unique index. PostgreSQL may still choose a table scan for very small tables;
the indexes provide access paths when they are beneficial.

## Route history

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | Integer primary key | Identifier for one completed calculation. |
| `source_name` | String, maximum 255 characters | Source name at calculation time. |
| `destination_name` | String, maximum 255 characters | Destination name at calculation time. |
| `total_latency` | Floating-point number | Calculated total at that time. |
| `path` | JSON | Ordered list of node names in the chosen route. |
| `created_at` | Timestamp with time zone | Time the result was saved. |

Each successful route calculation adds a new history row. These rows hold names and a
path snapshot, not foreign keys to current nodes. Deleting nodes or changing edges
therefore cannot change an old result. Unreachable routes are not stored.

The table has separate indexes on `source_name`, `destination_name`, and `created_at`
for the optional history filters and newest-first retrieval. The repository orders by
`created_at` and then `id` so ties have a stable order.
