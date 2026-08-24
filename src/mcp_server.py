import json
import sys
from pathlib import Path

from property_store import PropertyStore


PROTOCOL_VERSION = "2025-11-25"
ROOT = Path(__file__).resolve().parent.parent
PROPERTIES_FILE = ROOT / "data" / "properties.csv"
APPOINTMENTS_FILE = ROOT / "data" / "appointments.json"

store = PropertyStore(PROPERTIES_FILE, APPOINTMENTS_FILE)
initialized = False

TOOLS = [
    {
        "name": "search_properties",
        "description": "Search available properties using optional real-estate filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "municipality": {"type": "string"},
                "neighborhood": {"type": "string"},
                "property_type": {
                    "type": "string",
                    "enum": ["apartment", "house", "townhouse", "land"],
                },
                "operation": {
                    "type": "string",
                    "enum": ["sale", "rent"],
                },
                "currency": {"type": "string", "enum": ["USD", "GTQ"]},
                "min_price": {"type": "number", "minimum": 0},
                "max_price": {"type": "number", "minimum": 0},
                "bedrooms": {"type": "integer", "minimum": 0},
                "bathrooms": {"type": "number", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
        },
    },
    {
        "name": "schedule_property_visit",
        "description": "Schedule a visit for an available property.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "property_id": {"type": "string"},
                "client_name": {"type": "string"},
                "client_email": {"type": "string"},
                "visit_at": {
                    "type": "string",
                    "description": "ISO 8601 datetime with timezone, for example 2026-09-18T15:30:00-06:00",
                },
                "notes": {"type": "string"},
            },
            "required": [
                "property_id",
                "client_name",
                "client_email",
                "visit_at",
            ],
        },
    },
]


def success(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def protocol_error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def tool_result(data, is_error=False):
    result = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data, ensure_ascii=False, indent=2),
            }
        ]
    }
    if is_error:
        result["isError"] = True
    return result


def handle_message(message):
    global initialized

    if message.get("jsonrpc") != "2.0" or "method" not in message:
        return protocol_error(message.get("id"), -32600, "Invalid Request")

    request_id = message.get("id")
    method = message["method"]

    if "id" not in message:
        if method == "notifications/initialized":
            initialized = True
        return None

    if method == "initialize":
        requested_version = message.get("params", {}).get("protocolVersion")
        if requested_version != PROTOCOL_VERSION:
            return protocol_error(
                request_id,
                -32602,
                "Unsupported protocol version. Use 2025-11-25.",
            )
        return success(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "real-estate-mcp-server",
                    "version": "1.0.0",
                },
            },
        )

    if not initialized and method != "ping":
        return protocol_error(request_id, -32002, "Server is not initialized")

    if method == "ping":
        return success(request_id, {})

    if method == "tools/list":
        return success(request_id, {"tools": TOOLS})

    if method == "tools/call":
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in {tool["name"] for tool in TOOLS}:
            return protocol_error(request_id, -32602, "Unknown tool")

        try:
            if tool_name == "search_properties":
                properties = store.search(arguments)
                data = {
                    "total": len(properties),
                    "properties": properties,
                }
                result = tool_result(data)
                result["structuredContent"] = data
                return success(request_id, result)

            appointment = store.schedule_visit(arguments)
            result = tool_result({"appointment": appointment})
            result["structuredContent"] = {"appointment": appointment}
            return success(request_id, result)
        except (KeyError, TypeError, ValueError) as error:
            return success(
                request_id,
                tool_result({"message": str(error)}, is_error=True),
            )

    return protocol_error(request_id, -32601, "Method not found")


def main():
    print("Real Estate MCP Server started", file=sys.stderr)

    for line in sys.stdin:
        if not line.strip():
            continue

        try:
            message = json.loads(line)
            response = handle_message(message)
        except json.JSONDecodeError:
            response = protocol_error(None, -32700, "Parse error")
        except Exception as error:
            print(f"Server error: {error}", file=sys.stderr)
            response = protocol_error(None, -32603, "Internal error")

        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
