# Earth Defenders Assistant AI API

Single Python API endpoint for pulling different AI plugins.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Installation
Run using Turborepo from root:

```bash
bun dev:ai

```

## Setup
1. Duplicate the `.env.example` file and rename it to `.env` 


2. In the `.env` file configure the `API_KEY` entry. The key is used for authenticating our API. <br>
   A sample API key can be generated using Python REPL:

```python
import uuid
print(str(uuid.uuid4()))
```

## Run It

1. Start your  app with:

```bash
uv run
```

2. Go to [http://localhost:8000/docs](http://localhost:8000/docs).
3. Click `Authorize` and enter the API key as created in the Setup step.

## Linting

This skeleton code uses isort, mypy, flake, black, bandit for linting, formatting and static analysis.

Run linting with:

```bash
./scripts/linting.sh
```

## Run Tests

Run your tests with:

```bash
./scripts/test.sh
```

This runs tests and coverage for Python 3.11 and Flake8, Autopep8, Bandit.