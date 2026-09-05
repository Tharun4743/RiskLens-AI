import React, { useState, useEffect } from 'react';
import { InvestigationSummaryItem } from '../types';
import { api } from '../api';
import { 
  ShieldAlert, 
  Search, 
  ArrowRight, 
  AlertTriangle, 
  CheckCircle2, 
  Activity, 
  RefreshCw,
  Eye,
  Layers,
  Sparkles
} from 'lucide-react';

interface InvestigationCenterProps {
  onStartNew: () => void;
  onViewInvestigation: (id: number) => void;
}

export const InvestigationCenter: React.FC<InvestigationCenterProps> = ({ 
  onStartNew, 
  onViewInvestigation 
}) => {
  const [investigations, setInvestigations] = useState<InvestigationSummaryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  useEffect(() => {
    loadInvestigations();
  }, []);

  const loadInvestigations = async () => {
    setLoading(true);
    try {
      const data = await api.getInvestigations();
      setInvestigations(data);
    } catch (err) {
      console.error('Failed to load investigations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await loadInvestigations();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const filtered = investigations.filter(i => 
    i.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Hero Action Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-200/90 dark:border-slate-800/90 bg-gradient-to-br from-blue-50/90 via-indigo-50/40 to-slate-50 dark:from-[#0d1527] dark:via-[#0b1120] dark:to-[#090d16] p-8 lg:p-10 shadow-sm transition-all">
        {/* Subtle decorative background blur element */}
        <div className="absolute -right-16 -top-16 w-80 h-80 rounded-full bg-blue-400/10 dark:bg-blue-500/10 blur-3xl pointer-events-none"></div>
        <div className="absolute -left-16 -bottom-16 w-80 h-80 rounded-full bg-indigo-400/10 dark:bg-indigo-500/10 blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 dark:bg-blue-500/20 border border-blue-200 dark:border-blue-500/30 text-blue-700 dark:text-blue-300 text-xs font-semibold shadow-xs">
            <ShieldAlert className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Evidence-First Risk Triaging Engine</span>
          </div>

          <h1 className="text-3xl lg:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
            Transaction Risk Investigation
          </h1>

          <p className="text-slate-600 dark:text-slate-300 text-sm lg:text-base leading-relaxed max-w-2xl font-normal">
            Analyze customer transaction history, establish mathematical behavioral baselines, and deterministically detect anomalous activity requiring human review without premature fraud assertions.
          </p>

          <div className="pt-3 flex items-center gap-4 flex-wrap">
            <button
              id="btn-start-investigation"
              onClick={onStartNew}
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm flex items-center gap-2.5 shadow-lg shadow-blue-500/25 transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 cursor-pointer group"
            >
              <span>Start Investigation</span>
              <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
            </button>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/60 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="font-mono text-slate-700 dark:text-slate-300 font-semibold">Rules R001–R004 Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Triaging Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 opacity-80"></div>
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Investigations</span>
            <div className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono tracking-tight">
            {investigations.length}
          </div>
          <div className="text-xs text-slate-400 dark:text-slate-500 mt-1.5 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            Stored in local ledger
          </div>
        </div>

        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-orange-500 opacity-80"></div>
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Attention Required</span>
            <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-amber-600 dark:text-amber-400 font-mono tracking-tight">
            {investigations.filter(i => i.status === 'ATTENTION_REQUIRED').length}
          </div>
          <div className="text-xs text-slate-400 dark:text-slate-500 mt-1.5 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
            Flagged for analyst review
          </div>
        </div>

        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-80"></div>
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>No Attention</span>
            <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono tracking-tight">
            {investigations.filter(i => i.status === 'NO_ATTENTION').length}
          </div>
          <div className="text-xs text-slate-400 dark:text-slate-500 mt-1.5 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Conforms to baseline
          </div>
        </div>

        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-pink-500 opacity-80"></div>
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>AI Reasoning Layer</span>
            <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-purple-600 dark:text-purple-400 font-mono tracking-tight">
            Active
          </div>
          <div className="text-xs text-slate-400 dark:text-slate-500 mt-1.5 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
            Hallucination guardrails ON
          </div>
        </div>
      </div>

      {/* Recent Investigations Table */}
      <div className="enterprise-card rounded-2xl overflow-hidden shadow-sm">
        <div className="p-6 border-b border-slate-200/80 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/40 flex items-center justify-between flex-wrap gap-4">
          <div className="space-y-0.5">
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
              Recent Case Investigations
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Complete audit trail of customer transaction investigations and results
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                placeholder="Search customer or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 w-60 transition-all"
              />
            </div>
            <button
              onClick={handleManualRefresh}
              className={`p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-all cursor-pointer shadow-xs ${
                isRefreshing ? 'animate-spin' : ''
              }`}
              title="Refresh Records"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="p-16 text-center text-sm text-slate-500 space-y-3">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <div className="font-medium">Loading investigation records...</div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-16 text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800/80 flex items-center justify-center mx-auto text-slate-400 dark:text-slate-500">
              <Layers className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <div className="text-base font-semibold text-slate-800 dark:text-slate-200">No investigations found</div>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                {searchTerm ? 'No investigations match your search query.' : 'Select a customer profile or upload a CSV file to execute the first behavioral risk investigation.'}
              </p>
            </div>
            {!searchTerm && (
              <button
                onClick={onStartNew}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold inline-flex items-center gap-2 shadow-md shadow-blue-500/20 transition-all cursor-pointer"
              >
                Start Investigation Now
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 dark:bg-slate-900/80 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200/80 dark:border-slate-800/80 uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-6 py-4">Case ID</th>
                  <th className="px-6 py-4">Customer</th>
                  <th className="px-6 py-4">Txn Count</th>
                  <th className="px-6 py-4">Risk Level</th>
                  <th className="px-6 py-4">Outcome</th>
                  <th className="px-6 py-4">Completed At</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/70 dark:divide-slate-800/60 font-sans">
                {filtered.map((inv) => {
                  const isAttention = inv.status === 'ATTENTION_REQUIRED';
                  return (
                    <tr key={inv.id} className="table-row-hover transition-colors group">
                      <td className="px-6 py-4 font-mono text-slate-600 dark:text-slate-400 font-semibold text-xs">
                        INV-{inv.id.toString().padStart(4, '0')}
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-bold text-sm text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {inv.customer_name}
                        </div>
                        <div className="text-xs text-slate-400 font-mono">{inv.customer_id}</div>
                      </td>
                      <td className="px-6 py-4 text-slate-700 dark:text-slate-300 font-mono font-medium text-xs">
                        {inv.transactions_count}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border font-mono ${
                          inv.risk_level === 'HIGH' ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800/80 text-rose-700 dark:text-rose-400 badge-glow-rose' :
                          inv.risk_level === 'MODERATE' ? 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800/80 text-amber-700 dark:text-amber-400 badge-glow-amber' :
                          'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                        }`}>
                          {inv.risk_level}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
                          isAttention
                            ? 'bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800/80 text-amber-800 dark:text-amber-300'
                            : 'bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/80 text-emerald-800 dark:text-emerald-300'
                        }`}>
                          {isAttention ? (
                            <>
                              <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                              <span>Attention Required</span>
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                              <span>No Attention</span>
                            </>
                          )}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 dark:text-slate-400 text-xs font-mono">
                        {inv.completed_at ? inv.completed_at.replace('T', ' ').substring(0, 19) : 'In Progress'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          id={`view-inv-btn-${inv.id}`}
                          onClick={() => onViewInvestigation(inv.id)}
                          className="px-3.5 py-1.5 bg-slate-100 hover:bg-blue-600 dark:bg-slate-800 hover:text-white dark:hover:bg-blue-600 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold transition-all duration-200 inline-flex items-center gap-1.5 cursor-pointer shadow-xs hover:shadow-md hover:shadow-blue-500/20"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Analysis</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
