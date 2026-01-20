# Backend Foundation – FinTech-Oriented API

This project is a backend system designed to demonstrate
**financial-system engineering principles with a focus on correctness, safety, and domain integrity**.

It is built incrementally to mirror how real-world FinTech backends evolve.

---

## Key Concepts Implemented

- REST API design using FastAPI
- Persistent state with SQLite
- Transaction audit logging
- Idempotent operations for retry safety
- API key authentication
- Role-based authorization
- Clean architecture (service & repository layers)
- Consistent, machine-readable error contracts

---

## Domain & Correctness (Week 3)

Beyond API-level safety, the system encodes correctness directly into the domain:

- Explicit account states (`ACTIVE`, `FROZEN`, `CLOSED`)
- State-based behavior enforcement at the service layer
- Controlled state transitions via a domain state machine
- Terminal states (closed accounts cannot be reopened)
- Atomic deposit operations using database transactions
- Rollback on failure to prevent partial financial state

These guarantees ensure that invalid financial states are **structurally impossible**, even under failure.

---

## What This Project Is

- A learning-focused backend system
- Designed to model real FinTech and banking concerns
- Built with domain correctness as a first-class goal
- Intended to demonstrate backend engineering judgment, not just features

---

## What This Project Is Not

- A full banking core
- A production deployment
- A frontend application

---

## Project Structure

- `app.py` — HTTP / API layer
- `services/` — domain and business logic
- `repositories/` — data access and persistence
- `models/` — request schemas, errors, and domain states
- `database.py` — database setup and transaction control

---

## Safety Invariants

The system enforces the following invariants:

- Authorization is enforced before any state mutation
- Account state determines allowed behavior
- Closed accounts are terminal and cannot transition
- Deposits are idempotent to protect against retries
- Deposits are atomic (all-or-nothing)
- Withdrawals require elevated permissions
- All successful mutations are audit-logged
- Errors follow a consistent, machine-readable contract

These invariants are enforced by design, not by caller discipline.

---

## Notes

- The database file is intentionally excluded from version control
- Python cache files are ignored
- The focus is on **system design, safety, and correctness**, not deployment
