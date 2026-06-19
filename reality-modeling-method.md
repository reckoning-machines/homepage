# The Reality Modeling Method (Draft v0)

## Premise

Most software projects begin with workflows.

Users click buttons.
Data moves through screens.
APIs execute actions.

This is often backwards.

Workflows are projections of reality.

To build durable systems, reality must be modeled before workflows, screens, APIs, or databases.

The purpose of this method is to discover and formalize operational reality before implementation.

---

# Principle 1: Reality Exists Before Software

The software is not the system.

The software is a representation of the system.

Before discussing:

* screens
* APIs
* workflows
* jobs
* databases

ask:

> What exists even if the software disappears?

Examples:

Trading:

* Position
* Fill
* Reconciliation
* Trade Recommendation
* Execution

Research:

* Model
* Report
* Result
* Thesis

Accounting:

* Invoice
* Payment
* Liability
* Journal Entry

The first task is naming reality.

Not naming software.

---

# Principle 2: Enumerate Objects

List every object that exists.

Objects should be nouns.

Avoid actions.

Bad:

* Upload Position File
* Generate Trades
* Download Orders

Good:

* Position Snapshot
* Current Book
* Fill Import
* Trade Recommendation
* Execution
* Artifact

The goal is an inventory of reality.

---

# Principle 3: Authority

For every object ask:

> Why should this be trusted?

Every object must have a source of authority.

Examples:

Current Book

* Authority: Accepted Reconciliation

Trade Recommendation

* Authority: Approved Model

Report

* Authority: Accepted Workbook State

Authority must be singular whenever possible.

Multiple authorities create ambiguity.

Ambiguity eventually becomes operational failure.

---

# Principle 4: Ownership

For every object ask:

> Who creates it?

> Who may modify it?

> Who consumes it?

Ownership must be explicit.

Every significant production failure should first be examined as a possible ownership failure.

Common symptom:

Multiple systems believe they own the same object.

---

# Principle 5: Lineage

For every object ask:

> What chain of events produced this?

Lineage answers:

> Why does this exist?

Example:

Artifact
<- Execution Run
<- Sizing Run
<- Current Book
<- Accepted Reconciliation
<- Fill Import

Lineage should be reconstructable without human interpretation.

---

# Principle 6: Projection

Many objects are not reality.

They are projections of reality.

Examples:

* Dashboard
* CTA
* Status Indicator
* Report View
* Timeline View

Ask:

> Is this object authoritative?

or

> Is it a projection of an authoritative object?

Projection must never become authority.

A projection may be regenerated.

Authority must be preserved.

---

# Principle 7: Boundary Analysis

Reality changes when it crosses boundaries.

Every boundary must be identified.

Examples:

System
-> Human

System
-> Broker

System
-> Spreadsheet

System
-> AI

System
-> Vendor

System
-> File

For every boundary ask:

* What leaves?
* What returns?
* What authority survives?
* What lineage survives?
* What can be lost?

Most operational failures occur at boundaries.

---

# Principle 8: State

State is a summary of reality.

State is not reality itself.

State should be derived from authoritative objects and events.

Examples:

READY_TO_DOWNLOAD

READY_TO_UPLOAD

BLOCKED

COMPLETE

States should not invent reality.

They should summarize reality.

---

# Principle 9: Events

Reality changes through events.

List all events capable of changing authoritative state.

Examples:

Position Uploaded

Fills Uploaded

Reconciliation Accepted

Execution Completed

Events create transitions.

Not screens.

Not buttons.

---

# Principle 10: Workflow

Workflow is the final step.

Workflow should be derived from:

Reality
-> Authority
-> Ownership
-> Lineage
-> Boundaries
-> State
-> Events

Only then:

Workflow

A workflow is not reality.

A workflow is a human-facing projection of reality transitions.

---

# Diagnostic Rule

When a system fails, ask questions in this order:

1. What object is involved?
2. What is its authority?
3. Who owns it?
4. What is its lineage?
5. Did it cross a boundary?
6. Is the failure in reality or projection?
7. Did a state transition violate authority?

Do not begin with:

"What code is broken?"

Begin with:

"What reality contract failed?"

---

# Goal

The goal of the method is not software.

The goal is a single coherent model of reality.

When reality is coherent:

* workflows simplify
* UI simplifies
* testing simplifies
* debugging simplifies
* automation becomes possible

The software becomes an implementation detail of a well-defined world.
