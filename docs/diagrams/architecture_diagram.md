# Bifrost Architecture Diagram

This diagram illustrates the layered architecture of the Bifrost system, showing how different components interact.

```mermaid
flowchart TD
    %% User Interface Layer
    subgraph UILayer["User Interface Layer"]
        CLI["Command Line Interface"]
        GUI["Graphical User Interface"]
        API["REST/GraphQL API"]
        Webhooks["Webhooks"]
    end
    
    %% Service Layer
    subgraph ServiceLayer["Service Layer"]
        AssetService["Asset Service"]
        ShotService["Shot Service"]
        FolderService["Folder Service"]
        WorkflowService["Workflow Service"]
        SearchService["Search Service"]
        SyncService["Sync Service"]
    end
    
    %% Domain Layer
    subgraph DomainLayer["Domain Layer"]
        direction TB
        
        subgraph AssetDomain["Asset Domain"]
            Asset["Asset"]
            AssetVersion["Asset Version"]
            AssetDependency["Asset Dependency"]
            AssetType["Asset Type"]
        end
        
        subgraph ShotDomain["Shot Domain"]
            Shot["Shot"]
            Sequence["Sequence"]
            Episode["Episode"]
            ShotVersion["Shot Version"]
        end
        
        subgraph WorkflowDomain["Workflow Domain"]
            Task["Task"]
            Status["Status"]
            Approval["Approval"]
            Workflow["Workflow"]
        end
        
        subgraph UserDomain["User Domain"]
            User["User"]
            Role["Role"]
            Team["Team"]
            Activity["Activity"]
        end
    end
    
    %% Repository Layer
    subgraph RepositoryLayer["Repository Layer"]
        AssetRepository["Asset Repository"]
        ShotRepository["Shot Repository"]
        WorkflowRepository["Workflow Repository"]
        UserRepository["User Repository"]
    end
    
    %% Core Layer
    subgraph CoreLayer["Core Layer"]
        Database["Database"]
        Config["Configuration"]
        Auth["Authentication"]
        Logging["Logging"]
        Cache["Cache"]
    end
    
    %% Integration Layer
    subgraph IntegrationLayer["Integration Layer"]
        subgraph StorageIntegration["Storage"]
            LocalStorage["Local Storage"]
            NetworkStorage["Network Storage"]
            CloudStorage["Cloud Storage"]
        end
        
        subgraph DCCIntegration["DCC Tools"]
            MayaPlugin["Maya"]
            BlenderPlugin["Blender"]
            HoudiniPlugin["Houdini"]
        end
        
        subgraph ExternalIntegration["External Systems"]
            OpenAssetIO["OpenAssetIO"]
            USDPipeline["USD Pipeline"]
        end
    end
    
    %% Connections
    
    %% UI to Services
    CLI --> ServiceLayer
    GUI --> ServiceLayer
    API --> ServiceLayer
    Webhooks --> ServiceLayer
    
    %% Services to Domain/Repositories
    AssetService --> AssetDomain
    AssetService --> AssetRepository
    
    ShotService --> ShotDomain
    ShotService --> ShotRepository
    
    FolderService --> StorageIntegration
    
    WorkflowService --> WorkflowDomain
    WorkflowService --> WorkflowRepository
    
    SearchService --> AssetRepository
    SearchService --> ShotRepository
    SearchService --> WorkflowRepository
    
    SyncService --> StorageIntegration
    
    %% Repositories to Core
    RepositoryLayer --> Database
    
    %% Domain Events
    AssetDomain -.-> ServiceLayer
    ShotDomain -.-> ServiceLayer
    WorkflowDomain -.-> ServiceLayer
    
    %% Core Supporting Everything
    CoreLayer -.-> ServiceLayer
    CoreLayer -.-> DomainLayer
    CoreLayer -.-> RepositoryLayer
    CoreLayer -.-> IntegrationLayer
    
    %% Integrations
    StorageIntegration -.-> AssetDomain
    StorageIntegration -.-> ShotDomain
    
    DCCIntegration --> ServiceLayer
    
    OpenAssetIO --> AssetDomain
    USDPipeline --> AssetDomain
    USDPipeline --> ShotDomain
    
    classDef uiLayer fill:#fad2e1,stroke:#000,stroke-width:1px
    classDef serviceLayer fill:#c5dedd,stroke:#000,stroke-width:1px
    classDef domainLayer fill:#fff2cc,stroke:#000,stroke-width:1px
    classDef coreLayer fill:#d0e0e3,stroke:#000,stroke-width:1px
    classDef repoLayer fill:#dad2e0,stroke:#000,stroke-width:1px
    classDef integrationLayer fill:#ffe599,stroke:#000,stroke-width:1px
    
    class UILayer uiLayer
    class ServiceLayer serviceLayer
    class DomainLayer,AssetDomain,ShotDomain,WorkflowDomain,UserDomain domainLayer
    class CoreLayer coreLayer
    class RepositoryLayer repoLayer
    class IntegrationLayer,StorageIntegration,DCCIntegration,ExternalIntegration integrationLayer
```

## Diagram Description

### Layers

1. **User Interface Layer**
   - Command Line Interface: For script-based interaction
   - Graphical User Interface: Desktop application for visual asset management
   - REST/GraphQL API: For integration with other systems
   - Webhooks: Event-based notifications for external systems

2. **Service Layer**
   - Implements application use cases
   - Orchestrates domain objects
   - Handles cross-domain coordination
   - Manages transactions and security

3. **Domain Layer**
   - Contains core business logic and entities
   - Divided into bounded contexts (Asset, Shot, Workflow, User)
   - Implements domain-specific rules and behaviors
   - Raises domain events for important state changes

4. **Repository Layer**
   - Abstracts persistence details
   - Provides data access interfaces
   - Separates domain logic from data access
   - Supports different database implementations

5. **Core Layer**
   - Provides cross-cutting infrastructure
   - Database: Data persistence
   - Config: Configuration management
   - Auth: Authentication and authorization
   - Logging: Centralized logging
   - Cache: Performance optimization

6. **Integration Layer**
   - Connects to external systems
   - Storage: Local, network, and cloud storage
   - DCC Tools: Maya, Blender, Houdini integration
   - External Systems: OpenAssetIO, USD Pipeline

### Connection Types

- **Solid Lines (-->)**: Direct dependencies/method calls
- **Dotted Lines (-..->)**: Events or indirect dependencies

### Design Patterns

- **Repository Pattern**: For data access abstraction
- **Service Layer Pattern**: For application use cases
- **Domain-Driven Design**: For organizing business logic
- **Event-Driven Architecture**: For loose coupling between components
