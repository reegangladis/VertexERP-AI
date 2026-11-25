/**
 * Cross-Persona Interactive Demo & Fallback Store for VertexERP AI.
 * Persists in localStorage across persona switches (Employee <-> HR Manager <-> Admin)
 * so workflows like Employee Apply Leave -> Manager Approval, and full Organization
 * entities (Branches, Departments, Teams, Designations, Business Units, Cost Centers,
 * Locations, Work Calendars, Holidays) work end-to-end on both Vercel and offline mode.
 */

import { useEffect, useState } from "react";
import type {
  Branch,
  BusinessUnit,
  CostCenter,
  Department,
  DepartmentTreeNode,
  Designation,
  Holiday,
  Location,
  Team,
  TeamMember,
  WorkCalendar,
  WorkingDay,
} from "@/features/organization/types/organization.types";

export interface DemoLeaveBalance {
  code: string;
  id: string;
  name: string;
  total: number;
  used: number;
  pending: number;
  balance: number;
}

export interface DemoLeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  employee_email: string;
  leave_type_id: string;
  leave_type_code: string;
  leave_type_name: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: "SUBMITTED" | "PENDING" | "APPROVED" | "REJECTED" | "RETURNED";
  approver_name?: string;
  approved_at?: string;
  remarks?: string;
  created_at: string;
}

export interface DemoNotification {
  id: string;
  title: string;
  message: string;
  type: "INFO" | "WARNING" | "ACTION_REQUIRED" | "SUCCESS";
  createdAt: string;
  isRead: boolean;
  link?: string;
  targetRole?: "MANAGER" | "EMPLOYEE" | "ALL";
}

export interface DemoOtherApproval {
  id: string;
  entity_type: "REGULARIZATION" | "QUOTATION";
  entity_id: string;
  requester_name: string;
  requester_email?: string;
  title: string;
  summary: string;
  amount?: number;
  currency?: string;
  status: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  created_at: string;
  details: Record<string, any>;
}

export interface DemoState {
  branches: Branch[];
  departments: Department[];
  teams: Team[];
  teamMembers: Record<string, TeamMember[]>;
  designations: Designation[];
  businessUnits: BusinessUnit[];
  costCenters: CostCenter[];
  locations: Location[];
  calendars: WorkCalendar[];
  holidays: Holiday[];
  leaveBalances: DemoLeaveBalance[];
  leaveRequests: DemoLeaveRequest[];
  otherApprovals: DemoOtherApproval[];
  notifications: DemoNotification[];
}

const STORAGE_KEY = "vertexerp_interactive_demo_v2";
const NOW = "2026-11-24T09:00:00Z";
const TENANT_ID = "c7d4bb7c-8186-451c-80ca-c538e9d5afa0";
const ORG_ID = "9d8d79b7-e22b-4d9e-9130-3feeef872937";

function buildWorkingDays(calId: string, startTime: string, endTime: string, includeSat = false): WorkingDay[] {
  return [0, 1, 2, 3, 4, 5, 6].map((dow) => {
    const isWork = dow < 5 || (includeSat && dow === 5);
    return {
      id: `wd-${calId}-${dow}`,
      tenant_id: TENANT_ID,
      calendar_id: calId,
      day_of_week: dow,
      is_working_day: isWork,
      start_time: isWork ? (dow === 5 && includeSat ? "09:00" : startTime) : null,
      end_time: isWork ? (dow === 5 && includeSat ? "13:00" : endTime) : null,
      created_at: NOW,
    };
  });
}

