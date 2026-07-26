import React, { useState, useEffect } from 'react';
import { Plus, Box, Trash2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, FixedAsset } from '@/services/financeService';

export function FixedAssetsPage() {
  const { addNotification } = useNotification();
  const [assets, setAssets] = useState<FixedAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    asset_name: 'High Performance Server Rack',
    purchase_date: new Date().toISOString().split('T')[0],
    purchase_cost: 12500,
    salvage_value: 1500,
  });

  const loadAssets = async () => {
    setLoading(true);
    try {
      const data = await financeService.getFixedAssets();
      setAssets(data);
    } catch (err) {
      addNotification('Failed to load fixed assets.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssets();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const cats = await financeService.getAssetCategories();
      const catId = cats.length > 0 ? cats[0].id : '00000000-0000-0000-0000-000000000004';
      await financeService.createFixedAsset({ ...formData, category_id: catId });
      addNotification('Fixed asset registered.', 'success');
      setIsModalOpen(false);
      loadAssets();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to register asset.', 'error');
    }
  };

  const handleDispose = async (id: string) => {
    try {
      await financeService.disposeFixedAsset(id, 2000);
      addNotification('Asset marked as disposed.', 'success');
      loadAssets();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to dispose asset.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Fixed Asset Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Maintain fixed asset register, calculate straight-line depreciation, and process asset disposals
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> Register Asset
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Asset Register</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                <tr>
                  <th className="py-3 px-4">Asset #</th>
                  <th className="py-3 px-4">Asset Name</th>
                  <th className="py-3 px-4">Purchase Date</th>
                  <th className="py-3 px-4 text-right">Cost</th>
                  <th className="py-3 px-4 text-right">Book Value</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {assets.map((ast) => (
                  <tr key={ast.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 font-mono font-bold text-purple-600 dark:text-purple-400">{ast.asset_number}</td>
                    <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{ast.asset_name}</td>
                    <td className="py-3 px-4">{ast.purchase_date}</td>
                    <td className="py-3 px-4 text-right font-mono">${ast.purchase_cost?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold">${ast.current_value?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          ast.status === 'ACTIVE'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                        }`}
                      >
                        {ast.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {ast.status === 'ACTIVE' && (
                        <Button size="sm" variant="outline" onClick={() => handleDispose(ast.id)}>
                          <Trash2 className="w-3.5 h-3.5 mr-1 text-rose-500" /> Dispose
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Register Fixed Asset</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Asset Name</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.asset_name}
                  onChange={(e) => setFormData({ ...formData, asset_name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Purchase Cost ($)</label>
                  <input
                    type="number"
                    required
                    className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                    value={formData.purchase_cost}
                    onChange={(e) => setFormData({ ...formData, purchase_cost: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Salvage Value ($)</label>
                  <input
                    type="number"
                    className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                    value={formData.salvage_value}
                    onChange={(e) => setFormData({ ...formData, salvage_value: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit">Save Asset</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
