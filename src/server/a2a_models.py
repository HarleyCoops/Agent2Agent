"""
A2A protocol models.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Part(BaseModel):
    """A part of a message or artifact."""
    type: str
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    file: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """A message in the A2A protocol."""
    role: str
    parts: List[Part]


class TaskStatus(BaseModel):
    """The status of a task."""
    state: Literal["created", "working", "input-required", "completed", "failed", "canceled"]
    message: Optional[Message] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Artifact(BaseModel):
    """An artifact produced by an agent."""
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    index: int = 0
    append: Optional[bool] = None
    lastChunk: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class Task(BaseModel):
    """A task in the A2A protocol."""
    id: str
    status: TaskStatus
    artifacts: Optional[List[Artifact]] = None
    history: List[Any] = Field(default_factory=list)
    final: Optional[bool] = None
    artifact: Optional[Artifact] = None


class TaskIdParams(BaseModel):
    """Parameters for task ID-based requests."""
    id: str
    sessionId: str


class TaskQueryParams(BaseModel):
    """Parameters for task query requests."""
    id: str
    sessionId: str
    includeHistory: Optional[bool] = False


class TaskSendParams(BaseModel):
    """Parameters for task send requests."""
    id: str
    sessionId: str
    acceptedOutputModes: List[str] = ["text"]
    message: Message


class AgentCapabilities(BaseModel):
    """Agent capabilities."""
    streaming: bool = False
    pushNotifications: bool = False
    stateTransitionHistory: bool = False


class AgentSkill(BaseModel):
    """An agent skill."""
    id: str
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    inputModes: Optional[List[str]] = None
    outputModes: Optional[List[str]] = None


class AgentProvider(BaseModel):
    """Agent provider information."""
    organization: str
    url: Optional[str] = None


class AgentAuthentication(BaseModel):
    """Agent authentication information."""
    schemes: List[str]
    credentials: Optional[str] = None


class AgentCard(BaseModel):
    """Agent card with capabilities and skills."""
    name: str
    description: Optional[str] = None
    url: str
    provider: Optional[AgentProvider] = None
    version: str
    documentationUrl: Optional[str] = None
    capabilities: AgentCapabilities
    authentication: Optional[AgentAuthentication] = None
    defaultInputModes: List[str] = ["text"]
    defaultOutputModes: List[str] = ["text"]
    skills: List[AgentSkill]


class JSONRPCRequest(BaseModel):
    """JSON-RPC request."""
    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None
    method: str
    params: Any


class JSONRPCResponse(BaseModel):
    """JSON-RPC response."""
    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class JSONRPCError(BaseModel):
    """JSON-RPC error."""
    code: int
    message: str
    data: Optional[Any] = None
