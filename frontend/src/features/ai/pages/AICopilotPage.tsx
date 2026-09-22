/**
 * AI Copilot SPA Page
 * VertexERP AI V2
 * 
 * Features:
 * - Conversation management (threads, pinning, archiving)
 * - Multi-turn conversation feed with tool execution inspection
 * - Human-in-the-loop Pending Action Proposal workflow (Approve / Reject)
 * - Quick prompt action chips (Stock check, Invoices, HR headcount, Vendor bill drafting)
 * - Provider & Model indicators with real-time token and cost telemetry
 */

import React, { useEffect, useRef, useState } from "react";
import {
  Bot,
  Send,
  Plus,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Cpu,
  Clock,
  Coins,
  ShieldCheck,
  ChevronRight,
  Database,
  Sparkles,
  RefreshCw,
  Sliders,
  Terminal,
} from "lucide-react";
import { aiApi } from "../api/aiApi";
import {
  AIConversation,
  AIMessage,
  ConfirmActionRequest,
  CopilotChatResponse,
  PendingActionProposal,
} from "../types";

export const AICopilotPage: React.FC = () => {
  // State
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState<PendingActionProposal | null>(null);
  const [activeProvider, setActiveProvider] = useState("mock");
  const [activeModel, setActiveModel] = useState("mock-gpt-4o");
  const [actionConfirming, setActionConfirming] = useState(false);
  const [actionResult, setActionResult] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Quick suggestions
  const quickPrompts = [
    { label: "📦 Check Product Stock", prompt: "Check stock level and availability for SKU-ROBOT-01" },
    { label: "💰 Invoices & Receivables", prompt: "Give me a summary of open customer invoices and total receivables" },
    { label: "👥 Department Headcount", prompt: "What is our current active headcount broken down by department?" },
    { label: "📝 Draft Vendor Bill", prompt: "Draft a vendor bill of $5,400 for Chipsets Intel Fab" },
    { label: "🤝 Create Deal", prompt: "Create a deal opportunity for Global Tech Solutions worth $45,000" },
  ];

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load messages when active conversation changes
  useEffect(() => {
    if (activeConversationId) {
      loadMessages(activeConversationId);
    } else {
      setMessages([]);
      setPendingAction(null);
    }
  }, [activeConversationId]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [messages, isLoading, pendingAction]);

  const loadConversations = async () => {
    try {
      const res = await aiApi.listConversations();
      setConversations(res.items);
      if (res.items.length > 0 && !activeConversationId) {
        setActiveConversationId(res.items[0].id);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadMessages = async (convId: string) => {
    try {
      const res = await aiApi.getConversationMessages(convId);
      setMessages(res.items);
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  };

  const handleCreateNewChat = async () => {
    try {
      const newConv = await aiApi.createConversation("New Copilot Thread");
      setConversations([newConv, ...conversations]);
      setActiveConversationId(newConv.id);
      setMessages([]);
      setPendingAction(null);
      setActionResult(null);
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await aiApi.deleteConversation(convId);
      const remaining = conversations.filter((c) => c.id !== convId);
      setConversations(remaining);
      if (activeConversationId === convId) {
        setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    setInputMessage("");
    setActionResult(null);

    // Optimistically add user message
    const tempUserMsg: AIMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId || "temp",
      role: "user",
      content: text,
      prompt_tokens: 0,
      completion_tokens: 0,
      total_tokens: 0,
      cost_usd: 0,
      is_error: false,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const response: CopilotChatResponse = await aiApi.sendChatMessage({
        conversation_id: activeConversationId || undefined,
        message: text,
        provider: activeProvider,
        model: activeModel,
        tools_enabled: true,
      });

      if (!activeConversationId) {
        setActiveConversationId(response.conversation_id);
        loadConversations();
      }

      // Add assistant reply
      const assistantMsg: AIMessage = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: "assistant",
        content: response.content,
        tool_calls: response.tool_calls,
        prompt_tokens: response.usage.prompt_tokens,
        completion_tokens: response.usage.completion_tokens,
        total_tokens: response.usage.total_tokens,
        cost_usd: response.cost_usd,
        latency_ms: response.latency_ms,
        is_error: false,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // If pending proposal returned, surface confirmation card
      if (response.pending_action) {
        setPendingAction(response.pending_action);
      } else {
        setPendingAction(null);
      }
    } catch (err: any) {
      const errorMsg: AIMessage = {
        id: `err-${Date.now()}`,
        conversation_id: activeConversationId || "temp",
        role: "assistant",
        content: `Error: ${err.message || "Failed to communicate with AI Copilot."}`,
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0,
        cost_usd: 0,
        is_error: true,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmAction = async (confirmed: boolean) => {
    if (!pendingAction) return;

    setActionConfirming(true);
    try {
      const payload: ConfirmActionRequest = {
        action_id: pendingAction.action_id,
        confirmation_token: pendingAction.confirmation_token,
        confirmed,
      };
      const res = await aiApi.confirmAction(payload);
      setPendingAction(null);

      if (confirmed && res.status === "executed") {
        setActionResult(`Action Executed Successfully: ${res.tool_name}`);
        // Add system/tool response message to thread
        const confMsg: AIMessage = {
          id: `conf-${Date.now()}`,
          conversation_id: activeConversationId || "",
          role: "assistant",
          content: `✅ **Action Confirmed & Executed:**\n\`\`\`json\n${JSON.stringify(res.result, null, 2)}\n\`\`\``,
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0,
          cost_usd: 0,
          is_error: false,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, confMsg]);
      } else {
        setActionResult(`Action Rejected by User.`);
        const rejMsg: AIMessage = {
          id: `rej-${Date.now()}`,
          conversation_id: activeConversationId || "",
          role: "assistant",
          content: `❌ **Action Rejected:** The proposed operation was cancelled without modifying any ERP records.`,
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0,
          cost_usd: 0,
          is_error: false,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, rejMsg]);
      }
    } catch (err: any) {
      setActionResult(`Action Confirmation Failed: ${err.message}`);
    } finally {
      setActionConfirming(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-slate-950 text-slate-100 antialiased overflow-hidden">
      {/* Sidebar / Conversation Threads */}
      <aside className="w-80 border-r border-slate-800 bg-slate-900/60 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            <span className="font-semibold text-sm tracking-wide text-slate-200">
              Copilot Threads
            </span>
          </div>
          <button
            onClick={handleCreateNewChat}
            className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center space-x-1 text-xs px-2.5 font-medium shadow-sm shadow-indigo-500/20"
            title="New Chat Thread"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New</span>
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">
              No conversations yet. Click "New" to start.
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => setActiveConversationId(conv.id)}
                className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer text-xs transition border ${
                  activeConversationId === conv.id
                    ? "bg-slate-800/90 border-indigo-500/50 text-white font-medium"
                    : "border-transparent text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                }`}
              >
                <div className="truncate flex-1 pr-2">
                  <div className="truncate">{conv.title || "Untitled Conversation"}</div>
                  <div className="text-[10px] text-slate-500 flex items-center space-x-2 mt-0.5">
                    <span>{conv.message_count ?? 0} msgs</span>
                    <span>•</span>
                    <span>${(conv.estimated_cost_usd ?? conv.total_cost ?? 0).toFixed(4)}</span>
                  </div>
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition"
                  title="Archive Thread"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Provider & Model Selectors */}
        <div className="p-3 border-t border-slate-800 bg-slate-900/90 space-y-2">
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center space-x-1">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>AI Provider</span>
            </span>
            <select
              value={activeProvider}
              onChange={(e) => setActiveProvider(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="mock">Mock Gateway (Test)</option>
              <option value="openai">OpenAI (Direct)</option>
              <option value="anthropic">Anthropic Claude</option>
              <option value="gemini">Google Gemini</option>
            </select>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Model</span>
            <input
              type="text"
              value={activeModel}
              onChange={(e) => setActiveModel(e.target.value)}
              placeholder="e.g. mock-gpt-4o"
              className="w-32 bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="flex-1 flex flex-col bg-slate-950">
        {/* Chat Header */}
        <header className="h-14 border-b border-slate-800 px-6 flex items-center justify-between bg-slate-900/40">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <span>Vertex Copilot</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Zero-Trust Active
                </span>
              </h1>
              <p className="text-[11px] text-slate-400">
                ERP Intelligence • Multi-Tenant Isolated • Live Tool Registry Enabled
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs text-slate-400">
            <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Tenant Boundary Enforced</span>
            </div>
          </div>
        </header>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="max-w-2xl mx-auto text-center py-12 space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mx-auto">
                <Bot className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-semibold text-slate-200">
                How can Vertex Copilot assist your operations today?
              </h2>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Ask real-time questions across inventory levels, sales pipelines, financial ledger balances, or draft safe mutations requiring confirmation.
              </p>

              {/* Quick Prompts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-4 text-left">
                {quickPrompts.map((qp, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(qp.prompt)}
                    className="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 text-xs transition space-y-1 text-slate-300 hover:text-white"
                  >
                    <div className="font-medium text-slate-200">{qp.label}</div>
                    <div className="text-[11px] text-slate-400 line-clamp-1">{qp.prompt}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, i) => (
            <div
              key={msg.id || i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-3xl rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/10"
                    : msg.is_error
                    ? "bg-rose-950/40 border border-rose-800/50 text-rose-200 rounded-bl-none"
                    : "bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none shadow-sm"
                }`}
              >
                {/* Header info for assistant */}
                {msg.role === "assistant" && (
                  <div className="flex items-center justify-between text-[10px] text-slate-400 border-b border-slate-800/80 pb-1.5 mb-1.5">
                    <div className="flex items-center space-x-1.5 font-medium text-indigo-400">
                      <Bot className="w-3.5 h-3.5" />
                      <span>Vertex Copilot</span>
                    </div>
                    {msg.latency_ms && (
                      <div className="flex items-center space-x-2">
                        <span>{msg.latency_ms} ms</span>
                        <span>•</span>
                        <span>{msg.total_tokens} tokens</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Content */}
                <div className="whitespace-pre-wrap font-sans text-[13px]">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl rounded-bl-none p-4 flex items-center space-x-2 text-xs text-indigo-400">
                <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                <span>Vertex Copilot is analyzing ERP data and executing tools...</span>
              </div>
            </div>
          )}

          {/* Human-in-the-Loop Action Confirmation Proposal Card */}
          {pendingAction && (
            <div className="max-w-2xl mx-auto rounded-xl border border-amber-500/40 bg-amber-950/20 p-4 space-y-3 shadow-lg shadow-amber-950/30 animate-in fade-in">
              <div className="flex items-center space-x-2 text-amber-400 font-semibold text-xs">
                <AlertTriangle className="w-4 h-4" />
                <span>Action Confirmation Required (Human-in-the-Loop)</span>
              </div>
              <p className="text-xs text-slate-300">{pendingAction.preview_summary}</p>
              <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800 font-mono text-[11px] text-slate-300">
                <div className="text-[10px] text-slate-500 mb-1">
                  TOOL: {pendingAction.tool_name} | ACTION: {pendingAction.action_type}
                </div>
                <pre className="text-[11px] overflow-x-auto text-amber-200">
                  {JSON.stringify(pendingAction.parameters, null, 2)}
                </pre>
              </div>
              <div className="flex items-center justify-end space-x-2.5 pt-1">
                <button
                  disabled={actionConfirming}
                  onClick={() => handleConfirmAction(false)}
                  className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition flex items-center space-x-1"
                >
                  <XCircle className="w-3.5 h-3.5 text-rose-400" />
                  <span>Reject</span>
                </button>
                <button
                  disabled={actionConfirming}
                  onClick={() => handleConfirmAction(true)}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition flex items-center space-x-1 shadow-md shadow-emerald-600/20"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{actionConfirming ? "Executing..." : "Approve & Execute"}</span>
                </button>
              </div>
            </div>
          )}

          {actionResult && (
            <div className="max-w-2xl mx-auto p-2.5 rounded-lg bg-slate-900 border border-indigo-500/30 text-xs text-indigo-300 text-center font-medium">
              {actionResult}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2 max-w-4xl mx-auto"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask Copilot a question or request an ERP task (e.g. check stock for SKU-001)..."
              disabled={isLoading}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition shadow-inner"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white transition shadow-md shadow-indigo-600/20"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};
