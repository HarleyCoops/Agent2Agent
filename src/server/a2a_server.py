"""
A2A server implementation.
"""

import os
import json
import asyncio
import uuid
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .a2a_models import (
    AgentCard, AgentCapabilities, AgentSkill, AgentProvider,
    Task, TaskStatus, Artifact, Part, Message,
    JSONRPCRequest, JSONRPCResponse, JSONRPCError,
    TaskIdParams, TaskQueryParams, TaskSendParams
)

from ..agent import agent_graph, AgentState

# Load environment variables
load_dotenv()

# Session storage
sessions: Dict[str, Dict[str, AgentState]] = {}


class A2AServer:
    """A2A server implementation."""
    
    def __init__(self):
        """Initialize the A2A server."""
        self.app = FastAPI(title="A2A LangGraph Server")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self.app.post("/")(self.handle_jsonrpc)
    
    async def handle_jsonrpc(self, request: Request) -> JSONResponse:
        """Handle JSON-RPC requests."""
        try:
            # Parse request
            data = await request.json()
            jsonrpc_request = JSONRPCRequest(**data)
            
            # Route to appropriate handler
            if jsonrpc_request.method == "agent/getCard":
                result = self.get_agent_card()
                return JSONResponse(
                    content=JSONRPCResponse(
                        jsonrpc="2.0",
                        id=jsonrpc_request.id,
                        result=result
                    ).dict(exclude_none=True)
                )
            
            elif jsonrpc_request.method == "tasks/send":
                params = TaskSendParams(**jsonrpc_request.params)
                result = await self.process_task(params)
                return JSONResponse(
                    content=JSONRPCResponse(
                        jsonrpc="2.0",
                        id=jsonrpc_request.id,
                        result=result
                    ).dict(exclude_none=True)
                )
            
            elif jsonrpc_request.method == "tasks/sendSubscribe":
                params = TaskSendParams(**jsonrpc_request.params)
                return EventSourceResponse(self.stream_task(params, jsonrpc_request.id))
            
            elif jsonrpc_request.method == "tasks/get":
                params = TaskQueryParams(**jsonrpc_request.params)
                result = self.get_task(params)
                return JSONResponse(
                    content=JSONRPCResponse(
                        jsonrpc="2.0",
                        id=jsonrpc_request.id,
                        result=result
                    ).dict(exclude_none=True)
                )
            
            elif jsonrpc_request.method == "tasks/cancel":
                params = TaskIdParams(**jsonrpc_request.params)
                result = self.cancel_task(params)
                return JSONResponse(
                    content=JSONRPCResponse(
                        jsonrpc="2.0",
                        id=jsonrpc_request.id,
                        result=result
                    ).dict(exclude_none=True)
                )
            
            else:
                # Method not found
                return JSONResponse(
                    content=JSONRPCResponse(
                        jsonrpc="2.0",
                        id=jsonrpc_request.id,
                        error=JSONRPCError(
                            code=-32601,
                            message="Method not found",
                            data={"method": jsonrpc_request.method}
                        ).dict(exclude_none=True)
                    ).dict(exclude_none=True),
                    status_code=404
                )
        
        except Exception as e:
            # Internal error
            return JSONResponse(
                content=JSONRPCResponse(
                    jsonrpc="2.0",
                    id=getattr(jsonrpc_request, "id", None),
                    error=JSONRPCError(
                        code=-32603,
                        message="Internal error",
                        data={"error": str(e)}
                    ).dict(exclude_none=True)
                ).dict(exclude_none=True),
                status_code=500
            )
    
    def get_agent_card(self) -> AgentCard:
        """Get the agent card."""
        return AgentCard(
            name=os.getenv("AGENT_NAME", "LangGraph A2A Agent"),
            description=os.getenv("AGENT_DESCRIPTION", "A demo implementation of an A2A agent using LangGraph"),
            url=f"http://{os.getenv('SERVER_HOST', 'localhost')}:{os.getenv('SERVER_PORT', '10000')}",
            provider=AgentProvider(
                organization="LangGraph Demo",
                url="https://github.com/HarleyCoops/Agent2Agent"
            ),
            version=os.getenv("AGENT_VERSION", "1.0.0"),
            capabilities=AgentCapabilities(
                streaming=True,
                pushNotifications=False,
                stateTransitionHistory=False
            ),
            skills=[
                AgentSkill(
                    id="currency_conversion",
                    name="Currency Conversion",
                    description="Convert between different currencies",
                    examples=[
                        "Convert 100 USD to EUR",
                        "How much is 50 GBP in JPY?"
                    ]
                ),
                AgentSkill(
                    id="weather_information",
                    name="Weather Information",
                    description="Get weather information for a location",
                    examples=[
                        "What's the weather like in London?",
                        "Weather forecast for New York tomorrow"
                    ]
                )
            ]
        )
    
    def get_or_create_session(self, session_id: str) -> Dict[str, AgentState]:
        """Get or create a session."""
        if session_id not in sessions:
            sessions[session_id] = {}
        return sessions[session_id]
    
    def get_or_create_task_state(self, session_id: str, task_id: str) -> AgentState:
        """Get or create a task state."""
        session = self.get_or_create_session(session_id)
        if task_id not in session:
            session[task_id] = AgentState()
        return session[task_id]
    
    async def process_task(self, params: TaskSendParams) -> Task:
        """Process a task."""
        # Get or create task state
        state = self.get_or_create_task_state(params.sessionId, params.id)
        
        # Add user message to state
        user_content = next((part.text for part in params.message.parts if part.type == "text"), "")
        state.add_user_message(user_content)
        
        # Run the graph
        result = await agent_graph.ainvoke(state)
        
        # Convert result to A2A Task
        task = Task(
            id=params.id,
            status=TaskStatus(
                state=result.task_state,
                timestamp=datetime.now().isoformat()
            ),
            history=[]
        )
        
        # If completed, add artifacts
        if result.task_state == "completed" and result.final_response:
            task.artifacts = [
                Artifact(
                    parts=[Part(type="text", text=result.final_response)],
                    index=0
                )
            ]
        
        # If input required, add message to status
        if result.task_state == "input-required":
            assistant_message = result.get_last_assistant_message()
            if assistant_message:
                task.status.message = Message(
                    role="agent",
                    parts=[Part(type="text", text=assistant_message)]
                )
        
        return task
    
    async def stream_task(self, params: TaskSendParams, request_id: Any) -> AsyncGenerator[str, None]:
        """Stream a task."""
        # Get or create task state
        state = self.get_or_create_task_state(params.sessionId, params.id)
        
        # Add user message to state
        user_content = next((part.text for part in params.message.parts if part.type == "text"), "")
        state.add_user_message(user_content)
        
        # Initial working state
        yield self.format_sse_event(JSONRPCResponse(
            jsonrpc="2.0",
            id=request_id,
            result=Task(
                id=params.id,
                status=TaskStatus(
                    state="working",
                    message=Message(
                        role="agent",
                        parts=[Part(type="text", text="Processing your request...")]
                    ),
                    timestamp=datetime.now().isoformat()
                ),
                final=False
            )
        ).dict(exclude_none=True))
        
        # Run the graph with streaming
        async for intermediate_state in agent_graph.astream(state):
            # Yield intermediate updates if available
            if intermediate_state.intermediate_responses:
                latest_response = intermediate_state.intermediate_responses[-1]
                yield self.format_sse_event(JSONRPCResponse(
                    jsonrpc="2.0",
                    id=request_id,
                    result=Task(
                        id=params.id,
                        status=TaskStatus(
                            state="working",
                            message=Message(
                                role="agent",
                                parts=[Part(type="text", text=latest_response)]
                            ),
                            timestamp=datetime.now().isoformat()
                        ),
                        final=False
                    )
                ).dict(exclude_none=True))
                await asyncio.sleep(0.5)  # Add a small delay for better streaming experience
        
        # Get final state
        final_state = sessions[params.sessionId][params.id]
        
        # If completed, yield artifact
        if final_state.task_state == "completed" and final_state.final_response:
            yield self.format_sse_event(JSONRPCResponse(
                jsonrpc="2.0",
                id=request_id,
                result=Task(
                    id=params.id,
                    artifact=Artifact(
                        parts=[Part(type="text", text=final_state.final_response)],
                        index=0,
                        append=False
                    )
                )
            ).dict(exclude_none=True))
        
        # Yield final completion
        yield self.format_sse_event(JSONRPCResponse(
            jsonrpc="2.0",
            id=request_id,
            result=Task(
                id=params.id,
                status=TaskStatus(
                    state=final_state.task_state,
                    timestamp=datetime.now().isoformat()
                ),
                final=True
            )
        ).dict(exclude_none=True))
    
    def get_task(self, params: TaskQueryParams) -> Task:
        """Get a task."""
        # Check if session exists
        if params.sessionId not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if task exists
        if params.id not in sessions[params.sessionId]:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get task state
        state = sessions[params.sessionId][params.id]
        
        # Convert state to A2A Task
        task = Task(
            id=params.id,
            status=TaskStatus(
                state=state.task_state,
                timestamp=state.last_updated
            ),
            history=[]
        )
        
        # If completed, add artifacts
        if state.task_state == "completed" and state.final_response:
            task.artifacts = [
                Artifact(
                    parts=[Part(type="text", text=state.final_response)],
                    index=0
                )
            ]
        
        # If input required, add message to status
        if state.task_state == "input-required":
            assistant_message = state.get_last_assistant_message()
            if assistant_message:
                task.status.message = Message(
                    role="agent",
                    parts=[Part(type="text", text=assistant_message)]
                )
        
        return task
    
    def cancel_task(self, params: TaskIdParams) -> Task:
        """Cancel a task."""
        # Check if session exists
        if params.sessionId not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if task exists
        if params.id not in sessions[params.sessionId]:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get task state
        state = sessions[params.sessionId][params.id]
        
        # Update task state
        state.task_state = "canceled"
        state.last_updated = datetime.now().isoformat()
        
        # Convert state to A2A Task
        task = Task(
            id=params.id,
            status=TaskStatus(
                state="canceled",
                timestamp=state.last_updated
            ),
            history=[]
        )
        
        return task
    
    @staticmethod
    def format_sse_event(data: Any) -> str:
        """Format data for SSE."""
        if isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = json.dumps(data, default=lambda o: o.dict() if hasattr(o, "dict") else str(o))
        return f"data: {json_data}\n\n"
