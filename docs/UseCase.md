# Use Case Diagram & Actors

This document specifies the primary roles and operational capabilities implemented in Phase 3.

## Use Case Diagram

```mermaid
leftToRightDirection
actor Admin as Organization Administrator
actor HR as Human Resources Specialist
actor Emp as Standard Employee

rectangle "VertexERP AI - Org Platform" {
    usecase UC1 as "Manage Branch Hierarchy"
    usecase UC2 as "Configure Corporate Calendar"
    usecase UC3 as "Import branches via CSV"
    usecase UC4 as "Edit branding colors & metadata"
    usecase UC5 as "Upload policy handbooks"
    usecase UC6 as "Review reporting structure tree"
    usecase UC7 as "Download policy documents"
}

Admin --> UC1
Admin --> UC2
Admin --> UC3
Admin --> UC4
Admin --> UC5
Admin --> UC6

HR --> UC5
HR --> UC6

Emp --> UC6
Emp --> UC7
```

## Actors & Permissions
1.  **Organization Administrator**:
    *   Full read/write permissions to configure branches, parent departments, and calendar shifts.
    *   Authorized to update branding HEX variables and organization-wide key-value metadata parameters.
2.  **Human Resources Specialist**:
    *   Authorized to upload employee handbooks and modify designation profiles.
    *   Reads reporting structures.
3.  **Standard Employee**:
    *   Authorized to view the interactive hierarchical reporting structure tree.
    *   Can view and download policy handbooks or certificate files.
    *   Bound to a reporting designation and manager structure.
    *   Abides by local branch timezone and business calendar shift patterns.
    *   Accesses system under branch restrictions.
    *   View calendar holidays list.
