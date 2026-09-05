import React from 'react';
import { Finding } from '../types';
import { 
  X, 
  ExternalLink, 
  Database, 
  Info,
  ShieldCheck
} from 'lucide-react';

interface EvidenceDrawerProps {
  finding: Finding | null;
  onClose: () => void;
  onSelectTransaction?: (txnId: string) => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ 
  finding, 
  onClose,
  onSelectTransaction 
}) => {
  if (!finding) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/50 backdrop-blur-sm flex justify-end animate-fade-in transition-all">
      <div className="w-full max-w-xl bg-white dark:bg-[#0b1120] border-l border-slate-200 dark:border-slate-800 h-full shadow-2xl flex flex-col justify-between overflow-y-auto animate-slide-in-right">
        {/* Drawer Header */}
        <div className="p-6 border-b border-slate-200/80 dark:border-slate-800 bg-slate-50/90 dark:bg-slate-900/80 sticky top-0 z-10 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-200 dark:border-blue-500/30 flex items-center justify-center text-blue-700 dark:text-blue-300 font-mono text-xs font-bold shadow-xs">
                {finding.rule_id}
              </span>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white leading-tight">
                  Evidence Audit: {finding.finding_id}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                  Deterministic Rule {finding.rule_id} Verification
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Drawer Body */}
        <div className="p-6 space-y-6 flex-1">
          {/* Finding Core Info Box */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-3.5 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
                {finding.title}
              </span>
              <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border font-mono ${
                finding.severity === 'HIGH' 
                  ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 badge-glow-rose' 
                  : 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 badge-glow-amber'
              }`}>
                {finding.severity} SEVERITY
              </span>
            </div>
            <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
              {finding.description}
            </p>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center gap-2.5 pt-2 border-t border-slate-200/80 dark:border-slate-800">
              <span>Rule Confidence: <strong className="text-slate-800 dark:text-slate-200">{(finding.confidence * 100).toFixed(0)}%</strong></span>
              <span>•</span>
              <span>Source: <strong className="text-blue-600 dark:text-blue-400">Verified Database Ledger</strong></span>
            </div>
          </div>

          {/* Evidence Items Breakdown */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-500" />
              <span>Traceable Evidence Records ({finding.evidence?.length || 0})</span>
            </h4>

            <div className="space-y-3.5">
              {finding.evidence && finding.evidence.length > 0 ? (
                finding.evidence.map((item, idx) => (
                  <div key={idx} className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-3.5 shadow-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-blue-600 dark:text-blue-400">
                        Transaction: {item.transaction_id}
                      </span>
                      {onSelectTransaction && item.transaction_id && (
                        <button
                          onClick={() => {
                            onSelectTransaction(item.transaction_id);
                            onClose();
                          }}
                          className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center gap-1 font-semibold transition-colors cursor-pointer"
                        >
                          <span>Highlight in Table</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200/70 dark:border-slate-800">
                        <span className="text-[11px] text-slate-500 block uppercase font-mono font-semibold">Observed Value</span>
                        <span className="font-bold text-slate-900 dark:text-white font-mono text-xs mt-0.5 block">{item.observed_value}</span>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200/70 dark:border-slate-800">
                        <span className="text-[11px] text-slate-500 block uppercase font-mono font-semibold">Customer Baseline</span>
                        <span className="font-bold text-slate-700 dark:text-slate-300 font-mono text-xs mt-0.5 block">{item.baseline_value}</span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-blue-50/80 dark:bg-blue-950/30 border border-blue-200/80 dark:border-blue-900/50 text-xs text-blue-800 dark:text-blue-300 font-mono">
                      <span className="text-[10px] text-blue-600 dark:text-blue-400 block uppercase font-semibold">Calculated Deviation</span>
                      <strong className="text-slate-900 dark:text-white text-xs mt-0.5 block font-bold">{item.deviation}</strong>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      {item.explanation}
                    </p>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 italic p-4 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800">
                  Summary-level evidence based on overall temporal window.
                </div>
              )}
            </div>
          </div>

          {/* Traceability Audit Trail Notice */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400 space-y-2">
            <div className="flex items-center gap-2 text-slate-800 dark:text-slate-200 font-bold">
              <ShieldCheck className="w-4 h-4 text-blue-500" />
              <span>Evidence-First Guarantee</span>
            </div>
            <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              Every displayed metric was deterministically derived from verified transaction logs in the local database. 
              No external API or LLM altered the mathematical baseline or deviation calculation.
            </p>
          </div>
        </div>

        {/* Drawer Footer */}
        <div className="p-6 border-t border-slate-200/80 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 sticky bottom-0">
          <button
            onClick={onClose}
            className="w-full py-3 bg-slate-200 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs"
          >
            Close Evidence Drawer
          </button>
        </div>
      </div>
    </div>
  );
};
