# Nexus Roadmap

This roadmap describes how Nexus evolves from a simple CLI orchestrator
into a professional agent orchestration runtime.

The roadmap follows one principle:

Each stage exists because the previous stage exposes a limitation.

We only add complexity when a real need appears.

---

# Stage 0 — Concept and Foundations

Before writing significant code, the conceptual model of Nexus must be clear.

Key ideas:

- Nexus is a coordination hub for agents
- Agents operate inside a workspace
- Events act as signals in the system
- Runs represent the execution of agents

Conceptually:

agents → nodes  
events → signals  
runs → actions  
nexus → coordination network  

At this stage we define:

- architecture
- design principles
- development rules
- long-term vision

Goal:

Create a clear mental model before building.

---

# Stage 1 — Minimal CLI Orchestrator

The first version of Nexus is intentionally simple.

It exists to prove the core concept.

Capabilities:

- detect the workspace
- load agent definitions
- detect events (initially simple ones)
- trigger agent runs
- log execution

This version will likely include:

- a basic CLI
- simple event detection
- synchronous agent execution
- minimal run logging

Why this stage exists:

We need to validate the **core orchestration loop**:

event → trigger → run agent → log result

Goal:

Build the smallest system that demonstrates agent coordination.

---

# Stage 2 — Structured Runtime

Once agents can run, the next problem appears:

We need to understand what the system is doing.

This leads to better runtime structure.

Capabilities added:

- structured event objects
- structured run tracking
- better logging
- clearer runtime lifecycle
- clearer agent registry

Possible improvements:

- persistent run logs
- clearer run identifiers
- improved CLI commands

Why this stage exists:

As the system grows, we need to answer:

- what ran
- why it ran
- what failed

Goal:

Make the runtime observable and explainable.

---

# Stage 3 — State and Control

Once the runtime becomes active, control becomes important.

New needs appear:

- pause agents
- disable triggers
- inspect current state
- manage execution safely

Capabilities added:

- runtime state tracking
- agent enable/disable
- pause/resume functionality
- better command interface

Possible additions:

- state storage
- lock handling
- clearer execution context

Why this stage exists:

An orchestrator must not only run agents.
It must allow humans to **control the system safely**.

Goal:

Introduce operational control.

---

# Stage 4 — Worker Model

As agents grow more complex, synchronous execution becomes limiting.

New problem:

Agent runs may become slow or numerous.

Capabilities added:

- task queue
- worker execution model
- asynchronous runs
- run lifecycle management

Possible additions:

- worker heartbeats
- run scheduling
- better error handling

Why this stage exists:

We separate:

control plane → event detection and scheduling  
execution plane → workers performing tasks

Goal:

Create a scalable runtime architecture.

---

# Stage 5 — API Layer

Once the runtime becomes powerful, external control becomes necessary.

The CLI alone becomes insufficient.

Capabilities added:

- API endpoints
- runtime inspection
- agent control through API
- run history access
- inspection of configured tool providers (including MCP-backed ones) and
  their usage across runs

This API will eventually power:

- dashboards
- automation
- integrations

Why this stage exists:

A professional orchestrator needs a **control plane interface**.

Goal:

Expose Nexus as a programmable system.

---

# Stage 6 — Dashboard

Once APIs exist, a visual interface becomes valuable.

Capabilities added:

- agent status view
- run history
- event inspection
- runtime control
- prompt editing
- visibility into available tools and providers per workspace and agent

The first dashboard may be simple.

Possible technologies:

- Streamlit (early)
- modern JS framework (later)

Why this stage exists:

Humans need visibility into orchestration systems.

Goal:

Make Nexus operable at a glance.

---

# Stage 7 — Hierarchical Agent Networks

As Nexus matures, larger repositories will require deeper orchestration.

New need:

Agents that operate in subdirectories or project regions.

Capabilities added:

- subdirectory-scoped agents
- local agent clusters
- hierarchical triggers
- workspace segmentation
- subdirectory-local tool providers (for example, MCP servers attached to
  specific services or packages)

Conceptually this resembles:

mycelial networks spreading through a forest.

Agents can exist across the project tree and coordinate through Nexus.

Goal:

Enable orchestration across complex repositories.

---

# Stage 8 — Advanced Orchestration

Once the system is stable, more advanced capabilities can emerge.

Possible directions:

- agent messaging
- approval workflows
- permission systems
- provider adapters
- advanced scheduling
- dependency graphs
- deeper integration with MCP and similar provider standards so that
  workspace tools can be discovered and governed consistently

These features support more sophisticated agent ecosystems.

Goal:

Make Nexus a powerful orchestration substrate.

---

# Long-Term Vision

Nexus becomes a professional coordination runtime for agent ecosystems.

A mature Nexus system may support:

- multiple agent types
- rich event systems
- hierarchical workspaces
- dashboards and APIs
- observable orchestration
- scalable execution models

Large projects may eventually resemble **living ecosystems of agents**
connected through Nexus.

---

# Development Philosophy

Even though Nexus aims to become a serious system, development should remain disciplined.

We follow these rules:

- build incrementally
- solve real problems before adding complexity
- keep architecture understandable
- preserve modular boundaries
- avoid premature abstractions

The ambition is high.

The implementation remains deliberate.

Each stage prepares the next.