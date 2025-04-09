"""
Main entry point for the A2A server.
"""

import os
import uvicorn
from dotenv import load_dotenv

from .a2a_server import A2AServer

# Load environment variables
load_dotenv()

# Create A2A server
server = A2AServer()
app = server.app

if __name__ == "__main__":
    # Get server configuration
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", "10000"))
    
    # Start server
    print(f"Starting A2A server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
