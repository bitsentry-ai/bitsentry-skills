#!/usr/bin/env python3
"""
Design Spec Scaffolding Generator
Generates a basic structure for a new design specification document
Supports multiple architectural patterns
"""

import argparse
from datetime import datetime
import os

def generate_paradigm_section(spec_type: str) -> str:
    """Generate architecture-specific paradigm section."""

    paradigms = {
        "standard": """## Paradigm

We adopt a **[Choose Appropriate Architecture]**:

- **Key Principle 1**: [Description]
- **Key Principle 2**: [Description]
- **Key Principle 3**: [Description]
- **Key Principle 4**: [Description]
""",
        "ddd": """## Paradigm

We adopt a **DDD-lite approach with Hexagonal Architecture** principles:

- **Domain Layer**: Rich domain models with business rules
- **Application Layer**: Use cases for orchestrating domain operations
- **Infrastructure Layer**: Database persistence and external service adapters
- **Separation of Concerns**: Business logic isolated from infrastructure
""",
        "clean": """## Paradigm

We adopt a **Clean Architecture with Repository Pattern**:

- **Domain Layer**: Entities and business rules
- **Application Layer**: Use cases for operations and workflow orchestration
- **Infrastructure Layer**: Database persistence and external APIs
- **Repository Pattern**: Abstract data access for flexibility and testability
- **Dependency Rule**: Dependencies point inward toward the domain
""",
        "microservices": """## Paradigm

We adopt a **Microservices Architecture with Service Mesh**:

- **API Gateway**: Unified entry point with authentication and rate limiting
- **Service Discovery**: Dynamic service registration and discovery
- **Message Queue**: Asynchronous communication between services
- **Data Isolation**: Each service owns its database
- **Circuit Breaker**: Fault tolerance and graceful degradation
""",
        "event-sourcing": """## Paradigm

We adopt an **Event Sourcing with CQRS Pattern**:

- **Event Store**: Immutable log of all domain events
- **Event Projection**: Materialized views for queries
- **Command Validation**: Business rules enforced before event persistence
- **Saga Pattern**: Complex multi-step transactions with compensation
- **Temporal Queries**: Point-in-time state reconstruction
""",
        "soa": """## Paradigm

We adopt a **Service-Oriented Architecture with Integration Layer**:

- **Service Layer**: RESTful APIs for business operations
- **Integration Layer**: ESB/Message broker for service communication
- **Data Pipeline**: Shared analytics infrastructure
- **Cache Layer**: Centralized caching for performance
- **Service Registry**: Central service discovery and management
""",
        "document": """## Paradigm

We adopt a **Document-Oriented Architecture with Search-First Design**:

- **Document Store**: Flexible schema for rich content
- **Search Engine**: Full-text search and faceted filtering
- **Content Pipeline**: Async processing for enrichment
- **API Layer**: GraphQL for flexible client queries
- **CDN Integration**: Edge caching for static content
""",
        "monolith": """## Paradigm

We adopt a **Modular Monolith with Clear Boundaries**:

- **Module Structure**: Logical separation within single deployment
- **Shared Database**: Single database with schema separation
- **Internal APIs**: Well-defined interfaces between modules
- **Transaction Management**: ACID guarantees within boundaries
- **Future Migration**: Clear path to microservices if needed
""",
        "timeseries": """## Paradigm

We adopt a **Time-Series Architecture with Stream Processing**:

- **Time-Series Database**: Optimized storage for temporal data
- **Stream Processing**: Real-time aggregations and windowing
- **Data Retention**: Automatic downsampling and archival
- **Query Optimization**: Time-range queries and aggregations
- **Visualization Layer**: Real-time dashboards and alerts
"""
    }

    return paradigms.get(spec_type, paradigms["standard"])

