import React, { useState, useMemo } from 'react';
import { InvestigationResult, Finding, Transaction } from '../types';
import { 
  AlertTriangle, 
  CheckCircle2, 
  FileText, 
  Layers, 
  Clock, 
  TrendingUp, 
  Zap, 
  Eye, 
  Search, 
  CheckCircle, 
  MessageSquare,
  Sparkles,
  ArrowUpRight
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell, 
  CartesianGrid 
} from 'recharts';

interface AnalysisDashboardProps {
  investigation: InvestigationResult;
  transactions: Transaction[];
  onOpenEvidence: (finding: Finding) => void;
  onOpenReport: () => void;
  onOpenChat: () => void;
}

export const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({
  investigation,
  transactions,
  onOpenEvidence,
  onOpenReport,
  onOpenChat
}) => {
  const [filterType, setFilterType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortField, setSortField] = useState<'timestamp' | 'amount' | 'payee'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedTxn, setSelectedTxn] = useState<Transaction | null>(null);

  const isAttention = investigation.investigation_status === 'ATTENTION_REQUIRED';
  const baseline = investigation.baseline;

  // Format currency helper
  const formatINR = (amt: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amt);
  };

  // Map flagged transaction IDs
  const flaggedTxnMap = useMemo(() => {
    const map = new Map<string, string[]>();
    investigation.findings.forEach(f => {
      f.transaction_ids?.forEach(tid => {
        const existing = map.get(tid) || [];
        existing.push(f.rule_id);
        map.set(tid, existing);
      });
    });
    return map;
  }, [investigation.findings]);

  // Filtered and sorted transactions
  const processedTransactions = useMemo(() => {
    return transactions.filter(t => {
      const isFlagged = flaggedTxnMap.has(t.transaction_id);
      if (filterType === 'flagged' && !isFlagged) return false;
      if (filterType === 'normal' && isFlagged) return false;
      if (filterType === 'large' && t.amount < (baseline?.percentiles?.p95 || 25000)) return false;
      if (filterType === 'odd') {
        const h = new Date(t.timestamp).getHours();
        if (h > 5) return false;
      }

      if (searchTerm) {
        const s = searchTerm.toLowerCase();
        const matches = 
          t.transaction_id.toLowerCase().includes(s) ||
          t.payee.toLowerCase().includes(s) ||
          t.description.toLowerCase().includes(s) ||
          t.channel.toLowerCase().includes(s);
        if (!matches) return false;
      }

      return true;
    }).sort((a, b) => {
      if (sortField === 'amount') {
        return sortOrder === 'asc' ? a.amount - b.amount : b.amount - a.amount;
      }
      if (sortField === 'payee') {
        return sortOrder === 'asc' ? a.payee.localeCompare(b.payee) : b.payee.localeCompare(a.payee);
      }
      return sortOrder === 'asc' 
        ? new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        : new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
  }, [transactions, filterType, searchTerm, sortField, sortOrder, flaggedTxnMap, baseline]);

  // Hourly distribution data for Recharts
  const hourlyChartData = useMemo(() => {
    if (!baseline?.hourly_distribution) return [];
    return Array.from({ length: 24 }).map((_, h) => ({
      hour: `${h}:00`,
      count: baseline.hourly_distribution[h] || 0,
      isOddHour: h >= 0 && h <= 5
    }));
  }, [baseline]);

  // Channel volume data
  const channelChartData = useMemo(() => {
    if (!baseline?.channel_distribution_count_pct) return [];
    return Object.entries(baseline.channel_distribution_count_pct).map(([channel, pct]) => ({
      name: channel,
      value: pct
    }));
  }, [baseline]);

  // R004 Behavioural Break comparison data
  const r004Finding = investigation.findings.find(f => f.rule_id === 'R004');
  const channelShiftData = useMemo(() => {
    if (!r004Finding?.channel_shifts) return [];
    return Object.entries(r004Finding.channel_shifts).map(([ch, data]) => ({
      channel: ch,
      Historical: data.historical_pct,
      Recent: data.recent_pct,
      difference: data.difference_pct
    }));
  }, [r004Finding]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Top Header Card */}
      <div className="rounded-3xl p-6 lg:p-7 border border-slate-200/90 dark:border-slate-800/90 bg-gradient-to-r from-blue-50/80 via-indigo-50/30 to-slate-50 dark:from-[#0d1527] dark:via-[#0b1120] dark:to-[#090d16] flex items-center justify-between flex-wrap gap-4 shadow-sm">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="font-mono text-xs font-bold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 px-3 py-1 rounded-lg border border-slate-200 dark:border-slate-700 shadow-2xs">
              {investigation.customer_id}
            </span>
            <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {investigation.customer_name}
            </h1>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono font-medium">
              • {baseline?.date_span_days || 180} Day Behavioural Analysis
            </span>
          </div>
          <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 font-normal">
            Automated triaging based on deterministic statistical baseline thresholds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            id="btn-open-chat"
            onClick={onOpenChat}
            className="px-4 py-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/50 hover:bg-purple-100 dark:hover:bg-purple-900/60 border border-purple-200 dark:border-purple-800/80 text-purple-700 dark:text-purple-300 text-xs font-bold flex items-center gap-2 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer shadow-xs"
          >
            <MessageSquare className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <span>Analyst Q&A</span>
          </button>

          <button
            id="btn-view-report"
            onClick={onOpenReport}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-blue-500/20 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
          >
            <FileText className="w-4 h-4" />
            <span>Generate Full Report</span>
          </button>
        </div>
      </div>

      {/* Main Status & Disclaimer Banner */}
      <div className={`p-6 rounded-3xl border transition-all duration-300 ${
        isAttention 
          ? 'bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-amber-300 dark:border-amber-800/80 shadow-md shadow-amber-500/5' 
          : 'bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent border-emerald-300 dark:border-emerald-800/80 shadow-md shadow-emerald-500/5'
      }`}>
        <div className="flex items-start justify-between gap-6 flex-wrap">
          <div className="flex items-start gap-4 max-w-2xl">
            <div className={`p-3 rounded-2xl shrink-0 ${
              isAttention 
                ? 'bg-amber-100 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 shadow-xs ring-2 ring-amber-500/20' 
                : 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 shadow-xs ring-2 ring-emerald-500/20'
            }`}>
              {isAttention ? <AlertTriangle className="w-7 h-7" /> : <CheckCircle2 className="w-7 h-7" />}
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`text-lg font-extrabold tracking-wide uppercase ${
                  isAttention ? 'text-amber-700 dark:text-amber-400' : 'text-emerald-700 dark:text-emerald-400'
                }`}>
                  {investigation.badge_text}
                </span>
                <span className="text-xs px-3 py-1 rounded-full bg-white/90 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 font-mono font-bold shadow-xs">
                  Score: {investigation.priority_score}/100 ({investigation.risk_level})
                </span>
              </div>
              <p className="text-xs lg:text-sm text-slate-700 dark:text-slate-200 font-medium leading-relaxed">
                {investigation.summary}
              </p>
            </div>
          </div>

          <div className="text-right max-w-xs text-xs text-slate-500 dark:text-slate-400 border-l border-slate-200/80 dark:border-slate-800 pl-5 space-y-1">
            <span className="font-bold text-slate-800 dark:text-slate-200 block uppercase tracking-wider text-[11px]">
              Investigative Disclaimer:
            </span>
            <p className="leading-relaxed">
              {investigation.scoring?.disclaimer || "This system identifies unusual activity for investigation. It does not determine whether fraud occurred."}
            </p>
          </div>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-5">
        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-blue-500"></div>
          <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Transactions</span>
          <div className="mt-2 text-3xl font-extrabold font-mono text-slate-900 dark:text-white tracking-tight">
            {transactions.length}
          </div>
          <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">Across {baseline?.date_span_days || 180} days</span>
        </div>

        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-emerald-500"></div>
          <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Total Volume</span>
          <div className="mt-2 text-3xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400 tracking-tight">
            {formatINR(baseline?.total_volume || 0)}
          </div>
          <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">Median: {formatINR(baseline?.median_amount || 0)}</span>
        </div>

        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-amber-500"></div>
          <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Triggered Rules</span>
          <div className="mt-2 text-3xl font-extrabold font-mono text-amber-600 dark:text-amber-400 tracking-tight">
            {investigation.findings.length}
          </div>
          <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block font-mono">
            {investigation.findings.map(f => f.rule_id).join(', ') || 'None'}
          </span>
        </div>

        <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-purple-500"></div>
          <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Correlated Clusters</span>
          <div className="mt-2 text-3xl font-extrabold font-mono text-purple-600 dark:text-purple-400 tracking-tight">
            {investigation.correlated_events?.length || 0}
          </div>
          <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">Temporal / Payee clusters</span>
        </div>
      </div>

      {/* Section: Risk Findings Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span>Deterministic Risk Findings ({investigation.findings.length})</span>
          </h2>
          <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">Evaluated by Python Engine</span>
        </div>

        {investigation.findings.length === 0 ? (
          <div className="p-10 rounded-3xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 text-center space-y-3">
            <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto" />
            <div className="text-base font-bold text-slate-800 dark:text-slate-200">No Attention Required</div>
            <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
              No configured risk rule was triggered by the customer's transaction history. Behaviour conforms to normal profile.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {investigation.findings.map((f) => (
              <div 
                key={f.finding_id}
                id={`finding-card-${f.finding_id}`}
                className="enterprise-card enterprise-card-interactive rounded-2xl p-6 space-y-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-lg bg-blue-100 dark:bg-blue-950/80 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 font-mono text-xs font-bold">
                        {f.rule_id}
                      </span>
                      <span className="font-mono text-xs text-slate-400">{f.finding_id}</span>
                    </div>
                    <h3 className="font-bold text-base text-slate-900 dark:text-white mt-1">
                      {f.title}
                    </h3>
                  </div>

                  <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border font-mono ${
                    f.severity === 'HIGH' 
                      ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 badge-glow-rose' 
                      : 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 badge-glow-amber'
                  }`}>
                    {f.severity}
                  </span>
                </div>

                <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
                  {f.description}
                </p>

                {/* Metric callout */}
                {f.evidence && f.evidence[0] && (
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 text-xs font-mono space-y-2 shadow-xs">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500">Observed:</span>
                      <strong className="text-slate-900 dark:text-white font-bold">{f.evidence[0].observed_value}</strong>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500">Deviation:</span>
                      <strong className="text-amber-600 dark:text-amber-400 font-bold">{f.evidence[0].deviation}</strong>
                    </div>
                  </div>
                )}

                <div className="pt-3 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
                  <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">
                    {f.transaction_ids?.length || 0} txn(s) implicated
                  </span>
                  <button
                    id={`btn-view-evidence-${f.finding_id}`}
                    onClick={() => onOpenEvidence(f)}
                    className="px-3.5 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 dark:bg-blue-600/20 dark:hover:bg-blue-600/30 border border-blue-200 dark:border-blue-500/40 text-blue-700 dark:text-blue-300 text-xs font-semibold inline-flex items-center gap-1.5 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer shadow-xs"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Evidence</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Section: Correlated Incident Graph & Clusters */}
      {investigation.correlated_events && investigation.correlated_events.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-500" />
              <span>Correlated Incident Clusters ({investigation.correlated_events.length})</span>
            </h2>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">Multi-transaction co-occurrences</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {investigation.correlated_events.map((evt) => (
              <div key={evt.event_id} className="enterprise-card enterprise-card-interactive p-6 rounded-2xl space-y-3.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-bold text-purple-600 dark:text-purple-400 text-sm">{evt.event_id}</span>
                  <span className="text-xs text-slate-400 font-mono">{evt.time_window.duration_minutes} min window</span>
                </div>

                <div className="font-bold text-slate-900 dark:text-white text-sm">
                  {evt.summary}
                </div>

                {/* Node visualizer */}
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 font-mono text-xs text-slate-700 dark:text-slate-300 flex items-center gap-2 flex-wrap shadow-xs">
                  <span className="px-2.5 py-1 rounded-lg bg-blue-100 dark:bg-blue-900/60 border border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-300 font-semibold">
                    {evt.transaction_ids[0]}
                  </span>
                  <span className="text-slate-400 font-bold">→</span>
                  <span className="px-2.5 py-1 rounded-lg bg-purple-100 dark:bg-purple-900/60 border border-purple-200 dark:border-purple-700 text-purple-700 dark:text-purple-300 font-semibold">
                    {evt.payees[0]}
                  </span>
                  <span className="text-slate-400 font-bold">→</span>
                  <span className="px-2.5 py-1 rounded-lg bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium">
                    +{evt.transaction_ids.length - 1} connected txns
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-mono pt-2 border-t border-slate-200/80 dark:border-slate-800">
                  <span>Cluster Volume: <strong className="text-emerald-600 dark:text-emerald-400 font-bold">{evt.formatted_amount}</strong></span>
                  <span>Channels: {evt.channels.join(', ')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section: Customer Behaviour Profile */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-500" />
            <span>Customer Behaviour Profile</span>
          </h2>
          <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">Robust Non-Parametric Metrics</span>
        </div>

        {/* Profile Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-5">
          <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl">
            <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Typical Amount</span>
            <div className="mt-2 text-2xl font-bold font-mono text-slate-900 dark:text-white">
              {formatINR(baseline?.median_amount || 0)}
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">IQR: {formatINR(baseline?.percentiles?.p25 || 0)} – {formatINR(baseline?.percentiles?.p75 || 0)}</span>
          </div>

          <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl">
            <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Daily Frequency</span>
            <div className="mt-2 text-2xl font-bold font-mono text-slate-900 dark:text-white">
              {baseline?.daily_frequency?.median || 2} txns/day
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">Mean: {baseline?.daily_frequency?.mean || 2.1} txns/day</span>
          </div>

          <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl">
            <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Known Payees</span>
            <div className="mt-2 text-2xl font-bold font-mono text-slate-900 dark:text-white">
              {baseline?.known_payees_count || 0}
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">Verified historical pool</span>
          </div>

          <div className="enterprise-card enterprise-card-interactive p-5 rounded-2xl">
            <span className="text-xs text-slate-500 dark:text-slate-400 block uppercase font-bold tracking-wider">Normal Hours</span>
            <div className="mt-2 text-2xl font-bold font-mono text-slate-900 dark:text-white">
              {baseline?.typical_hours?.display || '08:00–22:00'}
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block">Night activity: {baseline?.odd_hours?.percentage || 0}%</span>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Hourly Distribution */}
          <div className="enterprise-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-sm text-slate-800 dark:text-slate-200">Transactions by Hour of Day</span>
              <span className="text-xs text-amber-600 dark:text-amber-400 font-mono font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                00:00–05:00 Odd-Hours Zone
              </span>
            </div>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.2} vertical={false} />
                  <XAxis dataKey="hour" stroke="#94a3b8" fontSize={11} interval={2} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px', color: '#f8fafc', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)' }} 
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {hourlyChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.isOddHour ? '#F59E0B' : '#3B82F6'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: Channel Breakdown */}
          <div className="enterprise-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-sm text-slate-800 dark:text-slate-200">Channel Distribution (% volume)</span>
              <span className="text-xs text-slate-400 font-mono">Historical Baseline</span>
            </div>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart layout="vertical" data={channelChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.2} horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" fontSize={11} unit="%" />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} width={80} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px', color: '#f8fafc', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)' }}
                    formatter={(val) => [`${val}%`, 'Frequency']}
                  />
                  <Bar dataKey="value" fill="#10B981" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Behaviour Comparison: Historical vs Recent (R004) */}
        {channelShiftData.length > 0 && (
          <div className="enterprise-card p-7 rounded-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800 pb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-500" />
                  <span>Behaviour Comparison: Historical vs Recent Activity</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Structural channel shift analysis for R004 Behavioural Pattern Break
                </p>
              </div>
              <span className="text-xs px-3 py-1 rounded-full bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 font-mono font-bold badge-glow-rose">
                R004 Triggered
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {channelShiftData.map((item) => (
                <div key={item.channel} className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-sm text-slate-900 dark:text-white font-mono">{item.channel}</span>
                    <span className={`font-mono text-xs font-bold ${
                      item.difference > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-500'
                    }`}>
                      {item.difference > 0 ? `+${item.difference}%` : `${item.difference}%`}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between text-slate-500">
                      <span>Historical Baseline:</span>
                      <strong className="text-slate-800 dark:text-slate-200 font-semibold">{item.Historical}%</strong>
                    </div>
                    <div className="w-full h-2.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${Math.min(100, item.Historical)}%` }}></div>
                    </div>

                    <div className="flex justify-between text-slate-500 pt-1">
                      <span>Recent Activity:</span>
                      <strong className="text-amber-600 dark:text-amber-400 font-semibold">{item.Recent}%</strong>
                    </div>
                    <div className="w-full h-2.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full transition-all duration-500" style={{ width: `${Math.min(100, item.Recent)}%` }}></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Section: Interactive Transaction Timeline */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-500" />
            <span>Interactive Transaction Timeline</span>
          </h2>
          <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">
            ● Normal • ⚠ Flagged Activity
          </span>
        </div>

        <div className="enterprise-card p-6 rounded-2xl overflow-x-auto">
          <div className="flex items-center gap-3.5 min-w-[700px] py-2">
            {transactions.slice(-30).map((t) => {
              const isFlagged = flaggedTxnMap.has(t.transaction_id);
              const isSelected = selectedTxn?.transaction_id === t.transaction_id;

              return (
                <div
                  key={t.transaction_id}
                  onClick={() => setSelectedTxn(t)}
                  className={`flex flex-col items-center gap-2 p-2.5 rounded-xl cursor-pointer transition-all duration-200 shrink-0 ${
                    isSelected ? 'bg-blue-50 dark:bg-blue-600/20 ring-2 ring-blue-500 scale-105 shadow-xs' : 'hover:bg-slate-100 dark:hover:bg-slate-800/80 hover:scale-105'
                  }`}
                  title={`${t.transaction_id} • ${t.payee} • ${formatINR(t.amount)} • ${t.timestamp}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    isFlagged 
                      ? 'bg-rose-100 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-300 dark:border-rose-500/50 animate-pulse badge-glow-rose' 
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                  }`}>
                    {isFlagged ? '⚠' : '●'}
                  </div>
                  <span className="text-[11px] font-mono font-medium text-slate-500 dark:text-slate-400">
                    {t.timestamp.substring(5, 10)}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400 dark:text-slate-500 font-semibold">
                    {formatINR(t.amount)}
                  </span>
                </div>
              );
            })}
          </div>

          {selectedTxn && (
            <div className="mt-5 p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-xs flex items-center justify-between flex-wrap gap-3 animate-fade-in shadow-xs">
              <div className="flex items-center gap-3.5 flex-wrap">
                <span className="font-mono font-bold text-sm text-blue-600 dark:text-blue-400">{selectedTxn.transaction_id}</span>
                <span className="text-slate-900 dark:text-white font-semibold text-xs">{selectedTxn.payee}</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-mono font-bold text-xs">{formatINR(selectedTxn.amount)}</span>
                <span className="px-2.5 py-0.5 rounded-md bg-slate-200 dark:bg-slate-800 text-xs font-mono text-slate-700 dark:text-slate-300 font-medium">{selectedTxn.channel}</span>
                <span className="text-slate-500 text-xs font-mono">{selectedTxn.timestamp}</span>
              </div>
              <button
                onClick={() => setSelectedTxn(null)}
                className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 text-xs font-medium cursor-pointer"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Section: Filterable Transaction Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Customer Transaction Ledger ({processedTransactions.length} of {transactions.length})
            </h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
              Filterable and traceable records loaded from Supabase database
            </p>
          </div>

          {/* Table Filters */}
          <div className="flex items-center gap-2.5 flex-wrap">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                placeholder="Search transaction..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3.5 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 w-48 transition-all"
              />
            </div>

            {['all', 'flagged', 'normal', 'large', 'odd'].map((f) => (
              <button
                key={f}
                id={`filter-btn-${f}`}
                onClick={() => setFilterType(f)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold capitalize transition-all duration-150 cursor-pointer ${
                  filterType === f
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/25 scale-105'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="enterprise-card rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 dark:bg-slate-900/80 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200/80 dark:border-slate-800 uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-6 py-3.5 font-mono">Transaction ID</th>
                  <th className="px-6 py-3.5">Timestamp</th>
                  <th className="px-6 py-3.5">Payee</th>
                  <th className="px-6 py-3.5">Description</th>
                  <th className="px-6 py-3.5 text-right">Amount</th>
                  <th className="px-6 py-3.5">Channel</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5">Triggered Rules</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/70 dark:divide-slate-800/60 font-sans">
                {processedTransactions.slice(0, 100).map((t) => {
                  const rules = flaggedTxnMap.get(t.transaction_id);
                  const isFlagged = Boolean(rules && rules.length > 0);

                  return (
                    <tr 
                      key={t.transaction_id}
                      className={`table-row-hover transition-colors ${isFlagged ? 'bg-amber-50/60 dark:bg-amber-950/20' : ''}`}
                    >
                      <td className="px-6 py-3.5 font-mono text-blue-600 dark:text-blue-400 font-bold text-xs">
                        {t.transaction_id}
                      </td>
                      <td className="px-6 py-3.5 font-mono text-slate-500 dark:text-slate-400 text-xs">
                        {t.timestamp}
                      </td>
                      <td className="px-6 py-3.5 font-semibold text-slate-900 dark:text-white text-xs">
                        {t.payee}
                      </td>
                      <td className="px-6 py-3.5 text-slate-500 dark:text-slate-400 text-xs">
                        {t.description}
                      </td>
                      <td className="px-6 py-3.5 text-right font-mono font-bold text-slate-900 dark:text-white text-xs">
                        {formatINR(t.amount)}
                      </td>
                      <td className="px-6 py-3.5">
                        <span className="px-2.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-xs font-mono text-slate-700 dark:text-slate-300 font-medium">
                          {t.channel}
                        </span>
                      </td>
                      <td className="px-6 py-3.5">
                        {isFlagged ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 font-semibold text-xs">
                            <AlertTriangle className="w-3 h-3 text-amber-500" />
                            <span>Flagged</span>
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400 font-mono">Normal</span>
                        )}
                      </td>
                      <td className="px-6 py-3.5">
                        {isFlagged && rules ? (
                          <div className="flex gap-1.5 flex-wrap">
                            {rules.map(r => (
                              <span key={r} className="px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300 text-xs font-mono font-bold">
                                {r}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {processedTransactions.length > 100 && (
            <div className="p-3.5 text-center text-xs text-slate-400 border-t border-slate-200/80 dark:border-slate-800 font-mono">
              Showing first 100 of {processedTransactions.length} records.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
