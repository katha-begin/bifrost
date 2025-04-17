# Bifrost Database Entity Relationship Diagram

This diagram illustrates the database schema design for the Bifrost system, showing entities and their relationships.

```mermaid
erDiagram
    %% Asset Domain
    ASSET {
        uuid id PK
        string name
        string description
        uuid asset_type_id FK
        string status
        datetime created_at
        string created_by
        datetime modified_at
        string modified_by
        jsonb metadata
        jsonb tags
    }
    
    ASSET_TYPE {
        uuid id PK
        string name
        string display_name
        string description
        string icon
        jsonb metadata
    }
    
    ASSET_VERSION {
        uuid id PK
        uuid asset_id FK
        int version_number
        string file_path
        string comment
        datetime created_at
        string created_by
        jsonb metadata
    }
    
    ASSET_DEPENDENCY {
        uuid id PK
        uuid source_asset_id FK
        uuid dependent_asset_id FK
        string dependency_type
        boolean optional
        jsonb metadata
    }
    
    %% Shot Domain
    SHOT {
        uuid id PK
        string name
        string description
        uuid sequence_id FK
        int frame_start
        int frame_end
        string status
        datetime created_at
        string created_by
        datetime modified_at
        string modified_by
        jsonb metadata
        jsonb tags
    }
    
    SEQUENCE {
        uuid id PK
        string name
        string code
        uuid episode_id FK
        string description
        jsonb metadata
    }
    
    EPISODE {
        uuid id PK
        string name
        string code
        uuid series_id FK
        string description
        jsonb metadata
    }
    
    SERIES {
        uuid id PK
        string name
        string code
        string description
        jsonb numbering
        jsonb metadata
    }
    
    SHOT_VERSION {
        uuid id PK
        uuid shot_id FK
        int version_number
        string file_path
        string comment
        datetime created_at
        string created_by
        jsonb metadata
    }
    
    SHOT_ASSET {
        uuid id PK
        uuid shot_id FK
        uuid asset_id FK
        string relationship_type
        jsonb metadata
    }
    
    %% Workflow Domain
    TASK {
        uuid id PK
        string name
        string description
        uuid assignee_id FK
        uuid asset_id FK "Nullable"
        uuid shot_id FK "Nullable"
        string status
        string priority
        datetime due_date
        datetime created_at
        string created_by
        jsonb tags
        int estimated_hours
        uuid department_id FK "Nullable"
        jsonb dependencies
        jsonb metadata
    }
    
    APPROVAL {
        uuid id PK
        uuid task_id FK
        uuid reviewer_id FK
        string status
        string comment
        datetime review_date
        jsonb metadata
    }
    
    WORKFLOW {
        uuid id PK
        string name
        string description
        jsonb states
        jsonb transitions
        jsonb metadata
    }
    
    %% User Domain
    USER {
        uuid id PK
        string username
        string email
        string password_hash
        string full_name
        string department
        boolean active
        datetime created_at
        datetime last_login
        jsonb preferences
        jsonb teams
        jsonb roles
        jsonb metadata
    }
    
    ROLE {
        uuid id PK
        string name
        string description
        jsonb permissions
    }
    
    USER_ROLE {
        uuid id PK
        uuid user_id FK
        uuid role_id FK
    }
    
    TEAM {
        uuid id PK
        string name
        string description
    }
    
    TEAM_MEMBER {
        uuid id PK
        uuid team_id FK
        uuid user_id FK
        string role
    }
    
    ACTIVITY {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        uuid entity_id
        jsonb changes
        datetime timestamp
        string ip_address
    }

    %% Relationships

    %% Asset Domain Relationships
    ASSET ||--|| ASSET_TYPE : "has type"
    ASSET ||--o{ ASSET_VERSION : "has versions"
    ASSET ||--o{ ASSET_DEPENDENCY : "is source of"
    ASSET }o--o{ ASSET_DEPENDENCY : "is dependent of"
    
    %% Shot Domain Relationships
    SERIES ||--o{ EPISODE : "contains"
    EPISODE ||--o{ SEQUENCE : "contains"
    SEQUENCE ||--o{ SHOT : "contains"
    SHOT ||--o{ SHOT_VERSION : "has versions"
    SHOT ||--o{ SHOT_ASSET : "uses"
    ASSET ||--o{ SHOT_ASSET : "used in"
    
    %% Workflow Domain Relationships
    TASK }o--|| USER : "assigned to"
    TASK }o--o| ASSET : "related to"
    TASK }o--o| SHOT : "related to"
    TASK ||--o{ APPROVAL : "has reviews"
    APPROVAL }o--|| USER : "reviewed by"
    
    %% User Domain Relationships
    USER ||--o{ USER_ROLE : "has"
    ROLE ||--o{ USER_ROLE : "assigned to"
    TEAM ||--o{ TEAM_MEMBER : "has"
    USER ||--o{ TEAM_MEMBER : "member of"
    USER ||--o{ ACTIVITY : "performed"
```

## Diagram Description

### Entity Domains

1. **Asset Domain**
   - **ASSET**: Core asset entity with metadata
   - **ASSET_TYPE**: Classification of assets (character, prop, environment, etc.)
   - **ASSET_VERSION**: Versioning history for assets
   - **ASSET_DEPENDENCY**: Relationship between assets

2. **Shot Domain**
   - **SERIES**: Top-level organization (show, film, etc.)
   - **EPISODE**: Sub-division of series 
   - **SEQUENCE**: Group of related shots
   - **SHOT**: Individual camera shot with frame range
   - **SHOT_VERSION**: Versioning history for shots
   - **SHOT_ASSET**: Junction table linking shots to assets

3. **Workflow Domain**
   - **TASK**: Work item that can be assigned to users
   - **APPROVAL**: Review record for tasks
   - **WORKFLOW**: Definition of workflow states and transitions

4. **User Domain**
   - **USER**: System user information
   - **ROLE**: User roles with permissions
   - **USER_ROLE**: Junction table for user-role assignments
   - **TEAM**: Groups of users
   - **TEAM_MEMBER**: User membership in teams
   - **ACTIVITY**: Audit log of user actions

### Relationship Types

- **||--||**: One-to-one relationship
- **||--o{**: One-to-many relationship
- **}o--o{**: Many-to-many relationship
- **}o--||**: Many-to-one relationship
- **}o--o|**: Many-to-optional-one relationship

### Database Design Principles

1. **Entity Integrity**: All tables have primary keys (PK)
2. **Referential Integrity**: Foreign keys (FK) maintain relationships
3. **Domain Segregation**: Tables are organized by domain
4. **Metadata Flexibility**: JSONB fields allow for extensibility
5. **Audit Trails**: Creation/modification timestamps and user tracking

### Implementation Notes

- UUID primary keys for distributed systems compatibility
- JSON/JSONB for flexible schema evolution
- Created/modified timestamps for auditing
- Soft-deletion (active flag) for recoverability
