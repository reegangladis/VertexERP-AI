/**
 * Vercel Serverless Function: GET /api/v1/identity/auth/me
 * Returns current authenticated identity profile.
 */
export default async function handler(req: any, res: any) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  return res.status(200).json({
    user_id: "usr_admin",
    email: "admin@vertexerp.com",
    full_name: "Alexander Wright (Super Admin)",
    tenant_id: "tenant_apex",
    organization_id: "org_apex_hq",
    roles: ["SUPER_ADMIN", "TenantAdmin"],
    permissions: ["*"],
    is_active: true,
  });
}
