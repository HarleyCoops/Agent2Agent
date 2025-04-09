"""
Sentry integration for error monitoring.
"""

import os
import sentry_sdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def initialize_sentry():
    """Initialize Sentry SDK for error monitoring."""
    # Get Sentry configuration from environment variables
    dsn = os.getenv("SENTRY_DSN")
    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0"))
    send_default_pii = os.getenv("SENTRY_SEND_DEFAULT_PII", "true").lower() == "true"
    
    # Initialize Sentry SDK
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            # Add request headers and IP for users
            send_default_pii=send_default_pii,
            # Set traces_sample_rate for tracing
            traces_sample_rate=traces_sample_rate,
            # Set profiles_sample_rate for profiling
            profiles_sample_rate=profiles_sample_rate,
            # Add release information
            release=os.getenv("AGENT_VERSION", "1.0.0"),
            # Add environment information
            environment=os.getenv("ENVIRONMENT", "development"),
        )
        
        # Set user information if available
        if send_default_pii:
            sentry_sdk.set_user({"id": "system", "username": "system"})
        
        return True
    
    return False


def capture_exception(exception, **kwargs):
    """Capture an exception and send it to Sentry."""
    return sentry_sdk.capture_exception(exception, **kwargs)


def capture_message(message, level="info", **kwargs):
    """Capture a message and send it to Sentry."""
    return sentry_sdk.capture_message(message, level=level, **kwargs)


def set_user(user_info):
    """Set user information for Sentry events."""
    return sentry_sdk.set_user(user_info)


def set_tag(key, value):
    """Set a tag for Sentry events."""
    return sentry_sdk.set_tag(key, value)


def set_context(name, context):
    """Set context for Sentry events."""
    return sentry_sdk.set_context(name, context)
