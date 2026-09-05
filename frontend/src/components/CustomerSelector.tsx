import React, { useState, useEffect } from 'react';
import { Customer } from '../types';
import { api } from '../api';
import { 
  Upload, 
  ArrowRight, 
  CheckCircle, 
  AlertCircle, 
  FileSpreadsheet, 
  ShieldAlert,
  Clock,
  Zap,
  Sparkles,
  FileCheck
} from 'lucide-react';

interface CustomerSelectorProps {
  onSelectCustomer: (customerId: string) => void;
  loading: boolean;
}

export const CustomerSelector: React.FC<CustomerSelectorProps> = ({ onSelectCustomer, loading }) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadMeta, setUploadMeta] = useState<any | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [customId, setCustomId] = useState<string>('');
  const [customName, setCustomName] = useState<string>('');

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const data = await api.getCustomers();
      setCustomers(data);
      if (data.length > 0) {
        setSelectedId(prev => prev && data.some(c => c.customer_id === prev) ? prev : data[0].customer_id);
      }
    } catch (err: any) {
      console.error('Failed to load customers:', err);
    }
  };

  const getCustomerBadge = (c: Customer) => {
    if (c.expected_result?.includes('NO ATTENTION')) {
      return {
        badge: 'NORMAL PROFILE',
        badgeColor: 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800/80 text-emerald-700 dark:text-emerald-400',
        icon: CheckCircle
      };
    }
    if (c.expected_result?.includes('R001') && c.expected_result?.includes('R004')) {
      return {
        badge: 'COMPLEX MULTI-VECTOR',
        badgeColor: 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800/80 text-rose-700 dark:text-rose-400',
        icon: ShieldAlert
      };
    }
    if (c.expected_result?.includes('R001')) {
      return {
        badge: 'LARGE TRANSFER (R001)',
        badgeColor: 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800/80 text-amber-800 dark:text-amber-400',
        icon: Zap
      };
    }
    if (c.expected_result?.includes('R002')) {
      return {
        badge: 'NEW PAYEE BURST (R002)',
        badgeColor: 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800/80 text-amber-800 dark:text-amber-400',
        icon: Clock
      };
    }
    if (c.expected_result?.includes('R003')) {
      return {
        badge: 'ODD-HOURS ACTIVITY (R003)',
        badgeColor: 'bg-purple-50 dark:bg-purple-950/60 border-purple-200 dark:border-purple-800/80 text-purple-700 dark:text-purple-400',
        icon: Clock
      };
    }
    return {
      badge: 'DATABASE LEDGER',
      badgeColor: 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300',
      icon: FileSpreadsheet
    };
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadFile(file);
    setUploadError(null);
    setUploadMeta(null);
    setUploading(true);

    try {
      const res = await api.uploadCSV(file, customId || undefined, customName || undefined);
      setUploadMeta(res);
      setSelectedId(res.customer_id);
      await loadCustomers();
    } catch (err: any) {
      setUploadError(err.message || 'CSV upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-fade-in">
      {/* Intro Banner */}
      <div className="rounded-3xl p-8 border border-slate-200/90 dark:border-slate-800/90 bg-gradient-to-r from-blue-50/80 via-indigo-50/30 to-slate-50 dark:from-[#0d1527] dark:via-[#0b1120] dark:to-[#090d16] shadow-sm">
        <div className="max-w-2xl space-y-2.5">
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/60 border border-blue-200 dark:border-blue-700/50 text-blue-700 dark:text-blue-300 uppercase tracking-wider inline-flex items-center gap-1.5">
            <Sparkles className="w-3 h-3" />
            Customer Profile Selection
          </span>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Select Customer or Ingest Transaction History
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
            Choose from predefined synthetic banking profiles designed to validate deterministic anomaly detection (R001–R004), or upload custom banking transaction CSVs.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Customer Demo Profiles */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Synthetic Demo Customers ({customers.length})
            </h3>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">Real deterministic records</span>
          </div>

          <div className="space-y-3.5">
            {customers.map((c) => {
              const badgeInfo = getCustomerBadge(c);
              const description = c.profile || 'Account ledger profile stored in database.';
              const expectedText = c.expected_result || 'Determined by rules';
              const isSelected = selectedId === c.customer_id;
              const Icon = badgeInfo.icon;

              return (
                <div
                  key={c.customer_id}
                  id={`cust-card-${c.customer_id}`}
                  onClick={() => setSelectedId(c.customer_id)}
                  className={`p-5 rounded-2xl border transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? 'bg-gradient-to-r from-blue-50/90 to-indigo-50/50 dark:from-blue-950/40 dark:to-indigo-950/30 border-blue-500 shadow-md ring-2 ring-blue-500/30 -translate-y-0.5'
                      : 'enterprise-card hover:border-slate-300 dark:hover:border-slate-700 hover:-translate-y-0.5'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3.5">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                        isSelected 
                          ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30' 
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <span className="font-bold text-base text-slate-900 dark:text-white">{c.name}</span>
                          <span className="font-mono text-xs text-slate-500 dark:text-slate-400 font-medium">({c.customer_id})</span>
                          <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-semibold ${badgeInfo.badgeColor}`}>
                            {badgeInfo.badge}
                          </span>
                        </div>
                        <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
                          {description}
                        </p>
                        <div className="pt-1.5 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 font-mono">
                          <span>Txns: <strong className="text-slate-800 dark:text-slate-200 font-bold">{c.transaction_count ?? '100+'}</strong></span>
                          <span>•</span>
                          <span>Expected: <strong className="text-blue-600 dark:text-blue-400 font-semibold">{expectedText}</strong></span>
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 pt-1">
                      <input
                        type="radio"
                        checked={isSelected}
                        onChange={() => setSelectedId(c.customer_id)}
                        className="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-700 focus:ring-blue-500 cursor-pointer"
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-3">
            <button
              id="btn-analyze-selected"
              onClick={() => onSelectCustomer(selectedId)}
              disabled={loading || !selectedId}
              className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold text-sm flex items-center justify-center gap-2.5 shadow-lg shadow-blue-500/25 transition-all duration-200 cursor-pointer group"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                  <span>Executing Deterministic Rules & Baselines...</span>
                </>
              ) : (
                <>
                  <span>Analyze {selectedId}</span>
                  <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* CSV Drag and Drop Ingestion Box */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Upload Transaction History
            </h3>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">CSV Only</span>
          </div>

          <div className="enterprise-card p-6 rounded-2xl space-y-4 shadow-sm">
            {/* Custom customer IDs optional */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block">
                Target Customer ID (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. CUST-CUSTOM-01"
                value={customId}
                onChange={(e) => setCustomId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 font-mono transition-all"
              />
            </div>

            {/* Drop Zone */}
            <label className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 rounded-2xl p-7 flex flex-col items-center justify-center gap-2.5 cursor-pointer transition-all bg-slate-50/60 dark:bg-slate-900/40 group">
              <div className="p-3 rounded-full bg-blue-50 dark:bg-blue-950/60 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 group-hover:scale-110 transition-all">
                <Upload className="w-6 h-6" />
              </div>
              <div className="text-center space-y-1">
                <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 block">
                  Click to browse or drop CSV
                </span>
                <span className="text-xs text-slate-500 dark:text-slate-400 block max-w-xs">
                  Required columns: transaction_id, date, payee, amount, channel, description
                </span>
              </div>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>

            {uploading && (
              <div className="text-xs text-blue-600 dark:text-blue-400 flex items-center justify-center gap-2.5 py-2 font-medium">
                <span className="w-4 h-4 border-2 border-blue-600 dark:border-blue-400 border-t-transparent rounded-full animate-spin"></span>
                <span>Validating schema, timestamps & amounts...</span>
              </div>
            )}

            {uploadError && (
              <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/80 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2.5 animate-fade-in">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-500" />
                <div className="space-y-0.5">
                  <strong className="block font-semibold">Upload Validation Failed</strong>
                  <span className="text-[11px] leading-relaxed">{uploadError}</span>
                </div>
              </div>
            )}

            {uploadMeta && (
              <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/80 text-emerald-800 dark:text-emerald-300 text-xs space-y-2 animate-fade-in">
                <div className="flex items-center gap-2 font-bold text-emerald-700 dark:text-emerald-400">
                  <FileCheck className="w-4 h-4" />
                  <span>Validation Passed ({uploadMeta.transactions_count} txns)</span>
                </div>
                <div className="text-xs text-slate-700 dark:text-slate-300 font-mono space-y-1">
                  <div>• Months Covered: {uploadMeta.months_covered}</div>
                  <div>• Payees: {uploadMeta.payees_detected}</div>
                  <div>• Channels: {uploadMeta.channels_detected}</div>
                </div>
                <button
                  id="btn-analyze-uploaded"
                  onClick={() => onSelectCustomer(uploadMeta.customer_id)}
                  className="mt-2 w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold text-xs shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
                >
                  Start Investigation for {uploadMeta.customer_id}
                </button>
              </div>
            )}

            {/* Schema reference */}
            <div className="text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800 pt-3.5 space-y-1.5">
              <span className="font-semibold text-slate-700 dark:text-slate-300">Supported Schema:</span>
              <code className="block bg-slate-100 dark:bg-slate-900/80 p-2.5 rounded-lg text-[11px] text-slate-700 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-800">
                transaction_id,date,description,payee,amount,channel
              </code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
