import React, { useEffect, useState } from 'react';
import {
  Table as TableIcon,
  Download,
  Search,
  Database,
  FileCode,
  Layers,
  CheckCircle2,
  Tag,
  Clock,
  Sparkles,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { dataEngineeringApi, Dataset } from '@/services/dataEngineeringApi';

export function DatasetExplorer() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await dataEngineeringApi.getDatasets();
      setDatasets(data);
      if (data.length > 0) {
        setSelectedDataset(data[0]);
      }
      setLoading(false);
    }
    load();
  }, []);

  const filteredDatasets = datasets.filter(
    (d) =>
      d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dataset Explorer & Data Catalog"
        subtitle="Explore pre-generated enterprise analytics datasets (Employee, Customer, Inventory, Financial, Manufacturing, Sales, Supplier)"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: List of Datasets */}
        <Card className="p-4 space-y-4">
          <div className="relative">
            <Input
              placeholder="Search datasets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
            <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {filteredDatasets.map((ds) => (
              <div
                key={ds.id}
                onClick={() => setSelectedDataset(ds)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedDataset?.id === ds.id
                    ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex justify-between items-start">
                  <h4 className="font-semibold text-sm text-slate-900">{ds.name}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    {ds.category}
                  </span>
                </div>
                <p className="text-xs text-slate-500 line-clamp-2 mt-1">{ds.description}</p>
                <div className="flex items-center justify-between mt-3 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <TableIcon className="h-3 w-3" />
                    {ds.record_count.toLocaleString()} rows
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {ds.update_frequency}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Right Column: Dataset Details & Schema Viewer */}
        {selectedDataset && (
          <div className="lg:col-span-2 space-y-6">
            <Card className="p-6">
              <div className="flex justify-between items-start border-b border-slate-100 pb-4 mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-bold text-slate-900">{selectedDataset.name}</h3>
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                      v1.0.0 Snapshot
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">{selectedDataset.description}</p>
                </div>
                <Button size="sm" variant="outline" onClick={() => alert(`Exporting ${selectedDataset.slug}.json file...`)}>
                  <Download className="h-4 w-4 mr-2" />
                  Export Dataset JSON
                </Button>
              </div>

              {/* Metadata Highlights */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-xs text-slate-500">Storage Location</span>
                  <p className="text-xs font-mono font-semibold text-slate-900 truncate mt-0.5">
                    {selectedDataset.data_lake_path || `datasets/${selectedDataset.slug}.json`}
                  </p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-xs text-slate-500">Record Volume</span>
                  <p className="text-xs font-semibold text-slate-900 mt-0.5">
                    {selectedDataset.record_count.toLocaleString()} Records
                  </p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-xs text-slate-500">Ownership Team</span>
                  <p className="text-xs font-semibold text-slate-900 mt-0.5">{selectedDataset.ownership_team}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-xs text-slate-500">Data Steward</span>
                  <p className="text-xs font-semibold text-slate-900 mt-0.5">{selectedDataset.data_steward || 'Enterprise Architect'}</p>
                </div>
              </div>

              {/* Data Schema & Column Attributes */}
              <div>
                <h4 className="font-semibold text-sm text-slate-900 mb-3 flex items-center">
                  <FileCode className="h-4 w-4 mr-2 text-indigo-600" />
                  Schema Field Definitions & AI Vector Flags
                </h4>

                <div className="bg-slate-950 p-4 rounded-lg text-xs font-mono text-slate-200 overflow-x-auto">
                  <pre>{JSON.stringify(selectedDataset.schema_definition, null, 2)}</pre>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
