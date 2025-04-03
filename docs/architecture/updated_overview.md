# Bifrost Architecture: Updated Overview

This document outlines the revised architecture for the Bifrost Animation Asset Management System, incorporating lessons learned from initial development and new requirements.

## System Overview

Bifrost is designed as a modular, cloud-ready system for managing animation production assets and shots across studios of different sizes. The architecture follows a domain-driven design approach with clear separation of concerns:

```
┌──────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
│     CLI              GUI            API            Webhooks  │
└───────────────┬─────────────┬───────────────┬────────────────┘
                │             │               │
┌───────────────▼─────────────▼───────────────▼────────────────┐
│                      Service Layer                           │
│                                                              │
│  ┌───────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │ Asset Service │  │ Folder Service │  │ Workflow Service │ │
│  └───────────────┘  └────────────────┘  └──────────────────┘ │
│                                                              │
│  ┌───────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │ Shot Service  │  │ Search Service │  │   Sync Service   │ │
│  └───────────────┘  └────────────────┘  └──────────────────┘ │
└───────────────┬─────────────┬───────────────┬────────────────┘
                │             │               │
┌───────────────▼─────────────▼───────────────▼────────────────┐
│                       Domain Layer                           │
│                                                              │
│  ┌────────────────────────┐  ┌────────────────────────────┐  │
│  │      Asset Domain      │  │      Shot Domain           │  │
│  │                        │  │                            │  │
│  │ • Assets               │  │ • Shots                    │  │
│  │ • Versions             │  │ • Sequences                │  │
│  │ • Dependencies         │  │ • Frames                   │  │
│  └────────────────────────┘  └────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────┐  ┌────────────────────────────┐  │
│  │   Workflow Domain      │  │    User Domain             │  │
│  │                        │  │                            │  │
│  │ • Tasks                │  │ • Users                    │  │
│  │ • Status               │  │ • Permissions              │  │
│  │ • Approvals            │  │ • Teams                    │  │
│  └────────────────────────┘  └────────────────────────────┘  │
└───────────────┬─────────────┬───────────────┬────────────────┘
                │             │               │
┌───────────────▼─────────────▼───────────────▼────────────────┐
│                        Core Layer                            │
│                                                              │
│  ┌────────────┐  ┌────────┐  ┌─────┐  ┌─────────┐  ┌───────┐ │
│  │  Database  │  │ Config │  │Auth │  │ Logging │  │ Cache │ │
│  └────────────┘  └────────┘  └─────┘  └─────────┘  └───────┘ │
└───────────────┬─────────────┬───────────────┬────────────────┘
                │             │               │
┌───────────────▼─────────────▼───────────────▼────────────────┐
│                     Integration Layer                        │
│                                                              │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────────────┐ │
│  │   Storage      │  │    DCC      │  │    External        │ │
│  │                │  │             │  │    Systems         │ │
│  │ • Local        │  │ • Maya      │  │                    │ │
│  │ • Network      │  │ • Blender   │  │ • OpenAssetIO      │ │
│  │ • Cloud        │  │ • Houdini   │  │ • USD Pipeline     │ │
│  └────────────────┘  └─────────────┘  └────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Key Architectural Changes

### 1. Domain-Driven Design

The architecture has been reorganized around distinct domain models:

- **Asset Domain**: Everything related to production assets, their versions, and dependencies
- **Shot Domain**: Shot organization, sequences, and frame management
- **Workflow Domain**: Tasks, statuses, and approvals
- **User Domain**: User accounts, permissions, and team organization

### 2. Expanded Integration Layer

The integration layer has been expanded to include:

- **OpenAssetIO Support**: Standard interface for asset management system interoperability
- **USD Pipeline Integration**: First-class support for Universal Scene Description workflows
- **Cloud Provider Support**: Abstracted interfaces for multiple cloud storage providers

### 3. Folder Structure Management

A new sub-system has been added for managing project folder structures:

- **Folder Templates**: Configurable templates for project organization
- **Folder Synchronization**: Keep file system in sync with database
- **Path Resolution**: Intelligent path resolution based on asset context

### 4. Workflow Engine

A flexible workflow engine has been added to support:

- **Customizable Pipelines**: Define different workflows for different asset types
- **State Machines**: Track asset/shot status through production
- **Approval Processes**: Structured review and approval workflows
- **Notifications**: Event-based notification system

## Core Components

### 1. Domain Layer

The domain layer contains the core business logic and entities:

- **Asset Domain**:
  - `Asset`: Production assets with metadata
  - `AssetVersion`: Version history for assets
  - `AssetDependency`: Relationships between assets
  - `AssetType`: Classification of assets

- **Shot Domain**:
  - `Shot`: Production shots with frame ranges
  - `Sequence`: Grouping of related shots
  - `ShotVersion`: Version history for shots
  - `ShotAsset`: Relationship between shots and assets

- **Workflow Domain**:
  - `Task`: Work items assigned to users
  - `Status`: Current state of work items
  - `Approval`: Review and approval records
  - `Workflow`: Definition of production processes

- **User Domain**:
  - `User`: User accounts and profiles
  - `Role`: User roles and permissions
  - `Team`: Team organization
  - `Activity`: User activity tracking

### 2. Service Layer

Services implement use cases by orchestrating domain objects:

- **Asset Service**: Asset lifecycle management
- **Shot Service**: Shot organization and tracking
- **Folder Service**: Project structure management
- **Search Service**: Cross-domain search capabilities
- **Workflow Service**: Task and approval management
- **Sync Service**: File system synchronization

### 3. Core Layer

Core infrastructure services:

- **Database**: SQLite (development), PostgreSQL (production)
- **Config**: Configuration management with environment overrides
- **Auth**: Authentication and authorization
- **Logging**: Centralized, structured logging
- **Cache**: In-memory and distributed caching

### 4. Integration Layer

Connects Bifrost to external systems:

- **Storage**:
  - `LocalStorage`: File system operations
  - `NetworkStorage`: Network share protocols
  - `CloudStorage`: Cloud storage providers (S3, GCS, Azure)

- **DCC Tools**:
  - `MayaIntegration`: Maya plugin
  - `BlenderIntegration`: Blender addon
  - `HoudiniIntegration`: Houdini integration

- **External Systems**:
  - `OpenAssetIO`: Asset management interoperability
  - `USDIntegration`: Universal Scene Description integration
  - `WebhookSystem`: External system notifications

### 5. User Interfaces

Multiple interfaces for different use cases:

- **CLI**: Command-line interface for scripting and automation
- **GUI**: Desktop application for visual asset management
- **API**: REST and GraphQL APIs for integration
- **Webhooks**: Event-based notifications

## Data Flow Patterns

### 1. Command Pattern

For operations that modify state:

1. **Command Creation**: UI/API creates a command object
2. **Validation**: Service validates the command
3. **Execution**: Service executes the command
4. **Event Generation**: Domain events are generated
5. **Response**: Result is returned to the caller

### 2. Query Pattern

For read operations:

1. **Query Creation**: UI/API creates a query object
2. **Filtering**: Service applies security and business filters
3. **Execution**: Query is executed against the database
4. **Transformation**: Results are mapped to DTOs
5. **Response**: Data is returned to the caller

### 3. Event Pattern

For asynchronous operations:

1. **Event Generation**: Domain event is published
2. **Event Processing**: Event handlers subscribe and process
3. **Side Effects**: Additional operations are triggered
4. **Notification**: Relevant users/systems are notified

## Technology Stack Updates

- **Language**: Python 3.10+ (updated from 3.9+)
- **Database**: SQLite (development), PostgreSQL 14+ (production)
- **API Framework**: FastAPI with Pydantic 2.0
- **GUI Framework**: PySide6 (Qt 6.5+)
- **Package Management**: Poetry for dependency management
- **Cloud SDK**: boto3, google-cloud-storage, azure-storage-blob
- **Testing**: pytest, pytest-cov with GitHub Actions CI

## Deployment Options

### 1. Single-User Mode
- Desktop application with SQLite
- Local file system storage
- Suitable for individual artists

### 2. Small Team Mode
- Central server with PostgreSQL
- Shared network storage
- 5-20 concurrent users

### 3. Studio Mode
- Clustered deployment
- PostgreSQL with connection pooling
- Cloud or hybrid storage
- 20-100+ concurrent users

### 4. Enterprise Mode
- Multi-region deployment
- Sharded database
- CDN-accelerated cloud storage
- 100+ concurrent users

## Security Architecture

- **Authentication**: OAuth 2.0 / OpenID Connect
- **Authorization**: Role-Based Access Control (RBAC)
- **Data Protection**: At-rest and in-transit encryption
- **API Security**: Rate limiting, JWT authentication
- **Audit**: Comprehensive audit logging

## Future Architecture Considerations

- **GraphQL API**: For more flexible data querying
- **Container Deployment**: Docker and Kubernetes support
- **Edge Computing**: Local processing with central coordination
- **Real-Time Collaboration**: WebSocket-based real-time features
- **Machine Learning Integration**: Asset tagging and suggestion systems
