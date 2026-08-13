import React from 'react';
import { Camera, UserPlus, BarChart3, Sparkles, ShieldCheck, Cpu, ArrowRight, CheckCircle2, Zap } from 'lucide-react';

export default function HomePage({ setActiveTab }) {
  const saasFeatures = [
    {
      title: 'Computer Vision AI',
      desc: 'OpenCV Haar Cascade & CLAHE Adaptive Illumination engine for real-time face localization.',
      icon: Cpu,
      color: 'from-cyan-500 to-blue-600',
    },
    {
      title: 'Machine Learning Model',
      desc: 'LBPH (Local Binary Patterns Histograms) texture vector analysis with Euclidean distance scoring.',
      icon: Sparkles,
      color: 'from-purple-500 to-indigo-600',
    },
    {
      title: 'Multi-Format Reports',
      desc: 'One-click automated export to formatted Excel (.xlsx), standard CSV, and styled HTML summary reports.',
      icon: BarChart3,
      color: 'from-emerald-500 to-teal-600',
    },
  ];

  const steps = [
    { num: '1', title: 'Enroll Member', desc: 'Register ID and capture 20 face photo samples.' },
    { num: '2', title: 'Train AI Model', desc: 'Compile texture features into LBPH binary model.' },
    { num: '3', title: 'Live Scanning', desc: 'Camera detects faces & auto-logs Present / Late.' },
    { num: '4', title: 'Export Reports', desc: 'One-click download of Excel, CSV, or HTML reports.' },
  ];

  return (
    <div className="space-y-8 pb-10">
      {/* HERO BANNER SECTION */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#151828] via-[#101322] to-[#0D0F1B] border border-[#232740] p-8 md:p-12 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-4xl space-y-6">
          {/* SaaS Pill Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 text-xs font-bold tracking-wide">
            <Zap className="w-3.5 h-3.5" />
            <span>POWERED BY ARTIFICIAL INTELLIGENCE & COMPUTER VISION</span>
          </div>

          {/* Hero Title */}
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Intelligent Real-Time <br />
            <span className="gradient-text">Face Attendance Platform</span>
          </h1>

          {/* Subtitle */}
          <p className="text-slate-300 text-base md:text-lg font-normal leading-relaxed max-w-3xl">
            Automate student and employee attendance logging with high-precision computer vision, anti-proxy cooldown protection, automated SQLite persistence, and instant multi-format report exports.
          </p>

          {/* Call to Action Buttons */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={() => setActiveTab('scanner')}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold text-sm shadow-lg shadow-emerald-500/25 hover:brightness-110 hover:scale-[1.02] transition-all"
            >
              <Camera className="w-4 h-4" />
              <span>Open Live Camera Scanner</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => setActiveTab('enrollment')}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-bold text-sm shadow-lg shadow-blue-500/25 hover:brightness-110 hover:scale-[1.02] transition-all"
            >
              <UserPlus className="w-4 h-4" />
              <span>Enroll New Member</span>
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-[#1D2138] text-slate-200 border border-[#232740] font-semibold text-sm hover:bg-[#232740] hover:text-white transition-all"
            >
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <span>View Analytics</span>
            </button>
          </div>
        </div>
      </div>

      {/* CORE FEATURES GRID */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-cyan-400" />
          <span>Core SaaS Platform Capabilities</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {saasFeatures.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div key={idx} className="glass-card glass-card-hover rounded-2xl p-6 space-y-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${feat.color} flex items-center justify-center shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white">{feat.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feat.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* HOW IT WORKS (4 STEPS) */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <span>How It Works (4 Simple Steps)</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {steps.map((st, idx) => (
            <div key={idx} className="glass-card rounded-2xl p-5 space-y-3 relative border-l-4 border-l-cyan-500">
              <div className="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-500/40 text-cyan-400 font-bold text-sm flex items-center justify-center">
                {st.num}
              </div>
              <h4 className="font-bold text-base text-white">{st.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{st.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
