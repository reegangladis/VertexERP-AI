/**
 * AI Knowledge Base & RAG Management Dashboard
 * VertexERP AI V2
 */

import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  Clock,
  Database,
  FileCode,
  FileText,
  Filter,
  Layers,
  Plus,
  RefreshCw,
  RotateCcw,
  Search,
  Shield,
  Sparkles,
  Tag,
  Trash2,
  X,
  XCircle,
} from "lucide-react";
import { aiApi } from "../api/aiApi";
import {
  RAGDocument,
  RAGDocumentDetail,
  RAGQueryCitation,
  RAGQueryResponse,
  RAGSearchResultItem,
} from "../types";

export const AIKnowledgeBasePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"documents" | "console" | "jobs">("documents");
  const [documents, setDocuments] = useState<RAGDocument[]>([]);
  const [totalDocs, setTotalDocs] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [accessFilter, setAccessFilter] = useState<string>("ALL");

  // Detail Drawer State
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [docDetail, setDocDetail] = useState<RAGDocumentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Upload Modal State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadDesc, setUploadDesc] = useState("");
  const [uploadContent, setUploadContent] = useState("");
  const [uploadFileType, setUploadFileType] = useState("markdown");
  const [uploadAccess, setUploadAccess] = useState("INTERNAL");
  const [uploadDept, setUploadDept] = useState("*");
  const [uploadTags, setUploadTags] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Version Upload State
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [versionDocId, setVersionDocId] = useState<string | null>(null);
  const [versionContent, setVersionContent] = useState("");
  const [versionChangelog, setVersionChangelog] = useState("");

  // RAG QA Console State
  const [queryInput, setQueryInput] = useState("");
  const [qaLoading, setQaLoading] = useState(false);
  const [qaResponse, setQaResponse] = useState<RAGQueryResponse | null>(null);
  const [searchResults, setSearchResults] = useState<RAGSearchResultItem[]>([]);
  const [consoleMode, setConsoleMode] = useState<"grounded" | "search">("grounded");

  useEffect(() => {
    loadDocuments();
  }, [accessFilter]);

  const loadDocuments = async () => {
    setIsLoading(true);
    try {
      const filterParam = accessFilter === "ALL" ? undefined : accessFilter;
      const res = await aiApi.listDocuments({
        access_level: filterParam,
        search: searchFilter || undefined,
      });
      setDocuments(res.items);
      setTotalDocs(res.total);
    } catch (err) {
      console.error("Failed to load knowledge documents:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenDocDetail = async (docId: string) => {
    setSelectedDocId(docId);
    setDetailLoading(true);
    try {
      const res = await aiApi.getDocumentDetails(docId);
      setDocDetail(res);
    } catch (err) {
      console.error("Failed to load document details:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreateDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadTitle.trim() || !uploadContent.trim()) return;

    setIsSubmitting(true);
    try {
      const tagsArray = uploadTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      const deptsArray = uploadDept
        .split(",")
        .map((d) => d.trim())
        .filter(Boolean);

      await aiApi.createDocument({
        title: uploadTitle,
        description: uploadDesc || undefined,
        raw_content: uploadContent,
        file_type: uploadFileType,
        access_level: uploadAccess,
        allowed_departments: deptsArray.length > 0 ? deptsArray : ["*"],
        allowed_roles: ["*"],
        tags: tagsArray,
      });

      setShowUploadModal(false);
      setUploadTitle("");
      setUploadDesc("");
      setUploadContent("");
      setUploadTags("");
      await loadDocuments();
    } catch (err) {
      console.error("Failed to upload document:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!versionDocId || !versionContent.trim()) return;

    setIsSubmitting(true);
    try {
      await aiApi.createDocumentVersion(versionDocId, {
        raw_content: versionContent,
        changelog: versionChangelog || undefined,
      });
      setShowVersionModal(false);
      setVersionContent("");
      setVersionChangelog("");
      if (selectedDocId === versionDocId) {
        await handleOpenDocDetail(versionDocId);
      }
      await loadDocuments();
    } catch (err) {
      console.error("Failed to create document version:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteDoc = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document from the knowledge base?")) return;
    try {
      await aiApi.deleteDocument(docId);
      if (selectedDocId === docId) setSelectedDocId(null);
      await loadDocuments();
    } catch (err) {
      console.error("Failed to delete document:", err);
    }
  };

  const handleRunQuery = async () => {
    if (!queryInput.trim()) return;
    setQaLoading(true);
    setQaResponse(null);
    setSearchResults([]);

    try {
      if (consoleMode === "grounded") {
        const resp = await aiApi.queryKnowledge({ query: queryInput, top_k: 5 });
        setQaResponse(resp);
      } else {
        const resp = await aiApi.searchKnowledge({ query: queryInput, top_k: 5 });
        setSearchResults(resp.results || []);
      }
    } catch (err) {
      console.error("RAG Query failed:", err);
    } finally {
      setQaLoading(false);
    }
  };

  const totalIndexedChunks = documents.reduce((acc, d) => acc + (d.total_chunks || 0), 0);

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] overflow-hidden bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="px-6 py-4 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white tracking-tight flex items-center space-x-2">
              <span>Knowledge Base & Production RAG</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono font-normal">
                Multi-Tenant Scoped
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Asynchronous document parsing, semantic chunking, 1536-dim embeddings, and grounded QA with verifiable citations
            </p>
          </div>
        </div>

        {/* Tab Switcher & Upload Button */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 space-x-1">
            <button
              onClick={() => setActiveTab("documents")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                activeTab === "documents"
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Document Repository
            </button>
            <button
              onClick={() => setActiveTab("console")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center space-x-1.5 ${
                activeTab === "console"
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>RAG QA Console</span>
            </button>
          </div>

          <button
            onClick={() => setShowUploadModal(true)}
            className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition flex items-center space-x-1.5 shadow-md shadow-indigo-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Upload Document</span>
          </button>
        </div>
      </header>

      {/* Metric Cards Banner */}
      <div className="grid grid-cols-4 gap-4 px-6 py-3 border-b border-slate-800/80 bg-slate-900/30">
        <div className="flex items-center space-x-3 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
          <FileText className="w-4 h-4 text-indigo-400" />
          <div>
            <div className="text-[11px] text-slate-400">Knowledge Documents</div>
            <div className="text-sm font-semibold text-white">{totalDocs}</div>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
          <Database className="w-4 h-4 text-emerald-400" />
          <div>
            <div className="text-[11px] text-slate-400">Indexed Chunks</div>
            <div className="text-sm font-semibold text-white">{totalIndexedChunks.toLocaleString()}</div>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
          <Shield className="w-4 h-4 text-amber-400" />
          <div>
            <div className="text-[11px] text-slate-400">Isolation Layer</div>
            <div className="text-sm font-semibold text-white">Strict Tenant Scoped</div>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
          <Layers className="w-4 h-4 text-purple-400" />
          <div>
            <div className="text-[11px] text-slate-400">Embedding Vectors</div>
            <div className="text-sm font-semibold text-white">1536 Dimensions</div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === "documents" && (
          <div className="space-y-4">
            {/* Filters Bar */}
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center space-x-2 flex-1 max-w-md">
                <div className="relative w-full">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                  <input
                    type="text"
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && loadDocuments()}
                    placeholder="Filter documents by title..."
                    className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <button
                  onClick={loadDocuments}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition"
                >
                  Search
                </button>
              </div>

              {/* Access Level Selector */}
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-400">Access Level:</span>
                {["ALL", "INTERNAL", "CONFIDENTIAL", "RESTRICTED", "PUBLIC"].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setAccessFilter(lvl)}
                    className={`px-2.5 py-1 rounded-md text-[11px] transition ${
                      accessFilter === lvl
                        ? "bg-indigo-600/30 border border-indigo-500/50 text-indigo-300 font-medium"
                        : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            {/* Document Table */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/90 text-slate-400 font-medium text-[11px]">
                    <th className="py-3 px-4">Title & Description</th>
                    <th className="py-3 px-4">Format</th>
                    <th className="py-3 px-4">Access Level</th>
                    <th className="py-3 px-4">Version</th>
                    <th className="py-3 px-4">Chunks</th>
                    <th className="py-3 px-4">Ingestion Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {isLoading ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500">
                        <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-indigo-400" />
                        Loading documents...
                      </td>
                    </tr>
                  ) : documents.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500">
                        No documents found. Click "Upload Document" to index your first SOP or guide.
                      </td>
                    </tr>
                  ) : (
                    documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                        <td className="py-3 px-4 max-w-xs">
                          <div className="font-medium text-slate-200 truncate">{doc.title}</div>
                          {doc.description && (
                            <div className="text-[11px] text-slate-500 truncate">{doc.description}</div>
                          )}
                          {doc.tags && doc.tags.length > 0 && (
                            <div className="flex items-center space-x-1 mt-1">
                              {doc.tags.map((t, idx) => (
                                <span
                                  key={idx}
                                  className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700/50"
                                >
                                  #{t}
                                </span>
                              ))}
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-4 uppercase text-[10px] font-mono text-slate-400">
                          {doc.file_type}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${
                              doc.access_level === "CONFIDENTIAL"
                                ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                                : doc.access_level === "RESTRICTED"
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                                : "bg-indigo-500/10 border-indigo-500/30 text-indigo-300"
                            }`}
                          >
                            {doc.access_level}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-300">v{doc.active_version || 1}</td>
                        <td className="py-3 px-4 text-slate-300">{doc.total_chunks || 0}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center space-x-1 text-[10px] px-2 py-0.5 rounded-full font-medium border ${
                              doc.latest_job_status === "COMPLETED"
                                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                                : doc.latest_job_status === "PROCESSING"
                                ? "bg-indigo-500/10 border-indigo-500/30 text-indigo-400 animate-pulse"
                                : doc.latest_job_status === "FAILED"
                                ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                                : "bg-slate-800 border-slate-700 text-slate-400"
                            }`}
                          >
                            {doc.latest_job_status === "COMPLETED" && <CheckCircle2 className="w-3 h-3" />}
                            {doc.latest_job_status === "PROCESSING" && <RefreshCw className="w-3 h-3 animate-spin" />}
                            {doc.latest_job_status === "FAILED" && <XCircle className="w-3 h-3" />}
                            <span>{doc.latest_job_status || "PENDING"}</span>
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right space-x-2">
                          <button
                            onClick={() => handleOpenDocDetail(doc.id)}
                            className="p-1 text-slate-400 hover:text-indigo-400 transition"
                            title="View Chunks & Details"
                          >
                            <FileCode className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              setVersionDocId(doc.id);
                              setShowVersionModal(true);
                            }}
                            className="p-1 text-slate-400 hover:text-emerald-400 transition"
                            title="Upload New Version"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteDoc(doc.id)}
                            className="p-1 text-slate-400 hover:text-rose-400 transition"
                            title="Delete Document"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* RAG QA Console & Citation Inspector Tab */}
        {activeTab === "console" && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    <span>Grounded RAG QA Console</span>
                  </h2>
                  <p className="text-[11px] text-slate-400">
                    Ask questions across indexed documents. Verifiable in-line citations are extracted automatically.
                  </p>
                </div>
                <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-[11px]">
                  <button
                    onClick={() => setConsoleMode("grounded")}
                    className={`px-2.5 py-1 rounded-md transition ${
                      consoleMode === "grounded" ? "bg-indigo-600 text-white font-medium" : "text-slate-400"
                    }`}
                  >
                    Grounded Answer
                  </button>
                  <button
                    onClick={() => setConsoleMode("search")}
                    className={`px-2.5 py-1 rounded-md transition ${
                      consoleMode === "search" ? "bg-indigo-600 text-white font-medium" : "text-slate-400"
                    }`}
                  >
                    Raw Vector Search
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleRunQuery()}
                  placeholder="Ask a question (e.g. What is the stock transfer authorization procedure?)..."
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  disabled={qaLoading || !queryInput.trim()}
                  onClick={handleRunQuery}
                  className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium rounded-xl transition flex items-center space-x-1.5 shadow-md shadow-indigo-600/20"
                >
                  {qaLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  <span>Ask Knowledge Base</span>
                </button>
              </div>
            </div>

            {/* QA Response Card */}
            {qaResponse && (
              <div className="rounded-xl border border-indigo-500/30 bg-slate-900/90 p-5 space-y-4 shadow-xl shadow-indigo-950/20 animate-in fade-in">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2 text-xs font-medium text-indigo-400">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Grounded Knowledge Answer</span>
                  </div>
                  <div className="flex items-center space-x-3 text-[10px] text-slate-400 font-mono">
                    <span>{qaResponse.latency_ms} ms</span>
                    <span>•</span>
                    <span>{qaResponse.total_tokens} tokens</span>
                    <span>•</span>
                    <span>${qaResponse.cost_usd.toFixed(5)}</span>
                  </div>
                </div>

                {/* Markdown Answer */}
                <div className="text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {qaResponse.answer}
                </div>

                {/* Structured Citations */}
                {qaResponse.citations && qaResponse.citations.length > 0 && (
                  <div className="border-t border-slate-800/80 pt-3 space-y-2">
                    <div className="text-[11px] font-semibold text-slate-300 flex items-center space-x-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Verified In-Line Citations ({qaResponse.citations.length})</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2.5">
                      {qaResponse.citations.map((cite, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] space-y-1"
                        >
                          <div className="font-medium text-indigo-300 flex items-center justify-between">
                            <span className="truncate">{cite.document_title}</span>
                            <span className="text-[9px] font-mono text-slate-500">
                              v{cite.version_number} #C{cite.chunk_index}
                            </span>
                          </div>
                          {cite.section_heading && (
                            <div className="text-[10px] text-slate-400 font-mono">
                              § {cite.section_heading}
                            </div>
                          )}
                          <p className="text-[10px] text-slate-400 line-clamp-2 italic">
                            "{cite.snippet}"
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Raw Search Results */}
            {searchResults.length > 0 && (
              <div className="space-y-3">
                <div className="text-xs font-semibold text-slate-300">
                  Top Matched Document Chunks ({searchResults.length})
                </div>
                {searchResults.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-slate-200">{item.document_title}</span>
                      <div className="flex items-center space-x-2 text-[10px] font-mono text-indigo-400">
                        <span>Score: {item.composite_score.toFixed(3)}</span>
                        <span>•</span>
                        <span>v{item.version_number}</span>
                      </div>
                    </div>
                    <div className="text-[11px] text-slate-300 font-sans whitespace-pre-wrap">
                      {item.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Document Detail Drawer */}
      {selectedDocId && (
        <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl p-6 z-50 overflow-y-auto space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-semibold text-white">Document Details</h3>
            <button
              onClick={() => setSelectedDocId(null)}
              className="p-1 text-slate-400 hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {detailLoading ? (
            <div className="py-8 text-center text-slate-500">
              <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-2 text-indigo-400" />
              Loading...
            </div>
          ) : docDetail ? (
            <div className="space-y-4 text-xs">
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-mono">Title</div>
                <div className="font-medium text-white">{docDetail.title}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-mono">Access Level</div>
                <div className="text-slate-300">{docDetail.access_level}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-mono">Allowed Departments</div>
                <div className="text-slate-300">
                  {docDetail.allowed_departments.join(", ")}
                </div>
              </div>

              {/* Version History */}
              <div className="border-t border-slate-800 pt-3">
                <div className="text-[11px] font-semibold text-slate-300 mb-2">Version History</div>
                <div className="space-y-2">
                  {docDetail.versions.map((v) => (
                    <div
                      key={v.id}
                      className="p-2 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px]"
                    >
                      <div className="flex items-center justify-between font-medium">
                        <span className="text-indigo-400">Version {v.version_number}</span>
                        <span className="text-[9px] text-slate-500 font-mono">
                          {new Date(v.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {v.changelog && <div className="text-slate-400 mt-0.5">{v.changelog}</div>}
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Chunks */}
              <div className="border-t border-slate-800 pt-3">
                <div className="text-[11px] font-semibold text-slate-300 mb-2">
                  Indexed Chunks ({docDetail.recent_chunks.length})
                </div>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {docDetail.recent_chunks.map((c) => (
                    <div
                      key={c.id}
                      className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] space-y-1 font-mono text-slate-400"
                    >
                      <div className="text-slate-300 font-semibold">Chunk #{c.chunk_index}</div>
                      <div className="line-clamp-3 text-slate-400">{c.content}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* Upload Document Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl p-6 space-y-4 shadow-2xl animate-in fade-in">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-indigo-400" />
                <span>Upload Knowledge Document</span>
              </h2>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateDocument} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Document Title *</label>
                <input
                  type="text"
                  required
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g. Standard Warehouse Stock Transfer Policy"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Access Classification</label>
                  <select
                    value={uploadAccess}
                    onChange={(e) => setUploadAccess(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="INTERNAL">INTERNAL (All Employees)</option>
                    <option value="CONFIDENTIAL">CONFIDENTIAL (Managers/Execs)</option>
                    <option value="RESTRICTED">RESTRICTED (Explicit Dept/Role)</option>
                    <option value="PUBLIC">PUBLIC</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Allowed Department(s)</label>
                  <input
                    type="text"
                    value={uploadDept}
                    onChange={(e) => setUploadDept(e.target.value)}
                    placeholder="* or Operations, Finance"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Tags (comma separated)</label>
                <input
                  type="text"
                  value={uploadTags}
                  onChange={(e) => setUploadTags(e.target.value)}
                  placeholder="sop, inventory, procurement, compliance"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Document Content (Markdown/Text) *</label>
                <textarea
                  required
                  rows={8}
                  value={uploadContent}
                  onChange={(e) => setUploadContent(e.target.value)}
                  placeholder="# Warehouse SOP&#10;&#10;## 1. Stock Transfers&#10;All transfers above 50 units require secondary supervisor approval..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 font-mono text-xs focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-3.5 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-300 text-xs transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition flex items-center space-x-1"
                >
                  {isSubmitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                  <span>Create & Ingest</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Version Upload Modal */}
      {showVersionModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-semibold text-white">Upload New Document Version</h2>
              <button
                onClick={() => setShowVersionModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateVersion} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Changelog Summary</label>
                <input
                  type="text"
                  value={versionChangelog}
                  onChange={(e) => setVersionChangelog(e.target.value)}
                  placeholder="e.g. Updated approval limits for Q3"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Updated Content *</label>
                <textarea
                  required
                  rows={8}
                  value={versionContent}
                  onChange={(e) => setVersionContent(e.target.value)}
                  placeholder="Paste revised content here..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 font-mono text-xs focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowVersionModal(false)}
                  className="px-3.5 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-300 text-xs transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition flex items-center space-x-1"
                >
                  {isSubmitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
                  <span>Ingest Version</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
