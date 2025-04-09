"""
Main entry point for the A2A LangGraph Demo.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Sentry for error monitoring
from src.utils.sentry import initialize_sentry

# Initialize Sentry
sentry_initialized = initialize_sentry()
if sentry_initialized:
    print("Sentry initialized for error monitoring")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="A2A LangGraph Demo")
    parser.add_argument("--mode", choices=["server", "client"], default="server", help="Run mode (server or client)")
    args = parser.parse_args()

    if args.mode == "server":
        # Run server
        from src.server.main import app
        import uvicorn

        host = os.getenv("SERVER_HOST", "localhost")
        port = int(os.getenv("SERVER_PORT", "10000"))

        print(f"Starting A2A server at http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)

    elif args.mode == "client":
        # Run client
        from src.client.main import run_client

        run_client()


if __name__ == "__main__":
    main()
