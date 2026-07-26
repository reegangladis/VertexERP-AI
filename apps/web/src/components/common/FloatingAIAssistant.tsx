import React, { useState } from 'react';
import {
  Sparkles,
  MessageSquare,
  X,
  Send,
  Bot,
  User,
  Zap,
  Mic,
  Code,
  CheckCircle2,
} from 'lucide-react';

export function FloatingAIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'Hello! I am your **VertexERP AI Assistant**. How can I help optimize your enterprise operations, workflows, or cloud infrastructure today?',
      time: 'Just now',
    },
  ]);

  const suggestedPrompts = [
    'Summarize monthly FinOps spend',
    'Run ML Demand Forecast',
    'Evaluate SOC 2 Security Posture',
  ];

  const handleSend = (textToSend?: string) => {
    const queryText = textToSend || input;
    if (!queryText.trim()) return;

    const userMsg = { sender: 'user', text: queryText, time: 'Just now' };
    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');

    // Simulated AI response
    setTimeout(() => {
      let aiText = `I have processed your query: **"${queryText}"**.\n\nEverything is operational. Latency percentiles remain < 28ms and multi-region replication status is HEALTHY.`;
      if (queryText.includes('FinOps')) {
        aiText = '📊 **FinOps Spend Analysis**:\nCurrent monthly cloud spend is **$38,450.00** (76.9% of $50,000 budget). 3 AWS Savings Plan right-sizing recommendations identified ($4,470/mo potential savings).';
      } else if (queryText.includes('Forecast')) {
        aiText = '🔮 **XGBoost Demand Forecast Run**:\nGenerated 90-day demand predictions with **98.4% accuracy (MAPE)**. Inventory allocation optimized for US-East and EU-Central warehouses.';
      }

      setMessages((prev) => [...prev, { sender: 'ai', text: aiText, time: 'Just now' }]);
    }, 800);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="px-4 py-3 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white rounded-full shadow-xl hover:shadow-2xl transition transform hover:-translate-y-1 flex items-center gap-2 font-bold text-sm pulse-glow"
        >
          <Sparkles className="h-5 w-5 animate-spin-slow" />
          <span>Vertex AI Copilot</span>
        </button>
      )}

      {/* Floating Panel */}
      {isOpen && (
        <div className="w-96 h-[540px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden glass-panel animate-in slide-in-from-bottom-5 duration-300">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <div>
                <h3 className="font-bold text-sm">Vertex AI Executive Copilot</h3>
                <p className="text-[11px] opacity-80">Autonomous Operating System Assistant</p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-white/20 rounded-lg">
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'ai' && (
                  <div className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 shrink-0">
                    <Sparkles className="h-3.5 w-3.5" />
                  </div>
                )}
                <div
                  className={`p-3 rounded-2xl max-w-[80%] ${
                    msg.sender === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none border border-slate-200/50 dark:border-slate-700/50'
                  }`}
                >
                  <p className="whitespace-pre-line leading-relaxed">{msg.text}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Suggested Prompts */}
          <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 border-t border-slate-200 dark:border-slate-800 flex gap-1.5 overflow-x-auto">
            {suggestedPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                className="px-2.5 py-1 rounded-full text-[11px] bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 whitespace-nowrap hover:bg-indigo-100 dark:hover:bg-indigo-950 hover:text-indigo-600 transition"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2">
            <input
              type="text"
              placeholder="Ask Vertex AI..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 text-xs bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-xl focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <button
              onClick={() => handleSend()}
              className="p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
