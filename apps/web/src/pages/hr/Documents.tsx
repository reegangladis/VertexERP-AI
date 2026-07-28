import { useState, useEffect, useRef } from 'react';
import {
  FileText,
  Lock,
  Upload,
  Trash2,
  Loader2,
  Search,
  Filter,
  Download,
  Shield,
  FolderOpen,
  FileCheck,
  FileLock,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const DOC_TYPE_OPTIONS = [
  { value: 'contract', label: 'Employment Contract' },
  { value: 'resume', label: 'Resume / CV' },
  { value: 'id_document', label: 'Identity Document' },
  { value: 'policy_acknowledgement', label: 'Policy Acknowledgement' },
  { value: 'certificate', label: 'Certificate / License' },
  { value: 'handbook', label: 'Employee Handbook' },
  { value: 'nda', label: 'NDA Agreement' },
  { value: 'other', label: 'Other' },
];

const DOC_TYPE_ICONS: Record<string, React.ReactNode> = {
  contract: <FileCheck className="h-5 w-5 text-blue-500" />,
  resume: <FileText className="h-5 w-5 text-purple-500" />,
  id_document: <Shield className="h-5 w-5 text-amber-500" />,
  policy_acknowledgement: <FileLock className="h-5 w-5 text-emerald-500" />,
  certificate: <FileCheck className="h-5 w-5 text-cyan-500" />,
  handbook: <FolderOpen className="h-5 w-5 text-orange-500" />,
  nda: <Lock className="h-5 w-5 text-red-500" />,
  other: <FileText className="h-5 w-5 text-muted-foreground" />,
};

function formatBytes(bytes: number): string {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function HRDocuments() {
  const { addNotification } = useNotification();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  // Upload form state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState('');
  const [uploadType, setUploadType] = useState('contract');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (filterType) params.doc_type = filterType;
      const res = await apiClient.get('/api/v1/documents', { params });
      setDocuments(res.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDocuments();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadFile(file);
      if (!uploadName) setUploadName(file.name.replace(/\.[^/.]+$/, ''));
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadName || !uploadType) {
      addNotification('Please fill all required fields and select a file', 'error');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('name', uploadName);
      formData.append('type', uploadType);
      formData.append('provider', 'local');
      await apiClient.post('/api/v1/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Document uploaded to secure vault successfully', 'success');
      setModalOpen(false);
      setUploadFile(null);
      setUploadName('');
      setUploadType('contract');
      fetchDocuments();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    setDeleting(id);
    try {
      await apiClient.delete(`/api/v1/documents/${id}`);
      addNotification('Document removed from secure vault', 'success');
      setConfirmDeleteId(null);
      fetchDocuments();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Delete failed', 'error');
    } finally {
      setDeleting(null);
    }
  };

  const handleDownload = async (doc: any) => {
    try {
      const res = await apiClient.get(`/api/v1/documents/${doc.id}/download`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Download failed', 'error');
    }
  };

  const getTypeLabel = (type: string) =>
    DOC_TYPE_OPTIONS.find((o) => o.value === type)?.label ?? type;

  const getTypeIcon = (type: string) => DOC_TYPE_ICONS[type] ?? DOC_TYPE_ICONS['other'];

  const statsMap = DOC_TYPE_OPTIONS.reduce(
    (acc, o) => {
      acc[o.value] = documents.filter((d) => d.type === o.value).length;
      return acc;
    },
    {} as Record<string, number>,
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Documents Vault</h1>
          <p className="text-sm text-muted-foreground">
            Securely store and manage identity proofs, contracts, certificates, and policy
            acknowledgements.
          </p>
        </div>
        <Button
          onClick={() => setModalOpen(true)}
          variant="primary"
          className="flex items-center gap-2"
        >
          <Upload className="h-4 w-4" />
          Upload Document
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Documents', value: documents.length, icon: <FileText className="h-4 w-4 text-primary" /> },
          {
            label: 'Contracts',
            value: statsMap['contract'] || 0,
            icon: <FileCheck className="h-4 w-4 text-blue-500" />,
          },
          {
            label: 'Identity Docs',
            value: statsMap['id_document'] || 0,
            icon: <Shield className="h-4 w-4 text-amber-500" />,
          },
          {
            label: 'NDA / Policy',
            value: (statsMap['nda'] || 0) + (statsMap['policy_acknowledgement'] || 0),
            icon: <Lock className="h-4 w-4 text-red-500" />,
          },
        ].map((stat, i) => (
          <Card key={i}>
            <CardContent className="pt-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-muted-foreground font-mono uppercase">{stat.label}</p>
                  <h3 className="text-2xl font-bold tracking-tight mt-1">{stat.value}</h3>
                </div>
                <div className="p-2 bg-secondary/30 rounded-lg">{stat.icon}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Search & Filter Bar */}
      <Card>
        <CardContent className="py-4">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search document name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 h-9 text-sm border border-input rounded-md bg-background px-3 focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="pl-8 h-9 text-sm border border-input rounded-md bg-background px-3 focus:outline-none focus:ring-2 focus:ring-ring min-w-[180px]"
              >
                <option value="">All Types</option>
                {DOC_TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <Button type="submit" variant="secondary" className="h-9 px-4 text-sm">
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Document Vault List */}
      <Card>
        <CardHeader>
          <CardTitle>Archived Identity &amp; Contracts</CardTitle>
          <CardDescription>
            Secure employee folders containing legal credentials, certificates, and NDA metadata.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="h-7 w-7 animate-spin text-primary" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 space-y-2">
              <FolderOpen className="h-10 w-10 text-muted-foreground mx-auto opacity-40" />
              <p className="text-sm text-muted-foreground italic">
                No documents found in the vault.
              </p>
              <p className="text-xs text-muted-foreground">
                Upload your first document using the button above.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex justify-between items-center p-3 border border-border rounded-lg bg-secondary/10 hover:bg-secondary/20 transition group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 bg-background border border-border rounded-lg shrink-0">
                      {getTypeIcon(doc.type)}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-sm font-semibold text-foreground truncate">{doc.name}</h4>
                      <p className="text-[10px] text-muted-foreground uppercase font-mono">
                        {getTypeLabel(doc.type)}
                        {doc.file_size ? ` • ${formatBytes(doc.file_size)}` : ''}
                        {doc.mime_type ? ` • ${doc.mime_type}` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right hidden sm:block">
                      <p className="text-[10px] text-muted-foreground font-mono">
                        {doc.created_at
                          ? new Date(doc.created_at).toLocaleDateString()
                          : '—'}
                      </p>
                      <div className="flex items-center gap-1 justify-end mt-0.5">
                        <Lock className="h-3 w-3 text-primary" />
                        <span className="text-[9px] text-primary font-mono uppercase">
                          {doc.storage_provider || 'local'}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition">
                      <button
                        onClick={() => handleDownload(doc)}
                        title="Download"
                        className="p-1.5 rounded border border-border hover:bg-primary/10 hover:border-primary/30 text-muted-foreground hover:text-primary transition"
                      >
                        <Download className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => setConfirmDeleteId(doc.id)}
                        title="Delete"
                        className="p-1.5 rounded border border-border hover:bg-red-500/10 hover:border-red-500/30 text-muted-foreground hover:text-red-500 transition"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Document Modal */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Upload Document">
        <form onSubmit={handleUpload} className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Document Type</label>
            <select
              value={uploadType}
              onChange={(e) => setUploadType(e.target.value)}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {DOC_TYPE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Document Name"
            value={uploadName}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUploadName(e.target.value)}
            placeholder="e.g. Employment Contract - John Doe"
          />

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">File</label>
            <div
              className="border-2 border-dashed border-border rounded-lg p-6 text-center cursor-pointer hover:border-primary/40 hover:bg-primary/5 transition"
              onClick={() => fileInputRef.current?.click()}
            >
              {uploadFile ? (
                <div className="space-y-1">
                  <FileText className="h-7 w-7 text-primary mx-auto" />
                  <p className="text-sm font-semibold text-foreground">{uploadFile.name}</p>
                  <p className="text-xs text-muted-foreground">{formatBytes(uploadFile.size)}</p>
                </div>
              ) : (
                <div className="space-y-1">
                  <Upload className="h-7 w-7 text-muted-foreground mx-auto opacity-50" />
                  <p className="text-sm text-muted-foreground">
                    Click to browse or drag & drop your file here
                  </p>
                  <p className="text-xs text-muted-foreground opacity-60">
                    PDF, DOCX, PNG, JPG — Max 25 MB
                  </p>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.txt"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={uploading}
              className="flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Uploading…
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Upload to Vault
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!confirmDeleteId}
        onClose={() => setConfirmDeleteId(null)}
        title="Confirm Delete"
      >
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Are you sure you want to permanently remove this document from the secure vault? This
            action cannot be undone.
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setConfirmDeleteId(null)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => confirmDeleteId && handleDelete(confirmDeleteId)}
              disabled={!!deleting}
              className="bg-red-500 hover:bg-red-600 text-white flex items-center gap-2"
            >
              {deleting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Removing…
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4" />
                  Delete Document
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default HRDocuments;
