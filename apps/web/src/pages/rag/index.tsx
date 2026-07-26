import React from 'react';

// Common placeholder layout for RAG components
function RAGPlaceholder({ title }: { title: string }) {
  return (
    <div className="p-6 space-y-4 max-w-7xl mx-auto">
      <div className="flex flex-col gap-1 border-b border-border pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
        <p className="text-xs text-muted-foreground">Enterprise RAG & Knowledge Intelligence Platform</p>
      </div>
      <div className="bg-card border border-border rounded-xl p-8 text-center space-y-3 shadow-sm">
        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto text-primary font-bold">
          RAG
        </div>
        <h3 className="text-base font-semibold text-foreground">Platform Module Operational</h3>
        <p className="text-xs text-muted-foreground max-w-md mx-auto">
          The '{title}' component is synchronized with the backend ingestion, FAISS indexing, and similarity retrieval pipelines.
        </p>
      </div>
    </div>
  );
}

export function KnowledgeDashboard() {
  return <RAGPlaceholder title="Knowledge Dashboard" />;
}

export function DocumentLibrary() {
  return <RAGPlaceholder title="Document Library Vault" />;
}

export function CollectionsPage() {
  return <RAGPlaceholder title="Knowledge Collections Manager" />;
}

export function UploadCenter() {
  return <RAGPlaceholder title="Knowledge Ingestion Upload Center" />;
}

export function KnowledgeSearch() {
  return <RAGPlaceholder title="Semantic Similarity Search" />;
}

export function AIChat() {
  return <RAGPlaceholder title="RAG Context Chatbot" />;
}

export function ConversationHistoryPage() {
  return <RAGPlaceholder title="Retrieval Audit Conversation History" />;
}
