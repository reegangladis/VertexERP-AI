# Production Scheduling & Shop Floor Execution Guide

## Overview
The Production Scheduling & Shop Floor Execution module manages the lifecycle of manufacturing orders, material reservation checks, real-time output logging, scrap tracking, and automated Material Requirement Planning (MRP).

## Production Order Lifecycle
1. **DRAFT / PLANNED**: Order initialized with target quantity, warehouse, BOM, and routing sequence.
2. **IN_PROGRESS**: Shop floor execution initiated; output quantity logged by operators.
3. **COMPLETED**: Finished goods logged; inventory updated and order closed.
4. **CANCELLED**: Order aborted before completion.

## Shop Floor Execution Logging
Operators use the Shop Floor interface to log output, record material consumption, track scrap rates, and report unplanned machine downtime.

## Material Requirement Planning (MRP) Engine
The MRP Engine explodes multi-level BOMs against active demand and inventory levels to generate:
- **Procurement Purchase Suggestions**: Raw materials below safety stock thresholds.
- **Production Suggestions**: Planned production orders needed to fulfill open demand.
- **Capacity Planning**: Work center workload and utilization percentages.