export function createInitialDemoState(): DemoState {
  return {
    branches: [
      {
        id: "br-nyc-01",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "BR-NYC",
        name: "New York Global HQ",
        address_line1: "One World Trade Center, Suite 8500",
        city: "New York",
        state: "NY",
        postal_code: "10007",
        country: "USA",
        phone: "+1 (212) 555-0100",
        email: "nyc@vertexerp.com",
        is_headquarters: true,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "br-sfo-02",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "BR-SFO",
        name: "San Francisco AI Hub",
        address_line1: "500 Howard Street, Suite 400",
        city: "San Francisco",
        state: "CA",
        postal_code: "94105",
        country: "USA",
        phone: "+1 (415) 555-0199",
        email: "sfo@vertexerp.com",
        is_headquarters: false,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "br-aus-03",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "BR-AUS",
        name: "Austin Hardware & Systems Lab",
        address_line1: "401 Congress Ave, Floor 18",
        city: "Austin",
        state: "TX",
        postal_code: "78701",
        country: "USA",
        phone: "+1 (512) 555-0142",
        email: "austin@vertexerp.com",
        is_headquarters: false,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "br-ldn-04",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "BR-LDN",
        name: "London EMEA Hub",
        address_line1: "25 Bank Street, Canary Wharf",
        city: "London",
        state: "England",
        postal_code: "E14 5JP",
        country: "GBR",
        phone: "+44 20 7946 0910",
        email: "london@vertexerp.com",
        is_headquarters: false,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "br-sgp-05",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "BR-SGP",
        name: "Singapore APAC Center",
        address_line1: "10 Collyer Quay, Ocean Financial Centre",
        city: "Singapore",
        state: "Central",
        postal_code: "049315",
        country: "SGP",
        phone: "+65 6789 0123",
        email: "apac@vertexerp.com",
        is_headquarters: false,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
    ],
    departments: [
      {
        id: "dept-eng-01",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        parent_department_id: null,
        code: "ENGI",
        name: "Engineering & Technology",
        description: "Core platform architecture, AI research, and cloud systems",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "dept-ai-02",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        parent_department_id: "dept-eng-01",
        code: "AI-CORE",
        name: "Applied AI & Copilot Labs",
        description: "LLM orchestration, RAG engines, and predictive ML models",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "dept-sre-03",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        parent_department_id: "dept-eng-01",
        code: "PLAT-SRE",
        name: "Cloud Platform & SRE",
        description: "Global cloud reliability, multi-region clusters, and security",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "dept-sales-04",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        parent_department_id: null,
        code: "SALE",
        name: "Sales & Commercial",
        description: "Global enterprise sales, solutions engineering, and revenue ops",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "dept-hr-05",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        parent_department_id: null,
        code: "PEOP",
        name: "People Operations",
        description: "Talent acquisition, HR governance, compensation, and culture",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "dept-fin-06",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        parent_department_id: null,
        code: "FINA",
        name: "Finance & Corporate",
        description: "Treasury, FP&A, accounting governance, and audit compliance",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
    ],
    teams: [
      {
        id: "team-ai-01",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        department_id: "dept-ai-02",
        code: "TEAM-AI",
        name: "Core AI Intelligence Squad",
        description: "Generative AI Copilot & RAG retrieval engineering squad",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "team-plat-02",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        department_id: "dept-sre-03",
        code: "TEAM-PLAT",
        name: "Platform Architecture Pod",
        description: "High-throughput API & distributed ledger core systems",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "team-ent-03",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        department_id: "dept-sales-04",
        code: "TEAM-ENT",
        name: "Enterprise GTM Pod",
        description: "Fortune 500 strategic account executives & solutions engineers",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "team-hr-04",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        department_id: "dept-hr-05",
        code: "TEAM-HR",
        name: "People & Talent Partners",
        description: "Employee experience, leave governance & global onboarding",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
      {
        id: "team-fin-05",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        department_id: "dept-fin-06",
        code: "TEAM-FIN",
        name: "Treasury & FP&A Desk",
        description: "General ledger automation & financial forecasting pod",
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
      },
    ],
    teamMembers: {
      "team-ai-01": [
        { id: "tm-1", tenant_id: TENANT_ID, team_id: "team-ai-01", user_id: "alex.morgan@vertexerp.com (Alex Morgan)", role: "MEMBER", joined_at: NOW, created_at: NOW },
        { id: "tm-2", tenant_id: TENANT_ID, team_id: "team-ai-01", user_id: "admin@vertexerp.com (System Architect)", role: "LEAD", joined_at: NOW, created_at: NOW },
      ],
      "team-hr-04": [
        { id: "tm-3", tenant_id: TENANT_ID, team_id: "team-hr-04", user_id: "eleanor.vance@vertexerp.com (Eleanor Vance)", role: "LEAD", joined_at: NOW, created_at: NOW },
      ],
    },
    designations: [
      { id: "des-1", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "VP-ENG", name: "VP of Cloud Engineering", description: "Executive engineering leadership and reliability governance", level: 9, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-2", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "PRIN-ARCH", name: "Principal AI Architect", description: "Cross-domain enterprise architecture & LLM safety", level: 8, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-3", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "DIR-SALES", name: "Enterprise Sales Director", description: "Commercial bookings and regional revenue pipelines", level: 7, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-4", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "MGR-HR", name: "People Operations Manager", description: "HR governance, leave approval, and payroll compliance", level: 6, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-5", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "FIN-CTRL", name: "Financial Controller", description: "GAAP close, multi-currency reconciliation & audit readiness", level: 6, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-6", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SWE-SR", name: "Senior Full-Stack Engineer", description: "Core frontend & backend ERP product engineering", level: 4, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-7", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "AE-SR", name: "Senior Enterprise AE", description: "Full-cycle enterprise account acquisition", level: 4, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "des-8", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "HR-BP", name: "HR Business Partner", description: "Workforce planning & departmental coaching", level: 5, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
    ],
    businessUnits: [
      { id: "bu-1", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-CLOUD", name: "Vertex Cloud ERP Suite", description: "Flagship multi-tenant SaaS ERP & Copilot division", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "bu-2", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-HW", name: "Quantum Edge & AI Systems", description: "Enterprise GPU clusters and industrial IoT hardware", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "bu-3", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-ADV", name: "Global Advisory & Enterprise Ops", description: "Dedicated implementation & managed cloud services", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "bu-4", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-FIN", name: "Vertex Pay & Embedded Treasury", description: "Automated B2B invoicing, settlement, and ledger ops", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
    ],
    costCenters: [
      { id: "cc-1", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-eng-01", code: "CC-AI-RD", name: "AI Research & Cloud Engineering", description: "Compute GPUs, LLM inference, and R&D talent", annual_budget: 1450000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "cc-2", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-sales-04", code: "CC-GTM", name: "Global Sales & Marketing GTM", description: "Enterprise pipeline, events, and partner commissions", annual_budget: 840000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "cc-3", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-hr-05", code: "CC-PEOPLE", name: "People Ops, Wellness & L&D", description: "Recruiting, training academies, and benefits", annual_budget: 420000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "cc-4", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-fin-06", code: "CC-FINOPS", name: "Finance, Audit & Compliance", description: "SOC2 audits, treasury operations, and legal", annual_budget: 310000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "cc-5", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-sre-03", code: "CC-INFRA", name: "Cloud Infrastructure & SRE", description: "Multi-region hosting, observability, and security", annual_budget: 680000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
    ],
    locations: [
      { id: "loc-1", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-nyc-01", code: "LOC-NYC-HQ", name: "One WTC Executive Suite", location_type: "OFFICE", address_line1: "One World Trade Center, Suite 8500", city: "New York", state: "NY", postal_code: "10007", country: "USA", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "loc-2", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-nyc-01", code: "LOC-JFK-WH", name: "East Coast Distribution Hub", location_type: "WAREHOUSE", address_line1: "145 Cargo Service Rd, Bldg 75", city: "Jamaica", state: "NY", postal_code: "11430", country: "USA", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "loc-3", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-aus-03", code: "LOC-AUS-FAB", name: "Austin Cleanroom Assembly Plant", location_type: "PLANT", address_line1: "401 Congress Ave, Tech Park B", city: "Austin", state: "TX", postal_code: "78701", country: "USA", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "loc-4", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-ldn-04", code: "LOC-LDN-OFC", name: "Canary Wharf EMEA Office", location_type: "OFFICE", address_line1: "25 Bank Street, Level 19", city: "London", state: "England", postal_code: "E14 5JP", country: "GBR", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
      { id: "loc-5", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-sgp-05", code: "LOC-SGP-DC", name: "Singapore Tier-IV Edge Data Center", location_type: "WAREHOUSE", address_line1: "10 Collyer Quay, Tower 2", city: "Singapore", state: "Central", postal_code: "049315", country: "SGP", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
    ],
    calendars: [
      {
        id: "cal-1",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "CAL-US-EST",
        name: "US Eastern Standard (40h)",
        description: "Standard Monday-Friday corporate operating hours",
        time_zone: "America/New_York",
        is_default: true,
        standard_hours_per_day: 8,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
        working_days: buildWorkingDays("cal-1", "09:00", "17:30", false),
      },
      {
        id: "cal-2",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "CAL-EMEA-LON",
        name: "EMEA London Schedule (37.5h)",
        description: "UK & European headquarters operating schedule",
        time_zone: "Europe/London",
        is_default: false,
        standard_hours_per_day: 7.5,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
        working_days: buildWorkingDays("cal-2", "08:30", "16:30", false),
      },
      {
        id: "cal-3",
        tenant_id: TENANT_ID,
        organization_id: ORG_ID,
        code: "CAL-APAC-24X7",
        name: "APAC Cloud & SRE Operations",
        description: "Follow-the-Sun SRE & Manufacturing floor rotation",
        time_zone: "Asia/Singapore",
        is_default: false,
        standard_hours_per_day: 8,
        is_active: true,
        version: 1,
        created_at: NOW,
        updated_at: NOW,
        working_days: buildWorkingDays("cal-3", "08:00", "16:00", true),
      },
    ],
    holidays: [
      { id: "hol-1", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: "br-nyc-01", name: "New Year's Day", holiday_date: "2026-01-01", holiday_type: "NATIONAL", is_recurring: true, description: "Global statutory public holiday", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-2", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: "br-nyc-01", name: "Memorial Day", holiday_date: "2026-05-25", holiday_type: "NATIONAL", is_recurring: true, description: "US Federal Memorial Day", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-3", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: "br-nyc-01", name: "Independence Day", holiday_date: "2026-07-04", holiday_type: "NATIONAL", is_recurring: true, description: "US National Independence Day", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-4", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-3", branch_id: "br-sgp-05", name: "Singapore National Day", holiday_date: "2026-08-09", holiday_type: "REGIONAL", is_recurring: true, description: "APAC Regional Statutory Holiday", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-5", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-2", branch_id: "br-ldn-04", name: "UK Summer Bank Holiday", holiday_date: "2026-08-31", holiday_type: "REGIONAL", is_recurring: true, description: "London EMEA Bank Holiday", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-6", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: "br-nyc-01", name: "Labor Day", holiday_date: "2026-09-07", holiday_type: "NATIONAL", is_recurring: true, description: "Labor & Workforce Day", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-7", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: "br-nyc-01", name: "Thanksgiving Day", holiday_date: "2026-11-26", holiday_type: "NATIONAL", is_recurring: true, description: "Annual Thanksgiving celebration", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-8", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: null, name: "Vertex Founders & Innovation Day", holiday_date: "2026-12-11", holiday_type: "COMPANY", is_recurring: true, description: "Annual global paid company wellness holiday", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-9", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: null, name: "Christmas Day", holiday_date: "2026-12-25", holiday_type: "NATIONAL", is_recurring: true, description: "Winter Festive Holiday", version: 1, created_at: NOW, updated_at: NOW },
      { id: "hol-10", tenant_id: TENANT_ID, organization_id: ORG_ID, calendar_id: "cal-1", branch_id: null, name: "New Year's Day 2027", holiday_date: "2027-01-01", holiday_type: "NATIONAL", is_recurring: true, description: "Global New Year Observation", version: 1, created_at: NOW, updated_at: NOW },
    ],
    leaveBalances: [
      { id: "lt-cl", code: "CL", name: "Casual Leave", total: 12.0, used: 1.0, pending: 2.0, balance: 11.0 },
      { id: "lt-sl", code: "SL", name: "Sick & Medical Leave", total: 10.0, used: 0.0, pending: 0.0, balance: 10.0 },
      { id: "lt-el", code: "EL", name: "Earned / Privilege Leave", total: 18.0, used: 4.0, pending: 0.0, balance: 14.0 },
      { id: "lt-co", code: "CO", name: "Compensatory Off", total: 2.0, used: 1.0, pending: 0.0, balance: 1.0 },
    ],
    leaveRequests: [
      {
        id: "LR-2026-102",
        employee_id: "9d6bcc63-5acf-471e-afac-18d4b7386ee6",
        employee_name: "Alex Morgan",
        employee_email: "employee@vertexerp.com",
        leave_type_id: "lt-cl",
        leave_type_code: "CL",
        leave_type_name: "Casual Leave",
        start_date: "2026-12-03",
        end_date: "2026-12-04",
        total_days: 2.0,
        reason: "Attending sister graduation ceremony out of town",
        status: "SUBMITTED",
        created_at: "2026-11-25T08:30:00Z",
      },
      {
        id: "LR-2026-101",
        employee_id: "9d6bcc63-5acf-471e-afac-18d4b7386ee6",
        employee_name: "Alex Morgan",
        employee_email: "employee@vertexerp.com",
        leave_type_id: "lt-el",
        leave_type_code: "EL",
        leave_type_name: "Earned / Privilege Leave",
        start_date: "2026-10-12",
        end_date: "2026-10-15",
        total_days: 4.0,
        reason: "Annual family autumn retreat",
        status: "APPROVED",
        approver_name: "Eleanor Vance (HR Manager)",
        approved_at: "2026-10-05T14:15:00Z",
        remarks: "Approved in accordance with policy. Have a great trip!",
        created_at: "2026-10-01T10:00:00Z",
      },
      {
        id: "LR-2026-100",
        employee_id: "9d6bcc63-5acf-471e-afac-18d4b7386ee6",
        employee_name: "Alex Morgan",
        employee_email: "employee@vertexerp.com",
        leave_type_id: "lt-cl",
        leave_type_code: "CL",
        leave_type_name: "Casual Leave",
        start_date: "2026-11-18",
        end_date: "2026-11-18",
        total_days: 1.0,
        reason: "Personal family appointment",
        status: "APPROVED",
        approver_name: "Eleanor Vance (HR Manager)",
        approved_at: "2026-11-16T09:00:00Z",
        remarks: "Approved.",
        created_at: "2026-11-15T11:20:00Z",
      },
    ],
    otherApprovals: [
      {
        id: "reg_201",
        entity_type: "REGULARIZATION",
        entity_id: "reg-201",
        requester_name: "Alex Morgan",
        requester_email: "employee@vertexerp.com",
        title: "Attendance Regularization Request",
        summary: "Nov 22 punch out correction to 18:15 (client deployment call ran late)",
        status: "PENDING",
        priority: "MEDIUM",
        created_at: "2026-11-23T10:15:00Z",
        details: { work_date: "2026-11-22", requested_check_out: "18:15", reason: "Deployment bridge" },
      },
      {
        id: "quote_301",
        entity_type: "QUOTATION",
        entity_id: "quote-301",
        requester_name: "Marcus Sterling (Sales)",
        requester_email: "sales@vertexerp.com",
        title: "Quote Approval: QT-2026-089 (Quantum BioPharma)",
        summary: "Enterprise 100-Seat Cloud + 4x Titan AI Cluster proposal ($185,000.00)",
        amount: 185000.0,
        currency: "USD",
        status: "PENDING_APPROVAL",
        priority: "HIGH",
        created_at: "2026-11-24T16:40:00Z",
        details: { customer: "Quantum BioPharma Labs", discount_pct: "6%" },
      },
    ],
    notifications: [
      {
        id: "notif-1",
        title: "Leave Approval Required",
        message: "Alex Morgan applied for 2.0 days Casual Leave (Dec 03 - Dec 04).",
        type: "ACTION_REQUIRED",
        createdAt: "2026-11-25T08:30:00Z",
        isRead: false,
        link: "/approvals",
        targetRole: "MANAGER",
      },
      {
        id: "notif-2",
        title: "Quote Sign-Off Needed",
        message: "QT-2026-089 ($185,000) submitted by Sales awaits commercial sign-off.",
        type: "WARNING",
        createdAt: "2026-11-24T16:40:00Z",
        isRead: false,
        link: "/approvals",
        targetRole: "MANAGER",
      },
      {
        id: "notif-3",
        title: "November Payroll Processed",
        message: "Monthly payroll batch PR-2026-11 completed with 100% compliance.",
        type: "SUCCESS",
        createdAt: "2026-11-24T09:00:00Z",
        isRead: true,
        link: "/hr/payroll",
        targetRole: "ALL",
      },
    ],
  };
}

class DemoStoreManager {
  private listeners = new Set<() => void>();

  getState(): DemoState {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        const initial = createInitialDemoState();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
        return initial;
      }
      return JSON.parse(raw) as DemoState;
    } catch {
      return createInitialDemoState();
    }
  }

  private setState(updater: (prev: DemoState) => DemoState): DemoState {
    const next = updater(this.getState());
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // ignore storage quota errors
    }
    this.listeners.forEach((l) => l());
    return next;
  }

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) listener();
    };
    if (typeof window !== "undefined") {
      window.addEventListener("storage", onStorage);
    }
    return () => {
      this.listeners.delete(listener);
      if (typeof window !== "undefined") {
        window.removeEventListener("storage", onStorage);
      }
    };
  }

  // ---- Organization Mutations ----
  createBranch(data: Partial<Branch>): Branch {
    const item: Branch = {
      id: `br-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      code: data.code || "BR-NEW",
      name: data.name || "New Branch",
      address_line1: data.address_line1 || "100 Enterprise Way",
      city: data.city || "New York",
      state: data.state || "NY",
      postal_code: data.postal_code || "10001",
      country: data.country || "USA",
      phone: data.phone || null,
      email: data.email || null,
      is_headquarters: !!data.is_headquarters,
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, branches: [item, ...s.branches] }));
    return item;
  }

  deleteBranch(id: string) {
    this.setState((s) => ({ ...s, branches: s.branches.filter((b) => b.id !== id) }));
  }

  createDepartment(data: Partial<Department>): Department {
    const item: Department = {
      id: `dept-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      parent_department_id: data.parent_department_id || null,
      code: data.code || "DEPT-NEW",
      name: data.name || "New Department",
      description: data.description || null,
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, departments: [...s.departments, item] }));
    return item;
  }

  deleteDepartment(id: string) {
    this.setState((s) => ({ ...s, departments: s.departments.filter((d) => d.id !== id) }));
  }

  getDepartmentTree(depts?: Department[]): DepartmentTreeNode[] {
    const list = depts || this.getState().departments;
    const nodeMap = new Map<string, DepartmentTreeNode>();
    list.forEach((d) => nodeMap.set(d.id, { ...d, children: [] }));
    const roots: DepartmentTreeNode[] = [];
    list.forEach((d) => {
      const node = nodeMap.get(d.id)!;
      if (d.parent_department_id && nodeMap.has(d.parent_department_id)) {
        nodeMap.get(d.parent_department_id)!.children.push(node);
      } else {
        roots.push(node);
      }
    });
    return roots;
  }

  createTeam(data: Partial<Team>): Team {
    const item: Team = {
      id: `team-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      department_id: data.department_id || null,
      code: data.code || "TEAM-NEW",
      name: data.name || "New Squad",
      description: data.description || null,
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, teams: [...s.teams, item] }));
    return item;
  }

  deleteTeam(id: string) {
    this.setState((s) => ({ ...s, teams: s.teams.filter((t) => t.id !== id) }));
  }

  addTeamMember(teamId: string, userId: string, role: string): TeamMember {
    const member: TeamMember = {
      id: `tm-${Date.now()}`,
      tenant_id: TENANT_ID,
      team_id: teamId,
      user_id: userId,
      role,
      joined_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    };
    this.setState((s) => ({
      ...s,
      teamMembers: {
        ...s.teamMembers,
        [teamId]: [...(s.teamMembers[teamId] || []), member],
      },
    }));
    return member;
  }

  createDesignation(data: Partial<Designation>): Designation {
    const item: Designation = {
      id: `des-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      code: data.code || "ROLE",
      name: data.name || "New Role",
      description: data.description || null,
      level: Number(data.level || 1),
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, designations: [...s.designations, item] }));
    return item;
  }

  deleteDesignation(id: string) {
    this.setState((s) => ({ ...s, designations: s.designations.filter((d) => d.id !== id) }));
  }

  createBusinessUnit(data: Partial<BusinessUnit>): BusinessUnit {
    const item: BusinessUnit = {
      id: `bu-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      code: data.code || "SBU-NEW",
      name: data.name || "New Business Unit",
      description: data.description || null,
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, businessUnits: [...s.businessUnits, item] }));
    return item;
  }

  deleteBusinessUnit(id: string) {
    this.setState((s) => ({ ...s, businessUnits: s.businessUnits.filter((b) => b.id !== id) }));
  }

  createCostCenter(data: Partial<CostCenter>): CostCenter {
    const item: CostCenter = {
      id: `cc-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      department_id: data.department_id || null,
      code: data.code || "CC-NEW",
      name: data.name || "New Cost Center",
      description: data.description || null,
      annual_budget: Number(data.annual_budget || 0),
      currency: data.currency || "USD",
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, costCenters: [...s.costCenters, item] }));
    return item;
  }

  deleteCostCenter(id: string) {
    this.setState((s) => ({ ...s, costCenters: s.costCenters.filter((c) => c.id !== id) }));
  }

  createLocation(data: Partial<Location>): Location {
    const item: Location = {
      id: `loc-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      branch_id: data.branch_id || null,
      code: data.code || "LOC-NEW",
      name: data.name || "New Location",
      location_type: data.location_type || "OFFICE",
      address_line1: data.address_line1 || "100 Corporate Blvd",
      city: data.city || "New York",
      state: data.state || "NY",
      postal_code: data.postal_code || "10001",
      country: data.country || "USA",
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, locations: [...s.locations, item] }));
    return item;
  }

  deleteLocation(id: string) {
    this.setState((s) => ({ ...s, locations: s.locations.filter((l) => l.id !== id) }));
  }

  createCalendar(data: Partial<WorkCalendar>): WorkCalendar {
    const calId = `cal-${Date.now()}`;
    const item: WorkCalendar = {
      id: calId,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      code: data.code || "CAL-NEW",
      name: data.name || "Custom Work Schedule",
      description: data.description || null,
      time_zone: data.time_zone || "America/New_York",
      is_default: !!data.is_default,
      standard_hours_per_day: Number(data.standard_hours_per_day || 8),
      is_active: data.is_active ?? true,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      working_days: data.working_days || buildWorkingDays(calId, "09:00", "17:30", false),
    };
    this.setState((s) => ({ ...s, calendars: [...s.calendars, item] }));
    return item;
  }

  deleteCalendar(id: string) {
    this.setState((s) => ({ ...s, calendars: s.calendars.filter((c) => c.id !== id) }));
  }

  createHoliday(data: Partial<Holiday>): Holiday {
    const item: Holiday = {
      id: `hol-${Date.now()}`,
      tenant_id: TENANT_ID,
      organization_id: ORG_ID,
      calendar_id: data.calendar_id || "cal-1",
      branch_id: data.branch_id || null,
      name: data.name || "New Holiday",
      holiday_date: data.holiday_date || "2026-12-31",
      holiday_type: data.holiday_type || "NATIONAL",
      is_recurring: !!data.is_recurring,
      description: data.description || null,
      version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.setState((s) => ({ ...s, holidays: [...s.holidays, item] }));
    return item;
  }

  deleteHoliday(id: string) {
    this.setState((s) => ({ ...s, holidays: s.holidays.filter((h) => h.id !== id) }));
  }

  // ---- Employee Apply Leave -> Manager Approve Leave Flow ----
  applyLeave(input: {
    employeeId: string;
    employeeName: string;
    employeeEmail: string;
    leaveTypeCode: string;
    startDate: string;
    endDate: string;
    totalDays: number;
    reason: string;
    overrideId?: string;
  }): DemoLeaveRequest {
    const state = this.getState();
    const bal = state.leaveBalances.find(
      (b) => b.code === input.leaveTypeCode || b.id === input.leaveTypeCode
    );
    const req: DemoLeaveRequest = {
      id: input.overrideId || `LR-${new Date().getFullYear()}-${Math.floor(200 + Math.random() * 800)}`,
      employee_id: input.employeeId,
      employee_name: input.employeeName || "Alex Morgan",
      employee_email: input.employeeEmail || "employee@vertexerp.com",
      leave_type_id: bal?.id || "lt-cl",
      leave_type_code: bal?.code || input.leaveTypeCode,
      leave_type_name: bal?.name || "Casual Leave",
      start_date: input.startDate,
      end_date: input.endDate,
      total_days: input.totalDays,
      reason: input.reason,
      status: "SUBMITTED",
      created_at: new Date().toISOString(),
    };

    const notif: DemoNotification = {
      id: `notif-${Date.now()}`,
      title: "New Leave Request Submitted",
      message: `${req.employee_name} requested ${req.total_days} day(s) of ${req.leave_type_name} (${req.start_date} to ${req.end_date}).`,
      type: "ACTION_REQUIRED",
      createdAt: new Date().toISOString(),
      isRead: false,
      link: "/approvals",
      targetRole: "MANAGER",
    };

    this.setState((s) => ({
      ...s,
      leaveRequests: [req, ...s.leaveRequests.filter((r) => r.id !== req.id)],
      leaveBalances: s.leaveBalances.map((b) =>
        b.code === req.leave_type_code || b.id === req.leave_type_id
          ? { ...b, pending: Number((b.pending + req.total_days).toFixed(1)) }
          : b
      ),
      notifications: [notif, ...s.notifications],
    }));

    return req;
  }

  reviewLeave(input: {
    requestId: string;
    action: "APPROVE" | "REJECT" | "RETURN";
    reviewerName: string;
    remarks?: string;
  }): DemoLeaveRequest | null {
    const newStatus =
      input.action === "APPROVE"
        ? "APPROVED"
        : input.action === "REJECT"
        ? "REJECTED"
        : "RETURNED";

    let updatedReq: DemoLeaveRequest | null = null;
    this.setState((s) => {
      const target = s.leaveRequests.find((r) => r.id === input.requestId);
      if (!target) return s;

      const wasPending = target.status === "SUBMITTED" || target.status === "PENDING";
      updatedReq = {
        ...target,
        status: newStatus,
        approver_name: input.reviewerName,
        approved_at: new Date().toISOString(),
        remarks:
          input.remarks ||
          (newStatus === "APPROVED"
            ? "Approved by Manager."
            : newStatus === "REJECTED"
            ? "Declined due to scheduling conflict."
            : "Returned for additional details."),
      };

      const nextBalances = wasPending
        ? s.leaveBalances.map((b) => {
            if (b.code !== target.leave_type_code && b.id !== target.leave_type_id) return b;
            const nextPending = Math.max(0, Number((b.pending - target.total_days).toFixed(1)));
            if (newStatus === "APPROVED") {
              return {
                ...b,
                pending: nextPending,
                used: Number((b.used + target.total_days).toFixed(1)),
                balance: Math.max(0, Number((b.balance - target.total_days).toFixed(1))),
              };
            }
            return { ...b, pending: nextPending };
          })
        : s.leaveBalances;

      const notif: DemoNotification = {
        id: `notif-${Date.now()}`,
        title: `Leave Request ${newStatus}`,
        message: `${target.employee_name}'s ${target.leave_type_name} (${target.total_days}d) was ${newStatus.toLowerCase()} by ${input.reviewerName}.`,
        type: newStatus === "APPROVED" ? "SUCCESS" : newStatus === "REJECTED" ? "WARNING" : "INFO",
        createdAt: new Date().toISOString(),
        isRead: false,
        link: "/ess/leave",
        targetRole: "ALL",
      };

      return {
        ...s,
        leaveRequests: s.leaveRequests.map((r) => (r.id === input.requestId ? updatedReq! : r)),
        leaveBalances: nextBalances,
        notifications: [notif, ...s.notifications],
      };
    });
    return updatedReq;
  }

  reviewOtherApproval(id: string, action: "APPROVE" | "REJECT" | "RETURN") {
    const newStatus =
      action === "APPROVE" ? "APPROVED" : action === "REJECT" ? "REJECTED" : "RETURNED";
    this.setState((s) => ({
      ...s,
      otherApprovals: s.otherApprovals.map((o) =>
        o.entity_id === id || o.id === id ? { ...o, status: newStatus } : o
      ),
    }));
  }

  markNotificationRead(id: string) {
    this.setState((s) => ({
      ...s,
      notifications: s.notifications.map((n) => (n.id === id ? { ...n, isRead: true } : n)),
    }));
  }

  markAllNotificationsRead() {
    this.setState((s) => ({
      ...s,
      notifications: s.notifications.map((n) => ({ ...n, isRead: true })),
    }));
  }
}

export const demoStore = new DemoStoreManager();

export function useDemoStore(): DemoState {
  const [state, setState] = useState<DemoState>(() => demoStore.getState());
  useEffect(() => {
    setState(demoStore.getState());
    return demoStore.subscribe(() => {
      setState(demoStore.getState());
    });
  }, []);
  return state;
}
