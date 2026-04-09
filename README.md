# EasyTicket

EasyTicket is a Python learning project for building a ticket search agent step by step.

The long-term goal is to build an AI-assisted ticket comparison system that can:
- accept one search request from the user
- query multiple ticket platforms
- normalize and compare results
- explain which option is cheaper, faster, or more flexible
- later extend to local-authorized member-only platform lookups

The current version is intentionally small. It focuses on the core backend flow before adding web UI, real platform connectors, or LLM integration.

## Current Scope

Implemented in the current milestone:
- a shared search input model
- a shared normalized ticket result model
- a connector abstraction for platforms
- two mock platform connectors
- a search service that aggregates all connector results
- a ranking service that filters and sorts results
- a CLI entrypoint for running the flow end to end

This first step is important because it defines the tool layer that a future AI agent will call. The model should interpret user intent, but deterministic Python code should handle querying, filtering, ranking, and output shaping.

## Project Structure

```text
app/
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

## Architecture Overview

Current data flow:

1. CLI collects user input
2. input is converted into a `SearchInput`
3. `SearchService` calls each connector
4. connectors return normalized `TicketResult` objects
5. `RankingService` applies filters and sorting
6. CLI prints the final ranked results

This separation keeps responsibilities clear:
- `schemas`: define what data looks like
- `connectors`: define how each platform provides data
- `services`: contain business logic such as aggregation and ranking
- `cli`: provides a simple user-facing interface for testing the system

## Run the Demo

```bash
python3 -m app.cli.main search \
  --origin "New York" \
  --destination "Boston" \
  --travel-date "2026-04-12"
```

Example with filters:

```bash
python3 -m app.cli.main search \
  --origin "New York" \
  --destination "Boston" \
  --travel-date "2026-04-12" \
  --max-price 80 \
  --direct-only
```

## What You Can Learn From This Stage

This stage is meant to help understand the foundations of an agent system:
- how to define clean input and output types
- how to separate platform-specific code from core business logic
- how to design a service layer the agent can call later
- how to keep the system deterministic before adding LLM behavior

## Planned Next Steps

Near-term steps:
- add an `agent/` module
- parse natural language into structured search parameters
- generate recommendation summaries for ranked results
- replace mock connectors with real platform integrations

Later steps:
- add a web API with FastAPI
- add async task execution for slow connector calls
- add local-authorized search for member-only platforms

## Design Principle

The project will follow one core rule:

`AI is responsible for understanding and planning. Python code is responsible for execution.`

That keeps the system easier to debug, test, and extend.
