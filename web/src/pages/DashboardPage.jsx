import React, { useState } from 'react';
import { Users, UserCheck, Clock, UserX, RefreshCw, TrendingUp, BarChart2 } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function DashboardPage({ stats, recentLogs, onRefresh }) {
  // Weekly Trend Mock Data
  const trendData = [
    { day: 'Mon', present: 24, late: 3, absent: 2 },
    { day: 'Tue', present: 27, late: 2, absent: 0 },
    { day: 'Wed', present: 25, late: 4, absent: 1 },
    { day: 'Thu', present: 28, late: 1, absent: 0 },
    { day: 'Fri', present: 26, late: 3, absent: 1 },
  ];

  const pieData = [
    { name: 'Present', value: stats.total_present || 3, color: '#10B981' },
    { name: 'Late', value: stats.total_late || 1, color: '#F59E0B' },
    { name: 'Absent', value: stats.total_absent || 0, color: '#EF4444' },
  ];

  return (
    <div className="space-y-8 pb-10">
      {/* HEADER SECTION */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">System Dashboard</h2>
          <p className="text-xs text-slate-400">Real-time metrics, weekly trend analytics, and today's live check-in logs</p>
        </div>
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#151828] border border-[#232740] text-slate-200 text-xs font-semibold hover:bg-[#1D2138] hover:text-white transition-all shadow-md"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* HERO STATS CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Enrolled Card */}
        <div className="glass-card glass-card-hover rounded-2xl p-5 relative overflow-hidden border-t-4 border-t-blue-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Registered</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mt-3">{stats.total_enrolled}</div>
          <p className="text-[11px] text-slate-400 mt-1">Active student & employee profiles</p>
        </div>

        {/* Present Card */}
        <div className="glass-card glass-card-hover rounded-2xl p-5 relative overflow-hidden border-t-4 border-t-emerald-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Present Today</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-3">{stats.total_present}</div>
          <p className="text-[11px] text-slate-400 mt-1">On-time check-ins today</p>
        </div>

        {/* Late Card */}
        <div className="glass-card glass-card-hover rounded-2xl p-5 relative overflow-hidden border-t-4 border-t-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Late Today</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-amber-400 mt-3">{stats.total_late}</div>
          <p className="text-[11px] text-slate-400 mt-1">Arrived after start threshold</p>
        </div>

        {/* Absent Card */}
        <div className="glass-card glass-card-hover rounded-2xl p-5 relative overflow-hidden border-t-4 border-t-rose-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Absent Today</span>
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
              <UserX className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-rose-400 mt-3">{stats.total_absent}</div>
          <p className="text-[11px] text-slate-400 mt-1">Unmarked / Absent count</p>
        </div>
      </div>

      {/* RECHARTS ANALYTICS SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Area Chart: Attendance Trend */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
              <h3 className="font-bold text-white text-base">Weekly Check-in Trend</h3>
            </div>
            <span className="text-xs font-semibold text-slate-400">Mon - Fri</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPresent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorLate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#232740" />
                <XAxis dataKey="day" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#151828', borderColor: '#232740', borderRadius: '12px', color: '#FFF' }} />
                <Area type="monotone" dataKey="present" stroke="#10B981" fillOpacity={1} fill="url(#colorPresent)" strokeWidth={2} />
                <Area type="monotone" dataKey="late" stroke="#F59E0B" fillOpacity={1} fill="url(#colorLate)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart: Status Distribution */}
        <div className="glass-card rounded-2xl p-6 space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-purple-400" />
            <h3 className="font-bold text-white text-base">Status Breakdown</h3>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} innerRadius={55} outerRadius={75} paddingAngle={4} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#151828', borderColor: '#232740', borderRadius: '12px', color: '#FFF' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex justify-around text-xs font-semibold pt-2 border-t border-[#232740]">
            <span className="text-emerald-400">● Present</span>
            <span className="text-amber-400">● Late</span>
            <span className="text-rose-400">● Absent</span>
          </div>
        </div>
      </div>

      {/* RECENT ACTIVITY TABLE */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>Recent Activity Feed (Today)</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#1E2235] text-slate-200 uppercase font-bold text-[11px] rounded-lg">
              <tr>
                <th className="p-3">ID</th>
                <th className="p-3">Name</th>
                <th className="p-3">Department</th>
                <th className="p-3">Time In</th>
                <th className="p-3">Time Out</th>
                <th className="p-3">Status</th>
                <th className="p-3">Match %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#232740]">
              {recentLogs && recentLogs.length > 0 ? (
                recentLogs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-[#1D2138] transition-colors">
                    <td className="p-3 font-mono text-cyan-400">{log.person_id}</td>
                    <td className="p-3 font-semibold text-white">{log.name}</td>
                    <td className="p-3 text-slate-400">{log.department || 'N/A'}</td>
                    <td className="p-3 font-mono">{log.time_in}</td>
                    <td className="p-3 font-mono text-slate-400">{log.time_out || '--'}</td>
                    <td className="p-3">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${
                        log.status === 'Present' ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/30' : 'bg-amber-950/80 text-amber-400 border border-amber-500/30'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="p-3 font-semibold text-slate-300">{log.confidence}%</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-4 text-center text-slate-400">No attendance records logged today yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
