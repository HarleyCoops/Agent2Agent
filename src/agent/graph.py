"""
LangGraph implementation of the agent.
"""

import os
from typing import Dict, List, Tuple, Optional, Any, Union, Annotated
from dotenv import load_dotenv
import json

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain.tools import tool
from langchain_core.messages import BaseMessage

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from .state import AgentState
from .tools import convert_currency, get_weather

# Load environment variables
load_dotenv()

# Initialize LLM
if os.getenv("OPENAI_API_KEY"):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
elif os.getenv("GOOGLE_API_KEY"):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
else:
    raise ValueError("No API key found. Please set OPENAI_API_KEY or GOOGLE_API_KEY in .env file.")


# Define tools
@tool
def currency_conversion(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another."""
    return convert_currency(amount, from_currency, to_currency)


@tool
def weather_information(location: str, date: Optional[str] = None) -> str:
    """Get weather information for a location."""
    return get_weather(location, date)


# Create tool executor
tools = [currency_conversion, weather_information]
tool_executor = ToolExecutor(tools)


# Define graph nodes
def parse_input(state: AgentState) -> AgentState:
    """Parse the user input and extract parameters."""
    # Get the last user message
    user_message = state.get_last_user_message()
    if not user_message:
        state.set_error("No user message found")
        return state
    
    # Update task state
    state.task_state = "working"
    state.add_intermediate_response("Analyzing your request...")
    
    # Create a prompt to extract parameters
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant that extracts parameters from user queries.
        Extract the following parameters if present:
        - task_type: The type of task (currency_conversion or weather_information)
        - amount: The amount to convert (for currency conversion)
        - from_currency: The source currency (for currency conversion)
        - to_currency: The target currency (for currency conversion)
        - location: The location (for weather information)
        - date: The date (for weather information)
        
        Return the parameters as a JSON object. If a parameter is not present, do not include it.
        """),
        ("user", "{input}")
    ])
    
    # Extract parameters
    chain = prompt | llm
    response = chain.invoke({"input": user_message})
    
    try:
        # Try to parse the response as JSON
        parameters = json.loads(response.content)
        state.parameters.update(parameters)
    except (json.JSONDecodeError, AttributeError):
        # If parsing fails, use a more direct approach
        state.add_intermediate_response("Analyzing your request further...")
        
        # Create a more structured prompt
        structured_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract parameters from the user query and return them in this exact JSON format:
            {
                "task_type": "currency_conversion OR weather_information",
                "amount": number (for currency conversion),
                "from_currency": "currency code" (for currency conversion),
                "to_currency": "currency code" (for currency conversion),
                "location": "city name" (for weather information),
                "date": "YYYY-MM-DD" (for weather information, optional)
            }
            
            Only include parameters that are present in the query. Return valid JSON.
            """),
            ("user", "{input}")
        ])
        
        chain = structured_prompt | llm
        response = chain.invoke({"input": user_message})
        
        try:
            parameters = json.loads(response.content)
            state.parameters.update(parameters)
        except (json.JSONDecodeError, AttributeError):
            state.set_error("Failed to parse parameters from user input")
            return state
    
    return state


def check_parameters(state: AgentState) -> str:
    """Check if all required parameters are present."""
    task_type = state.parameters.get("task_type")
    
    if not task_type:
        return "unknown_task"
    
    if task_type == "currency_conversion":
        required_params = ["amount", "from_currency", "to_currency"]
        missing_params = [p for p in required_params if p not in state.parameters]
        
        if missing_params:
            return "missing_parameters"
        else:
            return "complete_parameters"
    
    elif task_type == "weather_information":
        if "location" not in state.parameters:
            return "missing_parameters"
        else:
            return "complete_parameters"
    
    return "unknown_task"


def handle_unknown_task(state: AgentState) -> AgentState:
    """Handle unknown task types."""
    # Create a prompt to determine the task type
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant that helps users with currency conversion and weather information.
        Based on the user's message, determine if they want:
        1. Currency conversion (task_type: currency_conversion)
        2. Weather information (task_type: weather_information)
        3. Something else (task_type: unknown)
        
        Return your determination as a JSON object with a task_type field.
        """),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Get conversation history
    messages = [HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content) 
                for msg in state.messages]
    
    # Determine task type
    chain = prompt | llm
    response = chain.invoke({"messages": messages})
    
    try:
        result = json.loads(response.content)
        state.parameters["task_type"] = result.get("task_type", "unknown")
    except (json.JSONDecodeError, AttributeError):
        state.parameters["task_type"] = "unknown"
    
    if state.parameters["task_type"] == "unknown":
        # Ask the user what they want to do
        response = "I can help with currency conversion or weather information. What would you like to know?"
        state.add_assistant_message(response)
        state.task_state = "input-required"
    
    return state


