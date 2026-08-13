import React from 'react';
import { Home, BarChart3, Camera, UserPlus, FileSpreadsheet, Users, Sparkles, ShieldCheck } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'home', label: 'Home SaaS', icon: Home, badge: 'SaaS' },
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'scanner', label: 'Live Scanner', icon: Camera, highlight: true },
    { id: 'enrollment', label: 'Enrollment', icon: UserPlus },
    { id: 'logs', label: 'Attendance Logs', icon: FileSpreadsheet },
    { id: 'persons', label: 'Registered Users', icon: Users },
  ];

  return (
    <aside className="w-64 bg-[#101322] border-r border-[#232740] flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      {/* Top Menu Links */}
      <div className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Main Navigation
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl font-medium text-sm transition-all group ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/20 font-semibold'
                  : 'text-slate-400 hover:text-white hover:bg-[#151828]'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-cyan-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold bg-cyan-950/80 text-cyan-400 rounded-md border border-cyan-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom Info Card */}
      <div className="p-4 rounded-2xl bg-gradient-to-b from-[#151828] to-[#101322] border border-[#232740]">
        <div className="flex items-center gap-2 mb-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-slate-200">Anti-Proxy Protection</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
          Real-time LBPH feature matching with 5-minute automated cooldown limits.
        </p>
        <div className="flex items-center justify-between text-[11px] text-cyan-400 font-semibold pt-2 border-t border-[#232740]">
          <span>AI Engine</span>
          <span className="text-slate-300">LBPH + CLAHE</span>
        </div>
      </div>
    </aside>
  );
}
