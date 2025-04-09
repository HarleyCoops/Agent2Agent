import asyncio
import threading
import os
from typing import Any
from fastapi import APIRouter
from fastapi import Request
from common.types import Message, Task
from .in_memory_manager import InMemoryFakeAgentManager
from .application_manager import ApplicationManager
from .adk_host_manager import ADKHostManager
from service.types import (
    Conversation,
    Event,
    CreateConversationResponse,
    ListConversationResponse,
    SendMessageResponse,
    MessageInfo,
    ListMessageResponse,
    PendingMessageResponse,
    ListTaskResponse,
    RegisterAgentResponse,
    ListAgentResponse,
    GetEventResponse
)

class ConversationServer:
  """ConversationServer is the backend to serve the agent interactions in the UI

  This defines the interface that is used by the Mesop system to interact with
  agents and provide details about the executions.
  """
  def __init__(self, router: APIRouter):
    agent_manager = os.environ.get("A2A_HOST", "ADK")
    self.manager: ApplicationManager
    if agent_manager.upper() == "ADK":
      self.manager = ADKHostManager()
    else:
      self.manager = InMemoryFakeAgentManager()

    router.add_api_route(
        "/conversation/create",
        self._create_conversation,
        methods=["POST"])
    router.add_api_route(
        "/conversation/list",
        self._list_conversation,
        methods=["POST"])
    router.add_api_route(
        "/message/send",
        self._send_message,
        methods=["POST"])
    router.add_api_route(
        "/events/get",
        self._get_events,
        methods=["POST"])
    router.add_api_route(
        "/message/list",
        self._list_messages,
        methods=["POST"])
    router.add_api_route(
        "/message/pending",
        self._pending_messages,
        methods=["POST"])
    router.add_api_route(
        "/task/list",
        self._list_tasks,
        methods=["POST"])
    router.add_api_route(
        "/agent/register",
        self._register_agent,
        methods=["POST"])
    router.add_api_route(
        "/agent/list",
        self._list_agents,
        methods=["POST"])


  def _create_conversation(self):
    c = self.manager.create_conversation()
    return CreateConversationResponse(result=c)

  async def _send_message(self, request: Request):
    message_data = await request.json()
    message = Message(**message_data['params'])
    message = self.manager.sanitize_message(message)
    t = threading.Thread(target=lambda: asyncio.run(self.manager.process_message(message)))
    t.start()
    return SendMessageResponse(result=MessageInfo(
        message_id=message.metadata['message_id'],
        conversation_id=message.metadata['conversation_id'] if 'conversation_id' in message.metadata else '',
    ))

  async def _list_messages(self, request: Request):
    message_data = await request.json()
    conversation_id = message_data['params']
    conversation = self.manager.get_conversation(conversation_id)
    if conversation:
      return ListMessageResponse(result=conversation.messages)
    return ListMessageResponse(result=[])

  async def _pending_messages(self):
    return PendingMessageResponse(result=self.manager.get_pending_messages())

  def _list_conversation(self):
    return ListConversationResponse(result=self.manager.conversations)

  def _get_events(self):
    return GetEventResponse(result=self.manager.events)

  def _list_tasks(self):
    return ListTaskResponse(result=self.manager.tasks)

  async def _register_agent(self, request: Request):
    message_data = await request.json()
    url = message_data['params']
    self.manager.register_agent(url)
    return RegisterAgentResponse()

  async def _list_agents(self):
    return ListAgentResponse(result=self.manager.agents)

