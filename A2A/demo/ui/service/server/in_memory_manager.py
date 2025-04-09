import asyncio
import datetime
from typing import Tuple, Optional
import uuid
from service.types import Conversation, Event
from common.types import (
    Message,
    Task,
    TextPart,
    TaskState,
    TaskStatus,
    Artifact,
    AgentCard,
    DataPart,
)
from utils.agent_card import get_agent_card
from service.server.application_manager import ApplicationManager

class InMemoryFakeAgentManager(ApplicationManager):
  """An implementation of memory based management with fake agent actions

  This implements the interface of the ApplicationManager to plug into
  the AgentServer. This acts as the service contract that the Mesop app
  uses to send messages to the agent and provide information for the frontend.
  """
  _conversations: list[Conversation]
  _messages: list[Message]
  _tasks: list[Task]
  _events: list[Event]
  _pending_message_ids: list[str]
  _next_message_idx: int
  _agents: list[AgentCard]

  def __init__(self):
    self._conversations = []
    self._messages = []
    self._tasks = []
    self._events = []
    self._pending_message_ids = []
    self._next_message_idx = 0
    self._agents = []

  def create_conversation(self) -> Conversation:
    conversation_id = str(uuid.uuid4())
    c = Conversation(conversation_id=conversation_id, is_active=True)
    self._conversations.append(c)
    return c

  def sanitize_message(self, message: Message) -> Message:
    if not message.metadata:
      message.metadata = {}
    message.metadata.update({'message_id': str(uuid.uuid4())})
    return message

  async def process_message(self, message: Message):
    self._messages.append(message)
    self._pending_message_ids.append(message.metadata['message_id'])
    conversation_id = (
        message.metadata['conversation_id']
        if 'conversation_id' in message.metadata
        else None
    )
    # Now check the conversation and attach the message id.
    conversation = self.get_conversation(conversation_id)
    if conversation:
      conversation.messages.append(message)
    self._events.append(Event(
        id=str(uuid.uuid4()),
        actor="host",
        content=message,
        timestamp=datetime.datetime.utcnow().timestamp(),
    ))
    # Now actually process the message. If the response is async, return None
    # for the message response and the updated message information for the
    # incoming message (with ids attached).
    task_id = str(uuid.uuid4())
    if self._next_message_idx != 0:
      self.add_task(
          Task(
              id=task_id,
              sessionId=conversation_id,
              status=TaskStatus(
                  state=TaskState.SUBMITTED,
                  message=message,
              ),
          )
      )
    await asyncio.sleep(self._next_message_idx)
    response = self.next_message()
    response.metadata = {**message.metadata, **{'message_id': str(uuid.uuid4())}}
    if conversation:
      conversation.messages.append(response)
    self._events.append(Event(
        id=str(uuid.uuid4()),
        actor="host",
        content=response,
        timestamp=datetime.datetime.utcnow().timestamp(),
    ))
    self._pending_message_ids.remove(message.metadata['message_id'])
    # Now clean up the task
    task = next(filter(lambda x: x.id == task_id, self.tasks), None)
    if task:
      task.status.state = TaskState.COMPLETED
      task.artifacts = [Artifact(name="response", parts=response.parts)]
      self.update_task(task)

  def add_task(self, task: Task):
    self._tasks.append(task)

  def update_task(self, task: Task):
    for i, t in enumerate(self._tasks):
      if t.id == task.id:
        self._tasks[i] = task
        return

  def add_event(self, event: Event):
    self._events.append(event)

  def next_message(self) -> Message:
    message = _message_queue[self._next_message_idx]
    self._next_message_idx = (self._next_message_idx + 1) % len(_message_queue)
    return message

  def get_conversation(
      self,
      conversation_id: Optional[str]
  ) -> Optional[Conversation]:
    if not conversation_id:
      return None
    return next(
        filter(lambda c: c.conversation_id == conversation_id,
               self._conversations), None)

  def get_pending_messages(self) -> list[str]:
    return self._pending_message_ids

  def register_agent(self, url):
    agent_data = get_agent_card(url)
    if not agent_data.url:
      agent_data.url = url
    self._agents.append(agent_data)

  @property
  def agents(self) -> list[AgentCard]:
    return self._agents

  @property
  def conversations(self) -> list[Conversation]:
    return self._conversations

  @property
  def tasks(self) -> list[Task]:
    return self._tasks

  @property
  def events(self) -> list[Event]:
    return self._events

# This represents the precanned responses that will be returned in order.
# Extend this list to test more functionality of the UI
_message_queue: list[Message] = [
    Message(role="agent", parts=[TextPart(text="Hello")]),
    Message(role="agent", parts=[
        DataPart(
            data={
              'type': 'form',
              'form': {
                  'type': 'object',
                  'properties': {
                      'name': {
                          'type': 'string',
                          'description': 'Enter your name',
                          'title': 'Name',
                      },
                      'date': {
                          'type': 'string',
                          'format': 'date',
                          'description': 'Birthday',
                          'title': 'Birthday',
                      },
                  },
                  'required': ['date'],
              },
              'form_data': {
                  'name': 'John Smith',
              },
              'instructions': "Please provide your birthday and name",
           }
        ),
    ]),
    Message(role="agent", parts=[TextPart(text="I like cats")]),
    Message(role="agent", parts=[TextPart(text="And I like dogs")]),
]
