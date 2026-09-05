import React from 'react';
import { Sun, Moon, UserCheck, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isDark: boolean;
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, isDark, onToggleTheme }) => {
  return (
    <header className="h-18 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/85 dark:bg-[#0b1120]/85 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between transition-colors duration-300">
      <div className="space-y-0.5 animate-fade-in">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
          {title}
        </h2>
        {subtitle && <p className="text-xs text-slate-500 dark:text-slate-400 font-normal">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Theme Toggle Button */}
        <button
          onClick={onToggleTheme}
          id="btn-theme-toggle"
          className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-all duration-200 hover:scale-105 active:scale-95 shadow-xs cursor-pointer group"
          title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          aria-label="Toggle Theme"
        >
          {isDark ? (
            <Sun className="w-4 h-4 text-amber-400 transition-transform duration-300 group-hover:rotate-45" />
          ) : (
            <Moon className="w-4 h-4 text-slate-600 transition-transform duration-300 group-hover:-rotate-12" />
          )}
        </button>

        {/* Analyst Profile */}
        <div className="flex items-center gap-3 pl-3.5 border-l border-slate-200 dark:border-slate-800">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-500/15 to-indigo-500/15 border border-blue-200 dark:border-blue-500/30 flex items-center justify-center text-blue-600 dark:text-blue-400 text-xs font-semibold shadow-xs">
            <UserCheck className="w-4 h-4" />
          </div>
          <div className="text-left hidden sm:block">
            <div className="font-semibold text-xs text-slate-800 dark:text-slate-200">Risk Analyst</div>
            <div className="text-[11px] text-slate-400 font-mono">RA-8042</div>
          </div>
        </div>
      </div>
    </header>
  );
};
