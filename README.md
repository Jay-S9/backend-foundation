# Backend Foundation – FinTech-Oriented API

This project is a backend system designed to demonstrate
core financial-system engineering principles.

## Key Concepts Implemented

- REST API design using FastAPI
- Persistent state with SQLite
- Transaction audit logging
- Idempotent operations for retry safety
- API key authentication
- Role-based authorization
- Clean architecture (service & repository layers)
- Consistent error contracts

## What This Project Is

- A learning-focused backend system
- Designed to model real FinTech concerns
- Built incrementally with correctness in mind

## What This Project Is Not

- A full banking system
- A production deployment
- A frontend application

## Structure

- `app.py` — HTTP layer
- `services/` — business logic
- `repositories/` — data access
- `models/` — request & error contracts
- `database.py` — persistence setup

## Notes

The database file is intentionally excluded from version control.
The focus is on system design, safety, and clarity.
