import React, { useState, useEffect } from 'react';
import { Plus, Percent, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, TaxProfile } from '@/services/financeService';

export function TaxesPage() {
  const { addNotification } = useNotification();
  const [profiles, setProfiles] = useState<TaxProfile[]>([]);
  const [loading, setLoading] = useState(false);

  const loadTaxes = async () => {
    setLoading(true);
    try {
      const data = await financeService.getTaxProfiles();
      setProfiles(data);
    } catch (err) {
      addNotification('Failed to load tax profiles.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTaxes();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tax Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Configure jurisdiction tax profiles, GST/VAT rates, and compliance tax filings
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Jurisdiction Tax Profiles & GST/VAT Rates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {profiles.map((p) => (
              <div key={p.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg flex justify-between items-center">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-gray-900 dark:text-white">{p.name}</h4>
                    {p.is_default && (
                      <span className="px-2 py-0.5 text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 rounded">
                        Default
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Country: {p.country} | Standard Tax Engine Enabled</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-mono font-bold text-lg text-blue-600 dark:text-blue-400">10.0% VAT</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
