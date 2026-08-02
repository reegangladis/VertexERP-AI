import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient, getApiBaseUrl } from '@/services/apiClient';
import { Settings, Save, Sparkles, FolderOpen, FileText, Plus, Trash2, Download } from 'lucide-react';

interface OrgSetting {
  timezone: string;
  locale: string;
  currency: string;
  branding_primary_color: string;
  branding_secondary_color: string;
}

interface MetadataItem {
  id: string;
  key: string;
  value: string;
  value_type: string;
}

interface DocumentItem {
  id: string;
  name: string;
  type: string;
  file_path: string;
  storage_provider: string;
}

export function OrgSettings() {
  const { addNotification } = useNotification();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('branding');

  // settings
  const [config, setConfig] = useState<OrgSetting>({
    timezone: 'UTC',
    locale: 'en_US',
    currency: 'USD',
    branding_primary_color: '#09090b',
    branding_secondary_color: '#f4f4f5',
  });

  // metadata
  const [metadata, setMetadata] = useState<MetadataItem[]>([]);
  const [newMetaKey, setNewMetaKey] = useState('');
  const [newMetaVal, setNewMetaVal] = useState('');

  // documents
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [docName, setDocName] = useState('');
  const [docType, setDocType] = useState('policy');
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);

  const fetchAllData = async () => {
    try {
      const [settingsRes, docsResList] = await Promise.all([
        apiClient.get('/api/v1/organizations/me/org-settings'),
        apiClient.get('/api/v1/documents'),
      ]);
      if (settingsRes.data.data) {
        setConfig(settingsRes.data.data);
      }
      
      setDocs(docsResList.data.data || []);
      
      setMetadata([
        { id: '1', key: 'corporate.industry', value: 'Technology Services', value_type: 'string' },
        { id: '2', key: 'corporate.tax_id', value: 'TX-883-911', value_type: 'string' },
      ]);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleSaveBranding = async () => {
    setLoading(true);
    try {
      await apiClient.put('/api/v1/organizations/me/org-settings', config);
      addNotification('Branding and localization settings saved', 'success');
      fetchAllData();
    } catch (err: any) {
      addNotification(err.message || 'Save failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMetadata = () => {
    if (!newMetaKey || !newMetaVal) return;
    setMetadata([...metadata, { id: uuid4(), key: newMetaKey, value: newMetaVal, value_type: 'string' }]);
    setNewMetaKey('');
    setNewMetaVal('');
    addNotification('Metadata setting added locally', 'success');
  };

  const uuid4 = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };

  const handleDocUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileToUpload || !docName) return;

    const formData = new FormData();
    formData.append('name', docName);
    formData.append('type', docType);
    formData.append('provider', 'local');
    formData.append('file', fileToUpload);

    try {
      await apiClient.post('/api/v1/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Document uploaded successfully', 'success');
      setDocName('');
      setFileToUpload(null);
      
      const docsResList = await apiClient.get('/api/v1/documents');
      setDocs(docsResList.data.data || []);
    } catch (err: any) {
      addNotification(err.message || 'Upload failed', 'error');
    }
  };

  const handleDocDelete = async (id: string) => {
    if (!window.confirm('Delete this document?')) return;
    try {
      await apiClient.delete(`/api/v1/documents/${id}`);
      addNotification('Document deleted successfully', 'success');
      const docsResList = await apiClient.get('/api/v1/documents');
      setDocs(docsResList.data.data || []);
    } catch (err: any) {
      addNotification(err.message || 'Deletion failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Organization Settings</h1>
          <p className="text-sm text-muted-foreground">Govern localized options, brand color palettes, metadata keys, and corporate policies handbooks.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border select-none gap-4">
        {[
          { id: 'branding', label: 'Branding & Local', icon: <Sparkles className="h-4 w-4" /> },
          { id: 'metadata', label: 'Extensible Metadata', icon: <Settings className="h-4 w-4" /> },
          { id: 'handbooks', label: 'Policy Handbooks', icon: <FolderOpen className="h-4 w-4" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 pb-3 text-sm font-medium border-b-2 px-1 transition-all cursor-pointer ${
              activeTab === tab.id
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Branding Tab */}
      {activeTab === 'branding' && (
        <Card>
          <CardHeader>
            <CardTitle>Branding & Localization Details</CardTitle>
            <CardDescription>Setup brand colors, target locale parameters, and billing currency.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 max-w-xl">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Primary Brand Color (HEX)"
                value={config.branding_primary_color}
                onChange={(e) => setConfig({ ...config, branding_primary_color: e.target.value })}
              />
              <Input
                label="Secondary Brand Color (HEX)"
                value={config.branding_secondary_color}
                onChange={(e) => setConfig({ ...config, branding_secondary_color: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-3 gap-4 pt-2">
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase">Currency</label>
                <select
                  value={config.currency}
                  onChange={(e) => setConfig({ ...config, currency: e.target.value })}
                  className="h-10 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                </select>
              </div>
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase">Locale</label>
                <select
                  value={config.locale}
                  onChange={(e) => setConfig({ ...config, locale: e.target.value })}
                  className="h-10 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="en_US">en_US</option>
                  <option value="es_ES">es_ES</option>
                  <option value="fr_FR">fr_FR</option>
                </select>
              </div>
              <Input
                label="Default Timezone"
                value={config.timezone}
                onChange={(e) => setConfig({ ...config, timezone: e.target.value })}
              />
            </div>
            <div className="pt-4">
              <Button onClick={handleSaveBranding} disabled={loading} variant="primary" className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                {loading ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metadata Tab */}
      {activeTab === 'metadata' && (
        <Card>
          <CardHeader>
            <CardTitle>Organization Metadata Properties</CardTitle>
            <CardDescription>Configure extensible parameters for custom business logic mapping.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-3 gap-3 bg-secondary/15 p-4 rounded border border-border">
              <div className="flex flex-col space-y-1">
                <label className="text-[10px] font-semibold uppercase text-muted-foreground">Property Key</label>
                <input
                  type="text"
                  placeholder="e.g. corporate.tax_id"
                  value={newMetaKey}
                  onChange={(e) => setNewMetaKey(e.target.value)}
                  className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <div className="flex flex-col space-y-1">
                <label className="text-[10px] font-semibold uppercase text-muted-foreground">Property Value</label>
                <input
                  type="text"
                  placeholder="e.g. TX-883"
                  value={newMetaVal}
                  onChange={(e) => setNewMetaVal(e.target.value)}
                  className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <div className="flex items-end">
                <Button onClick={handleAddMetadata} variant="secondary" className="w-full h-9 flex items-center justify-center gap-2 text-xs font-semibold">
                  <Plus className="h-4 w-4" /> Add Parameter
                </Button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground uppercase font-mono text-[10px]">
                    <th className="py-2.5 px-3">Metadata Key</th>
                    <th className="py-2.5 px-3">Value</th>
                    <th className="py-2.5 px-3">Type</th>
                  </tr>
                </thead>
                <tbody>
                  {metadata.map((item) => (
                    <tr key={item.id} className="border-b border-border hover:bg-secondary/5">
                      <td className="py-3 px-3 font-mono font-semibold">{item.key}</td>
                      <td className="py-3 px-3 text-muted-foreground font-mono">{item.value}</td>
                      <td className="py-3 px-3 text-muted-foreground">{item.value_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Handbooks Tab */}
      {activeTab === 'handbooks' && (
        <Card>
          <CardHeader>
            <CardTitle>Corporate Policy Registry</CardTitle>
            <CardDescription>Upload policy handbooks, store licenses, and metadata records.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleDocUpload} className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-secondary/15 p-4 rounded border border-border">
              <div className="flex flex-col space-y-1">
                <label className="text-[10px] font-semibold uppercase text-muted-foreground">Document Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Employee Handbook"
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <div className="flex flex-col space-y-1">
                <label className="text-[10px] font-semibold uppercase text-muted-foreground">Doc Type</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="handbook">Handbook</option>
                  <option value="policy">Policy Policy</option>
                  <option value="certificate">Certificate</option>
                  <option value="business_license">Business License</option>
                </select>
              </div>
              <div className="flex flex-col space-y-1">
                <label className="text-[10px] font-semibold uppercase text-muted-foreground">Select File</label>
                <input
                  type="file"
                  required
                  onChange={(e) => setFileToUpload(e.target.files?.[0] || null)}
                  className="h-9 border border-input rounded bg-background text-xs pt-1.5 px-3 focus:outline-none"
                />
              </div>
              <div className="flex items-end">
                <Button type="submit" variant="secondary" className="w-full h-9 flex items-center justify-center gap-2 text-xs font-semibold">
                  <Plus className="h-4 w-4" /> Upload Document
                </Button>
              </div>
            </form>

            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase">Uploaded Policy Handbooks</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {docs.map((doc) => (
                  <div key={doc.id} className="border border-border p-4 rounded bg-card flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 border border-border bg-secondary/35 rounded text-primary">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div className="text-left space-y-0.5">
                        <h4 className="text-xs font-bold font-mono text-foreground">{doc.name}</h4>
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-mono font-semibold">{doc.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <a
                        href={`${getApiBaseUrl()}/api/v1/documents/${doc.id}/download`}
                        download
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground cursor-pointer"
                      >
                        <Download className="h-4.5 w-4.5" />
                      </a>
                      <button
                        onClick={() => handleDocDelete(doc.id)}
                        className="p-1.5 hover:bg-secondary rounded text-red-500 hover:text-red-600"
                      >
                        <Trash2 className="h-4.5 w-4.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
export default OrgSettings;
