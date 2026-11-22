import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("Frontend Vite Configuration Security & Proxy", () => {
  const configPath = path.resolve(__dirname, "../../vite.config.ts");
  const content = fs.readFileSync(configPath, "utf-8");

  it("defines explicit allowedHosts for local development without wildcards", () => {
    // Verify allowedHosts includes localhost and 127.0.0.1
    expect(content).toMatch(/allowedHosts:\s*\[[^\]]*"localhost"[^\]]*\]/);
    expect(content).toMatch(/allowedHosts:\s*\[[^\]]*"127\.0\.0\.1"[^\]]*\]/);

    // Verify it is not a wildcard or boolean true
    expect(content).not.toContain("allowedHosts: true");
    expect(content).not.toMatch(/allowedHosts:\s*\[[^\]]*"\*"[^\]]*\]/);
  });

  it("configures port 3000 for development server", () => {
    expect(content).toMatch(/port:\s*3000/);
  });

  it("configures /api proxy with changeOrigin disabled to preserve client Host header", () => {
    expect(content).toContain('"/api"');
    expect(content).toMatch(/changeOrigin:\s*false/);
    expect(content).not.toMatch(/changeOrigin:\s*true/);
  });

  it("preserves VITE_API_TARGET fallback configuration", () => {
    expect(content).toContain('process.env.VITE_API_TARGET || "http://127.0.0.1:8000"');
  });
});
