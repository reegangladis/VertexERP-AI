import React, { useEffect, useState } from 'react';
import {
  FileText,
  Search,
  Shield,
  Tag,
  UserCheck,
  CheckCircle2,
  Lock,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';
import { dataEngineeringApi } from '@/services/dataEngineeringApi';

export function MetadataCatalogPage() {
  const [catalog, setCatalog] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function load() {
      const data = await dataEngineeringApi.getMetadataCatalog();
      setCatalog(data);
    }
    load();
  }, []);

  const filteredCatalog = catalog.filter(
    (item) =>
      item.column_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.business_definition.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Data Catalog & Metadata Glossary"
        subtitle="Searchable business data dictionary, column definitions, PII classification, and data steward assignments"
      />

      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div className="relative w-72">
            <Input
              placeholder="Search catalog fields..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
            <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
          </div>
          <div className="text-xs text-slate-500">
            Showing <span className="font-bold text-slate-900">{filteredCatalog.length}</span> cataloged attributes
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-slate-700 uppercase text-xs font-semibold">
              <tr>
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-4">Data Type</th>
                <th className="py-3 px-4">Business Definition</th>
                <th className="py-3 px-4">PII Sensitivity</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4">Data Steward</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredCatalog.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-slate-900">{item.column_name}</td>
                  <td className="py-3 px-4 font-mono text-xs text-indigo-600">{item.data_type}</td>
                  <td className="py-3 px-4 text-xs text-slate-600">{item.business_definition}</td>
                  <td className="py-3 px-4">
                    {item.is_pii ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        <Lock className="h-3 w-3 mr-1" />
                        PII Protected
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                        Non-PII
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 font-semibold text-xs text-slate-700">{item.classification}</td>
                  <td className="py-3 px-4 text-xs font-medium text-slate-800">{item.data_steward || 'Unassigned'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
