"""
A2A client implementation.
"""

import json
import uuid
import asyncio
import requests
import sseclient
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Callable
from datetime import datetime


class A2AClient:
    """A2A client implementation."""
    
    def __init__(self, url: str = "http://localhost:10000"):
        """Initialize the A2A client."""
        self.url = url
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Get the agent card."""
        response = requests.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "agent/getCard",
                "params": {}
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get agent card: {response.text}")
        
        return response.json()["result"]
    
    def send_task(self, task_id: str, session_id: str, message: str) -> Dict[str, Any]:
        """Send a task to the agent."""
        response = requests.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tasks/send",
                "params": {
                    "id": task_id,
                    "sessionId": session_id,
                    "acceptedOutputModes": ["text"],
                    "message": {
                        "role": "user",
                        "parts": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to send task: {response.text}")
        
        return response.json()["result"]
    
    def stream_task(self, task_id: str, session_id: str, message: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Stream a task from the agent."""
        response = requests.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tasks/sendSubscribe",
                "params": {
                    "id": task_id,
                    "sessionId": session_id,
                    "acceptedOutputModes": ["text"],
                    "message": {
                        "role": "user",
                        "parts": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                }
            },
            stream=True
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to stream task: {response.text}")
        
        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            callback(data["result"])
    
    def get_task(self, task_id: str, session_id: str) -> Dict[str, Any]:
        """Get a task."""
        response = requests.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tasks/get",
                "params": {
                    "id": task_id,
                    "sessionId": session_id,
                    "includeHistory": False
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get task: {response.text}")
        
        return response.json()["result"]
    
    def cancel_task(self, task_id: str, session_id: str) -> Dict[str, Any]:
        """Cancel a task."""
        response = requests.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tasks/cancel",
                "params": {
                    "id": task_id,
                    "sessionId": session_id
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to cancel task: {response.text}")
        
        return response.json()["result"]
