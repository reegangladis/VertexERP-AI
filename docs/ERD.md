# Entity Relationship Diagram (ERD)

This document contains a Mermaid entity-relationship diagram of all Phase 3 database schemas.

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ BRANCHES : "contains"
    ORGANIZATIONS ||--o{ DEPARTMENTS : "contains"
    ORGANIZATIONS ||--o{ DESIGNATIONS : "defines"
    ORGANIZATIONS ||--o{ LOCATIONS : "operates"
    ORGANIZATIONS ||--o{ BUSINESS_CALENDARS : "schedules"
    ORGANIZATIONS ||--o{ ORGANIZATION_DOCUMENTS : "archives"
    ORGANIZATIONS ||--o{ ORGANIZATION_METADATA : "annotates"

    BRANCHES ||--o{ DEPARTMENTS : "houses"
    BRANCHES ||--o{ BRANCHES : "reports to (self)"
    
    DEPARTMENTS ||--o{ TEAMS : "coordinates"
    DEPARTMENTS ||--o{ DEPARTMENTS : "reports to (self)"
    
    TEAMS ||--o{ TEAMS : "reports to (self)"
    
    BUSINESS_CALENDARS ||--o{ WORKING_DAYS : "schedules"
    BUSINESS_CALENDARS ||--o{ HOLIDAYS : "excludes"

    USERS }o--|| DESIGNATIONS : "assigned"
    USERS }o--|| USERS : "reports to manager (self)"
```

### Key Relationships
*   **Self-Referencing Parent Fields**: `branches`, `departments`, and `teams` implement hierarchical parenthood keys with cyclic logic validation checks in services.
*   **User Assignment**: `users` maps back to `designations` (job roles) and self-references another user via `manager_id` to generate recursive tree structures.
