/**
 * Vercel Serverless Function: Catch-all fallback for /api/*
 * Prevents 404/405/500 errors on static/serverless Vercel frontend deployments.
 */
export default async function handler(req: any, res: any) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  return res.status(200).json({
    status: "ok",
    items: [],
    total: 0,
    page: 1,
    page_size: 50,
  });
}
