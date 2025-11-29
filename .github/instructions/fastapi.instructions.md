---
applyTo: 'fastapi/*'
---

# FastAPI Instruction

This document describes the design principles and development guidelines of this project.

---

## Core Principles
- **Test-Driven Development (TDD)** will be conducted.
- **Dependency directions** are restricted as follows:

```mermaid
flowchart TD
    UI[UI Layer] --> APP[Application Layer]
    INFRA[Infrastructure Layer] --> APP
    APP --> DOMAIN[Domain Layer]
````

---

## Layer Structure and Responsibilities

### Domain Layer

* **Core**: LP model
* **Constraint Definitions**
* **Service Classes**: responsible for mathematical logic
* **Helper Logic**
* **Value Objects (VO)**
* Must not depend on external systems or technical details.

### Application Layer

* **Use Cases**: orchestration of processes
* **Factories**: responsible for DTO ⇔ VO conversion
* **DTOs**: data transfer objects for communication with UI and external interfaces
* **Port Interfaces**: abstractions for infrastructure implementations

### Infrastructure Layer

* Classes for connecting to optimization solvers installed on VM
* Implements the port interfaces defined in the application layer
* Handles technical dependencies

### UI Layer

* Invokes use cases in the application layer
* Communicates with end-users through FastAPI

---

## Directory Structure

```
src/
├── application/          # Use cases, factories, DTOs
├── common/              # Shared constants and utilities
├── domain/              # Business logic and domain models
│   ├── constraints/     # Constraint definitions for timetable optimization
│   ├── models/          # Domain models (LP models)
│   ├── services/        # Domain services
│   └── vo/              # Value objects (AnnualDataVo)
├── infrastructure/      # External dependencies
└── interface/           # API layer (routers, schemas, presenters)
```

---

## DTO ↔ VO Mapping Rules

* **To be defined**

---

## Testing Strategy

* **To be defined**

---

## Implementation Rules

* **To be defined**

### Logging Strategy

* **To be defined**

### Dependency Injection Strategy

* **To be defined**

---

## Naming Conventions

* Factory: `XxxFactory`
* Use Case: `XxxUseCase`
* VO: domain concepts directly as names
* DTO: `XxxDto`
* Constraint Definition: `ConstraintDefinitionDto` / `ConstraintDefinitionVo`
