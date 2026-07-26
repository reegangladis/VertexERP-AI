# Bill of Materials (BOM) & Cost Rollup Guide

## Overview
The Bill of Materials (BOM) engine supports multi-level component nesting, version control, alternative component mapping, approval workflows, and automated cost rollups.

## Multi-Level BOM Structure
- **BOM Header**: Maps to a finished product, version number, base quantity, and status (`DRAFT`, `PENDING_APPROVAL`, `APPROVED`, `OBSOLETE`).
- **BOM Items**: Component line items referencing raw materials or semi-finished goods, quantity per base batch, unit name, scrap factor %, and optional parent item link for multi-level nesting.

## Automated Cost Rollup Methodology
`Total BOM Cost = Sum(Component Qty * Unit Cost * (1 + Scrap Factor %)) + Operations Standard Labor & Machine Cost`

Running cost rollup updates the BOM master record dynamically and generates cost breakdown summaries.
