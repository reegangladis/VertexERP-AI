import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Send,
  Pin,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  ChevronRight,
  ChevronDown,
  Layers,
  Brain,
  History,
  AlertCircle,
  HelpCircle,
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  Trash2,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Alert } from '@/components/Alert';
import { useNotification } from '@/hooks/useNotification';
import { copilotService, CopilotSession, CopilotMessage } from '@/services/copilotService';

export function AICopilot() {
  const { addNotification } = useNotification();
  const [sessions, setSessions] = useState<CopilotSession[]>([]);
  const [activeSession, setActiveSession] = useState<CopilotSession | null>(null);
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Chat controls
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [provider, setProvider] = useState('openai');
  const [modelName, setModelName] = useState('gpt-4o');
  const [temperature, setTemperature] = useState(0.7);
  const [department, setDepartment] = useState('generic');
  
  // UI states
  const [expandedToolExecs, setExpandedToolExecs] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested Prompts
  const suggestedPrompts = [
    { label: 'Check Leave Balance', prompt: 'Show me my vacation and paid time off (PTO) leave balances.', dept: 'hr' },
    { label: 'CRM Sales Leads', prompt: 'Retrieve the latest active sales leads details from CRM pipeline.', dept: 'crm' },
    { label: 'Review Q2 Budgets', prompt: 'Summarize the finance budget allocations and spend metrics for Q2.', dept: 'finance' },
    { label: 'Warehouse Stock Check', prompt: 'Query the inventory stock level for product SKU-PROD-A.', dept: 'inventory' },
    { label: 'List BOM Materials', prompt: 'Retrieve manufacturing Bill of Materials (BOM) items for BOM-2026-X.', dept: 'manufacturing' },
  ];

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (activeSession) {
      loadMessages(activeSession.id);
    } else {
      setMessages([]);
    }
  }, [activeSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const loadSessions = async () => {
    try {
      const data = await copilotService.listSessions();
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        setActiveSession(data[0]);
      }
    } catch (err: any) {
      addNotification(err.message || 'Failed to retrieve sessions', 'error');
    }
  };

  const loadMessages = async (sid: string) => {
    try {
      const data = await copilotService.listMessages(sid);
      setMessages(data);
    } catch (err: any) {
      addNotification('Error loading session transcript', 'error');
    }
  };

  const handleCreateSession = async () => {
    try {
      const session = await copilotService.createSession(`Copilot Session ${new Date().toLocaleDateString()}`);
      setSessions((prev) => [session, ...prev]);
      setActiveSession(session);
      addNotification('Conversation thread created', 'success');
    } catch (err: any) {
      addNotification('Failed to create new session', 'error');
    }
  };

  const handleDeleteSession = async (sid: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await copilotService.deleteSession(sid);
      setSessions((prev) => prev.filter((s) => s.id !== sid));
      if (activeSession?.id === sid) {
        setActiveSession(null);
      }
      addNotification('Conversation thread deleted', 'success');
    } catch (err: any) {
      addNotification('Could not delete session', 'error');
    }
  };

  const handleTogglePin = async (session: CopilotSession, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const updated = await copilotService.updateSession(session.id, { is_pinned: !session.is_pinned });
      setSessions((prev) =>
        prev
          .map((s) => (s.id === session.id ? updated : s))
          .sort((a, b) => (b.is_pinned ? 1 : 0) - (a.is_pinned ? 1 : 0))
      );
      if (activeSession?.id === session.id) {
        setActiveSession(updated);
      }
      addNotification(updated.is_pinned ? 'Conversation pinned' : 'Conversation unpinned', 'success');
    } catch (err: any) {
      addNotification('Failed to update pin', 'error');
    }
  };

  const handleSendMessage = async (customContent?: string) => {
    const text = (customContent || inputMessage).trim();
    if (!text || !activeSession) return;

    setInputMessage('');
    setIsLoading(true);
    
    // Add user message optimistically
    const optimisticUserMsg: CopilotMessage = {
      id: Math.random().toString(),
      session_id: activeSession.id,
      role: 'user',
      content: text,
      prompt_tokens: 0,
      completion_tokens: 0,
      latency_ms: 0,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);

    try {
      const response = await copilotService.sendChatMessage(
        activeSession.id,
        text,
        provider,
        modelName,
        temperature,
        department === 'generic' ? undefined : department
      );
      
      // Replace messages with final synchronized data
      setMessages((prev) =>
        prev
          .filter((m) => m.id !== optimisticUserMsg.id)
          .concat([response.user_message, response.assistant_message])
      );
      
      // Update session listing timestamps
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSession.id ? { ...s, updated_at: new Date().toISOString() } : s))
      );
    } catch (err: any) {
      addNotification(err.message || 'Chat error', 'error');
      // Remove optimistic message on failure
      setMessages((prev) => prev.filter((m) => m.id !== optimisticUserMsg.id));
    } finally {
      setIsLoading(false);
    }
  };

  const submitFeedback = async (msgId: string, rating: number) => {
    try {
      await copilotService.submitFeedback(msgId, rating, rating >= 4 ? 'Good response' : 'Needs improvement');
      addNotification('Feedback rating saved', 'success');
      // Update local state
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, feedback_rating: rating } : m))
      );
    } catch (err: any) {
      addNotification('Failed to save feedback', 'error');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleToolDetails = (msgId: string) => {
    setExpandedToolExecs((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background select-none overflow-hidden border-t border-border">
      {/* LEFT COLUMN PANEL - Sessions history lists */}
      <div className="w-80 border-r border-border bg-card/40 flex flex-col justify-between shrink-0">
        <div className="p-4 space-y-4 flex-1 flex flex-col min-h-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              <h2 className="text-sm font-semibold text-foreground">Copilot Threads</h2>
            </div>
            <Button size="sm" onClick={handleCreateSession} className="px-2 h-8 text-[11px] gap-1">
              New Chat
            </Button>
          </div>
          
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground/60" />
            <input
              type="text"
              placeholder="Search conversation..."
              className="w-full text-xs bg-background/50 border border-border rounded-lg pl-9 pr-4 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0 pr-1">
            {filteredSessions.length === 0 ? (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No active chat threads found.
              </div>
            ) : (
              filteredSessions.map((session) => {
                const isActive = activeSession?.id === session.id;
                return (
                  <div
                    key={session.id}
                    onClick={() => setActiveSession(session)}
                    className={`group flex items-center justify-between p-3 rounded-lg text-xs font-medium cursor-pointer transition-all border ${
                      isActive
                        ? 'bg-primary/5 border-primary/20 text-foreground'
                        : 'border-transparent text-muted-foreground hover:bg-secondary/40 hover:text-foreground'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                      <MessageSquare className={`h-4 w-4 shrink-0 ${isActive ? 'text-primary' : 'text-muted-foreground/60'}`} />
                      <span className="truncate pr-2">{session.title}</span>
                    </div>
                    
                    <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleTogglePin(session, e)}
                        className={`p-1 rounded hover:bg-secondary text-muted-foreground/70 hover:text-foreground ${session.is_pinned ? 'text-primary opacity-100' : ''}`}
                      >
                        <Pin className={`h-3 w-3 ${session.is_pinned ? 'fill-primary' : ''}`} />
                      </button>
                      <button
                        onClick={(e) => handleDeleteSession(session.id, e)}
                        className="p-1 rounded hover:bg-destructive/10 text-muted-foreground/70 hover:text-destructive"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Configurations details */}
        <div className="p-4 border-t border-border bg-card/60 space-y-3">
          <div className="space-y-1">
            <label className="text-[10px] font-semibold text-muted-foreground/80 uppercase">LLM Provider</label>
            <select
              className="w-full text-xs bg-background border border-border rounded p-1.5 text-foreground"
              value={provider}
              onChange={(e) => {
                setProvider(e.target.value);
                if (e.target.value === 'openai') setModelName('gpt-4o');
                else if (e.target.value === 'gemini') setModelName('gemini-1.5-flash');
                else if (e.target.value === 'anthropic') setModelName('claude-3-5-sonnet');
                else setModelName('local');
              }}
            >
              <option value="openai">OpenAI (GPT-4o)</option>
              <option value="gemini">Google Gemini</option>
              <option value="anthropic">Anthropic Claude</option>
              <option value="local">Local Model (Ollama)</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <label className="text-[10px] font-semibold text-muted-foreground/80 uppercase">Department</label>
              <select
                className="w-full text-xs bg-background border border-border rounded p-1.5 text-foreground"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
              >
                <option value="generic">General</option>
                <option value="hr">HR Platform</option>
                <option value="crm">CRM Sales</option>
                <option value="finance">Finance</option>
                <option value="inventory">Inventory</option>
                <option value="manufacturing">Manufacturing</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-semibold text-muted-foreground/80 uppercase">Temp: {temperature}</label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-1 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary mt-2"
              />
            </div>
          </div>
        </div>
      </div>

      {/* MAIN VIEWPORT PANEL - Chat feed */}
      <div className="flex-1 flex flex-col justify-between bg-background">
        {activeSession ? (
          <>
            {/* Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-foreground">{activeSession.title}</h3>
                <p className="text-[10px] text-muted-foreground flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  Pluggable Tool Architecture Ready • Active API validation active
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={() => loadMessages(activeSession.id)} className="p-2">
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Messages Feed */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.length === 0 ? (
                /* Empty state / Suggested Prompts */
                <div className="max-w-2xl mx-auto py-12 text-center space-y-8">
                  <div className="space-y-3">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto text-primary">
                      <Sparkles className="h-6 w-6" />
                    </div>
                    <h2 className="text-lg font-bold text-foreground">Welcome to VertexERP AI Copilot</h2>
                    <p className="text-xs text-muted-foreground max-w-md mx-auto">
                      Ask questions, trigger ERP transactions, generate reports, search policy docs, and run multi-step workflows.
                    </p>
                  </div>
                  
                  <div className="space-y-3 text-left">
                    <h4 className="text-xs font-semibold text-muted-foreground px-1 uppercase tracking-wider">Suggested Actions</h4>
                    <div className="grid grid-cols-1 gap-2.5">
                      {suggestedPrompts.map((p, idx) => (
                        <div
                          key={idx}
                          onClick={() => {
                            setDepartment(p.dept);
                            handleSendMessage(p.prompt);
                          }}
                          className="flex items-center justify-between p-3 rounded-lg border border-border bg-card/30 hover:bg-secondary/40 cursor-pointer transition-all text-xs group"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-primary font-bold uppercase text-[9px] bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
                              {p.dept}
                            </span>
                            <span className="text-foreground/90 font-medium">{p.label}</span>
                          </div>
                          <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                /* Message Feed rendering */
                <div className="max-w-4xl mx-auto space-y-6">
                  {messages.map((msg) => {
                    const isUser = msg.role === 'user';
                    return (
                      <div key={msg.id} className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        {!isUser && (
                          <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                            <Brain className="h-4.5 w-4.5 text-primary" />
                          </div>
                        )}

                        <div className="space-y-2 max-w-[80%]">
                          <div
                            className={`p-4 rounded-xl border text-xs leading-relaxed ${
                              isUser
                                ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                                : 'bg-card text-foreground border-border shadow-sm'
                            }`}
                          >
                            <p className="whitespace-pre-line">{msg.content}</p>
                            
                            {/* Citations references */}
                            {msg.citations && msg.citations.length > 0 && (
                              <div className="mt-3 pt-2.5 border-t border-border/60 text-[10px] text-muted-foreground space-y-1">
                                <span className="font-semibold block text-foreground/80 uppercase tracking-wide">References:</span>
                                {msg.citations.map((cit, cidx) => (
                                  <div key={cidx} className="flex gap-1.5 items-start">
                                    <span className="bg-secondary px-1 py-0.5 rounded text-foreground text-[8px] font-bold">API</span>
                                    <span>{cit.details || cit.snippet || JSON.stringify(cit)}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Tool Execution Logs */}
                          {!isUser && msg.tool_calls && (
                            <div className="bg-secondary/40 border border-border/80 rounded-lg p-2 text-[10px]">
                              <button
                                onClick={() => toggleToolDetails(msg.id)}
                                className="flex items-center justify-between w-full font-medium text-muted-foreground hover:text-foreground text-left"
                              >
                                <span className="flex items-center gap-1.5">
                                  <Layers className="h-3.5 w-3.5 text-primary" />
                                  Tool Integrations Executed ({msg.tool_calls.length})
                                </span>
                                {expandedToolExecs[msg.id] ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                              </button>
                              
                              {expandedToolExecs[msg.id] && (
                                <div className="mt-2 space-y-1.5 border-t border-border/40 pt-1.5">
                                  {msg.tool_calls.map((tcall: any, tcidx: number) => (
                                    <div key={tcidx} className="flex items-start justify-between py-1 border-b border-border/10 last:border-b-0">
                                      <div className="space-y-0.5">
                                        <div className="font-bold text-foreground">{tcall.function.name}</div>
                                        <div className="text-[9px] text-muted-foreground/85">
                                          Args: <code className="bg-secondary/80 px-1 rounded">{tcall.function.arguments}</code>
                                        </div>
                                      </div>
                                      <span className="text-[8px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded font-semibold uppercase">
                                        success
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}

                          {/* Message Footer: Latency, tokens, and feedback rating */}
                          {!isUser && (
                            <div className="flex items-center justify-between text-[9px] text-muted-foreground/85 px-1.5">
                              <span className="flex items-center gap-2">
                                <span>Latency: {msg.latency_ms}ms</span>
                                <span>•</span>
                                <span>Tokens: {msg.prompt_tokens + msg.completion_tokens}</span>
                              </span>
                              
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => submitFeedback(msg.id, 5)}
                                  className={`p-1 rounded hover:bg-secondary ${msg.feedback_rating === 5 ? 'text-primary bg-primary/5' : ''}`}
                                >
                                  <ThumbsUp className="h-3 w-3" />
                                </button>
                                <button
                                  onClick={() => submitFeedback(msg.id, 1)}
                                  className={`p-1 rounded hover:bg-secondary ${msg.feedback_rating === 1 ? 'text-destructive bg-destructive/5' : ''}`}
                                >
                                  <ThumbsDown className="h-3 w-3" />
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Input area */}
            <div className="p-6 border-t border-border bg-card/30">
              <div className="max-w-4xl mx-auto flex items-end gap-3 bg-card border border-border rounded-xl p-2 shadow-sm focus-within:ring-1 focus-within:ring-primary">
                <textarea
                  placeholder="Type a message, trigger tool executions, or check policies..."
                  className="flex-1 text-xs bg-transparent border-0 resize-none p-2 text-foreground focus:outline-none focus:ring-0 max-h-36 min-h-[2.5rem]"
                  rows={2}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                
                <div className="flex items-center gap-2.5 shrink-0 px-2 pb-1.5">
                  <Button
                    variant="primary"
                    size="sm"
                    className="h-8 w-8 p-0 rounded-lg justify-center"
                    onClick={() => handleSendMessage()}
                    isLoading={isLoading}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="text-[10px] text-center text-muted-foreground mt-2 max-w-md mx-auto">
                VertexERP AI Copilot complies with strict RBAC data isolation. All operational transactions log audits automatically.
              </div>
            </div>
          </>
        ) : (
          /* Empty Session selection */
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-4">
            <Brain className="h-14 w-14 text-muted-foreground/30 animate-pulse" />
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-foreground">No Chat Active</h3>
              <p className="text-xs text-muted-foreground max-w-sm">
                Create a new chat thread or select an existing session from the side list to begin pairs-programming ERP integrations.
              </p>
            </div>
            <Button onClick={handleCreateSession}>Create Chat Thread</Button>
          </div>
        )}
      </div>
    </div>
  );
}
export default AICopilot;
