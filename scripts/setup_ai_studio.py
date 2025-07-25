#!/usr/bin/env python3
"""Setup script to prepare an AI studio environment.

This script installs dependencies from ``requirements.txt`` and optionally
creates a ``.env`` file with API keys for LLM services such as OpenAI or
Anthropic. It unifies packages needed by AutoGPT, LibreChat, and the
Aletheometer.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / 'requirements.txt'
ENV_FILE = ROOT / '.env'


def install_requirements() -> None:
    """Install required Python packages using pip."""
    if REQ_FILE.exists():
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(REQ_FILE)])
    else:
        print(f"Requirements file not found: {REQ_FILE}")


def configure_api_keys() -> None:
    """Prompt the user for API keys and store them in .env."""
    print('Configure API keys for LLM services (leave blank to skip).')
    keys = {}
    try:
        keys['OPENAI_API_KEY'] = input('OpenAI API key: ').strip()
        keys['ANTHROPIC_API_KEY'] = input('Anthropic API key: ').strip()
        keys['HUGGINGFACE_API_KEY'] = input('Hugging Face API key: ').strip()
    except KeyboardInterrupt:
        print('\nSetup cancelled by user.')
        sys.exit(1)

    with ENV_FILE.open('w') as f:
        for k, v in keys.items():
            if v:
                f.write(f"{k}={v}\n")
    print(f'API keys written to {ENV_FILE}')


def main() -> None:
    install_requirements()
    configure_api_keys()
    print('AI studio setup complete.')


if __name__ == '__main__':
    main()