def request_missing_parameters(state: AgentState) -> AgentState:
    """Request missing parameters from the user."""
    task_type = state.parameters.get("task_type")
    
    if task_type == "currency_conversion":
        required_params = ["amount", "from_currency", "to_currency"]
        missing_params = [p for p in required_params if p not in state.parameters]
        
        # Create a prompt to ask for missing parameters
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that helps users with currency conversion.
            The user wants to convert currency, but some parameters are missing.
            Ask for the missing parameters in a conversational way.
            
            Missing parameters: {missing_params}
            Current parameters: {current_params}
            """),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Get conversation history
        messages = [HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content) 
                    for msg in state.messages]
        
        # Generate response
        chain = prompt | llm
        response = chain.invoke({
            "messages": messages,
            "missing_params": missing_params,
            "current_params": {k: v for k, v in state.parameters.items() if k in required_params}
        })
        
        # Update state
        state.add_assistant_message(response.content)
        state.task_state = "input-required"
    
    elif task_type == "weather_information":
        if "location" not in state.parameters:
            response = "Which location would you like to get weather information for?"
            state.add_assistant_message(response)
            state.task_state = "input-required"
    
    return state


def execute_task(state: AgentState) -> AgentState:
    """Execute the task with the given parameters."""
    task_type = state.parameters.get("task_type")
    
    if task_type == "currency_conversion":
        try:
            amount = float(state.parameters.get("amount"))
            from_currency = state.parameters.get("from_currency")
            to_currency = state.parameters.get("to_currency")
            
            # Execute the tool
            result = tool_executor.invoke({
                "tool_name": "currency_conversion",
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            })
            
            # Update state
            state.add_intermediate_response(f"Converting {amount} {from_currency} to {to_currency}...")
            state.add_assistant_message(result)
            state.set_final_response(result)
            state.task_state = "completed"
        
        except Exception as e:
            state.set_error(f"Error executing currency conversion: {str(e)}")
    
    elif task_type == "weather_information":
        try:
            location = state.parameters.get("location")
            date = state.parameters.get("date")
            
            # Execute the tool
            result = tool_executor.invoke({
                "tool_name": "weather_information",
                "location": location,
                "date": date
            })
            
            # Update state
            state.add_intermediate_response(f"Getting weather information for {location}...")
            state.add_assistant_message(result)
            state.set_final_response(result)
            state.task_state = "completed"
        
        except Exception as e:
            state.set_error(f"Error executing weather information: {str(e)}")
    
    return state


# Create the graph
def create_agent_graph() -> StateGraph:
    """Create the LangGraph agent graph."""
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("parse_input", parse_input)
    graph.add_node("handle_unknown_task", handle_unknown_task)
    graph.add_node("request_missing_parameters", request_missing_parameters)
    graph.add_node("execute_task", execute_task)
    
    # Add edges
    graph.add_edge("parse_input", check_parameters)
    graph.add_conditional_edges(
        check_parameters,
        {
            "unknown_task": "handle_unknown_task",
            "missing_parameters": "request_missing_parameters",
            "complete_parameters": "execute_task"
        }
    )
    
    # Set the entry point
    graph.set_entry_point("parse_input")
    
    # Add end states
    graph.add_edge("execute_task", END)
    graph.add_edge("handle_unknown_task", END)
    graph.add_edge("request_missing_parameters", END)
    
    return graph


# Compile the graph
agent_graph = create_agent_graph().compile()
