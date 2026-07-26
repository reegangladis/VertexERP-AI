import { useEffect, useState } from 'react';
import { Layers, Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

interface Opportunity {
  id: string;
  title: string;
  description: string | null;
  stage: string;
  close_date: string;
}

export function CRMPipeline() {
  const { addNotification } = useNotification();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchOpps = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get('/api/v1/crm/deals/opportunities');
        setOpportunities(res.data.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchOpps();
  }, []);

  const stages = ['qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Sales pipeline</h1>
        <p className="text-sm text-muted-foreground">Monitor corporate deal flows and verify deal staging statuses.</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {stages.map((stage) => {
            const stageOpps = opportunities.filter((o) => o.stage === stage);
            return (
              <div key={stage} className="space-y-3 bg-secondary/10 p-3 rounded border border-border h-[400px] overflow-y-auto">
                <div className="flex justify-between items-center border-b border-border pb-2">
                  <span className="text-[10px] font-bold font-mono uppercase tracking-wider text-muted-foreground">{stage.replace('_', ' ')}</span>
                  <span className="bg-secondary/40 border border-border px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold">
                    {stageOpps.length}
                  </span>
                </div>

                <div className="space-y-2">
                  {stageOpps.map((opp) => (
                    <div key={opp.id} className="p-3 border border-border bg-card rounded shadow-sm text-xs space-y-1">
                      <h4 className="font-semibold text-foreground">{opp.title}</h4>
                      <p className="text-muted-foreground line-clamp-2">{opp.description || 'No description logged'}</p>
                      <div className="text-[10px] text-muted-foreground font-mono pt-1">
                        Close target: {opp.close_date}
                      </div>
                    </div>
                  ))}
                  {stageOpps.length === 0 && (
                    <p className="text-[10px] text-muted-foreground/60 italic text-center py-4">No opportunities in this stage.</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
export default CRMPipeline;
