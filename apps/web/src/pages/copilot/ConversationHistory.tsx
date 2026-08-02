import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  MessageSquare,
  Clock,
  Pin,
  Trash2,
  Eye,
  Calendar,
} from 'lucide-react';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { copilotService, CopilotSession, CopilotMessage } from '@/services/copilotService';
import PageHeader from '@/components/PageHeader';

export function ConversationHistory() {
  const { addNotification } = useNotification();
  const [sessions, setSessions] = useState<CopilotSession[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Selected session detailed view
  const [selectedSession, setSelectedSession] = useState<CopilotSession | null>(null);
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await copilotService.listSessions();
      setSessions(data);
    } catch (err: any) {
      addNotification('Failed to load conversation history list', 'error');
    }
  };

  const handleSelectSession = async (session: CopilotSession) => {
    setSelectedSession(session);
    setIsLoadingMessages(true);
    try {
      const data = await copilotService.listMessages(session.id);
      setMessages(data);
    } catch (err) {
      addNotification('Could not load conversation transcript', 'error');
    } finally {
      setIsLoadingMessages(false);
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
      if (selectedSession?.id === session.id) {
        setSelectedSession(updated);
      }
      addNotification(updated.is_pinned ? 'Conversation pinned' : 'Conversation unpinned', 'success');
    } catch (err) {
      addNotification('Failed to toggle pin state', 'error');
    }
  };

  const handleDeleteSession = async (sid: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await copilotService.deleteSession(sid);
      setSessions((prev) => prev.filter((s) => s.id !== sid));
      if (selectedSession?.id === sid) {
        setSelectedSession(null);
        setMessages([]);
      }
      addNotification('Conversation deleted from history', 'success');
    } catch (err) {
      addNotification('Failed to delete history item', 'error');
    }
  };

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Conversation History"
        description="Audit past AI sessions, examine performance logs, and review operational tool executions."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Side: Listing List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground/60" />
            <Input
              type="text"
              placeholder="Filter threads..."
              className="pl-9 text-xs"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="bg-card border border-border rounded-xl p-2 space-y-1 max-h-[60vh] overflow-y-auto">
            {filteredSessions.length === 0 ? (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No past sessions matched the search criteria.
              </div>
            ) : (
              filteredSessions.map((session) => {
                const isSelected = selectedSession?.id === session.id;
                return (
                  <div
                    key={session.id}
                    onClick={() => handleSelectSession(session)}
                    className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all border ${
                      isSelected
                        ? 'bg-primary/5 border-primary/20 text-foreground'
                        : 'border-transparent text-muted-foreground hover:bg-secondary/30 hover:text-foreground'
                    }`}
                  >
                    <div className="min-w-0 flex-1 space-y-1">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground truncate pr-2">
                        <MessageSquare className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                        <span>{session.title}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-muted-foreground/80">
                        <Clock className="h-3 w-3" />
                        <span>{new Date(session.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleTogglePin(session, e)}
                        className={`p-1 rounded hover:bg-secondary ${session.is_pinned ? 'text-primary opacity-100' : 'text-muted-foreground/50'}`}
                      >
                        <Pin className={`h-3 w-3 ${session.is_pinned ? 'fill-primary' : ''}`} />
                      </button>
                      <button
                        onClick={(e) => handleDeleteSession(session.id, e)}
                        className="p-1 rounded hover:bg-destructive/10 text-muted-foreground/50 hover:text-destructive"
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

        {/* Right Side: Detailed session view */}
        <div className="lg:col-span-2 space-y-4">
          {selectedSession ? (
            <div className="bg-card border border-border rounded-xl flex flex-col shadow-sm min-h-[50vh]">
              {/* Detail Header */}
              <div className="p-4 border-b border-border flex items-center justify-between bg-card/60">
                <div className="space-y-0.5">
                  <h3 className="text-xs font-bold text-foreground">{selectedSession.title}</h3>
                  <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                    <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> Created: {new Date(selectedSession.created_at).toLocaleString()}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1"><History className="h-3 w-3" /> Messages: {messages.length}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded border ${
                    selectedSession.is_pinned
                      ? 'bg-primary/10 border-primary/20 text-primary'
                      : 'bg-secondary/40 border-border text-muted-foreground'
                  }`}>
                    {selectedSession.is_pinned ? 'Pinned' : 'Regular'}
                  </span>
                </div>
              </div>

              {/* Transcript list */}
              <div className="p-6 flex-1 overflow-y-auto space-y-5">
                {isLoadingMessages ? (
                  <div className="text-center py-12 text-xs text-muted-foreground">
                    Loading transcript history...
                  </div>
                ) : messages.length === 0 ? (
                  <div className="text-center py-12 text-xs text-muted-foreground">
                    No transcript logs recorded for this session.
                  </div>
                ) : (
                  messages.map((msg) => {
                    const isUser = msg.role === 'user';
                    return (
                      <div key={msg.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        <div className={`p-4 rounded-xl border text-xs max-w-[85%] leading-relaxed ${
                          isUser
                            ? 'bg-primary/5 text-foreground border-primary/20'
                            : 'bg-secondary/20 text-foreground border-border'
                        }`}>
                          <div className="flex items-center justify-between border-b border-border/40 pb-1.5 mb-2 text-[9px] font-semibold uppercase tracking-wider text-muted-foreground">
                            <span>{msg.role}</span>
                            <span>{new Date(msg.created_at).toLocaleTimeString()}</span>
                          </div>
                          <p className="whitespace-pre-line">{msg.content}</p>
                          
                          {msg.tool_calls && (
                            <div className="mt-3 p-2 bg-background border border-border rounded-lg text-[9px] text-muted-foreground font-mono space-y-1">
                              <span className="font-bold text-foreground">Executed API calls:</span>
                              {msg.tool_calls.map((tcall: any, idx) => (
                                <div key={idx} className="flex gap-1.5">
                                  <span className="text-primary font-semibold">{tcall.function.name}</span>
                                  <span>({tcall.function.arguments})</span>
                                </div>
                              ))}
                            </div>
                          )}

                          {!isUser && (
                            <div className="mt-2.5 pt-2 border-t border-border/40 flex items-center justify-between text-[8px] text-muted-foreground/80">
                              <span>Tokens: {msg.prompt_tokens + msg.completion_tokens} (Prompt: {msg.prompt_tokens}, Gen: {msg.completion_tokens})</span>
                              <span>Speed: {msg.latency_ms}ms</span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-12 text-center text-muted-foreground flex flex-col items-center justify-center min-h-[50vh] space-y-2">
              <Eye className="h-10 w-10 text-muted-foreground/30" />
              <h4 className="text-sm font-semibold text-foreground">Audit Viewer</h4>
              <p className="text-xs text-muted-foreground max-w-sm">
                Select a thread from the history log to inspect the step-by-step chat records, token metrics, and execution logs.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
export default ConversationHistory;
