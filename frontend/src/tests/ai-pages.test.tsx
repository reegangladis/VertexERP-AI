/**
 * Unit & Integration Tests for AI Copilot & Telemetry Frontend Pages
 * VertexERP AI V2
 */

import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { AICopilotPage, AIKnowledgeBasePage, AIUsageTelemetryPage } from "@/features/ai";
import { aiApi } from "@/features/ai/api/aiApi";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("AI Platform & Copilot Frontend Pages", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders AICopilotPage with sidebar threads and quick prompt suggestions", async () => {
    vi.spyOn(aiApi, "listConversations").mockResolvedValue({
      items: [
        {
          id: "conv-1",
          tenant_id: "tenant-1",
          user_id: "user-1",
          title: "Executive Strategy Session",
          domain_context: "GENERAL",
          model_used: "mock-gpt-4o",
          total_prompt_tokens: 150,
          total_completion_tokens: 80,
          total_cost: 0.002,
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
    });

    vi.spyOn(aiApi, "getConversationMessages").mockResolvedValue({
      items: [
        {
          id: "msg-1",
          conversation_id: "conv-1",
          tenant_id: "tenant-1",
          role: "user",
          content: "What is the stock level for product SKU-ROBOT-01?",
          token_count: 15,
          cost: 0.0,
          created_at: new Date().toISOString(),
        },
        {
          id: "msg-2",
          conversation_id: "conv-1",
          tenant_id: "tenant-1",
          role: "assistant",
          content: "Current stock level for SKU-ROBOT-01 is 42 units.",
          token_count: 25,
          cost: 0.0001,
          latency_ms: 120,
          created_at: new Date().toISOString(),
        },
      ],
      total: 2,
    });

    renderWithProviders(<AICopilotPage />);

    // Header & Brand checks
    expect(screen.getByText("Copilot Threads")).toBeInTheDocument();
    expect(screen.getByText("Vertex Copilot")).toBeInTheDocument();
    expect(screen.getByText("Zero-Trust Active")).toBeInTheDocument();

    // Verify conversation thread and messages appear
    await waitFor(() => {
      expect(screen.getByText("Executive Strategy Session")).toBeInTheDocument();
      expect(screen.getByText("What is the stock level for product SKU-ROBOT-01?")).toBeInTheDocument();
      expect(screen.getByText("Current stock level for SKU-ROBOT-01 is 42 units.")).toBeInTheDocument();
    });
  });

  it("renders AIKnowledgeBasePage with document repository and metrics", async () => {
    vi.spyOn(aiApi, "listDocuments").mockResolvedValue({
      items: [
        {
          id: "doc-1",
          tenant_id: "tenant-1",
          organization_id: "org-1",
          title: "Warehouse Stock Transfer Policy",
          description: "SOP for warehouse transfers",
          file_type: "markdown",
          file_size_bytes: 1450,
          access_level: "INTERNAL",
          allowed_departments: ["Operations"],
          allowed_roles: ["*"],
          tags: ["inventory", "sop"],
          metadata_json: {},
          is_active: true,
          active_version: 1,
          total_chunks: 4,
          latest_job_status: "COMPLETED",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
      skip: 0,
      limit: 50,
    });

    renderWithProviders(<AIKnowledgeBasePage />);

    expect(screen.getByText("Knowledge Base & Production RAG")).toBeInTheDocument();
    expect(screen.getByText("Document Repository")).toBeInTheDocument();
    expect(screen.getByText("RAG QA Console")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Warehouse Stock Transfer Policy")).toBeInTheDocument();
      expect(screen.getByText("SOP for warehouse transfers")).toBeInTheDocument();
      expect(screen.getByText("COMPLETED")).toBeInTheDocument();
    });
  });

  it("renders AIUsageTelemetryPage with metrics, breakdown table, and registered tools", async () => {
    vi.spyOn(aiApi, "getUsageSummary").mockResolvedValue({
      total_calls: 1240,
      total_tokens: 385000,
      total_cost_usd: 1.4852,
      by_provider: [
        {
          provider: "mock",
          model: "mock-gpt-4o",
          total_calls: 1000,
          total_prompt_tokens: 200000,
          total_completion_tokens: 100000,
          total_tokens: 300000,
          total_cost_usd: 0.0,
          avg_latency_ms: 85.4,
          error_rate: 0.0,
        },
        {
          provider: "openai",
          model: "gpt-4o",
          total_calls: 240,
          total_prompt_tokens: 55000,
          total_completion_tokens: 30000,
          total_tokens: 85000,
          total_cost_usd: 1.4852,
          avg_latency_ms: 620.1,
          error_rate: 0.0,
        },
      ],
      by_feature: {},
    });

    vi.spyOn(aiApi, "getAvailableTools").mockResolvedValue({
      count: 2,
      tools: [
        {
          name: "check_product_stock",
          description: "Check product stock across warehouses",
          action_type: "inventory.stock.query",
          is_mutation: false,
          parameters_schema: {},
        },
        {
          name: "create_deal_opportunity",
          description: "Create a new sales deal in CRM",
          action_type: "crm.deal.create",
          is_mutation: true,
          parameters_schema: {},
        },
      ],
    });

    renderWithProviders(<AIUsageTelemetryPage />);

    expect(screen.getByText("AI Platform Telemetry & Observability")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("1,240")).toBeInTheDocument();
      expect(screen.getByText("385,000")).toBeInTheDocument();
      expect(screen.getByText("$1.4852")).toBeInTheDocument();
      expect(screen.getByText("check_product_stock")).toBeInTheDocument();
      expect(screen.getByText("create_deal_opportunity")).toBeInTheDocument();
    });
  });
});
