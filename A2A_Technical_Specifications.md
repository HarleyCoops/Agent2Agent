# Agent2Agent (A2A) Protocol Technical Specifications

## Introduction

The Agent2Agent (A2A) protocol is a JSON-RPC based protocol designed to enable communication and interoperability between AI agents built on different frameworks. This document provides detailed technical specifications of the protocol, including message formats, API methods, and implementation guidelines.

## Protocol Overview

A2A uses JSON-RPC 2.0 as its underlying communication protocol. All messages follow the JSON-RPC format with methods specific to agent discovery, task management, and push notifications.

### Core Concepts

1. **Agents**: Autonomous entities that expose capabilities through Agent Cards
2. **Tasks**: Units of work that agents perform, with defined lifecycle states
3. **Artifacts**: Outputs produced by agents during task execution
4. **Sessions**: Persistent contexts for maintaining state across interactions

## Message Format

All A2A messages follow the JSON-RPC 2.0 format:

```json
{
  "jsonrpc": "2.0",
  "id": <id>,
  "method": <method>,
  "params": <params>
}
```

Responses follow this format:

```json
{
  "jsonrpc": "2.0",
  "id": <id>,
  "result": <result>,
  "error": <error>
}
```

## Data Structures

### Agent Card

The Agent Card is a metadata structure that describes an agent's capabilities:

```json
{
  "name": "String",
  "description": "String",
  "url": "String",
  "provider": {
    "organization": "String",
    "url": "String"
  },
  "version": "String",
  "documentationUrl": "String",
  "capabilities": {
    "streaming": Boolean,
    "pushNotifications": Boolean,
    "stateTransitionHistory": Boolean
  },
  "authentication": {
    "schemes": ["String"],
    "credentials": "String"
  },
  "defaultInputModes": ["String"],
  "defaultOutputModes": ["String"],
  "skills": [
    {
      "id": "String",
      "name": "String",
      "description": "String",
      "tags": ["String"],
      "examples": ["String"],
      "inputModes": ["String"],
      "outputModes": ["String"]
    }
  ]
}
```

### Task

A Task represents a unit of work and has the following structure:

```json
{
  "id": "String",
  "status": {
    "state": "String",
    "message": {
      "role": "String",
      "parts": [
        {
          "type": "String",
          "text": "String"
        }
      ]
    },
    "timestamp": "String"
  },
  "artifacts": [
    {
      "name": "String",
      "description": "String",
      "parts": [
        {
          "type": "String",
          "text": "String"
        }
      ],
      "index": Number,
      "append": Boolean,
      "lastChunk": Boolean,
      "metadata": {}
    }
  ],
  "history": []
}
```

### Message Parts

Messages and artifacts contain parts, which can be of different types:

#### Text Part

```json
{
  "type": "text",
  "text": "String"
}
```

#### Data Part

```json
{
  "type": "data",
  "data": {},
  "metadata": {}
}
```

#### File Part

```json
{
  "type": "file",
  "file": {
    "name": "String",
    "mimeType": "String",
    "bytes": "String",
    "uri": "String"
  },
  "metadata": {}
}
```

## API Methods

### Agent Discovery

#### agent/getCard

Retrieves the agent's card with capabilities and skills.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "agent/getCard",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    // Agent Card structure
  }
}
```

### Task Management

#### tasks/send

Sends a task to an agent.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tasks/send",
  "params": {
    "id": "String",
    "sessionId": "String",
    "acceptedOutputModes": ["String"],
    "message": {
      "role": "String",
      "parts": [
        {
          "type": "String",
          "text": "String"
        }
      ]
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    // Task structure
  }
}
```

#### tasks/sendSubscribe

Sends a task and subscribes to streaming updates.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tasks/sendSubscribe",
  "params": {
    "id": "String",
    "sessionId": "String",
    "acceptedOutputModes": ["String"],
    "message": {
      "role": "String",
      "parts": [
        {
          "type": "String",
          "text": "String"
        }
      ]
    }
  }
}
```

**Response Stream:**
```
data: {"jsonrpc":"2.0","id":3,"result":{"id":"String","status":{"state":"working","message":{"role":"agent","parts":[{"type":"text","text":"String"}]},"timestamp":"String"},"final":false}}

