import React, { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { FileText, Upload, Download, CheckCircle2, Shield } from "lucide-react";

export const MyDocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState([
    {
      id: "DOC-001",
      title: "Employment Contract Agreement",
      category: "CONTRACT",
      fileName: "employment_contract_signed.pdf",
      uploadDate: "Jan 15, 2024",
      size: "2.4 MB",
      status: "VERIFIED",
    },
    {
      id: "DOC-002",
      title: "Government Passport / Photo Identity",
      category: "IDENTITY",
      fileName: "passport_front_back.pdf",
      uploadDate: "Jan 12, 2024",
      size: "1.1 MB",
      status: "VERIFIED",
    },
    {
      id: "DOC-003",
      title: "Degree Certificate (B.S. Computer Science)",
      category: "EDUCATION",
      fileName: "degree_certificate.pdf",
      uploadDate: "Jan 12, 2024",
      size: "3.8 MB",
      status: "VERIFIED",
    },
    {
      id: "DOC-004",
      title: "Tax Withholding W-4 Declaration",
      category: "TAX",
      fileName: "tax_declaration_w4_2026.pdf",
      uploadDate: "Feb 01, 2026",
      size: "820 KB",
      status: "VERIFIED",
    },
  ]);

  const [isUploading, setIsUploading] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("IDENTITY");
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    const newDoc = {
      id: `DOC-00${documents.length + 1}`,
      title: newTitle || "Uploaded Official Document",
      category: newCategory,
      fileName: `${newTitle.toLowerCase().replace(/\s+/g, "_") || "doc"}.pdf`,
      uploadDate: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
      size: "1.5 MB",
      status: "PENDING",
    };
    setDocuments([newDoc, ...documents]);
    setUploadSuccess("Document uploaded securely to tenant vault and queued for HR verification.");
    setTimeout(() => {
      setIsUploading(false);
      setUploadSuccess(null);
      setNewTitle("");
    }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-400" />
            <span>My Documents & Statutory Vault</span>
          </h1>
          <p className="text-xs text-slate-400">
            Access your signed employment agreements, identity credentials, educational records, and tax forms.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setIsUploading(true)}
          className="text-xs font-semibold flex items-center gap-1.5"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Document</span>
        </Button>
      </div>

      {/* Upload Modal / Card */}
      {isUploading && (
        <div className="p-6 rounded-2xl border border-brand-500/40 bg-slate-900/95 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-100">Upload Statutory Document</h3>
            <button
              onClick={() => setIsUploading(false)}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
          </div>

          {uploadSuccess ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{uploadSuccess}</span>
            </div>
          ) : (
            <form onSubmit={handleUpload} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Document Title
                  </label>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. State Driving License or Certification"
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Category
                  </label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  >
                    <option value="IDENTITY">Identity Verification</option>
                    <option value="TAX">Tax & Remuneration</option>
                    <option value="EDUCATION">Educational Qualifications</option>
                    <option value="CONTRACT">Contract & NDA</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Select File (PDF, PNG, JPG - Max 10MB)
                </label>
                <input
                  type="file"
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsUploading(false)}
                  className="text-xs"
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" className="text-xs font-semibold">
                  Upload to Vault
                </Button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Documents Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-sm p-6 space-y-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Document Title</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>File Name</TableHead>
              <TableHead>File Size</TableHead>
              <TableHead>Upload Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell className="font-semibold text-slate-200">{doc.title}</TableCell>
                <TableCell>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {doc.category}
                  </span>
                </TableCell>
                <TableCell className="text-xs text-slate-400">{doc.fileName}</TableCell>
                <TableCell className="text-xs text-slate-500">{doc.size}</TableCell>
                <TableCell className="text-xs text-slate-400">{doc.uploadDate}</TableCell>
                <TableCell>
                  <StatusBadge status={doc.status} />
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => alert(`Downloading ${doc.fileName}...`)}
                    className="h-7 px-2 text-xs"
                  >
                    <Download className="w-3.5 h-3.5 text-brand-400 mr-1" />
                    Download
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
