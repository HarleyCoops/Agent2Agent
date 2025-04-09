# A2A LangGraph Implementation Documentation

## Overview

The LangGraph implementation of the Agent2Agent (A2A) protocol demonstrates how to build an A2A-compatible agent using the LangGraph framework. This implementation is particularly significant as it showcases how to integrate a popular agent orchestration framework with the A2A protocol, enabling interoperability with other agent frameworks.

## What is LangGraph?

[LangGraph](https://langchain-ai.github.io/langgraph/) is a library for building stateful, multi-actor applications with LLMs. It extends LangChain with:

- A graph-based data structure for orchestrating the flow of information between components
- Persistence of state across multiple interactions
- Tools for debugging and visualizing agent behavior

LangGraph is particularly well-suited for building complex, multi-step reasoning processes and conversational agents that maintain context across interactions.

## A2A LangGraph Agent Architecture

The sample A2A LangGraph agent implements a Currency Converter that:

1. Takes user queries about currency conversion
2. Processes the queries to extract relevant information
3. Requests additional information if needed
4. Performs currency conversions using external tools
5. Returns results to the user

### Key Components

The implementation consists of several key components:

#### 1. Agent State Management

The LangGraph agent maintains state across interactions, which is crucial for implementing the A2A task lifecycle. The state includes:

- User inputs and agent responses
- Extracted parameters (source currency, target currency, amount)
- Task status (working, input-required, completed)

#### 2. Graph Structure

The agent uses a directed graph to define the flow of information and decision-making:

- Nodes represent processing steps (parse input, check parameters, convert currency, etc.)
- Edges define the flow between steps based on conditions
- Conditional routing handles different scenarios (complete information, missing information)

#### 3. A2A Protocol Integration

The implementation integrates with the A2A protocol by:

- Exposing an HTTP endpoint that accepts A2A JSON-RPC requests
- Mapping LangGraph state to A2A task states
- Converting LangGraph outputs to A2A artifacts
- Supporting both synchronous and streaming responses

## Multi-turn Conversation Support

One of the key features of the LangGraph implementation is its support for multi-turn conversations, which aligns perfectly with the A2A task lifecycle:

1. When a user sends an initial query that lacks complete information (e.g., "How much is 1 USD?"), the agent:
   - Sets the task state to `input-required`
   - Generates a response asking for the missing information
   - Maintains the conversation context

2. When the user provides the additional information, the agent:
   - Retrieves the previous context
   - Combines it with the new information
   - Completes the task
   - Sets the task state to `completed`

This multi-turn capability is essential for complex tasks that require clarification or additional information from users.

## Streaming Support

The LangGraph implementation also demonstrates how to support streaming responses in the A2A protocol:

1. When a streaming request is received (`tasks/sendSubscribe`), the agent:
   - Processes the request asynchronously
   - Sends intermediate updates as the task progresses
   - Streams the final result in chunks
   - Sends a completion notification

This streaming capability is important for providing responsive user experiences, especially for tasks that take time to complete.

## Code Structure

The LangGraph A2A implementation is structured as follows:

### 1. Agent Definition

The agent is defined using LangGraph's graph-based structure, with nodes for:
- Parsing user input
- Checking for required parameters
- Requesting additional information
- Performing currency conversion
- Generating responses

### 2. A2A Server Integration

The agent is integrated with the A2A server through:
- Task management (creation, retrieval, cancellation)
- State mapping between LangGraph and A2A
- Response formatting according to A2A specifications

### 3. External Tool Integration

The agent integrates with external tools for currency conversion, demonstrating how LangGraph agents can leverage external capabilities.

## Example Interactions

### Basic Conversion

**User Query:**
```
How much is 100 USD in EUR?
```

**Agent Processing:**
1. Parses the query to extract parameters (amount=100, source=USD, target=EUR)
2. Checks that all required parameters are present
3. Performs the currency conversion
4. Returns the result in A2A format

**A2A Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "123",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:53:29.301828"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "100 USD is equivalent to 92.34 EUR based on the current exchange rate."
          }
        ],
        "index": 0
      }
    ],
    "history": []
  }
}
```

### Multi-turn Conversation

**User Query (Initial):**
```
How much is 1 USD?
```

**Agent Processing:**
1. Parses the query but identifies missing parameter (target currency)
2. Sets task state to `input-required`
3. Generates a response asking for the missing information

**A2A Response (Intermediate):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "id": "124",
    "status": {
      "state": "input-required",
      "message": {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "Which currency do you want to convert to? Also, do you want the latest exchange rate or a specific date?"
          }
        ]
      },
      "timestamp": "2025-04-02T16:57:02.336787"
    },
    "history": []
  }
}
```

**User Query (Follow-up):**
```
JPY
```

**Agent Processing:**
1. Retrieves previous context (1 USD)
2. Combines with new information (target=JPY)
3. Performs the currency conversion
4. Sets task state to `completed`

**A2A Response (Final):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "id": "124",
    "status": {
      "state": "completed",
      "timestamp": "2025-04-02T16:57:40.033328"
    },
    "artifacts": [
      {
        "parts": [
          {
            "type": "text",
            "text": "The current exchange rate is 1 USD = 151.72 JPY."
          }
        ],
        "index": 0
      }
    ],
    "history": []
  }
}
```

## Integration with Other A2A Agents

The LangGraph implementation can interact with other A2A-compatible agents, regardless of their underlying framework. This interoperability is achieved through:

1. **Common Protocol**: Using the standardized A2A JSON-RPC methods and message formats
2. **Capability Negotiation**: Exchanging agent cards to understand capabilities
3. **Task Lifecycle Management**: Following the A2A task state transitions

This allows the LangGraph agent to participate in multi-agent systems where agents built with different frameworks (Google ADK, CrewAI, etc.) collaborate to solve complex problems.

## Conclusion

The LangGraph implementation of A2A demonstrates how this protocol can be integrated with a powerful agent orchestration framework. The implementation showcases key A2A features including:

- Multi-turn conversations through task state management
- Streaming responses for responsive user experiences
- Integration with external tools
- Interoperability with other agent frameworks

This implementation serves as a valuable reference for developers looking to build A2A-compatible agents using LangGraph, contributing to the broader ecosystem of interoperable AI agents.
