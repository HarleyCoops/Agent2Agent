"""
State definitions for the LangGraph agent.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """A message in the conversation."""
    role: str
    content: str


class AgentState(BaseModel):
    """The state of the agent."""
    
    # Conversation history
    messages: List[Message] = Field(default_factory=list)
    
    # Task-specific parameters
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # A2A task state: created, working, input-required, completed, failed, canceled
    task_state: str = "created"
    
    # Additional context
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamp of the last update
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Final response to be returned
    final_response: Optional[str] = None
    
    # Intermediate responses for streaming
    intermediate_responses: List[str] = Field(default_factory=list)
    
    # Error message if any
    error: Optional[str] = None
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self.messages.append(Message(role="user", content=content))
        self.last_updated = datetime.now().isoformat()
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        self.messages.append(Message(role="assistant", content=content))
        self.last_updated = datetime.now().isoformat()
    
    def add_intermediate_response(self, content: str) -> None:
        """Add an intermediate response for streaming."""
        self.intermediate_responses.append(content)
        self.last_updated = datetime.now().isoformat()
    
    def set_final_response(self, content: str) -> None:
        """Set the final response."""
        self.final_response = content
        self.last_updated = datetime.now().isoformat()
    
    def set_error(self, error: str) -> None:
        """Set an error message."""
        self.error = error
        self.task_state = "failed"
        self.last_updated = datetime.now().isoformat()
    
    def get_conversation_history(self) -> str:
        """Get the conversation history as a string."""
        return "\n".join([f"{msg.role}: {msg.content}" for msg in self.messages])
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last assistant message."""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return None
