import React, { useEffect, useState } from 'react';
import {
  Users,
  Target,
  FileText,
  ShoppingBag,
  Briefcase,
  CheckSquare,
  Calendar,
  Clock,
  TrendingUp,
  Plus,
  ArrowUpRight,
  Filter,
  Search,
  Download,
  DollarSign,
  UserCheck,
  Building2,
  FileCheck,
  Sparkles,
} from 'lucide-react';
import {
  crmSalesService,
  CRMDashboardSummary,
  Lead,
  Customer,
  Opportunity,
  Quotation,
  SalesOrder,
  CRMTask,
  Meeting,
} from '../../services/crmSales';

export function CrmModule() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'leads' | 'customers' | 'pipeline' | 'quotations' | 'orders' | 'tasks'
  >('dashboard');
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<CRMDashboardSummary | null>(null);

  const [leads, setLeads] = useState<Lead[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [tasks, setTasks] = useState<CRMTask[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);

  // Modals & form state
  const [showLeadModal, setShowLeadModal] = useState<boolean>(false);
  const [showConvertModal, setShowConvertModal] = useState<boolean>(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  // Form inputs
  const [companyName, setCompanyName] = useState('');
  const [contactName, setContactName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [expectedVal, setExpectedVal] = useState(50000);

  const [customerCode, setCustomerCode] = useState('');
  const [oppTitle, setOppTitle] = useState('');

  const mockOrgId = '00000000-0000-0000-0000-000000000001';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, leadsRes, custRes, oppRes, qRes, soRes, taskRes, mtgRes] = await Promise.all([
        crmSalesService.getDashboardSummary(mockOrgId).catch(() => null),
        crmSalesService.getLeads(mockOrgId).catch(() => []),
        crmSalesService.getCustomers(mockOrgId).catch(() => []),
        crmSalesService.getOpportunities().catch(() => []),
        crmSalesService.getQuotations().catch(() => []),
        crmSalesService.getSalesOrders().catch(() => []),
        crmSalesService.getTasks().catch(() => []),
        crmSalesService.getMeetings().catch(() => []),
      ]);

      setSummary(
        sumRes || {
          total_leads: leadsRes.length,
          qualified_leads: leadsRes.filter((l) => l.status === 'Qualified').length,
          total_customers: custRes.length,
          open_opportunities: oppRes.filter((o) => o.status === 'Open').length,
          pipeline_value: oppRes.reduce((acc, o) => acc + o.expected_revenue, 0),
          sales_revenue: soRes.reduce((acc, s) => acc + s.grand_total, 0),
          pending_quotations: qRes.filter((q) => q.status === 'Draft').length,
          total_sales_orders: soRes.length,
          meetings_today: mtgRes.length,
          tasks_due: taskRes.length,
        }
      );

      setLeads(leadsRes);
      setCustomers(custRes);
      setOpportunities(oppRes);
      setQuotations(qRes);
      setOrders(soRes);
      setTasks(taskRes);
      setMeetings(mtgRes);
    } catch (err) {
      console.error('Failed to load CRM data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await crmSalesService.createLead({
        organization_id: mockOrgId,
        company_name: companyName,
        contact_name: contactName,
        email: email,
        phone: phone,
        expected_value: expectedVal,
        status: 'New',
        priority: 'High',
      });
      setShowLeadModal(false);
      setCompanyName('');
      setContactName('');
      setEmail('');
      setPhone('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create lead');
    }
  };

  const handleConvertLead = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLead) return;
    try {
      await crmSalesService.convertLead(selectedLead.id, {
        customer_code: customerCode || `CUST-${Math.floor(1000 + Math.random() * 9000)}`,
        opportunity_title: oppTitle || `Enterprise Opportunity - ${selectedLead.company_name}`,
        expected_revenue: selectedLead.expected_value,
      });
      setShowConvertModal(false);
      setSelectedLead(null);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to convert lead');
    }
  };

  const handleDownloadPDF = async (quotationNumber: string) => {
    try {
      const pdfText = await crmSalesService.downloadQuotationPDF(quotationNumber);
      const element = document.createElement('a');
      const file = new Blob([pdfText], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = `Quotation_${quotationNumber}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (err: any) {
      alert('Failed to download quotation PDF.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 shadow-lg shadow-indigo-500/30">
              <TrendingUp className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
                Enterprise CRM & Sales Platform
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Sales Pipeline, Lead Scoring, Quotes, Orders & Executive Customer Analytics
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowLeadModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-blue-600 hover:from-indigo-600 hover:to-blue-700 text-white px-4 py-2.5 rounded-lg font-medium shadow-md shadow-indigo-500/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Add Lead
          </button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'dashboard', label: 'Executive Dashboard', icon: TrendingUp },
          { id: 'leads', label: 'Leads & Capture', icon: Target },
          { id: 'customers', label: 'Customer Accounts', icon: Building2 },
          { id: 'pipeline', label: 'Sales Pipeline', icon: Briefcase },
          { id: 'quotations', label: 'Quotations & Quotes', icon: FileText },
          { id: 'orders', label: 'Sales Orders', icon: ShoppingBag },
          { id: 'tasks', label: 'Meetings & Tasks', icon: CheckSquare },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap cursor-pointer ${
                active
                  ? 'bg-slate-800 text-indigo-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Tab Contents */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Pipeline Value</span>
                <DollarSign className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                ${summary?.pipeline_value.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
                <ArrowUpRight className="w-3.5 h-3.5" /> +14.2% from last quarter
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Sales Revenue</span>
                <ShoppingBag className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                ${summary?.sales_revenue.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-slate-400 mt-2">Confirmed closed orders</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total Leads</span>
                <Target className="w-5 h-5 text-amber-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.total_leads || 0}
              </div>
              <p className="text-xs text-amber-400 mt-2">
                {summary?.qualified_leads || 0} Qualified Leads
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Customer Accounts</span>
                <Building2 className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.total_customers || 0}
              </div>
              <p className="text-xs text-purple-400 mt-2">
                {summary?.open_opportunities || 0} Active Deals
              </p>
            </div>
          </div>

          {/* Quick Analytics & Pipeline Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-indigo-400" /> Active Opportunities & Deals
              </h3>
              <div className="space-y-3">
                {opportunities.length === 0 ? (
                  <p className="text-slate-500 text-sm">No active opportunities in pipeline.</p>
                ) : (
                  opportunities.slice(0, 5).map((opp) => (
                    <div
                      key={opp.id}
                      className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-semibold text-slate-200">{opp.title}</div>
                        <div className="text-xs text-slate-400 mt-0.5">
                          Stage: <span className="text-indigo-400">{opp.stage}</span> | Probability: {opp.probability}%
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-emerald-400">
                          ${opp.expected_revenue.toLocaleString()}
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          Close Date: {opp.expected_close_date}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-400" /> Executive Schedule
              </h3>
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/60">
                  <div className="text-xs text-slate-400 mb-1">Meetings Scheduled</div>
                  <div className="text-xl font-bold text-white">
                    {summary?.meetings_today || 0} Meetings
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/60">
                  <div className="text-xs text-slate-400 mb-1">CRM Tasks Pending</div>
                  <div className="text-xl font-bold text-white">{summary?.tasks_due || 0} Tasks</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/60">
                  <div className="text-xs text-slate-400 mb-1">Pending Quotes</div>
                  <div className="text-xl font-bold text-white">
                    {summary?.pending_quotations || 0} Draft Quotes
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leads Tab */}
      {activeTab === 'leads' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Leads Directory</h3>
            <button
              onClick={() => setShowLeadModal(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-2 rounded-lg text-sm font-medium cursor-pointer"
            >
              + Add New Lead
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">Company</th>
                  <th className="p-3.5">Contact Person</th>
                  <th className="p-3.5">Email</th>
                  <th className="p-3.5">Expected Value</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {leads.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No leads registered. Click "Add New Lead" to get started.
                    </td>
                  </tr>
                ) : (
                  leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-semibold text-slate-100">{lead.company_name}</td>
                      <td className="p-3.5">{lead.contact_name}</td>
                      <td className="p-3.5">{lead.email}</td>
                      <td className="p-3.5 text-emerald-400 font-semibold">
                        ${lead.expected_value.toLocaleString()}
                      </td>
                      <td className="p-3.5">
                        <span
                          className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                            lead.status === 'Converted'
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                          }`}
                        >
                          {lead.status}
                        </span>
                      </td>
                      <td className="p-3.5">
                        {lead.status !== 'Converted' && (
                          <button
                            onClick={() => {
                              setSelectedLead(lead);
                              setShowConvertModal(true);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded text-xs font-semibold cursor-pointer"
                          >
                            Convert to Account
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Customers Tab */}
      {activeTab === 'customers' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-xl font-bold text-white mb-6">Customer Accounts Directory</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">Code</th>
                  <th className="p-3.5">Company Name</th>
                  <th className="p-3.5">Email</th>
                  <th className="p-3.5">Payment Terms</th>
                  <th className="p-3.5">Credit Limit</th>
                  <th className="p-3.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {customers.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No customer accounts found.
                    </td>
                  </tr>
                ) : (
                  customers.map((cust) => (
                    <tr key={cust.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-mono text-indigo-400 font-bold">{cust.customer_code}</td>
                      <td className="p-3.5 font-semibold text-slate-100">{cust.company_name}</td>
                      <td className="p-3.5">{cust.email}</td>
                      <td className="p-3.5">{cust.payment_terms}</td>
                      <td className="p-3.5 text-emerald-400 font-semibold">
                        ${cust.credit_limit.toLocaleString()}
                      </td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                          {cust.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quotations Tab */}
      {activeTab === 'quotations' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-xl font-bold text-white mb-6">Quotations & Price Proposals</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">Quotation #</th>
                  <th className="p-3.5">Date</th>
                  <th className="p-3.5">Valid Until</th>
                  <th className="p-3.5">Grand Total</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {quotations.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No quotations generated yet.
                    </td>
                  </tr>
                ) : (
                  quotations.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-mono text-indigo-400 font-bold">{q.quotation_number}</td>
                      <td className="p-3.5">{q.quotation_date}</td>
                      <td className="p-3.5">{q.valid_until}</td>
                      <td className="p-3.5 text-emerald-400 font-bold">
                        ${q.grand_total.toLocaleString()}
                      </td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                          {q.status}
                        </span>
                      </td>
                      <td className="p-3.5">
                        <button
                          onClick={() => handleDownloadPDF(q.quotation_number)}
                          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 px-3 py-1.5 rounded text-xs font-semibold cursor-pointer"
                        >
                          <Download className="w-3.5 h-3.5" /> Download PDF
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

      {/* Add Lead Modal */}
      {showLeadModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Add New Lead</h3>
            <form onSubmit={handleCreateLead} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Company Name</label>
                <input
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Contact Person Name</label>
                <input
                  type="text"
                  required
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Phone</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Expected Value ($)</label>
                <input
                  type="number"
                  value={expectedVal}
                  onChange={(e) => setExpectedVal(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowLeadModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Save Lead
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Convert Lead Modal */}
      {showConvertModal && selectedLead && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Convert Lead to Customer Account</h3>
            <p className="text-xs text-slate-400 mb-4">
              Converting lead <span className="text-indigo-400 font-bold">{selectedLead.company_name}</span> into Customer & Opportunity.
            </p>
            <form onSubmit={handleConvertLead} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Customer Code</label>
                <input
                  type="text"
                  placeholder="e.g. CUST-8821"
                  value={customerCode}
                  onChange={(e) => setCustomerCode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Opportunity Title</label>
                <input
                  type="text"
                  placeholder="Opportunity Title"
                  value={oppTitle}
                  onChange={(e) => setOppTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowConvertModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Confirm Lead Conversion
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
