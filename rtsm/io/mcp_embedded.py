"""
Embedded MCP Server — runs inside the RTSM process, zero HTTP overhead.

Mounts on the existing FastAPI app at /mcp/ using SSE transport.
Tools call working_memory, clip_adapter, vectors, and proximity_index
directly via Python — no HTTP round-trip.

Enable via config/rtsm.yaml:
    mcp:
      enable: true

MCP clients connect to:
    SSE stream:  GET  http://localhost:8002/mcp/sse
    Messages:    POST http://localhost:8002/mcp/messages/
"""
from __future__ import annotations

import json
import logging
from math import ceil
from typing import Any, Optional

import numpy as np
from starlette.responses import Response

import mcp.types as types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport

logger = logging.getLogger(__name__)

# ── Shared tool definitions ──

TOOLS = [
    types.Tool(
        name="rtsm.semantic_query",
        description=(
            "Search RTSM spatial memory by natural language. "
            "Returns objects matching the query with 3D positions and similarity scores. "
            'Example: "where is the coffee mug?"'
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"},
                "top_k": {"type": "integer", "description": "Max results to return", "default": 5},
                "threshold": {"type": "number", "description": "Min similarity (0-1)", "default": 0.2},
            },
            "required": ["query"],
        },
    ),
    types.Tool(
        name="rtsm.spatial_query",
        description=(
            "Find all tracked objects within a radius of a 3D point in world coordinates. "
            "Returns objects sorted by distance."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "X coordinate (meters)"},
                "y": {"type": "number", "description": "Y coordinate (meters)"},
                "z": {"type": "number", "description": "Z coordinate (meters)"},
                "radius_m": {"type": "number", "description": "Search radius in meters", "default": 1.0},
            },
            "required": ["x", "y", "z"],
        },
    ),
    types.Tool(
        name="rtsm.relational_query",
        description=(
            "Find objects near a named reference object. "
            'Example: "what is next to the laptop?" — finds the laptop, '
            "then returns nearby objects."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name of the reference object to search around"},
                "radius_m": {"type": "number", "description": "Search radius in meters", "default": 1.0},
            },
            "required": ["query"],
        },
    ),
    types.Tool(
        name="rtsm.list_objects",
        description="List all objects currently tracked in RTSM spatial memory with positions and labels.",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="rtsm.get_object",
        description="Get full details for a specific tracked object by its ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "object_id": {"type": "string", "description": "Object ID"},
                "include_vectors": {"type": "boolean", "description": "Include embedding vectors", "default": False},
            },
            "required": ["object_id"],
        },
    ),
    types.Tool(
        name="rtsm.status",
        description="Get RTSM system status: health, object counts, and pipeline statistics.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


def create_mcp_app(
    *,
    working_memory: Any,
    clip_adapter: Optional[Any] = None,
    vectors: Optional[Any] = None,
):
    """
    Create a Starlette sub-application that serves MCP over SSE.

    Returns an ASGI app that should be mounted on the FastAPI app:
        app.mount("/mcp", create_mcp_app(working_memory=wm, ...))

    MCP clients connect to:
        GET  /mcp/sse          — SSE event stream
        POST /mcp/messages/    — client-to-server messages
    """
    server = Server("rtsm")
    # The endpoint path is relative to the mount point.
    # FastAPI sets root_path="/mcp", so the SDK builds: root_path + endpoint
    # → "/mcp" + "/messages/" → "/mcp/messages/" (correct full URL for clients).
    sse_transport = SseServerTransport("/messages/")

    # ── Tool registration ──

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            result = _dispatch(name, arguments, working_memory, clip_adapter, vectors)
            text = json.dumps(result, indent=2, default=str)
        except Exception as e:
            text = json.dumps({"error": type(e).__name__, "message": str(e)})
        return [types.TextContent(type="text", text=text)]

    # ── Raw ASGI app (bypasses Starlette routing) ──
    # handle_post_message is a raw ASGI callable that sends its own response
    # via `send`. Starlette Route/Mount wrapping breaks it because the routing
    # layer expects endpoints to return a Response object. We route manually.

    init_options = InitializationOptions(
        server_name="rtsm",
        server_version="0.1.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    async def mcp_asgi_app(scope, receive, send):
        # FastAPI Mount keeps full path in scope["path"] and sets root_path.
        # Strip root_path prefix to get the local path.
        root = scope.get("root_path", "")
        path = scope.get("path", "")
        local_path = path[len(root):] if root and path.startswith(root) else path

        if scope["type"] == "http" and local_path == "/sse":
            async with sse_transport.connect_sse(scope, receive, send) as (
                read_stream,
                write_stream,
            ):
                await server.run(read_stream, write_stream, init_options)
        elif scope["type"] == "http" and local_path.startswith("/messages"):
            await sse_transport.handle_post_message(scope, receive, send)
        else:
            response = Response("Not found", status_code=404)
            await response(scope, receive, send)

    return mcp_asgi_app


# ── Direct Python dispatch (no HTTP) ──

def _dispatch(
    name: str,
    args: dict,
    wm: Any,
    clip_adapter: Optional[Any],
    vectors: Optional[Any],
) -> dict:
    """Route tool calls to direct Python operations on live RTSM objects."""

    if name == "rtsm.semantic_query":
        return _semantic_query(
            wm, clip_adapter, vectors,
            query=args["query"],
            top_k=args.get("top_k", 5),
            threshold=args.get("threshold", 0.2),
        )

    if name == "rtsm.spatial_query":
        return _spatial_query(
            wm,
            x=args["x"], y=args["y"], z=args["z"],
            radius_m=args.get("radius_m", 1.0),
        )

    if name == "rtsm.relational_query":
        return _relational_query(
            wm, clip_adapter, vectors,
            query=args["query"],
            radius_m=args.get("radius_m", 1.0),
        )

    if name == "rtsm.list_objects":
        return _list_objects(wm)

    if name == "rtsm.get_object":
        return _get_object(
            wm,
            object_id=args["object_id"],
            include_vectors=args.get("include_vectors", False),
        )

    if name == "rtsm.status":
        return _status(wm)

    raise ValueError(f"Unknown tool: {name}")


def _obj_summary(o: Any) -> dict:
    return {
        "id": o.id,
        "xyz_world": o.xyz_world.tolist() if o.xyz_world is not None else None,
        "label_primary": getattr(o, "label_primary", None),
        "confirmed": bool(getattr(o, "confirmed", False)),
        "stability": round(float(getattr(o, "stability", 0.0)), 3),
        "hits": int(getattr(o, "hits", 0)),
    }


def _semantic_query(wm, clip_adapter, vectors, *, query: str, top_k: int, threshold: float) -> dict:
    if not clip_adapter or not vectors:
        return {"error": "unavailable", "message": "Semantic search not available (CLIP or vectors not configured)"}

    query_emb = clip_adapter.encode_text(query)
    matches = vectors.search(query_emb, top_k=top_k)

    results = []
    for oid, score in matches:
        if score < threshold:
            continue
        obj = wm.get(oid)
        results.append({
            "id": oid,
            "score": round(float(score), 4),
            "label_hint": obj.label_primary if obj else None,
            "confirmed": obj.confirmed if obj else True,
            "xyz_world": obj.xyz_world.tolist() if obj and obj.xyz_world is not None else None,
        })
    return {"query": query, "results": results}


def _spatial_query(wm, *, x: float, y: float, z: float, radius_m: float) -> dict:
    if wm.index is None:
        return {"error": "unavailable", "message": "Spatial search not available (no proximity index)"}

    center = np.array([x, y, z], dtype=np.float32)
    grid = wm.index.grid
    rings = min(10, max(1, int(ceil(radius_m / grid.cell_m))))

    oids = wm.index.nearby_ids(center, rings=rings)

    results = []
    for oid in oids:
        obj = wm.get(oid)
        if obj is None:
            continue
        dist = float(np.linalg.norm(obj.xyz_world - center))
        if dist > radius_m:
            continue
        results.append({
            "id": oid,
            "distance_m": round(dist, 4),
            "label_primary": getattr(obj, "label_primary", None),
            "xyz_world": obj.xyz_world.tolist(),
            "confirmed": bool(getattr(obj, "confirmed", False)),
            "stability": round(float(getattr(obj, "stability", 0.0)), 3),
        })

    results.sort(key=lambda r: r["distance_m"])
    return {"center": [x, y, z], "radius_m": radius_m, "results": results}


def _relational_query(wm, clip_adapter, vectors, *, query: str, radius_m: float) -> dict:
    # Step 1: find the reference object via semantic search
    sem = _semantic_query(wm, clip_adapter, vectors, query=query, top_k=1, threshold=0.15)
    if "error" in sem:
        return sem
    results = sem.get("results", [])
    if not results:
        return {"error": "not_found", "message": f"No object matching '{query}' found in memory."}

    ref = results[0]
    xyz = ref.get("xyz_world")
    if not xyz:
        return {"error": "no_position", "message": f"Object '{query}' found but has no 3D position."}

    # Step 2: spatial query around the reference
    spatial = _spatial_query(wm, x=xyz[0], y=xyz[1], z=xyz[2], radius_m=radius_m)
    ref_id = ref.get("id")
    nearby = [o for o in spatial.get("results", []) if o.get("id") != ref_id]
    return {"reference": ref, "nearby": nearby}


def _list_objects(wm) -> dict:
    objs = list(wm.iter_objects())
    return {
        "count": len(objs),
        "objects": [_obj_summary(o) for o in objs],
    }


def _get_object(wm, *, object_id: str, include_vectors: bool = False) -> dict:
    obj = wm.get(object_id)
    if obj is None:
        return {"error": "not_found", "id": object_id}

    d = _obj_summary(obj)
    d.update({
        "cov_world": obj.cov_world.tolist() if getattr(obj, "cov_world", None) is not None else None,
        "label_scores": dict(getattr(obj, "label_scores", {}) or {}),
        "last_seen_wall_utc": float(getattr(obj, "last_seen_wall_utc", 0.0)),
        "created_wall_utc": float(getattr(obj, "created_wall_utc", 0.0)),
        "view_bins_count": len(getattr(obj, "view_bins", {}) or {}),
        "image_crops_count": len(getattr(obj, "image_crops", []) or []),
    })
    if include_vectors:
        emb = getattr(obj, "emb_mean", None)
        d["emb_mean"] = emb.tolist() if emb is not None else None
    return d


def _status(wm) -> dict:
    stats = {}
    try:
        stats = dict(wm.stats())
    except Exception:
        pass
    return {
        "health": {"status": "ok"},
        "stats": stats,
    }
