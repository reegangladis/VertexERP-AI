/**
 * Vercel Serverless Function: POST /api/v1/identity/auth/login
 * Handles authentication for VertexERP AI cloud deployments.
 */
export default async function handler(req: any, res: any) {
  // Handle CORS Preflight
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method Not Allowed" });
  }

  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch {
      body = {};
    }
  }
  body = body || {};

  const email = (body.email || "admin@vertexerp.com").toLowerCase().trim();

  let roles = ["SUPER_ADMIN", "TenantAdmin"];
  let fullName = "Alexander Wright (Super Admin)";

  if (email.includes("employee")) {
    roles = ["EMPLOYEE"];
    fullName = "Jordan Lee (Employee)";
  } else if (email.includes("sales")) {
    roles = ["SALES_MANAGER"];
    fullName = "Sophia Chen (Sales Director)";
  } else if (email.includes("hr")) {
    roles = ["HR_MANAGER"];
    fullName = "Marcus Vance (VP People Ops)";
  } else if (email.includes("reegangladis")) {
    roles = ["SUPER_ADMIN", "TenantAdmin"];
    fullName = "Reegan Gladis (Platform Owner)";
  }

  return res.status(200).json({
    access_token: `vtx_demo_jwt_${Date.now()}_${Math.random().toString(36).substring(7)}`,
    user_id: `usr_${email.replace(/[^a-zA-Z0-9]/g, "_")}`,
    tenant_id: "tenant_apex",
    organization_id: "org_apex_hq",
    full_name: fullName,
    email,
    roles,
    permissions: ["*"],
    mfa_required: false,
  });
}
