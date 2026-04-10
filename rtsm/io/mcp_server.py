"""
RTSM MCP Server — Model Context Protocol interface for AI agents.

Exposes RTSM's spatial memory as MCP tools that any AI agent (Claude,
Cursor, LangGraph, etc.) can query via stdio transport.

Requires a running RTSM instance with REST API. Configure the URL via
the RTSM_API_URL environment variable (default: http://localhost:8002).

Usage:
    python -m rtsm.io.mcp_server
    # or via console script:
    rtsm-mcp
"""
from __future__ import annotations

import asyncio
import json
import os

import httpx
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions

RTSM_API_URL = os.environ.get("RTSM_API_URL", "http://localhost:8002")

server = Server("rtsm")
_client: httpx.AsyncClient | None = None


async def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=RTSM_API_URL, timeout=10.0)
    return _client


async def _api_get(path: str, **params) -> dict:
    """GET from RTSM REST API. Raises on connection errors."""
    client = await _get_client()
    resp = await client.get(path, params=params)
    resp.raise_for_status()
    return resp.json()


# ── Tool definitions ──

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
                "threshold": {"type": "number", "description": "Min cosine similarity threshold (default 0 = return all ranked; SigLIP scores are ~0.05-0.15)", "default": 0.0},
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


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        result = await _dispatch(name, arguments)
        text = json.dumps(result, indent=2, default=str)
    except httpx.ConnectError:
        text = json.dumps({
            "error": "connection_failed",
            "message": f"RTSM is not reachable at {RTSM_API_URL}. Is it running?",
        })
    except httpx.HTTPStatusError as e:
        text = json.dumps({
            "error": "http_error",
            "status_code": e.response.status_code,
            "message": e.response.text,
        })
    except Exception as e:
        text = json.dumps({"error": str(type(e).__name__), "message": str(e)})
    return [types.TextContent(type="text", text=text)]


async def _dispatch(name: str, args: dict) -> dict:
    if name == "rtsm.semantic_query":
        return await _api_get(
            "/search/semantic",
            query=args["query"],
            top_k=args.get("top_k", 5),
            threshold=args.get("threshold", 0.0),
        )

    if name == "rtsm.spatial_query":
        return await _api_get(
            "/search/spatial",
            x=args["x"],
            y=args["y"],
            z=args["z"],
            radius_m=args.get("radius_m", 1.0),
        )

    if name == "rtsm.relational_query":
        query = args["query"]
        radius_m = args.get("radius_m", 1.0)
        # Step 1: find the reference object
        sem = await _api_get("/search/semantic", query=query, top_k=1, threshold=0.15)
        results = sem.get("results", [])
        if not results:
            return {"error": "not_found", "message": f"No object matching '{query}' found in memory."}
        ref = results[0]
        xyz = ref.get("xyz_world")
        if not xyz:
            return {"error": "no_position", "message": f"Object '{query}' found but has no 3D position."}
        # Step 2: spatial query around the reference
        spatial = await _api_get("/search/spatial", x=xyz[0], y=xyz[1], z=xyz[2], radius_m=radius_m)
        # Exclude the reference object itself from nearby list
        ref_id = ref.get("id")
        nearby = [o for o in spatial.get("results", []) if o.get("id") != ref_id]
        return {"reference": ref, "nearby": nearby}

    if name == "rtsm.list_objects":
        return await _api_get("/objects")

    if name == "rtsm.get_object":
        oid = args["object_id"]
        include_vectors = args.get("include_vectors", False)
        return await _api_get(f"/objects/{oid}", include_vectors=include_vectors)

    if name == "rtsm.status":
        health = await _api_get("/healthz")
        stats = await _api_get("/stats")
        return {"health": health, "stats": stats}

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="rtsm",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main_sync():
    """Synchronous entry point for console_scripts."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
