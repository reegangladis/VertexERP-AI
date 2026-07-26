import { FileText, ShieldAlert, Award, FileSpreadsheet, Lock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';

export function HRDocuments() {
  const documents = [
    { name: 'Standard Employment Agreement.pdf', type: 'contract', size: '2.4 MB', updated: '2026-07-24' },
    { name: 'Candidate Resume - Sarah Connor.pdf', type: 'resume', size: '1.1 MB', updated: '2026-07-20' },
    { name: 'National ID scan - Tony Stark.pdf', type: 'id_document', size: '4.8 MB', updated: '2026-07-15' },
    { name: 'NDA Acknowledgement template.pdf', type: 'policy_acknowledgement', size: '420 KB', updated: '2026-07-02' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Documents Vault</h1>
        <p className="text-sm text-muted-foreground">Store and review sensitive identity proofs, passports, certificates, and NDA acknowledgements.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Archived Identity & Contracts</CardTitle>
          <CardDescription>Secure employee folders containing legal credentials metadata.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {documents.map((doc, idx) => (
              <div key={idx} className="flex justify-between items-center p-3 border border-border rounded bg-secondary/15 hover:bg-secondary/25 transition">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-foreground">{doc.name}</h4>
                    <p className="text-[10px] text-muted-foreground uppercase font-mono">{doc.type} • {doc.size}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
                  <span>Logged: {doc.updated}</span>
                  <Lock className="h-3.5 w-3.5 text-primary shrink-0" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
export default HRDocuments;
