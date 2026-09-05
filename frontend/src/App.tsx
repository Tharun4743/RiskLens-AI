import React, { useState, useEffect } from 'react';
import { api } from './api';
import { 
  Customer, 
  InvestigationResult, 
  Finding, 
  Transaction 
} from './types';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { InvestigationCenter } from './components/InvestigationCenter';
import { CustomerSelector } from './components/CustomerSelector';
import { AnalysisDashboard } from './components/AnalysisDashboard';
import { EvidenceDrawer } from './components/EvidenceDrawer';
import { ReportView } from './components/ReportView';
import { AnalystChatDrawer } from './components/AnalystChatDrawer';
import { CheckCircle2, AlertCircle, X } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [activeInvestigation, setActiveInvestigation] = useState<InvestigationResult | null>(null);
  const [activeTransactions, setActiveTransactions] = useState<Transaction[]>([]);
  const [activeFindingForEvidence, setActiveFindingForEvidence] = useState<Finding | null>(null);
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [systemHealthy, setSystemHealthy] = useState<boolean>(true);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [isDark, setIsDark] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('risklens_theme');
      if (saved) return saved === 'dark';
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      if (isDark) {
        document.documentElement.classList.add('dark');
        document.documentElement.style.colorScheme = 'dark';
        const meta = document.getElementById('meta-theme-color');
        if (meta) meta.setAttribute('content', '#09090b');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.style.colorScheme = 'light';
        const meta = document.getElementById('meta-theme-color');
        if (meta) meta.setAttribute('content', '#ffffff');
      }
    } catch (e) {}
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(prev => {
      const next = !prev;
      try {
        localStorage.setItem('risklens_theme', next ? 'dark' : 'light');
      } catch (e) {}
      return next;
    });
  };

  useEffect(() => {
    // Initial health check
    api.getHealth()
      .then(() => setSystemHealthy(true))
      .catch(() => setSystemHealthy(false));
  }, []);

  const handleSelectAndAnalyzeCustomer = async (customerId: string) => {
    setLoading(true);
    try {
      const inv = await api.createInvestigation(customerId);
      const txnsRes = await api.getTransactions(customerId, { limit: 1000 });
      setActiveInvestigation(inv);
      setActiveTransactions(txnsRes.transactions);
      setCurrentTab('analysis');
      setNotification({ message: `Investigation successfully completed for ${customerId}`, type: 'success' });
    } catch (err: any) {
      setNotification({ message: err.message || 'Investigation failed', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleViewInvestigation = async (investigationId: number) => {
    setLoading(true);
    try {
      const inv = await api.getInvestigation(investigationId);
      const txnsRes = await api.getTransactions(inv.customer_id, { limit: 1000 });
      setActiveInvestigation(inv);
      setActiveTransactions(txnsRes.transactions);
      setCurrentTab('analysis');
    } catch (err: any) {
      setNotification({ message: err.message || 'Failed to load investigation', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#f8fafc] dark:bg-[#090d16] text-slate-900 dark:text-slate-100 antialiased overflow-hidden font-sans transition-colors duration-300">
      {/* Sidebar */}
      <Sidebar 
        currentTab={currentTab} 
        setCurrentTab={setCurrentTab} 
        systemHealthy={systemHealthy}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Header 
          title={
            currentTab === 'overview' ? 'Investigation Center' :
            currentTab === 'customers' ? 'Customer Profile Selection & Ingestion' :
            currentTab === 'analysis' ? `Analysis Dashboard: ${activeInvestigation?.customer_id || ''}` :
            currentTab === 'reports' ? 'Formal Investigation Report' :
            'RiskLens AI'
          }
          subtitle={
            currentTab === 'overview' ? 'Evidence-First Triaging & Automated Risk Audits' :
            currentTab === 'customers' ? 'Select pre-seeded profiles or upload raw transaction history' :
            currentTab === 'analysis' ? 'Deterministic Baseline, Finding Deviations & Incident Clusters' :
            currentTab === 'reports' ? 'Exportable Banking Artifacts & Traceable Evidence' :
            undefined
          }
          isDark={isDark}
          onToggleTheme={toggleTheme}
        />

        {/* Global Toast Notification */}
        {notification && (
          <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
            <div className={`p-4 rounded-2xl shadow-xl border text-xs lg:text-sm font-medium flex items-center gap-3 backdrop-blur-md ${
              notification.type === 'success'
                ? 'bg-emerald-50/95 dark:bg-emerald-950/90 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                : 'bg-rose-50/95 dark:bg-rose-950/90 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200'
            }`}>
              {notification.type === 'success' ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />
              )}
              <span>{notification.message}</span>
              <button
                onClick={() => setNotification(null)}
                className="text-slate-400 hover:text-slate-700 dark:hover:text-white ml-3 p-1 rounded-lg transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        <main className="flex-1 pb-16">
          {currentTab === 'overview' && (
            <InvestigationCenter 
              onStartNew={() => setCurrentTab('customers')}
              onViewInvestigation={handleViewInvestigation}
            />
          )}

          {currentTab === 'customers' && (
            <CustomerSelector 
              onSelectCustomer={handleSelectAndAnalyzeCustomer}
              loading={loading}
            />
          )}

          {currentTab === 'investigations' && (
            <InvestigationCenter 
              onStartNew={() => setCurrentTab('customers')}
              onViewInvestigation={handleViewInvestigation}
            />
          )}

          {currentTab === 'analysis' && activeInvestigation && (
            <AnalysisDashboard 
              investigation={activeInvestigation}
              transactions={activeTransactions}
              onOpenEvidence={(finding) => setActiveFindingForEvidence(finding)}
              onOpenReport={() => setCurrentTab('reports')}
              onOpenChat={() => setIsChatOpen(true)}
            />
          )}

          {currentTab === 'reports' && activeInvestigation && (
            <ReportView 
              investigation={activeInvestigation}
              onBack={() => setCurrentTab('analysis')}
              onOpenEvidence={(findingId) => {
                const f = activeInvestigation.findings.find(item => item.finding_id === findingId);
                if (f) setActiveFindingForEvidence(f);
              }}
            />
          )}

          {/* Fallback if analysis tab opened without investigation */}
          {(currentTab === 'analysis' || currentTab === 'reports') && !activeInvestigation && (
            <div className="p-20 text-center space-y-4 max-w-md mx-auto animate-fade-in">
              <div className="text-base font-bold text-slate-800 dark:text-slate-200">No active investigation loaded</div>
              <p className="text-xs lg:text-sm text-slate-500 leading-relaxed">
                Please select a customer profile or upload a transaction history CSV to start an investigation.
              </p>
              <button
                onClick={() => setCurrentTab('customers')}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-blue-500/20 transition-all cursor-pointer"
              >
                Go to Customers
              </button>
            </div>
          )}
        </main>
      </div>

      {/* Slide-over Evidence Drawer */}
      <EvidenceDrawer 
        finding={activeFindingForEvidence}
        onClose={() => setActiveFindingForEvidence(null)}
      />

      {/* Analyst Q&A Grounded Chat Drawer */}
      {activeInvestigation?.id && (
        <AnalystChatDrawer 
          investigationId={activeInvestigation.id}
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
        />
      )}
    </div>
  );
};
