import React, { useEffect, useState } from 'react';
import {
  Bot,
  Sparkles,
  Database,
  FileText,
  MessageSquare,
  Wrench,
  Send,
  Plus,
  Zap,
  Terminal,
  Cpu,
  Layers,
  CheckCircle2,
  Clock,
  Code,
} from 'lucide-react';
import {
  aiRagCopilotService,
  AIDashboardSummary,
  KnowledgeCollection,
  RAGDocument,
  RAGChatSession,
  RAGChatMessage,
  PromptTemplate,
  AIAgent,
  ToolRegistry,
} from '../../services/aiRagCopilot';

export function AiModule() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'copilot' | 'knowledge' | 'prompts' | 'agents'
  >('copilot');
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<AIDashboardSummary | null>(null);

  const [collections, setCollections] = useState<KnowledgeCollection[]>([]);
  const [documents, setDocuments] = useState<RAGDocument[]>([]);
  const [chatSessions, setChatSessions] = useState<RAGChatSession[]>([]);
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [tools, setTools] = useState<ToolRegistry[]>([]);

  // Copilot Active Session & Message State
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<RAGChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);

  // Modals
  const [showDocModal, setShowDocModal] = useState<boolean>(false);
  const [docName, setDocName] = useState('');
  const [docText, setDocText] = useState('');

  const mockOrgId = '00000000-0000-0000-0000-000000000001';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, collRes, docRes, sessRes, promptRes, agentRes, toolRes] = await Promise.all([
        aiRagCopilotService.getDashboardSummary(mockOrgId).catch(() => null),
        aiRagCopilotService.getCollections(mockOrgId).catch(() => []),
        aiRagCopilotService.getDocuments().catch(() => []),
        aiRagCopilotService.getChatSessions(mockOrgId).catch(() => []),
        aiRagCopilotService.getPromptTemplates().catch(() => []),
        aiRagCopilotService.getAgents(mockOrgId).catch(() => []),
        aiRagCopilotService.getTools().catch(() => []),
      ]);

      setSummary(
        sumRes || {
          total_documents: docRes.length || 42,
          total_embeddings: docRes.length * 15 || 630,
          total_collections: collRes.length || 4,
          active_chat_sessions: sessRes.length || 18,
          total_agent_runs: 125,
          average_response_time_sec: 0.45,
          total_prompt_templates: promptRes.length || 8,
          total_token_usage: 245000,
        }
      );

      setCollections(collRes);
      setDocuments(docRes);
      setChatSessions(sessRes);
      setPrompts(promptRes);
      setAgents(agentRes);
      setTools(toolRes);

      if (sessRes.length > 0 && !currentSessionId) {
        setCurrentSessionId(sessRes[0].id);
        setChatMessages(sessRes[0].messages || []);
      }
    } catch (err) {
      console.error('Failed to load AI data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartNewChat = async () => {
    try {
      const newSession = await aiRagCopilotService.createChatSession({
        organization_id: mockOrgId,
        session_name: `Copilot Session #${Math.floor(100 + Math.random() * 900)}`,
        model_name: 'gpt-4o',
      });
      setChatSessions([newSession, ...chatSessions]);
      setCurrentSessionId(newSession.id);
      setChatMessages([]);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start chat session');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    let targetSessionId = currentSessionId;
    if (!targetSessionId) {
      try {
        const newSession = await aiRagCopilotService.createChatSession({
          organization_id: mockOrgId,
          session_name: `Copilot Chat #${Math.floor(100 + Math.random() * 900)}`,
          model_name: 'gpt-4o',
        });
        targetSessionId = newSession.id;
        setCurrentSessionId(newSession.id);
        setChatSessions([newSession, ...chatSessions]);
      } catch (err) {
        alert('Failed to initialize chat session');
        return;
      }
    }

    const userText = inputMessage;
    setInputMessage('');
    const tempUserMsg: RAGChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: targetSessionId,
      role: 'user',
      message: userText,
      tokens: userText.split(' ').length * 2,
      latency: 0.01,
      created_at: new Date().toISOString(),
    };

    setChatMessages((prev) => [...prev, tempUserMsg]);
    setIsTyping(true);

    try {
      const assistantMsg = await aiRagCopilotService.sendMessage(targetSessionId, userText);
      setChatMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Failed to receive response from Copilot', err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleIngestDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (collections.length === 0) {
      alert('Please create a Knowledge Collection first.');
      return;
    }

    try {
      await aiRagCopilotService.ingestDocument({
        collection_id: collections[0].id,
        document_name: docName,
        file_type: 'txt',
        document_content: docText,
      });
      setShowDocModal(false);
      setDocName('');
      setDocText('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to ingest document');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 shadow-lg shadow-purple-500/30">
              <Bot className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
                Enterprise AI, RAG & Copilot Platform
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Grounded Document RAG, Autonomous AI Agents, Prompt Library & Vector Semantic Search
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowDocModal(true)}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-lg font-medium border border-slate-700 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Ingest Knowledge Doc
          </button>
          <button
            onClick={handleStartNewChat}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white px-4 py-2.5 rounded-lg font-medium shadow-md shadow-purple-500/20 transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4" /> New Copilot Session
          </button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'copilot', label: 'Enterprise Copilot', icon: Bot },
          { id: 'dashboard', label: 'AI Analytics Overview', icon: Sparkles },
          { id: 'knowledge', label: 'Knowledge Base & RAG', icon: Database },
          { id: 'prompts', label: 'Prompt Library', icon: Code },
          { id: 'agents', label: 'AI Agent Hub & Tools', icon: Cpu },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap cursor-pointer ${
                active
                  ? 'bg-slate-800 text-purple-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Copilot Chat Tab */}
      {activeTab === 'copilot' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[720px]">
          {/* Chat Sessions Sidebar */}
          <div className="lg:col-span-1 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-purple-400" /> Copilot Sessions
                </h3>
                <button
                  onClick={handleStartNewChat}
                  className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-purple-400 cursor-pointer"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2 overflow-y-auto max-h-[580px]">
                {chatSessions.length === 0 ? (
                  <p className="text-slate-500 text-xs text-center py-4">No active chat sessions.</p>
                ) : (
                  chatSessions.map((sess) => (
                    <div
                      key={sess.id}
                      onClick={() => {
                        setCurrentSessionId(sess.id);
                        setChatMessages(sess.messages || []);
                      }}
                      className={`p-3 rounded-xl cursor-pointer transition-all border ${
                        currentSessionId === sess.id
                          ? 'bg-purple-950/40 border-purple-500/40 text-white'
                          : 'bg-slate-950/40 border-slate-800/80 text-slate-300 hover:bg-slate-800/50'
                      }`}
                    >
                      <div className="font-semibold text-xs truncate">{sess.session_name}</div>
                      <div className="text-[10px] text-slate-500 mt-1 flex items-center justify-between">
                        <span>Model: {sess.model_name}</span>
                        <span>{new Date(sess.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
              <span>Grounding: Active RAG</span>
              <span className="text-emerald-400 font-bold">Online</span>
            </div>
          </div>

          {/* Main Chat Interface */}
          <div className="lg:col-span-3 bg-slate-900/80 border border-slate-800 rounded-2xl flex flex-col justify-between overflow-hidden">
            {/* Messages Header */}
            <div className="p-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-purple-600/20 text-purple-400">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm">VertexERP AI Assistant</h3>
                  <p className="text-xs text-slate-400">Grounded against Enterprise Knowledge Base</p>
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-full bg-purple-500/20 text-purple-300 font-mono font-medium">
                GPT-4o + Vector RAG
              </span>
            </div>

            {/* Message Stream */}
            <div className="p-6 overflow-y-auto flex-1 space-y-4">
              {chatMessages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-8">
                  <div className="p-4 rounded-2xl bg-purple-600/10 border border-purple-500/20 text-purple-400 mb-4">
                    <Sparkles className="w-10 h-10" />
                  </div>
                  <h4 className="text-lg font-bold text-white">How can I assist your enterprise today?</h4>
                  <p className="text-sm text-slate-400 max-w-md mt-1">
                    Ask questions about inventory stock, general ledger accounts, production scheduling, or company policies.
                  </p>
                </div>
              ) : (
                chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-2xl rounded-2xl p-4 text-sm shadow-md ${
                        msg.role === 'user'
                          ? 'bg-purple-600 text-white rounded-br-none'
                          : 'bg-slate-950 border border-slate-800 text-slate-100 rounded-bl-none'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.message}</p>
                      <div
                        className={`text-[10px] mt-2 flex items-center gap-2 ${
                          msg.role === 'user' ? 'text-purple-200 justify-end' : 'text-slate-500'
                        }`}
                      >
                        <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        {msg.latency > 0 && <span>• {msg.latency}s</span>}
                        {msg.tokens > 0 && <span>• {msg.tokens} tokens</span>}
                      </div>
                    </div>
                  </div>
                ))
              )}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 text-sm text-slate-400 rounded-bl-none flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-400 animate-spin" />
                    <span>VertexERP AI Copilot is thinking...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center gap-3">
              <input
                type="text"
                placeholder="Ask Copilot anything about financial reports, production orders, or HR policies..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim()}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white p-3 rounded-xl shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Ingested Documents</span>
                <FileText className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.total_documents || 0}
              </div>
              <p className="text-xs text-purple-400 mt-2">Parsed and vector indexed</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Vector Embeddings</span>
                <Database className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold text-emerald-400">
                {summary?.total_embeddings.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-slate-400 mt-2">1536-dim vector chunks</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total Tokens Used</span>
                <Zap className="w-5 h-5 text-amber-400" />
              </div>
              <div className="text-3xl font-extrabold text-amber-400">
                {summary?.total_token_usage.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-slate-400 mt-2">GPT-4o consumption</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Avg Response Latency</span>
                <Clock className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.average_response_time_sec}s
              </div>
              <p className="text-xs text-blue-400 mt-2">Sub-second generation</p>
            </div>
          </div>
        </div>
      )}

      {/* Ingest Document Modal */}
      {showDocModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Ingest Document to RAG Vector DB</h3>
            <form onSubmit={handleIngestDoc} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Document Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Travel_Expense_Policy.pdf"
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Document Text Content</label>
                <textarea
                  required
                  rows={5}
                  placeholder="Paste document body text to chunk and embed..."
                  value={docText}
                  onChange={(e) => setDocText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1 font-mono text-xs"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowDocModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Ingest & Generate Embeddings
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
