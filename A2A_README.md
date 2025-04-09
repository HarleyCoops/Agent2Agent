# Agent2Agent (A2A) Protocol

![A2A Banner](https://github.com/google/A2A/raw/main/images/A2A_banner.png)

**An open protocol enabling communication and interoperability between opaque agentic applications.**

## Overview

The Agent2Agent (A2A) protocol is a groundbreaking open protocol developed by Google that enables seamless communication and interoperability between AI agents built on different frameworks and platforms. Released in April 2025, A2A addresses one of the biggest challenges in enterprise AI adoption: getting agents built on different frameworks and vendors to work together effectively.

A2A provides a common language for agents across different ecosystems to communicate with each other, regardless of the framework or vendor they are built on. This protocol is critical for supporting multi-agent communication by allowing agents to:

- Discover each other's capabilities
- Negotiate how they will interact with users (via text, forms, or bidirectional audio/video)
- Work securely together in enterprise environments

## Key Features

- **Framework Agnostic**: Works with any agent framework (Google ADK, LangGraph, CrewAI, etc.)
- **Standardized Communication**: JSON-RPC based protocol with well-defined methods
- **Task Lifecycle Management**: Structured task states (created, working, input-required, completed, failed, canceled)
- **Multi-modal Interactions**: Support for text, data, files, and forms
- **Streaming Responses**: Real-time updates during task processing
- **Push Notifications**: Asynchronous updates for long-running tasks
- **Enterprise Ready**: Security, authentication, and scalability built-in

## LangGraph Implementation

The A2A protocol includes a powerful implementation using [LangGraph](https://langchain-ai.github.io/langgraph/), a library for building stateful, multi-actor applications with LLMs. The LangGraph implementation showcases how to build A2A-compatible agents using a graph-based architecture.

### Key Aspects of the LangGraph Implementation

- **Graph-based Architecture**: Defines the flow of information between components using directed graphs
- **State Management**: Maintains state across multiple interactions, perfect for A2A's task lifecycle
- **Multi-turn Conversations**: Supports complex interactions through the `input-required` state
- **Streaming Support**: Provides real-time updates during task processing
- **Tool Integration**: Demonstrates integration with external tools for currency conversion

### Sample Agent: Currency Converter

The sample LangGraph implementation is a Currency Converter agent that:
- Takes user queries about currency conversion
- Requests additional information if needed
- Performs currency conversions using external tools
- Returns results in both synchronous and streaming modes

## Getting Started

### Prerequisites

- Python 3.13 or higher
- UV package manager
- Access to an LLM (the sample uses Google Gemini)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/google/A2A.git
   ```

2. Navigate to the samples directory:
   ```bash
   cd A2A/samples/python
   ```

3. Create an environment file for the LangGraph agent:
   ```bash
   touch agents/langgraph/.env
   ```

4. Add your API key to the .env file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Running the LangGraph Agent

1. Start the LangGraph agent:
   ```bash
   uv run agents/langgraph
   ```

2. Run one of the client applications:
   ```bash
   uv run hosts/cli
   ```

### Example Interactions

#### Basic Conversion

**User Query:**
```
How much is 100 USD in EUR?
```

**Agent Response:**
```
Based on the current exchange rate, 100 USD is equivalent to 92.34 EUR.
```

#### Multi-turn Conversation

**User Query (Initial):**
```
How much is 1 USD?
```

**Agent Response (Intermediate):**
```
Which currency do you want to convert to? Also, do you want the latest exchange rate or a specific date?
```

**User Query (Follow-up):**
```
JPY
```

**Agent Response (Final):**
```
The current exchange rate is 1 USD = 151.72 JPY.
```

## Protocol Documentation

### Agent Card

The Agent Card is a metadata structure that describes an agent's capabilities:

```json
{
  "name": "Currency Converter",
  "description": "Converts between different currencies",
  "url": "http://localhost:10000",
  "provider": {
    "organization": "Example Org",
    "url": "https://example.org"
  },
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "skills": [
    {
      "id": "currency_conversion",
      "name": "Currency Conversion",
      "description": "Convert between different currencies",
      "examples": [
        "Convert 100 USD to EUR",
        "How much is 50 GBP in JPY?"
      ]
    }
  ]
}
```

### Task Lifecycle

Tasks in A2A follow a defined lifecycle with these states:

1. **created**: Initial state when a task is created
2. **working**: The agent is actively processing the task
3. **input-required**: The agent needs additional input to continue
4. **completed**: The task has been successfully completed
5. **failed**: The task could not be completed
6. **canceled**: The task was canceled before completion

### API Methods

The A2A protocol defines several JSON-RPC methods:

- `agent/getCard`: Retrieves the agent's card with capabilities and skills
- `tasks/send`: Sends a task to an agent
- `tasks/sendSubscribe`: Sends a task and subscribes to streaming updates
- `tasks/get`: Retrieves the current state of a task
- `tasks/cancel`: Cancels an ongoing task

## Building Your Own A2A Agent with LangGraph

The LangGraph implementation provides an excellent starting point for building your own A2A-compatible agents. Key components to understand:

1. **State Management**: Define your agent's state using Pydantic models
2. **Graph Structure**: Create a directed graph with nodes for different processing steps
3. **A2A Integration**: Map between LangGraph states and A2A task states
4. **Streaming Support**: Implement streaming for real-time updates

For a detailed guide on building A2A agents with LangGraph, see the [A2A LangGraph Guide](A2A_LangGraph_Guide.md).

## Framework Integrations

A2A supports multiple agent frameworks:

- **Google Agent Development Kit (ADK)**: [Sample implementation](https://github.com/google/A2A/tree/main/samples/python/agents/google_adk)
- **LangGraph**: [Sample implementation](https://github.com/google/A2A/tree/main/samples/python/agents/langgraph)
- **CrewAI**: [Sample implementation](https://github.com/google/A2A/tree/main/samples/python/agents/crewai)
- **Genkit**: [Sample implementation](https://github.com/google/A2A/tree/main/samples/js/src/agents)

## Key Topics

- [A2A and MCP](https://google.github.io/A2A/#/topics/a2a_and_mcp.md): Relationship between A2A and the Multi-agent Conversation Protocol
- [Agent Discovery](https://google.github.io/A2A/#/topics/agent_discovery.md): How agents discover each other's capabilities
- [Enterprise Ready](https://google.github.io/A2A/#/topics/enterprise_ready.md): Enterprise features of A2A
- [Push Notifications](https://google.github.io/A2A/#/topics/push_notifications.md): Asynchronous updates for long-running tasks

## Future Developments

The A2A protocol is evolving with planned enhancements:
- Agent Discovery improvements with authorization schemes
- Agent collaboration capabilities
- Dynamic UX re-negotiation within tasks
- Extended support for client methods
- Improvements to streaming and push notifications

## Contributing

We welcome contributions! Please see the [contributing guide](https://github.com/google/A2A/blob/main/CONTRIBUTING.md) to get started.

## License

A2A Protocol is an open source project run by Google LLC, under [Apache 2.0 License](https://github.com/google/A2A/blob/main/LICENSE) and open to contributions from the entire community.
