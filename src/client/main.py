"""
Main entry point for the A2A client.
"""

import os
import uuid
import time
from dotenv import load_dotenv

from .a2a_client import A2AClient

# Load environment variables
load_dotenv()


def print_task_result(task):
    """Print task result."""
    print(f"\nTask ID: {task['id']}")
    print(f"Status: {task['status']['state']}")
    
    if task['status'].get('message'):
        print(f"Message: {task['status']['message']['parts'][0]['text']}")
    
    if task.get('artifacts'):
        print(f"Result: {task['artifacts'][0]['parts'][0]['text']}")
    
    if task.get('artifact'):
        print(f"Result: {task['artifact']['parts'][0]['text']}")
    
    print(f"Timestamp: {task['status']['timestamp']}")
    print("-" * 50)


def handle_stream_event(event):
    """Handle stream event."""
    if event.get('status'):
        if event['status']['state'] == 'working':
            if event['status'].get('message'):
                print(f"Working: {event['status']['message']['parts'][0]['text']}")
        else:
            print(f"Status: {event['status']['state']}")
    
    if event.get('artifact'):
        print(f"Result: {event['artifact']['parts'][0]['text']}")
    
    if event.get('final'):
        print("Task completed.")


def run_client():
    """Run the A2A client."""
    # Create client
    client = A2AClient(f"http://{os.getenv('SERVER_HOST', 'localhost')}:{os.getenv('SERVER_PORT', '10000')}")
    
    # Get agent card
    print("Getting agent card...")
    agent_card = client.get_agent_card()
    print(f"Agent: {agent_card['name']} (v{agent_card['version']})")
    print(f"Description: {agent_card['description']}")
    print(f"Skills: {', '.join([skill['name'] for skill in agent_card['skills']])}")
    print("-" * 50)
    
    # Interactive session
    session_id = str(uuid.uuid4())
    print(f"Starting interactive session (Session ID: {session_id})")
    print("Type 'exit' to quit, 'stream' to toggle streaming mode.")
    
    streaming_mode = False
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            break
        
        if user_input.lower() == 'stream':
            streaming_mode = not streaming_mode
            print(f"Streaming mode: {'ON' if streaming_mode else 'OFF'}")
            continue
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        try:
            if streaming_mode:
                print("\nAgent (streaming):")
                client.stream_task(task_id, session_id, user_input, handle_stream_event)
            else:
                print("\nAgent:")
                task = client.send_task(task_id, session_id, user_input)
                print_task_result(task)
                
                # If input required, wait for user input
                while task['status']['state'] == 'input-required':
                    follow_up = input("You: ")
                    task = client.send_task(task_id, session_id, follow_up)
                    print_task_result(task)
        
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    run_client()
