# Real Estate MCP Server

This project is a local MCP server for a simulated real-estate agency. It allows a client or chatbot to search available properties and schedule visits for customers.

The server was created for the Redes course project. It uses JSON-RPC 2.0 and the MCP stdio transport. The JSON-RPC messages and MCP operations are implemented manually without using FastMCP or another MCP SDK.

## Requirements

- Python 3.10 or newer
- Visual Studio Code or another code editor
- No external Python packages are required

## Project structure

```text
Proyecto1_Redes/
├── data/
│   ├── appointments.json
│   └── properties.csv
├── src/
│   ├── generate_dataset.py
│   ├── property_store.py
│   └── mcp_server.py
├── test_mcp_server.py
└── README.md
```

## Installation

Open the project folder in Visual Studio Code. Open a terminal in the project folder and run:

```powershell
python src\generate_dataset.py
```

## Running the server

The server communicates through standard input and standard output. It receives one JSON-RPC message per line.

From the project folder, run:

```powershell
python src\mcp_server.py
```

The message `Real Estate MCP Server started` means that the server started successfully. The server waits for JSON-RPC messages.

## Testing the MCP connection

## Automated test

The project includes `test_mcp_server.py`, which verifies the MCP initialization, tool discovery, property search and input validation.

Run it from the project folder with:

```
powershell
python -m unittest test_mcp_server.py -v
```

## MCP communication flow

The client begins with `initialize`. The server responds with the protocol version and its capabilities. The client then sends `notifications/initialized`, discovers the tools with `tools/list`, and invokes a tool with `tools/call`.

The local transport is `stdio`: the client launches the server as a process, sends messages through standard input and receives responses through standard output. Diagnostic messages are sent to standard error.

## Limitations

This is a course project that uses simulated data. It does not connect to real agencies, process payments or create contracts. A production system would need authentication, authorization, a database, encrypted communication and privacy controls.
