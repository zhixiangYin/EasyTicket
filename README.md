# EasyTicket

EasyTicket is a Python learning project for building a ticket search agent step by step.

The long-term goal is to build an AI-assisted ticket comparison system that can:
- accept one search request from the user
- query multiple ticket platforms
- normalize and compare results
- explain which option is cheaper, faster, or more flexible
- later extend to local-authorized member-only platform lookups

The current version is intentionally small. It focuses on the core backend flow before adding web UI, real platform connectors, or a real external LLM integration.

## Current Scope

Implemented in the current milestone:
- a shared normalized ticket result model
- a connector abstraction for platforms
- two mock platform connectors
- a search service that aggregates all connector results
- a ranking service that filters and sorts results
- a rule-based parser that converts natural-language requests into structured input
- a model-parser interface with validation and a temporary mock model client
- a CLI entrypoint for running the flow end to end

This first step is important because it defines the tool layer that a future AI agent will call. The model should interpret user intent, but deterministic Python code should handle querying, filtering, ranking, and output shaping.

The project now has two parser modes behind the same interface:
- `rule`: deterministic extraction with Python rules
- `llm`: a model-parser workflow that validates structured output before execution

The user-facing product now has a single input method: free-form natural language. Internally, the system tries the OpenAI parser first, then falls back to the rule-based parser if the LLM path fails.

## Project Structure

```text
app/
  agent/
    base.py
    clients.py
    llm_parser.py
    parser.py
    validators.py
  cli/
    main.py
  connectors/
    base.py
    mock_a.py
    mock_b.py
  schemas/
    result.py
    search.py
  services/
    ranking_service.py
    search_service.py
pyproject.toml
README.md
```

Local config files:
- `.env.example`: checked-in template for local API configuration
- `.env`: your real local secrets file, ignored by git

## Architecture Overview

Current data flow:

1. CLI collects one natural-language user request
2. OpenAI parses the request into a `SearchInput`
3. `SearchService` calls each connector
4. connectors return normalized `TicketResult` objects
5. `RankingService` applies filters and sorting
6. CLI prints the final ranked results

This separation keeps responsibilities clear:
- `schemas`: define what data looks like
- `agent`: converts user intent into structured inputs
- `agent/clients.py`: selects the mock or real LLM client based on environment configuration
- `agent/validators.py`: checks model output before it reaches business logic
- `connectors`: define how each platform provides data
- `services`: contain business logic such as aggregation and ranking
- `cli`: provides a simple user-facing interface for testing the system

## Run the Demo

```bash
python3 -m app.cli.main ask \
  "find me a direct ticket from New York to Boston tomorrow under 80 dollars for 2 passengers"
```

Another example:

```bash
python3 -m app.cli.main ask \
  "I need a business class option from New York to Boston next Friday for 1 passenger"
```

Fallback-disabled mode:

```bash
python3 -m app.cli.main ask \
  --no-fallback-to-rule \
  "find me a direct ticket from New York to Boston tomorrow under 80 dollars for 2 passengers"
```

## OpenAI API Integration

The repository now includes a real OpenAI client implementation in [app/agent/clients.py](/Users/inshishou/Documents/JobApplication/Projects/EasyTicket/app/agent/clients.py).

Default behavior:
- `EASYTICKET_LLM_CLIENT=mock` uses the local mock client
- `EASYTICKET_LLM_CLIENT=openai` enables the real OpenAI client
- `EASYTICKET_LLM_CLIENT=real` is kept as an alias for the OpenAI client
- the CLI always tries the OpenAI parser first and falls back to the rule parser unless `--no-fallback-to-rule` is passed

Environment variables for OpenAI mode:

```bash
export EASYTICKET_LLM_CLIENT=openai
export OPENAI_API_KEY="your-api-key"
export EASYTICKET_OPENAI_MODEL="gpt-5.4-mini"
```

You can now put the same values in a local `.env` file instead of exporting them manually every time.

Example `.env`:

```bash
EASYTICKET_LLM_CLIENT=openai
OPENAI_API_KEY="your-api-key"
EASYTICKET_OPENAI_MODEL="gpt-5.4-mini"
```

The CLI loads `.env` automatically at startup through [app/config.py](/Users/inshishou/Documents/JobApplication/Projects/EasyTicket/app/config.py). Exported shell variables still take priority over `.env` values.

Optional override:

```bash
export EASYTICKET_OPENAI_BASE_URL="https://api.openai.com/v1/chat/completions"
```

The OpenAI client uses Chat Completions with `response_format.type=json_schema` so the model is asked to return a strict JSON object matching the ticket search schema.

## What You Can Learn From This Stage

This stage is meant to help understand the foundations of an agent system:
- how to define clean input and output types
- how to separate platform-specific code from core business logic
- how to design a service layer the agent can call later
- how to introduce an agent layer without giving up deterministic execution
- how to simplify the user interface to one natural-language entry point
- how to constrain model output without constraining user input
- how to wire a real model API into the parser layer while keeping deterministic validation
- how to keep the system deterministic before adding LLM behavior

## Planned Next Steps

Near-term steps:
- generate recommendation summaries for ranked results
- add confidence or validation feedback for parsed queries
- add request tracing and richer retry handling for the OpenAI client
- replace mock connectors with real platform integrations

Later steps:
- add a web API with FastAPI
- add async task execution for slow connector calls
- add local-authorized search for member-only platforms

## Design Principle

The project will follow one core rule:

`AI is responsible for understanding and planning. Python code is responsible for execution.`

That keeps the system easier to debug, test, and extend.
