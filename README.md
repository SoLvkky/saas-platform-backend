# SaaS Platform Backend

## Tech Stack

- FastAPI (async)
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Redis
- Docker

## Implemented

- Dockerized environment
- Async database setup
- Alembic migrations
- User registration with layered architecture
- JWT authentication (access token)
- Argon2 password hashing
- Protected endpoints

## Architecture

API → Service → Repository → Database

## Run locally

docker compose up --build
