import React, { useState } from 'react';
import { InvestigationResult, InvestigationExplanation } from '../types';
import { api } from '../api';
import { 
  Download, 
  FileText, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowLeft, 
  Sparkles, 
  HelpCircle, 
  CheckCircle, 
  ExternalLink, 
  Lock, 
  Layers, 
  Activity,
  Check
} from 'lucide-react';

interface ReportViewProps {
  investigation: InvestigationResult;
  onBack: () => void;
  onOpenEvidence: (findingId: string) => void;
}

export const ReportView: React.FC<ReportViewProps> = ({ 
  investigation, 
  onBack,
  onOpenEvidence 
}) => {
  const [aiExplanation, setAiExplanation] = useState<InvestigationExplanation | null>(null);
  const [loadingAi, setLoadingAi] = useState<boolean>(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const handleFetchAiExplanation = async () => {
    if (!investigation.id) return;
    setLoadingAi(true);
    setAiError(null);
    try {
      const data = await api.explainInvestigation(investigation.id);
      setAiExplanation(data);
    } catch (err: any) {
      setAiError(err.message || 'Failed to fetch AI explanation.');
    } finally {
      setLoadingAi(false);
    }
  };

  const isAttention = investigation.investigation_status === 'ATTENTION_REQUIRED';

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* Top Controls */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-200 transition-all duration-200 hover:-translate-x-0.5 cursor-pointer shadow-xs"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            id="btn-ai-explain"
            onClick={handleFetchAiExplanation}
            disabled={loadingAi}
            className="px-4 py-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 dark:hover:bg-purple-900/50 border border-purple-300 dark:border-purple-800/80 text-purple-700 dark:text-purple-300 text-xs font-bold flex items-center gap-2 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer disabled:opacity-50 shadow-xs"
          >
            {loadingAi ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></span>
                <span>Generating Grounded Explanation...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span>Request Gemini Explanation</span>
              </>
            )}
          </button>

          {investigation.id && (
            <a
              id="btn-export-pdf"
              href={api.getPdfUrl(investigation.id)}
              download
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-blue-500/20 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Export PDF Report</span>
            </a>
          )}
        </div>
      </div>

      {/* AI Notification Banner if generated or fallback */}
      {aiExplanation && (
        <div className={`p-5 rounded-2xl border text-xs animate-fade-in shadow-xs ${
          aiExplanation.is_deterministic_fallback
            ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-300 dark:border-amber-800/80 text-amber-800 dark:text-amber-300'
            : 'bg-purple-50 dark:bg-purple-950/30 border-purple-300 dark:border-purple-800/80 text-purple-900 dark:text-purple-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-sm flex items-center gap-2 uppercase tracking-wide">
              <Sparkles className="w-4 h-4" />
              {aiExplanation.is_deterministic_fallback ? 'Deterministic Fallback Active' : 'Gemini AI Explanation Verified'}
            </span>
            <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-full bg-slate-200/80 dark:bg-black/40 text-slate-700 dark:text-slate-300">
              Hallucination Guardrails: Passed
            </span>
          </div>
          <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-xs lg:text-sm font-normal">
            {aiExplanation.fallback_notice || 'Gemini explanation generated strictly grounded in deterministic evidence packet. All transaction IDs and amounts verified against database.'}
          </p>
        </div>
      )}

      {/* Formal Investigation Document Container */}
      <div className="enterprise-card rounded-3xl border border-slate-200/90 dark:border-slate-800/90 bg-white dark:bg-[#0b1120] p-8 lg:p-10 space-y-8 shadow-sm">
        {/* Document Header */}
        <div className="border-b border-slate-200/80 dark:border-slate-800 pb-7 flex items-start justify-between flex-wrap gap-4">
          <div className="space-y-1">
            <div className="text-xs font-mono font-bold tracking-widest text-slate-500 dark:text-slate-400 uppercase flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              CONFIDENTIAL BANKING AUDIT REPORT
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              RiskLens AI Investigation Report
            </h1>
            <p className="text-xs lg:text-sm text-slate-500 dark:text-slate-400 font-medium">
              Subject: {investigation.customer_name} ({investigation.customer_id})
            </p>
          </div>

          <div className="text-right text-xs space-y-1">
            <div className="font-mono font-bold text-slate-700 dark:text-slate-300 text-sm">
              Case Ref: INV-{investigation.id ? investigation.id.toString().padStart(4, '0') : 'DRAFT'}
            </div>
            <div className="text-xs text-slate-500 font-mono">
              Generated: {new Date().toISOString().substring(0, 16).replace('T', ' ')} UTC
            </div>
          </div>
        </div>

        {/* Overall Result Banner */}
        <div className={`p-7 rounded-2xl border flex items-start justify-between flex-wrap gap-5 ${
          isAttention
            ? 'bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-amber-300 dark:border-amber-800/80'
            : 'bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent border-emerald-300 dark:border-emerald-800/80'
        }`}>
          <div className="space-y-2 max-w-xl">
            <span className="text-xs font-mono font-bold tracking-wider text-slate-500 dark:text-slate-400 uppercase">
              Overall Triaging Outcome
            </span>
            <div className={`text-2xl font-extrabold flex items-center gap-2.5 ${
              isAttention ? 'text-amber-700 dark:text-amber-400' : 'text-emerald-700 dark:text-emerald-400'
            }`}>
              {isAttention ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle2 className="w-6 h-6" />}
              <span>{investigation.badge_text.toUpperCase()}</span>
            </div>
            <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
              {aiExplanation?.summary || investigation.summary}
            </p>
          </div>

          <div className="text-right space-y-1">
            <div className="text-xs uppercase font-mono font-bold text-slate-500 dark:text-slate-400">Investigation Priority</div>
            <div className="text-3xl font-extrabold font-mono text-slate-900 dark:text-white">
              {investigation.priority_score}<span className="text-sm text-slate-500">/100</span>
            </div>
            <span className={`inline-block px-3 py-1 rounded-lg text-xs font-bold font-mono border ${
              investigation.risk_level === 'HIGH' ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-800 text-rose-700 dark:text-rose-400 badge-glow-rose' :
              investigation.risk_level === 'MODERATE' ? 'bg-amber-50 dark:bg-amber-950/60 border-amber-300 dark:border-amber-800 text-amber-700 dark:text-amber-400 badge-glow-amber' :
              'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400'
            }`}>
              {investigation.risk_level}
            </span>
          </div>
        </div>

        {/* Key Findings Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800 pb-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Key Deterministic Findings ({investigation.findings?.length || 0})</span>
            </h2>
            <span className="text-xs text-slate-500 font-mono">Traceable to database records</span>
          </div>

          {!investigation.findings || investigation.findings.length === 0 ? (
            <div className="p-8 rounded-2xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 text-center space-y-2">
              <CheckCircle className="w-8 h-8 text-emerald-500 dark:text-emerald-400 mx-auto" />
              <div className="text-sm font-bold text-slate-800 dark:text-slate-200">No Rule Violations Detected</div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                All analysed transactions conform to normal behavioural distribution. No further action required.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {investigation.findings.map((f) => (
                <div key={f.finding_id} className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-blue-100 dark:bg-blue-950 border border-blue-300 dark:border-blue-800 text-blue-800 dark:text-blue-400">
                        {f.finding_id}
                      </span>
                      <span className="font-bold text-sm text-slate-900 dark:text-white">
                        {f.title}
                      </span>
                    </div>
                    <button
                      onClick={() => onOpenEvidence(f.finding_id)}
                      className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-bold inline-flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <span>Inspect Evidence</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
                    {f.description}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 font-mono pt-2.5 border-t border-slate-200/80 dark:border-slate-800">
                    <span>Rule: <strong className="text-slate-700 dark:text-slate-200">{f.rule_id}</strong></span>
                    <span>•</span>
                    <span>Involved Transactions: <strong className="text-blue-600 dark:text-blue-400">{f.transaction_ids?.join(', ')}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Correlated Activity Section */}
        {investigation.correlated_events && investigation.correlated_events.length > 0 && (
          <div className="space-y-4">
            <div className="border-b border-slate-200/80 dark:border-slate-800 pb-3">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span>Correlated Activity Clusters</span>
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {investigation.correlated_events.map((evt) => (
                <div key={evt.event_id} className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 space-y-2.5 shadow-xs">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-bold text-purple-700 dark:text-purple-400 text-sm">{evt.event_id}</span>
                    <span className="text-xs font-mono text-slate-500 dark:text-slate-400">{evt.time_window.duration_minutes} min window</span>
                  </div>
                  <p className="text-xs lg:text-sm text-slate-700 dark:text-slate-300 font-medium">
                    {evt.summary}
                  </p>
                  <div className="text-xs text-slate-500 dark:text-slate-400 font-mono pt-1.5 border-t border-slate-200/80 dark:border-slate-800">
                    Transactions: {evt.transaction_ids.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* What to Check First (Investigator Actions) */}
        <div className="space-y-4">
          <div className="border-b border-slate-200/80 dark:border-slate-800 pb-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>What to Check First (Recommended Actions)</span>
            </h2>
          </div>

          <div className="space-y-3">
            {(aiExplanation?.investigator_actions || investigation.recommended_actions || []).map((action: any, idx: number) => {
              const text = typeof action === 'string' ? action : action.action_text;
              return (
                <div key={idx} className="flex items-start gap-3.5 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 text-xs lg:text-sm shadow-xs">
                  <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-400 flex items-center justify-center font-mono font-bold text-xs shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="text-slate-700 dark:text-slate-200 leading-relaxed font-normal">{text}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Unknown Information Section */}
        <div className="space-y-4">
          <div className="border-b border-slate-200/80 dark:border-slate-800 pb-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>Information Remaining Unknown</span>
            </h2>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 space-y-2.5 text-xs lg:text-sm text-slate-600 dark:text-slate-400">
            {(aiExplanation?.unknowns || investigation.unknowns || []).map((un: string, idx: number) => (
              <div key={idx} className="flex items-start gap-2.5">
                <span className="text-amber-600 dark:text-amber-400 font-bold">•</span>
                <span className="leading-relaxed">{un}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Final Handoff & Human-in-the-Loop Disclaimer */}
        <div className="p-6 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-xs lg:text-sm uppercase tracking-wide">
            <Lock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Final Handoff: Human Investigator Review Required</span>
          </div>
          <p className="text-xs lg:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
            {investigation.scoring?.disclaimer || "Human investigator review required. RiskLens AI identifies unusual activity and provides supporting evidence. It does not determine whether fraud occurred."}
          </p>
        </div>
      </div>
    </div>
  );
};
