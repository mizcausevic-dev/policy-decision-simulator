# Architecture

## Purpose

`policy-decision-simulator` is a compact Scala service for converting scenario assumptions into an operational decision. It sits between strategy framing and release execution.

## Inputs

- dependency breach count
- freeze-window state
- rollback confidence
- customer exposure
- risk band

## Outputs

- `approve`
- `watch`
- `hold`

Each output is paired with a recommended operator action.

## Structure

- `PolicyDecisionSimulator.scala` handles HTTP entry and bind-failure messaging.
- `PolicyDecisionEngine.scala` contains the scoring model.
- `SampleScenarioData.scala` provides seeded example lanes.
- `tests/PolicyDecisionSimulatorTest.scala` verifies summary and critical hold logic.

## Design Notes

- Scala CLI keeps the repo one-shot and avoids SBT setup drag.
- The engine is simple enough to read quickly, but concrete enough to feel like a real decision surface.
- The HTTP layer uses the JDK server to keep the dependency surface small and stable.

## Extension Paths

- add sensitivity weighting by product or market
- track scenario history and prior outcomes
- export scenario deltas for executive briefing systems
- plug into release readiness or workflow orchestration repos already in the portfolio

