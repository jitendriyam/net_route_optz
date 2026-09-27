from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.api import edges, nodes, routes, test_data
from app.api.health import router as health_router
from app.exceptions import ConflictError, NotFoundError

app = FastAPI(title="Network Route Optimization API", version="0.1.0")
app.include_router(health_router, prefix="/api/v1")
app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(routes.router)
app.include_router(test_data.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> str:
    """Render a landing page with links to the interactive API documentation."""
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Network Route Optimization API</title>
    <style>
      :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
      body { display: grid; min-height: 100vh; place-items: center; margin: 0; }
      main { width: min(90%, 640px); padding: 3rem; border: 1px solid #8885;
             border-radius: 1rem; box-sizing: border-box; }
      h1 { margin-top: 0; }
      a { display: inline-block; margin: .5rem .5rem .5rem 0; padding: .7rem 1rem;
          border-radius: .5rem; background: #2563eb; color: white; text-decoration: none; }
      a:hover { background: #1d4ed8; }
    </style>
  </head>
  <body>
    <main>
      <h1>Network Route Optimization API</h1>
      <p>Minimum-latency routes through a directed network.</p>
      <p>Explore the API documentation:</p>
      <a href="/docs">Swagger UI</a>
      <a href="/redoc">ReDoc</a>
    </main>
  </body>
</html>"""


@app.exception_handler(NotFoundError)
async def not_found(_request: Request, error: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(ConflictError)
async def conflict(_request: Request, error: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(error)})
