# A2A LangGraph Demo

A demonstration of implementing the Agent2Agent (A2A) protocol using LangGraph.

## Overview

This project showcases how to build an A2A-compatible agent using LangGraph, a library for building stateful, multi-actor applications with LLMs. The implementation demonstrates key A2A features including:

- Task lifecycle management
- Multi-turn conversations
- Streaming responses
- Integration with external tools

## Project Structure

```
a2a_langgraph_demo/
├── src/
│   ├── agent/         # LangGraph agent implementation
│   ├── server/        # A2A server implementation
│   └── client/        # Simple test client
├── .env               # Environment variables (not committed)
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore file
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Prerequisites

- Python 3.9+
- OpenAI API key or Google API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HarleyCoops/Agent2Agent.git
   cd Agent2Agent/a2a_langgraph_demo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and add your API keys.

## Usage

1. Start the A2A server:
   ```bash
   python -m src.server.main
   ```

2. In another terminal, run the test client:
   ```bash
   python -m src.client.main
   ```

## Features

- **Task-based Agent**: Implements a task-oriented agent that can handle multi-turn conversations
- **A2A Protocol**: Fully implements the A2A protocol for agent communication
- **LangGraph Architecture**: Uses LangGraph's graph-based architecture for agent logic
- **Streaming Support**: Supports streaming responses for real-time updates

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