data: {"jsonrpc":"2.0","id":3,"result":{"id":"String","artifact":{"parts":[{"type":"text","text":"String"}],"index":0,"append":false}}}

data: {"jsonrpc":"2.0","id":3,"result":{"id":"String","status":{"state":"completed","timestamp":"String"},"final":true}}
```

#### tasks/get

Retrieves the current state of a task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tasks/get",
  "params": {
    "id": "String",
    "sessionId": "String"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    // Task structure
  }
}
```

#### tasks/cancel

Cancels an ongoing task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tasks/cancel",
  "params": {
    "id": "String",
    "sessionId": "String"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    // Task structure with state "canceled"
  }
}
```

### Push Notifications

#### tasks/pushNotification/get

Gets push notification configuration.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tasks/pushNotification/get",
  "params": {
    "id": "String",
    "sessionId": "String"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "url": "String",
    "headers": {}
  }
}
```

#### tasks/pushNotification/set

Sets push notification configuration.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tasks/pushNotification/set",
  "params": {
    "id": "String",
    "sessionId": "String",
    "url": "String",
    "headers": {}
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "url": "String",
    "headers": {}
  }
}
```

## Task Lifecycle

Tasks in A2A follow a defined lifecycle with these states:

1. **created**: Initial state when a task is created
2. **working**: The agent is actively processing the task
3. **input-required**: The agent needs additional input to continue
4. **completed**: The task has been successfully completed
5. **failed**: The task could not be completed
6. **canceled**: The task was canceled before completion

State transitions follow these rules:
- `created` → `working`
- `working` → `input-required` | `completed` | `failed`
- `input-required` → `working` (after receiving input)
- Any state → `canceled` (via explicit cancellation)

## Error Handling

A2A defines standard error codes following the JSON-RPC specification:

- `-32700`: Parse error (Invalid JSON)
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000` to `-32099`: Server error

Additionally, A2A defines custom error codes:
- `-32001`: Task not found
- `-32002`: Session not found
- `-32003`: Push notification not supported

Error responses follow this format:

```json
{
  "jsonrpc": "2.0",
  "id": <id>,
  "error": {
    "code": <code>,
    "message": <message>,
    "data": <data>
  }
}
```

## Authentication and Security

A2A supports multiple authentication schemes:

1. **None**: No authentication (for development/testing)
2. **Bearer**: Bearer token authentication
3. **OAuth2**: OAuth 2.0 authentication
4. **Custom**: Custom authentication schemes

Authentication information is included in the Agent Card:

```json
"authentication": {
  "schemes": ["bearer"],
  "credentials": "token"
}
```

## Implementation Guidelines

### Server Implementation

To implement an A2A server:

1. Create an HTTP endpoint that accepts JSON-RPC requests
2. Implement the required methods (agent/getCard, tasks/send, etc.)
3. Handle task lifecycle management
4. Support streaming responses if needed
5. Implement push notifications if needed

### Client Implementation

To implement an A2A client:

1. Create an HTTP client that can send JSON-RPC requests
2. Implement methods to call server endpoints
3. Handle streaming responses if needed
4. Implement push notification handling if needed

## Transport Protocol

A2A primarily uses HTTP/HTTPS as its transport protocol:

- Regular requests use standard HTTP POST
- Streaming responses use Server-Sent Events (SSE)
- Push notifications use HTTP callbacks

## Content Types

A2A supports these content types:

- `application/json` for regular requests/responses
- `text/event-stream` for streaming responses

## Versioning

A2A uses semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality
- PATCH: Backwards-compatible bug fixes

The current version is included in the Agent Card.

## Conclusion

The A2A protocol provides a standardized way for AI agents to communicate and interoperate. By following these technical specifications, developers can create agents that seamlessly work together, regardless of their underlying frameworks or implementations.
