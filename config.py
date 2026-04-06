import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get provider configuration
PROVIDER = os.getenv("PROVIDER", "openai").lower()

# Common configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# Initialize client based on provider
client = None
model = None

if PROVIDER == "openai":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    model = OPENAI_MODEL

    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, timeout=TIMEOUT)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            client = None

elif PROVIDER == "anthropic":
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    model = ANTHROPIC_MODEL

    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"Error initializing Anthropic client: {e}")
            client = None


def is_configured():
    """Check if AI provider is properly configured."""
    return client is not None


def get_provider():
    """Get the current provider name."""
    return PROVIDER


def get_model():
    """Get the configured model name."""
    return model
