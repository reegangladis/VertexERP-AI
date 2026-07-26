import React, { useState } from 'react';
import { Activity, Play, Plus, AlertOctagon, CheckCircle2, ShieldAlert } from 'lucide-react';
import { manufacturingService } from '@/services/manufacturingService';

export function ShopFloorPage() {
  const [orderId, setOrderId] = useState<string>('');
  const [operator, setOperator] = useState<string>('');
  const [qtyProduced, setQtyProduced] = useState<number>(10);
  const [scrapQty, setScrapQty] = useState<number>(0);
  const [notes, setNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderId) {
      alert('Please enter a valid Production Order UUID');
      return;
    }
    setSubmitting(true);
    setMessage(null);
    try {
      await manufacturingService.logShopFloorProgress({
        production_order_id: orderId,
        operator_name: operator || 'Floor Operator 1',
        quantity_produced: Number(qtyProduced),
        scrap_quantity: Number(scrapQty),
        notes,
      });
      setMessage('Shop Floor progress successfully logged!');
      setQtyProduced(10);
      setScrapQty(0);
      setNotes('');
    } catch (err) {
      console.error('Failed to log shop floor progress', err);
      setMessage('Failed to submit production log.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <div className="border-b border-border pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          Shop Floor Operator Execution & Progress Logging
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Real-time Output Recording, Material Consumption & Scrap Tracking
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
        {message && (
          <div
            className={`p-4 rounded-lg text-xs font-semibold ${
              message.includes('successfully')
                ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                : 'bg-red-500/10 text-red-500 border border-red-500/20'
            }`}
          >
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">Production Order ID (UUID)</label>
            <input
              type="text"
              placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              required
              className="w-full px-3 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Operator Name</label>
              <input
                type="text"
                placeholder="Operator / Station Lead Name"
                value={operator}
                onChange={(e) => setOperator(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Good Quantity Produced</label>
              <input
                type="number"
                value={qtyProduced}
                onChange={(e) => setQtyProduced(Number(e.target.value))}
                min={1}
                required
                className="w-full px-3 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Scrap / Defect Quantity</label>
              <input
                type="number"
                value={scrapQty}
                onChange={(e) => setScrapQty(Number(e.target.value))}
                min={0}
                className="w-full px-3 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono text-red-500"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Execution Notes</label>
              <input
                type="text"
                placeholder="Shift comments or batch details..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>

          <div className="pt-3">
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
            >
              {submitting ? 'Submitting Execution Log...' : 'Record Production Log'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
