"""
Setup script for the A2A LangGraph Demo.
"""

from setuptools import setup, find_packages

setup(
    name="a2a_langgraph_demo",
    version="1.0.0",
    description="A demonstration of implementing the Agent2Agent (A2A) protocol using LangGraph",
    author="Harley Cooper",
    author_email="christian.cooper.us@gmail.com",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-google-genai>=0.0.5",
        "langchain-core>=0.1.0",
        "langgraph>=0.0.20",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
        "openai>=1.3.0",
        "google-generativeai>=0.3.0",
        "requests>=2.31.0",
        "sse-starlette>=1.6.5",
        "python-multipart>=0.0.6",
        "sseclient-py>=1.7.2",
        "sentry-sdk>=1.40.0"
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "a2a-server=a2a_langgraph_demo.main:main",
        ],
    },
)
