import React from 'react';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Users, 
  FileText, 
  Activity, 
  Server,
  Sparkles,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  systemHealthy: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab, systemHealthy }) => {
  const navItems = [
    { id: 'overview', label: 'Investigation Center', icon: LayoutDashboard, badge: null },
    { id: 'customers', label: 'Customers & Ingestion', icon: Users, badge: null },
    { id: 'investigations', label: 'Active Investigations', icon: Activity, badge: null },
    { id: 'reports', label: 'Audit & Reports', icon: FileText, badge: null },
  ];

  return (
    <aside className="w-68 bg-white dark:bg-[#0b1120] border-r border-slate-200 dark:border-slate-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0 transition-colors duration-300 z-20">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-200/80 dark:border-slate-800/80 bg-gradient-to-b from-slate-50/50 to-transparent dark:from-slate-900/30 dark:to-transparent">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/25 ring-2 ring-blue-500/20">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">
                RiskLens
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Banking Risk Protocol</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="px-3.5 py-6 space-y-1.5">
          <div className="text-xs font-bold tracking-wider text-slate-400 dark:text-slate-500 px-3.5 uppercase mb-3">
            Investigation Suite
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                id={`nav-btn-${item.id}`}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-500/10 to-indigo-500/10 dark:from-blue-500/20 dark:to-indigo-500/15 text-blue-600 dark:text-blue-400 border border-blue-200/80 dark:border-blue-500/30 font-semibold shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/80 dark:hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30' 
                      : 'text-slate-400 dark:text-slate-500 group-hover:text-slate-700 dark:group-hover:text-slate-300'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="tracking-tight">{item.label}</span>
                </div>
                <ChevronRight className={`w-4 h-4 transition-transform duration-200 ${
                  isActive 
                    ? 'text-blue-500 dark:text-blue-400 translate-x-0.5' 
                    : 'text-transparent group-hover:text-slate-400 dark:group-hover:text-slate-500 -translate-x-1 group-hover:translate-x-0'
                }`} />
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
};
