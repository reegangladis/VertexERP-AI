import React, { useState } from 'react';
import {
  Layers,
  Search,
  CheckCircle2,
  Settings,
  Plus,
  ShieldCheck,
  Zap,
  ExternalLink,
  Lock,
} from 'lucide-react';

interface ConnectorItem {
  id: string;
  name: string;
  provider: string;
  category: 'ERP' | 'CRM' | 'Payment' | 'Storage' | 'Email' | 'SMS' | 'Messaging' | 'AI' | 'IdP';
  description: string;
  status: 'Connected' | 'Available' | 'Configuring';
  version: string;
  icon: string;
}

export default function ConnectorMarketplace() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [activeTab, setActiveTab] = useState<'All' | 'Connected'>('All');

  const connectors: ConnectorItem[] = [
    { id: '1', name: 'SAP S/4HANA', provider: 'SAP', category: 'ERP', description: 'Enterprise ERP sync for orders, financials, and inventory.', status: 'Connected', version: '2.4.0', icon: '🏢' },
    { id: '2', name: 'Oracle NetSuite', provider: 'Oracle', category: 'ERP', description: 'Cloud ERP connector for ledgers and purchase requisitions.', status: 'Available', version: '1.2.0', icon: '🏛️' },
    { id: '3', name: 'Salesforce CRM', provider: 'Salesforce', category: 'CRM', description: 'Bi-directional lead, opportunity, and contact sync.', status: 'Connected', version: '3.1.0', icon: '☁️' },
    { id: '4', name: 'HubSpot Marketing', provider: 'HubSpot', category: 'CRM', description: 'Inbound marketing pipeline and deal tracking integration.', status: 'Available', version: '2.0.0', icon: '🟠' },
    { id: '5', name: 'Stripe Payments', provider: 'Stripe', category: 'Payment', description: 'Global credit card, billing, and subscription payouts.', status: 'Connected', version: '4.0.0', icon: '💳' },
    { id: '6', name: 'Razorpay Gateway', provider: 'Razorpay', category: 'Payment', description: 'UPI, NetBanking, and automated settlements engine.', status: 'Connected', version: '1.5.0', icon: '⚡' },
    { id: '7', name: 'AWS S3 Storage', provider: 'AWS', category: 'Storage', description: 'High-durability object storage for document archives.', status: 'Connected', version: '2.1.0', icon: '🪣' },
    { id: '8', name: 'Azure Blob Storage', provider: 'Microsoft', category: 'Storage', description: 'Cloud blob storage integration for unstructured files.', status: 'Available', version: '1.1.0', icon: '🔷' },
    { id: '9', name: 'SendGrid Email', provider: 'Twilio', category: 'Email', description: 'Transactional email API and delivery monitoring.', status: 'Connected', version: '2.0.0', icon: '✉️' },
    { id: '10', name: 'Twilio SMS Engine', provider: 'Twilio', category: 'SMS', description: 'Global SMS and WhatsApp notification channel.', status: 'Connected', version: '3.0.0', icon: '📱' },
    { id: '11', name: 'Slack Messaging', provider: 'Salesforce', category: 'Messaging', description: 'Interactive channel alerts and workflow bot dispatches.', status: 'Connected', version: '2.2.0', icon: '💬' },
    { id: '12', name: 'Microsoft Teams', provider: 'Microsoft', category: 'Messaging', description: 'Teams channel notifications and adaptive card popups.', status: 'Available', version: '1.4.0', icon: '👥' },
    { id: '13', name: 'OpenAI GPT-4o', provider: 'OpenAI', category: 'AI', description: 'GenAI text completion, extraction, and embedding engine.', status: 'Connected', version: '4.5.0', icon: '🤖' },
    { id: '14', name: 'Auth0 Identity', provider: 'Okta', category: 'IdP', description: 'Enterprise SSO, OAuth2, and user profile federation.', status: 'Connected', version: '2.0.0', icon: '🔑' },
  ];

  const categories = ['All', 'ERP', 'CRM', 'Payment', 'Storage', 'Email', 'SMS', 'Messaging', 'AI', 'IdP'];

  const filteredConnectors = connectors.filter((c) => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase()) || c.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'All' || c.category === selectedCategory;
    const matchesTab = activeTab === 'All' || (activeTab === 'Connected' && c.status === 'Connected');
    return matchesSearch && matchesCat && matchesTab;
  });

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Connector Marketplace</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Pluggable connectors for ERP, CRM, Payments, Cloud Storage, Messaging, AI, and Identity.
          </p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition">
          <Plus className="h-4 w-4 mr-1.5" /> Build Custom Connector
        </button>
      </div>

      {/* Controls Bar */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search connectors or providers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Connectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredConnectors.map((c) => (
          <div
            key={c.id}
            className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{c.icon}</span>
                  <div>
                    <h3 className="font-bold text-base">{c.name}</h3>
                    <p className="text-xs text-slate-400 font-mono">{c.provider} • v{c.version}</p>
                  </div>
                </div>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
                    c.status === 'Connected'
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-800'
                      : 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:border-slate-600'
                  }`}
                >
                  {c.status}
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-3 line-clamp-2">{c.description}</p>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-400 uppercase bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">
                {c.category}
              </span>
              <div className="flex items-center gap-2">
                {c.status === 'Connected' ? (
                  <button className="px-3 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-medium transition flex items-center gap-1">
                    <Settings className="h-3.5 w-3.5" /> Configure
                  </button>
                ) : (
                  <button className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-medium transition flex items-center gap-1">
                    <Zap className="h-3.5 w-3.5" /> Connect
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
