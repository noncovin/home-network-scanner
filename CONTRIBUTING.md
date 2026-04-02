# Contributing

## Getting Started

1. Fork the repository.
2. Create a feature branch.
3. Install dependencies.
4. Run tests before opening a pull request.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Guidelines

- Keep scanner logic separate from route handlers.
- Add tests for new features when practical.
- Prefer small, focused pull requests.
- Document any new configuration or environment variables.

## Pull Requests

Please include:

- A clear summary of the change
- Testing notes
- Any known limitations
