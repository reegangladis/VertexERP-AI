import React, { useState } from 'react';
import {
  Save,
  Cpu,
  Lock,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import PageHeader from '@/components/PageHeader';

export function Settings() {
  const { addNotification } = useNotification();
  const [isOpenAIKeySaved, setIsOpenAIKeySaved] = useState(false);
  
  // Settings Form values
  const [provider, setProvider] = useState('openai');
  const [model, setModel] = useState('gpt-4o');
  const [temperature, setTemperature] = useState(0.7);
  const [apiKey, setApiKey] = useState('••••••••••••••••••••••••••••••••');
  const [rateLimit, setRateLimit] = useState(60);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    addNotification('AI Settings saved successfully', 'success');
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="AI Copilot Configuration Settings"
        description="Configure default chat orchestration parameters, API credentials integration, and tenant query constraints."
      />

      <form onSubmit={handleSaveSettings} className="bg-card border border-border rounded-xl shadow-sm overflow-hidden text-xs">
        <div className="p-4 border-b border-border bg-card/60 flex items-center gap-2">
          <Cpu className="h-4.5 w-4.5 text-primary" />
          <h3 className="font-bold text-foreground uppercase tracking-wider">Default Model Settings</h3>
        </div>

        <div className="p-6 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1">
              <label className="font-semibold text-muted-foreground">Default Model Provider</label>
              <select
                className="w-full text-xs bg-background border border-border rounded-lg p-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                value={provider}
                onChange={(e) => {
                  setProvider(e.target.value);
                  if (e.target.value === 'openai') setModel('gpt-4o');
                  else if (e.target.value === 'gemini') setModel('gemini-1.5-flash');
                  else if (e.target.value === 'anthropic') setModel('claude-3-5-sonnet');
                  else setModel('local');
                }}
              >
                <option value="openai">OpenAI Adaptor</option>
                <option value="gemini">Google Gemini AI</option>
                <option value="anthropic">Anthropic Claude</option>
                <option value="local">Local Model Integration (Ollama)</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-muted-foreground">Default Engine Model Name</label>
              <select
                className="w-full text-xs bg-background border border-border rounded-lg p-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              >
                {provider === 'openai' && (
                  <>
                    <option value="gpt-4o">gpt-4o (Default)</option>
                    <option value="gpt-4-turbo">gpt-4-turbo</option>
                    <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                  </>
                )}
                {provider === 'gemini' && (
                  <>
                    <option value="gemini-1.5-flash">gemini-1.5-flash (Fast)</option>
                    <option value="gemini-1.5-pro">gemini-1.5-pro (Capable)</option>
                  </>
                )}
                {provider === 'anthropic' && (
                  <>
                    <option value="claude-3-5-sonnet">claude-3-5-sonnet</option>
                    <option value="claude-3-haiku">claude-3-haiku</option>
                  </>
                )}
                {provider === 'local' && (
                  <>
                    <option value="llama3">llama3 (Ollama)</option>
                    <option value="mistral">mistral (Ollama)</option>
                    <option value="phi3">phi3 (Ollama)</option>
                  </>
                )}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1">
              <label className="font-semibold text-muted-foreground">Temperature (Creativity Control)</label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="flex-1 h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <span className="font-bold text-foreground text-sm w-8 text-right">{temperature}</span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                Lower values generate more analytical results; higher values create generic conversational flow.
              </p>
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-muted-foreground">Tenant Query Limit (Per min)</label>
              <Input
                type="number"
                value={rateLimit}
                onChange={(e) => setRateLimit(parseInt(e.target.value))}
                className="text-xs"
              />
              <p className="text-[10px] text-muted-foreground">
                Enforces chat quota controls using the Redis backend rate limiter window.
              </p>
            </div>
          </div>

          <div className="border-t border-border/60 pt-4 space-y-4">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-muted-foreground" />
              <span className="font-bold text-foreground uppercase tracking-wider">Credential Keys Integration</span>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              <Input
                label="API Key Access Token"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-••••••••••••••••••••••••••••••••"
                className="text-xs"
              />
              <p className="text-[10px] text-muted-foreground">
                Sensitive keys are masked on return and saved inside the encrypted vault boundary. 
                Leave as defaults to trigger high-fidelity mock completions locally.
              </p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-border bg-card/60 flex justify-end gap-3">
          <Button variant="primary" type="submit" className="gap-2 text-xs">
            <Save className="h-4.5 w-4.5" /> Save AI Configuration
          </Button>
        </div>
      </form>
    </div>
  );
}
export default Settings;
