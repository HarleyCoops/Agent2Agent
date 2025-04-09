# Agent2Agent (A2A) Protocol Documentation

## Overview

The Agent2Agent (A2A) protocol is an open protocol designed to enable communication and interoperability between opaque agentic applications. Developed by Google, it addresses one of the biggest challenges in enterprise AI adoption: getting agents built on different frameworks and vendors to work together.

A2A provides a common language for agents across different ecosystems to communicate with each other, regardless of the framework or vendor they are built on. This protocol is critical for supporting multi-agent communication by allowing agents to:

- Show each other their capabilities
- Negotiate how they will interact with users (via text, forms, or bidirectional audio/video)
- Work securely together

## Key Concepts

### Agent Cards

Agent Cards are metadata structures that describe an agent's capabilities, skills, and interaction modes. They allow agents to discover and understand each other's abilities before initiating communication.

Key components of an Agent Card include:
- Basic information (name, description, version)
- Provider details
- Capabilities (streaming, push notifications, state transition history)
- Authentication schemes
- Input/output modes
- Skills (with IDs, descriptions, and examples)

### Tasks

Tasks represent units of work that agents perform. The A2A protocol defines a task lifecycle with various states:
- `created`: Initial state when a task is created
- `working`: The agent is actively processing the task
- `input-required`: The agent needs additional input to continue
- `completed`: The task has been successfully completed
- `failed`: The task could not be completed
- `canceled`: The task was canceled before completion

### Artifacts

Artifacts are the outputs produced by agents during task execution. They can include:
- Text responses
- Data structures
- Files
- Forms for user input

### Communication Patterns

A2A supports several communication patterns:
- Synchronous request-response
- Streaming responses
- Push notifications for asynchronous updates

## Protocol Specification

The A2A protocol is defined using JSON Schema. The core structures include:

### Agent Card Schema

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

### Task Schema

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

## API Methods

The A2A protocol defines several JSON-RPC methods:

### Agent Discovery
- `agent/getCard`: Retrieves the agent's card with capabilities and skills

### Task Management
- `tasks/send`: Sends a task to an agent
- `tasks/sendSubscribe`: Sends a task and subscribes to streaming updates
- `tasks/get`: Retrieves the current state of a task
- `tasks/cancel`: Cancels an ongoing task

### Push Notifications
- `tasks/pushNotification/get`: Gets push notification configuration
- `tasks/pushNotification/set`: Sets push notification configuration

## Framework Integrations

A2A can be integrated with various agent frameworks:

### Google Agent Development Kit (ADK)

The Google ADK integration demonstrates how to create an A2A-compatible agent using Google's agent framework. The sample implementation shows an "Expense Reimbursement" agent that:
- Takes text requests from clients
- Returns webforms for missing details
- Processes the completed forms
- Returns results to the client

### LangGraph

The LangGraph integration showcases how to build an A2A-compatible agent using the LangGraph framework. The sample implementation is a Currency Converter agent that:
- Supports multi-turn conversations
- Requests additional information when needed
- Provides currency conversion results
- Supports both synchronous and streaming responses

Key features of the LangGraph implementation include:
- State management for multi-turn conversations
- Handling of different task states (working, input-required, completed)
- Integration with external tools for currency conversion
- Support for streaming responses

### CrewAI

The CrewAI integration demonstrates how to use A2A with the CrewAI framework for multi-agent collaboration.

## Enterprise Readiness

A2A is designed with enterprise requirements in mind:

### Security
- Authentication schemes for secure agent-to-agent communication
- Credential management
- Authorization controls

### Scalability
- Efficient communication patterns
- Support for asynchronous operations
- Push notifications for long-running tasks

### Interoperability
- Common protocol across different agent frameworks
- Standardized message formats
- Capability negotiation

## Getting Started

To start using A2A:

1. Review the [JSON specification](https://github.com/google/A2A/blob/main/specification/json/a2a.json)
2. Explore the sample implementations:
   - [Python samples](https://github.com/google/A2A/tree/main/samples/python)
   - [JavaScript samples](https://github.com/google/A2A/tree/main/samples/js)
3. Try the [multi-agent web app demo](https://github.com/google/A2A/tree/main/demo)

## Future Developments

The A2A protocol is evolving with planned enhancements:
- Agent Discovery improvements with authorization schemes
- Agent collaboration capabilities
- Dynamic UX re-negotiation within tasks
- Extended support for client methods
- Improvements to streaming and push notifications

## Conclusion

The Agent2Agent (A2A) protocol represents a significant step forward in enabling interoperability between AI agents. By providing a standardized way for agents to communicate, discover capabilities, and collaborate, A2A helps unlock the full potential of multi-agent systems in enterprise environments.
