# Building A2A Agents with LangGraph: A Comprehensive Guide

## Introduction

This guide focuses on implementing Agent2Agent (A2A) protocol using LangGraph, a powerful framework for building stateful, multi-actor applications with Large Language Models (LLMs). LangGraph is particularly well-suited for A2A implementation due to its graph-based architecture and state management capabilities, which align perfectly with A2A's task lifecycle and multi-turn conversation requirements.

## What is LangGraph?

[LangGraph](https://langchain-ai.github.io/langgraph/) is a library built on top of LangChain that provides:

- **Graph-based orchestration**: Define the flow of information between components using directed graphs
- **State management**: Maintain state across multiple interactions
- **Conditional routing**: Direct the flow based on the output of previous steps
- **Debugging tools**: Visualize and debug agent behavior

LangGraph is designed for building complex, multi-step reasoning processes and conversational agents that maintain context across interactions - making it ideal for A2A implementations.

## A2A and LangGraph: The Perfect Match

The A2A protocol and LangGraph complement each other in several ways:

1. **State Management**: 
   - A2A defines task states (created, working, input-required, completed, failed, canceled)
   - LangGraph provides built-in state management across interactions

2. **Multi-turn Conversations**:
   - A2A supports multi-turn interactions through the `input-required` state
   - LangGraph's graph structure naturally handles conversation flows

3. **Streaming Responses**:
   - A2A supports streaming through the `tasks/sendSubscribe` method
   - LangGraph can be configured to yield intermediate results

## Setting Up Your Environment

To get started with A2A and LangGraph, you'll need:

1. Python 3.13 or higher
2. UV package manager
3. Access to an LLM (the sample uses Google Gemini)

### Installation Steps

1. Clone the A2A repository:
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

## Understanding the LangGraph A2A Implementation

The sample LangGraph implementation in the A2A repository is a Currency Converter agent that demonstrates key A2A features:

### Core Components

1. **Agent State**: Defined as a Pydantic model with:
   - User inputs and agent responses
   - Extracted parameters (source currency, target currency, amount)
   - Task status tracking

2. **Graph Structure**: A directed graph with nodes for:
   - Parsing user input
   - Checking for required parameters
   - Requesting additional information
   - Performing currency conversion
   - Generating responses

3. **A2A Integration**: Components that map between LangGraph and A2A:
   - Task state mapping
   - Response formatting
   - Streaming support

### Key Files

- `agent.py`: Main agent implementation
- `graph.py`: LangGraph graph definition
- `state.py`: State management
- `tools.py`: Currency conversion tools
- `__main__.py`: Server startup

## Building Your Own A2A Agent with LangGraph

Let's walk through the process of building an A2A-compatible agent using LangGraph:

### 1. Define Your Agent State

Start by defining the state your agent needs to maintain:

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class AgentState(BaseModel):
    # Conversation history
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Task-specific parameters
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # A2A task state
    task_state: str = "created"
    
    # Additional context
    context: Dict[str, Any] = Field(default_factory=dict)
```

### 2. Create Your Graph Nodes

Define the functions that will process information in your graph:

```python
def parse_input(state: AgentState) -> AgentState:
    """Extract parameters from user input."""
    # Extract parameters from the latest user message
    latest_message = state.messages[-1]["content"]
    
    # Use an LLM to parse the input
    parsed_params = llm.invoke(f"Extract parameters from: {latest_message}")
    
    # Update state
    state.parameters.update(parsed_params)
    state.task_state = "working"
    
    return state

def check_parameters(state: AgentState) -> str:
    """Check if all required parameters are present."""
    required_params = ["param1", "param2"]
    
    missing_params = [p for p in required_params if p not in state.parameters]
    
    if missing_params:
        return "missing_parameters"
    else:
        return "complete_parameters"

def request_missing_parameters(state: AgentState) -> AgentState:
    """Request missing parameters from the user."""
    missing_params = [p for p in ["param1", "param2"] if p not in state.parameters]
    
    # Generate a response asking for missing parameters
    response = llm.invoke(f"Ask the user for: {', '.join(missing_params)}")
    
    # Add response to messages
    state.messages.append({"role": "assistant", "content": response})
    
    # Update task state
    state.task_state = "input-required"
    
    return state

def process_task(state: AgentState) -> AgentState:
    """Process the task with complete parameters."""
    # Perform the actual task
    result = perform_task(state.parameters)
    
    # Generate a response
    response = llm.invoke(f"Generate a response for result: {result}")
    
    # Add response to messages
    state.messages.append({"role": "assistant", "content": response})
    
    # Update task state
    state.task_state = "completed"
    
    return state
```

### 3. Define Your Graph

Connect your nodes into a graph:

```python
from langgraph.graph import StateGraph

# Create a graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("parse_input", parse_input)
graph.add_node("request_missing_parameters", request_missing_parameters)
graph.add_node("process_task", process_task)

# Add edges
graph.add_edge("parse_input", check_parameters)
graph.add_conditional_edges(
    "check_parameters",
    {
        "missing_parameters": "request_missing_parameters",
        "complete_parameters": "process_task"
    }
)

# Set the entry point
graph.set_entry_point("parse_input")

# Compile the graph
app = graph.compile()
```

### 4. Integrate with A2A Server

Connect your LangGraph agent to the A2A protocol:

```python
from a2a.server import A2AServer
from a2a.models import Task, TaskStatus, Artifact, Part

class LangGraphA2AAgent:
    def __init__(self):
        self.graph = app
        self.sessions = {}
    
    def process_task(self, task_id: str, session_id: str, message: dict) -> Task:
        """Process a task according to A2A protocol."""
        # Initialize or retrieve session state
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentState()
        
        state = self.sessions[session_id]
        
        # Add user message to state
        state.messages.append({
            "role": "user", 
            "content": message["parts"][0]["text"]
        })
        
        # Run the graph
        result = self.graph.invoke(state)
        
        # Convert result to A2A Task
        task = Task(
            id=task_id,
            status=TaskStatus(
                state=result.task_state,
                timestamp=datetime.now().isoformat()
            )
        )
        
        # If completed, add artifacts
        if result.task_state == "completed":
            assistant_message = next(
                (m for m in reversed(result.messages) if m["role"] == "assistant"),
                None
            )
            if assistant_message:
                task.artifacts = [
                    Artifact(
                        parts=[Part(type="text", text=assistant_message["content"])],
                        index=0
                    )
                ]
        
        # If input required, add message to status
        if result.task_state == "input-required":
            assistant_message = next(
                (m for m in reversed(result.messages) if m["role"] == "assistant"),
                None
            )
            if assistant_message:
                task.status.message = {
                    "role": "agent",
                    "parts": [{"type": "text", "text": assistant_message["content"]}]
                }
        
        return task

# Create and start the A2A server
agent = LangGraphA2AAgent()
server = A2AServer(agent=agent)
server.start()
```

### 5. Add Streaming Support

Enhance your agent with streaming capabilities:

```python
async def process_task_stream(self, task_id: str, session_id: str, message: dict):
    """Process a task with streaming support."""
    # Initialize or retrieve session state
    if session_id not in self.sessions:
        self.sessions[session_id] = AgentState()
    
    state = self.sessions[session_id]
    
    # Add user message to state
    state.messages.append({
        "role": "user", 
        "content": message["parts"][0]["text"]
    })
    
    # Set initial task state
    state.task_state = "working"
    
    # Yield initial working state
    yield Task(
        id=task_id,
        status=TaskStatus(
            state="working",
            message={
                "role": "agent",
                "parts": [{"type": "text", "text": "Processing your request..."}]
            },
            timestamp=datetime.now().isoformat()
        ),
        final=False
    )
    
    # Run the graph with streaming
    async for intermediate_state in self.graph.astream(state):
        # Yield intermediate updates
        if intermediate_state.task_state == "working":
            # Find the latest assistant message
            assistant_message = next(
                (m for m in reversed(intermediate_state.messages) if m["role"] == "assistant"),
                None
            )
            if assistant_message:
                yield Task(
                    id=task_id,
                    status=TaskStatus(
                        state="working",
                        message={
                            "role": "agent",
                            "parts": [{"type": "text", "text": assistant_message["content"]}]
                        },
                        timestamp=datetime.now().isoformat()
                    ),
                    final=False
                )
    
    # Get final state
    final_state = self.sessions[session_id]
    
    # If completed, yield artifact
    if final_state.task_state == "completed":
        assistant_message = next(
            (m for m in reversed(final_state.messages) if m["role"] == "assistant"),
            None
        )
        if assistant_message:
            yield Task(
                id=task_id,
                artifact=Artifact(
                    parts=[Part(type="text", text=assistant_message["content"])],
                    index=0,
                    append=False
                )
            )
    
    # Yield final completion
    yield Task(
        id=task_id,
        status=TaskStatus(
            state=final_state.task_state,
            timestamp=datetime.now().isoformat()
        ),
        final=True
    )
```

## Advanced LangGraph Features for A2A

### 1. Parallel Processing

LangGraph supports parallel processing, which can be useful for complex A2A agents:

```python
# Create branches for parallel processing
with graph.branch("parallel_branch") as branch:
    branch.add_node("process_branch_1", process_branch_1)
    branch.add_node("process_branch_2", process_branch_2)
    
    # Set the entry point for this branch
    branch.set_entry_point("process_branch_1")
    
    # Add edges within the branch
    branch.add_edge("process_branch_1", "process_branch_2")

# Continue with the main graph
graph.add_edge("some_node", "parallel_branch")
graph.add_edge("parallel_branch", "next_node")
```

### 2. Human-in-the-Loop

Implement human-in-the-loop workflows using A2A's `input-required` state:

```python
def check_human_approval_needed(state: AgentState) -> str:
    """Determine if human approval is needed."""
    if state.parameters.get("amount", 0) > 1000:
        return "need_approval"
    else:
        return "auto_approve"

def request_human_approval(state: AgentState) -> AgentState:
    """Request approval from a human."""
    # Generate approval request
    request = f"Please approve transaction of {state.parameters.get('amount')} {state.parameters.get('currency')}"
    
    # Add to messages
    state.messages.append({"role": "assistant", "content": request})
    
    # Set task state to input-required
    state.task_state = "input-required"
    
    return state

# Add conditional edges
graph.add_conditional_edges(
    "check_human_approval_needed",
    {
        "need_approval": "request_human_approval",
        "auto_approve": "process_transaction"
    }
)
```

### 3. Tool Integration

Integrate external tools with your LangGraph A2A agent:

```python
from langchain.tools import Tool

# Define a tool
currency_converter_tool = Tool(
    name="currency_converter",
    description="Convert between currencies",
    func=lambda amount, from_currency, to_currency: convert_currency(amount, from_currency, to_currency)
)

def use_tools(state: AgentState) -> AgentState:
    """Use tools to perform tasks."""
    # Extract parameters
    amount = state.parameters.get("amount")
    from_currency = state.parameters.get("from_currency")
    to_currency = state.parameters.get("to_currency")
    
    # Use the tool
    result = currency_converter_tool.invoke({
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency
    })
    
    # Store result
    state.context["conversion_result"] = result
    
    return state

# Add to graph
graph.add_node("use_tools", use_tools)
graph.add_edge("process_parameters", "use_tools")
graph.add_edge("use_tools", "generate_response")
```

## Testing Your A2A LangGraph Agent

### 1. Unit Testing

Test individual components of your LangGraph agent:

```python
def test_parse_input():
    # Create a test state
    state = AgentState()
    state.messages.append({
        "role": "user",
        "content": "Convert 100 USD to EUR"
    })
    
    # Run the function
    result = parse_input(state)
    
    # Assert expectations
    assert "amount" in result.parameters
    assert result.parameters["amount"] == 100
    assert result.parameters["from_currency"] == "USD"
    assert result.parameters["to_currency"] == "EUR"
```

### 2. Integration Testing

Test the A2A protocol integration:

```python
async def test_a2a_integration():
    # Create a test client
    from a2a.client import A2AClient
    
    client = A2AClient(url="http://localhost:10000")
    
    # Send a task
    response = await client.send_task(
        task_id="test_task",
        session_id="test_session",
        message={
            "role": "user",
            "parts": [{"type": "text", "text": "Convert 100 USD to EUR"}]
        }
    )
    
    # Assert expectations
    assert response.status.state == "completed"
    assert len(response.artifacts) > 0
    assert "EUR" in response.artifacts[0].parts[0].text
```

## Best Practices for A2A LangGraph Agents

1. **State Management**:
   - Keep your state model clean and well-structured
   - Use Pydantic for type validation
   - Consider persistence for long-running sessions

2. **Error Handling**:
   - Implement proper error states in your graph
   - Map errors to appropriate A2A task states
   - Provide meaningful error messages

3. **Performance**:
   - Use caching for LLM calls
   - Implement timeouts for external tools
   - Consider batching for multiple operations

4. **Security**:
   - Validate and sanitize user inputs
   - Implement authentication for your A2A server
   - Use secure connections (HTTPS)

5. **Monitoring**:
   - Log state transitions
   - Track LLM usage
   - Monitor performance metrics

## Conclusion

LangGraph provides a powerful framework for implementing A2A-compatible agents. Its graph-based architecture and state management capabilities align perfectly with A2A's requirements for multi-turn conversations, task lifecycle management, and streaming responses.

By following this guide, you can build sophisticated A2A agents that leverage LangGraph's strengths while conforming to the A2A protocol, enabling interoperability with other agents in the ecosystem.

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [A2A Protocol Specification](https://github.com/google/A2A/blob/main/specification/json/a2a.json)
- [A2A LangGraph Sample](https://github.com/google/A2A/tree/main/samples/python/agents/langgraph)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