def generate_spec_scaffold(
    title: str,
    author: str,
    spec_type: str = "standard",
) -> str:
    """Generate a scaffold for a design specification."""

    date_str = datetime.now().strftime("%Y-%m-%d")

    # Base template
    template = f"""# {title}

## Review Table

| Version | Date | Name | Role | Description |
| --- | --- | --- | --- | --- |
| 1.0 | {date_str} | {author} | Author | Initial Draft |

## Approval Table

| Approved By | Approved At | Note |
| --- | --- | --- |
|  |  |  |

---

## Background

[Provide historical context and current state. What problem exists today?]

## Context

[Describe current system limitations, pain points, and user needs]

## Objective

Implement a comprehensive [system/service] that:

1. **[Primary Goal]** - [Description]
2. **[Secondary Goal]** - [Description]
3. **[Tertiary Goal]** - [Description]
4. **[Additional Goal]** - [Description]

{generate_paradigm_section(spec_type)}

---

## Database Design

### Database Schema Diagram

```mermaid
erDiagram
    table_name {{
        int id PK
        string field_name
        datetime created_at
        datetime updated_at
    }}

    related_table {{
        int id PK
        int table_id FK
        string status
    }}

    table_name ||--o{{ related_table : has_many
```

### SQL Schema

```sql
-- Main table
CREATE TABLE table_name (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  field_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_field_name (field_name)
);

-- Related table
CREATE TABLE related_table (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  table_id BIGINT NOT NULL,
  status VARCHAR(50) NOT NULL,

  FOREIGN KEY (table_id) REFERENCES table_name(id),
  INDEX idx_table_id (table_id)
);
```

---

## Activity Lifecycle

### State Machine

```mermaid
stateDiagram-v2
    [*] --> INITIATED: Create
    INITIATED --> PROCESSING: Start Processing
    PROCESSING --> COMPLETED: Success
    PROCESSING --> FAILED: Error
    FAILED --> PROCESSING: Retry
    COMPLETED --> [*]

    INITIATED : Entry created
    PROCESSING : Operation in progress
    COMPLETED : Successfully completed
    FAILED : Error occurred
```

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Client]
        Mobile[Mobile App]
        API_Client[API Client]
    end

    subgraph "Application Layer"
        Gateway[API Gateway]
        Service[Core Service]
        Worker[Background Workers]
    end

    subgraph "Data Layer"
        Cache[(Redis Cache)]
        DB[(Primary Database)]
        Queue[Message Queue]
    end

    subgraph "External Services"
        External1[External API 1]
        External2[External API 2]
    end

    Web --> Gateway
    Mobile --> Gateway
    API_Client --> Gateway

    Gateway --> Service
    Service --> Cache
    Service --> DB
    Service --> Queue
    Queue --> Worker
    Worker --> DB

    Service --> External1
    Worker --> External2
```

---

## Processing Sequences

### Main Flow Sequence

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Database
    participant External

    Client->>API: POST /endpoint
    API->>Service: Process Request
    Service->>Database: Validate Data
    Database-->>Service: Validation Result

    alt Valid Request
        Service->>External: Call External API
        External-->>Service: External Response
        Service->>Database: Store Result
        Database-->>Service: Stored
        Service-->>API: Success Response
        API-->>Client: 200 OK
    else Invalid Request
        Service-->>API: Validation Error
        API-->>Client: 400 Bad Request
    end
```

---

## API Endpoints

### POST /api/resource

Create a new resource.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Y | Resource name |
| type | string | Y | Resource type |
| metadata | object | N | Additional metadata |

**Response (201 Created)**

```json
{{
  "id": "resource_123",
  "name": "Example Resource",
  "type": "example",
  "status": "CREATED",
  "created_at": "2024-01-01T00:00:00Z"
}}
```

**Response (400 Bad Request)**

```json
{{
  "error": "VALIDATION_ERROR",
  "message": "Invalid resource type",
  "details": {{
    "field": "type",
    "reason": "Must be one of: example, test, production"
  }}
}}
```

---

### GET /api/resource/{{id}}

Retrieve a specific resource.

**Response (200 OK)**

```json
{{
  "id": "resource_123",
  "name": "Example Resource",
  "type": "example",
  "status": "ACTIVE",
  "metadata": {{}},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}}
```

**Response (404 Not Found)**

```json
{{
  "error": "NOT_FOUND",
  "message": "Resource not found"
}}
```

---

## Security Considerations

### Authentication & Authorization

- [Authentication method: JWT, OAuth2, API Keys]
- [Authorization model: RBAC, ABAC]
- [Token management and refresh strategy]

### Data Protection

- [Encryption at rest and in transit]
- [PII handling and compliance]
- [Audit logging requirements]

---

## Testing Strategy

### Unit Tests

- [Core business logic coverage]
- [Edge cases and error handling]
- [Mock external dependencies]

### Integration Tests

- [API endpoint testing]
- [Database operations]
- [External service integration]

### Performance Tests

- [Load testing targets]
- [Response time requirements]
- [Concurrent user limits]

---

## Monitoring & Alerting

### Key Metrics

| Metric | Target | Alert Threshold |
| --- | --- | --- |
| API Response Time | < 200ms p50 | > 500ms p50 |
| Error Rate | < 0.1% | > 1% |
| Database Query Time | < 50ms p50 | > 100ms p50 |
| Queue Processing Time | < 1s | > 5s |

### Logging Strategy

- [Structured logging format]
- [Log levels and verbosity]
- [Log retention policy]
- [Sensitive data masking]

---

## Rollback Plan

### Deployment Strategy

1. [Blue-green deployment / Canary / Rolling]
2. [Health checks and readiness probes]
3. [Gradual traffic shift]

### Rollback Triggers

- [Automated rollback conditions]
- [Manual rollback procedures]
- [Data migration rollback]

---

## Implementation Notes

### Technical Considerations

- [Technology stack choices and rationale]
- [Scalability considerations]
- [Performance optimizations]
- [Technical debt and future improvements]

### Dependencies

- [External service dependencies]
- [Library and framework versions]
- [Infrastructure requirements]

---

## Acceptance Criteria

1. ✅ [Measurable criterion 1]
2. ✅ [Measurable criterion 2]
3. ✅ [Measurable criterion 3]
4. ✅ [Performance requirement]
5. ✅ [Security requirement]
6. ✅ [User experience requirement]

---

## Summary

[Brief summary of the solution, key benefits, and expected outcomes]
"""

    # Add DDD-specific sections if needed
    if spec_type == "ddd":
        template += """
---

## Domain-Driven Design

### Bounded Contexts

```mermaid
graph TB
    subgraph "Context A"
        AggA[Aggregate A]
        EntA[Entity A]
    end

    subgraph "Context B"
        AggB[Aggregate B]
        EntB[Entity B]
    end

    AggA -.->|Domain Event| AggB
```

### Aggregates

| Aggregate Root | Context | Invariants |
| --- | --- | --- |
| [Aggregate Name] | [Context] | [Business Rules] |

### Domain Events

| Event | Triggered By | Consumers |
| --- | --- | --- |
| [EventName] | [Aggregate.Method] | [Services] |

### Ports and Adapters

#### Inbound Ports (Use Cases)

```typescript
interface CreateResourceUseCase {
  execute(input: CreateResourceInput): Promise<CreateResourceOutput>;
}
```

#### Outbound Ports (Infrastructure)

```typescript
interface ResourceRepository {
  save(resource: Resource): Promise<void>;
  findById(id: string): Promise<Resource | null>;
}
```
"""

    return template


def main():
    parser = argparse.ArgumentParser(description="Generate design spec scaffolding")
    parser.add_argument("title", help="Title of the specification")
    parser.add_argument("--author", default="Author Name", help="Author name")
    parser.add_argument("--type",
                       choices=["standard", "ddd", "clean", "microservices",
                               "event-sourcing", "soa", "document", "monolith", "timeseries"],
                       default="standard",
                       help="Architecture type for the spec")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    # Generate the scaffold
    content = generate_spec_scaffold(
        title=args.title,
        author=args.author,
        spec_type=args.type
    )

    # Output the result
    if args.output:
        output_path = args.output
        if not output_path.endswith('.md'):
            output_path += '.md'

        with open(output_path, 'w') as f:
            f.write(content)
        print(f"✅ Spec scaffold generated: {output_path}")
        print(f"   Architecture: {args.type}")
    else:
        print(content)


if __name__ == "__main__":
    main()