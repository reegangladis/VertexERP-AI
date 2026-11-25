/**
 * Vercel Serverless Function: Unified API Router for /api/v1/*
 * Serves pre-seeded Organization, HR Leave, Workflow Approvals, CRM, and Analytics
 * payloads cleanly on Vercel deployments while tagging responses with X-Vertex-Demo: serverless.
 */

const TENANT_ID = "c7d4bb7c-8186-451c-80ca-c538e9d5afa0";
const ORG_ID = "9d8d79b7-e22b-4d9e-9130-3feeef872937";
const NOW = "2026-11-24T09:00:00Z";

function buildWorkingDays(calId: string, start: string, end: string, includeSat = false) {
  return [0, 1, 2, 3, 4, 5, 6].map((dow) => {
    const isWork = dow < 5 || (includeSat && dow === 5);
    return {
      id: `wd-${calId}-${dow}`,
      tenant_id: TENANT_ID,
      calendar_id: calId,
      day_of_week: dow,
      is_working_day: isWork,
      start_time: isWork ? (dow === 5 && includeSat ? "09:00" : start) : null,
      end_time: isWork ? (dow === 5 && includeSat ? "13:00" : end) : null,
      created_at: NOW,
    };
  });
}

const BRANCHES = [
  { id: "br-nyc-01", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "BR-NYC", name: "New York Global HQ", address_line1: "One World Trade Center, Suite 8500", city: "New York", state: "NY", postal_code: "10007", country: "USA", phone: "+1 (212) 555-0100", email: "nyc@vertexerp.com", is_headquarters: true, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "br-sfo-02", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "BR-SFO", name: "San Francisco AI Hub", address_line1: "500 Howard Street, Suite 400", city: "San Francisco", state: "CA", postal_code: "94105", country: "USA", phone: "+1 (415) 555-0199", email: "sfo@vertexerp.com", is_headquarters: false, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "br-aus-03", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "BR-AUS", name: "Austin Hardware & Systems Lab", address_line1: "401 Congress Ave, Floor 18", city: "Austin", state: "TX", postal_code: "78701", country: "USA", phone: "+1 (512) 555-0142", email: "austin@vertexerp.com", is_headquarters: false, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "br-ldn-04", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "BR-LDN", name: "London EMEA Hub", address_line1: "25 Bank Street, Canary Wharf", city: "London", state: "England", postal_code: "E14 5JP", country: "GBR", phone: "+44 20 7946 0910", email: "london@vertexerp.com", is_headquarters: false, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "br-sgp-05", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "BR-SGP", name: "Singapore APAC Center", address_line1: "10 Collyer Quay, Ocean Financial Centre", city: "Singapore", state: "Central", postal_code: "049315", country: "SGP", phone: "+65 6789 0123", email: "apac@vertexerp.com", is_headquarters: false, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const DEPARTMENTS = [
  { id: "dept-eng-01", tenant_id: TENANT_ID, organization_id: ORG_ID, parent_department_id: null, code: "ENGI", name: "Engineering & Technology", description: "Core platform architecture, AI research, and cloud systems", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "dept-ai-02", tenant_id: TENANT_ID, organization_id: ORG_ID, parent_department_id: "dept-eng-01", code: "AI-CORE", name: "Applied AI & Copilot Labs", description: "LLM orchestration, RAG engines, and predictive ML models", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "dept-sre-03", tenant_id: TENANT_ID, organization_id: ORG_ID, parent_department_id: "dept-eng-01", code: "PLAT-SRE", name: "Cloud Platform & SRE", description: "Global cloud reliability, multi-region clusters, and security", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "dept-sales-04", tenant_id: TENANT_ID, organization_id: ORG_ID, parent_department_id: null, code: "SALE", name: "Sales & Commercial", description: "Global enterprise sales, solutions engineering, and revenue ops", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "dept-hr-05", tenant_id: TENANT_ID, organization_id: ORG_ID, parent_department_id: null, code: "PEOP", name: "People Operations", description: "Talent acquisition, HR governance, compensation, and culture", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "dept-fin-06", tenant_id: TENANT_ID, organization_id: ORG_ID, parent_department_id: null, code: "FINA", name: "Finance & Corporate", description: "Treasury, FP&A, accounting governance, and audit compliance", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const TEAMS = [
  { id: "team-ai-01", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-ai-02", code: "TEAM-AI", name: "Core AI Intelligence Squad", description: "Generative AI Copilot & RAG retrieval engineering squad", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "team-plat-02", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-sre-03", code: "TEAM-PLAT", name: "Platform Architecture Pod", description: "High-throughput API & distributed ledger core systems", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "team-ent-03", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-sales-04", code: "TEAM-ENT", name: "Enterprise GTM Pod", description: "Fortune 500 strategic account executives & solutions engineers", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "team-hr-04", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-hr-05", code: "TEAM-HR", name: "People & Talent Partners", description: "Employee experience, leave governance & global onboarding", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "team-fin-05", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-fin-06", code: "TEAM-FIN", name: "Treasury & FP&A Desk", description: "General ledger automation & financial forecasting pod", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const DESIGNATIONS = [
  { id: "des-1", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "VP-ENG", name: "VP of Cloud Engineering", description: "Executive engineering leadership and reliability governance", level: 9, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-2", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "PRIN-ARCH", name: "Principal AI Architect", description: "Cross-domain enterprise architecture & LLM safety", level: 8, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-3", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "DIR-SALES", name: "Enterprise Sales Director", description: "Commercial bookings and regional revenue pipelines", level: 7, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-4", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "MGR-HR", name: "People Operations Manager", description: "HR governance, leave approval, and payroll compliance", level: 6, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-5", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "FIN-CTRL", name: "Financial Controller", description: "GAAP close, multi-currency reconciliation & audit readiness", level: 6, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-6", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SWE-SR", name: "Senior Full-Stack Engineer", description: "Core frontend & backend ERP product engineering", level: 4, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-7", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "AE-SR", name: "Senior Enterprise AE", description: "Full-cycle enterprise account acquisition", level: 4, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "des-8", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "HR-BP", name: "HR Business Partner", description: "Workforce planning & departmental coaching", level: 5, is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const BUSINESS_UNITS = [
  { id: "bu-1", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-CLOUD", name: "Vertex Cloud ERP Suite", description: "Flagship multi-tenant SaaS ERP & Copilot division", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "bu-2", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-HW", name: "Quantum Edge & AI Systems", description: "Enterprise GPU clusters and industrial IoT hardware", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "bu-3", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-ADV", name: "Global Advisory & Enterprise Ops", description: "Dedicated implementation & managed cloud services", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "bu-4", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "SBU-FIN", name: "Vertex Pay & Embedded Treasury", description: "Automated B2B invoicing, settlement, and ledger ops", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const COST_CENTERS = [
  { id: "cc-1", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-eng-01", code: "CC-AI-RD", name: "AI Research & Cloud Engineering", description: "Compute GPUs, LLM inference, and R&D talent", annual_budget: 1450000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "cc-2", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-sales-04", code: "CC-GTM", name: "Global Sales & Marketing GTM", description: "Enterprise pipeline, events, and partner commissions", annual_budget: 840000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "cc-3", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-hr-05", code: "CC-PEOPLE", name: "People Ops, Wellness & L&D", description: "Recruiting, training academies, and benefits", annual_budget: 420000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "cc-4", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-fin-06", code: "CC-FINOPS", name: "Finance, Audit & Compliance", description: "SOC2 audits, treasury operations, and legal", annual_budget: 310000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "cc-5", tenant_id: TENANT_ID, organization_id: ORG_ID, department_id: "dept-sre-03", code: "CC-INFRA", name: "Cloud Infrastructure & SRE", description: "Multi-region hosting, observability, and security", annual_budget: 680000, currency: "USD", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const LOCATIONS = [
  { id: "loc-1", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-nyc-01", code: "LOC-NYC-HQ", name: "One WTC Executive Suite", location_type: "OFFICE", address_line1: "One World Trade Center, Suite 8500", city: "New York", state: "NY", postal_code: "10007", country: "USA", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "loc-2", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-nyc-01", code: "LOC-JFK-WH", name: "East Coast Distribution Hub", location_type: "WAREHOUSE", address_line1: "145 Cargo Service Rd, Bldg 75", city: "Jamaica", state: "NY", postal_code: "11430", country: "USA", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "loc-3", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-aus-03", code: "LOC-AUS-FAB", name: "Austin Cleanroom Assembly Plant", location_type: "PLANT", address_line1: "401 Congress Ave, Tech Park B", city: "Austin", state: "TX", postal_code: "78701", country: "USA", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "loc-4", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-ldn-04", code: "LOC-LDN-OFC", name: "Canary Wharf EMEA Office", location_type: "OFFICE", address_line1: "25 Bank Street, Level 19", city: "London", state: "England", postal_code: "E14 5JP", country: "GBR", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
  { id: "loc-5", tenant_id: TENANT_ID, organization_id: ORG_ID, branch_id: "br-sgp-05", code: "LOC-SGP-DC", name: "Singapore Tier-IV Edge Data Center", location_type: "WAREHOUSE", address_line1: "10 Collyer Quay, Tower 2", city: "Singapore", state: "Central", postal_code: "049315", country: "SGP", is_active: true, version: 1, created_at: NOW, updated_at: NOW },
];

const CALENDARS = [
  { id: "cal-1", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "CAL-US-EST", name: "US Eastern Standard (40h)", description: "Standard Monday-Friday corporate operating hours", time_zone: "America/New_York", is_default: true, standard_hours_per_day: 8, is_active: true, version: 1, created_at: NOW, updated_at: NOW, working_days: buildWorkingDays("cal-1", "09:00", "17:30", false) },
  { id: "cal-2", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "CAL-EMEA-LON", name: "EMEA London Schedule (37.5h)", description: "UK & European headquarters operating schedule", time_zone: "Europe/London", is_default: false, standard_hours_per_day: 7.5, is_active: true, version: 1, created_at: NOW, updated_at: NOW, working_days: buildWorkingDays("cal-2", "08:30", "16:30", false) },
  { id: "cal-3", tenant_id: TENANT_ID, organization_id: ORG_ID, code: "CAL-APAC-24X7", name: "APAC Cloud & SRE Operations", description: "Follow-the-Sun SRE & Manufacturing floor rotation", time_zone: "Asia/Singapore", is_default: false, standard_hours_per_day: 8, is_active: true, version: 1, created_at: NOW, updated_at: NOW, working_days: buildWorkingDays("cal-3", "08:00", "16:00", true) },
];

const HOLIDAYS = [
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
];

export default async function handler(req: any, res: any) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");
  res.setHeader("X-Vertex-Demo", "serverless");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const routeParam = req.query?.route;
  const rawRoute = Array.isArray(routeParam) ? routeParam.join("/") : String(routeParam || "");
  const url = rawRoute ? `/${rawRoute.replace(/^\/+/, "")}` : (req.url || "").split("?")[0];

  if (req.method === "POST" || req.method === "PUT" || req.method === "PATCH" || req.method === "DELETE") {
    let body = req.body;
    if (typeof body === "string") {
      try { body = JSON.parse(body); } catch { body = {}; }
    }
    return res.status(req.method === "POST" ? 201 : 200).json({
      success: true,
      id: `demo-${Date.now()}`,
      ...(typeof body === "object" && body !== null ? body : {}),
    });
  }

  if (url.includes("/branches")) return res.status(200).json(BRANCHES);
  if (url.includes("/departments/tree")) {
    return res.status(200).json([
      {
        ...DEPARTMENTS[0],
        children: [
          { ...DEPARTMENTS[1], children: [] },
          { ...DEPARTMENTS[2], children: [] },
        ],
      },
      { ...DEPARTMENTS[3], children: [] },
      { ...DEPARTMENTS[4], children: [] },
      { ...DEPARTMENTS[5], children: [] },
    ]);
  }
  if (url.includes("/departments")) return res.status(200).json(DEPARTMENTS);
  if (url.includes("/teams") && url.includes("/members")) {
    return res.status(200).json([
      { id: "tm-1", tenant_id: TENANT_ID, team_id: "team-ai-01", user_id: "Alex Morgan (Member)", role: "MEMBER", joined_at: NOW, created_at: NOW },
      { id: "tm-2", tenant_id: TENANT_ID, team_id: "team-ai-01", user_id: "Eleanor Vance (Lead)", role: "LEAD", joined_at: NOW, created_at: NOW },
    ]);
  }
  if (url.includes("/teams")) return res.status(200).json(TEAMS);
  if (url.includes("/designations")) return res.status(200).json(DESIGNATIONS);
  if (url.includes("/business-units")) return res.status(200).json(BUSINESS_UNITS);
  if (url.includes("/cost-centers")) return res.status(200).json(COST_CENTERS);
  if (url.includes("/locations")) return res.status(200).json(LOCATIONS);
  if (url.includes("/calendars/")) {
    const calId = url.split("/calendars/")[1]?.replace(/\//g, "");
    if (calId) {
      return res.status(200).json(CALENDARS.find((c) => c.id === calId) || CALENDARS[0]);
    }
    return res.status(200).json(CALENDARS);
  }
  if (url.includes("/calendars")) return res.status(200).json(CALENDARS);
  if (url.includes("/holidays")) return res.status(200).json(HOLIDAYS);

  if (url.includes("/hr/leaves/types")) {
    return res.status(200).json([
      { id: "lt-cl", code: "CL", name: "Casual Leave", is_paid: true, is_encashable: false, max_consecutive_days: 10, color_code: "#f97316", is_active: true },
      { id: "lt-sl", code: "SL", name: "Sick & Medical Leave", is_paid: true, is_encashable: false, max_consecutive_days: 15, color_code: "#10b981", is_active: true },
      { id: "lt-el", code: "EL", name: "Earned / Privilege Leave", is_paid: true, is_encashable: true, max_consecutive_days: 30, color_code: "#f59e0b", is_active: true },
    ]);
  }
  if (url.includes("/hr/employees")) {
    return res.status(200).json([
      { id: "9d6bcc63-5acf-471e-afac-18d4b7386ee6", employee_number: "EMP-001", first_name: "Alex", last_name: "Morgan", email: "employee@vertexerp.com", employment_status: "ACTIVE", hire_date: "2024-01-15", is_active: true },
      { id: "edf566e6-dc96-4e92-bf12-8f22008e31db", employee_number: "EMP-002", first_name: "Marcus", last_name: "Sterling", email: "sales@vertexerp.com", employment_status: "ACTIVE", hire_date: "2024-01-15", is_active: true },
      { id: "8d75646b-c665-4fe2-9165-e67fe942951e", employee_number: "EMP-003", first_name: "Eleanor", last_name: "Vance", email: "hr@vertexerp.com", employment_status: "ACTIVE", hire_date: "2024-01-15", is_active: true },
    ]);
  }
  if (url.includes("/hr/leaves/requests") || url.includes("/workflows/inbox")) {
    return res.status(200).json([]);
  }
  if (url.includes("/workflows/stats")) {
    return res.status(200).json({ pending_total: 3, pending_leaves: 1, pending_regularizations: 1, pending_quotations: 1, approved_this_month: 8, rejected_this_month: 0 });
  }

  return res.status(200).json({
    status: "ok",
    items: [],
    total: 0,
    page: 1,
    page_size: 50,
  });
}
