import React, { useState, useEffect } from 'react';
import { Camera, Sparkles, Clock, ShieldCheck, Cpu } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) + ' | ' + now.toLocaleTimeString());
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-[#101322] border-b border-[#232740] px-6 flex items-center justify-between sticky top-0 z-40 backdrop-blur-md">
      {/* Left Brand */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Camera className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-bold text-base tracking-wide text-white">FACE ATTENDANCE</h1>
            <span className="px-2 py-0.5 text-[10px] font-extrabold bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 rounded-full tracking-wider">
              TANSTACK SAAS
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Real-Time Computer Vision & ML Platform</p>
        </div>
      </div>

      {/* Center Navigation Quick Pills */}
      <div className="hidden md:flex items-center gap-1 bg-[#151828] p-1 rounded-xl border border-[#232740]">
        <button
          onClick={() => setActiveTab('home')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'home'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          🏠 Home
        </button>
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'dashboard'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          📊 Dashboard
        </button>
        <button
          onClick={() => setActiveTab('scanner')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'scanner'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          📹 Live Scanner
        </button>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* System Online Badge */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>SYSTEM ONLINE</span>
        </div>

        {/* Live Clock Pill */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#151828] border border-[#232740] text-slate-300 text-xs font-mono">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{timeStr}</span>
        </div>
      </div>
    </header>
  );
}
