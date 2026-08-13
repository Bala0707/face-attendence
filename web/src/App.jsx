import React, { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import ScannerPage from './pages/ScannerPage';
import EnrollmentPage from './pages/EnrollmentPage';
import LogsPage from './pages/LogsPage';
import PersonsPage from './pages/PersonsPage';
import {
  addPersonApi,
  clearLogsApi,
  deleteLogApi,
  deletePersonApi,
  fetchLogs,
  fetchPersons,
  fetchStats,
  getExportUrl,
  markAttendanceApi,
  trainModelApi,
} from './services/api';

const emptyStats = {
  total_enrolled: 0,
  total_present: 0,
  total_late: 0,
  total_absent: 0,
};

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [persons, setPersons] = useState([]);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(emptyStats);

  const refreshData = async () => {
    const [nextPersons, nextLogs, nextStats] = await Promise.all([
      fetchPersons(),
      fetchLogs(),
      fetchStats(),
    ]);

    if (Array.isArray(nextPersons)) setPersons(nextPersons);
    if (Array.isArray(nextLogs)) setLogs(nextLogs);
    if (nextStats) setStats(nextStats);
  };

  useEffect(() => {
    refreshData();
  }, []);

  const handleMarkAttendance = async (personId, name, confidence) => {
    if (!personId) return;

    const result = await markAttendanceApi(personId, confidence || 95);
    if (result && result.success) {
      await refreshData();
    }
  };

  const handleRegisterPerson = async (newPerson) => {
    const result = await addPersonApi(newPerson);
    if (result?.success) {
      await refreshData();
      return true;
    }
    return false;
  };

  const handleEditPerson = async (updated) => {
    const result = await addPersonApi(updated);
    if (result?.success) {
      await refreshData();
      return true;
    }
    return false;
  };

  const handleDeletePerson = async (personId) => {
    if (!confirm(`Are you sure you want to delete person ${personId}?`)) return;

    const result = await deletePersonApi(personId);
    if (result?.success) {
      await refreshData();
    }
  };

  const handleDeleteLog = async (logId) => {
    const result = await deleteLogApi(logId);
    if (result?.success) {
      await refreshData();
    }
  };

  const handleClearLogs = async () => {
    if (!confirm('Are you sure you want to clear all attendance logs?')) return;

    const result = await clearLogsApi();
    if (result?.success) {
      await refreshData();
    }
  };

  const handleTrainModel = async () => {
    const result = await trainModelApi();
    if (result?.success) {
      await refreshData();
      return true;
    }
    return false;
  };

  const handleExport = (format) => {
    window.open(getExportUrl(format), '_blank');
  };

  return (
    <div className="min-h-screen bg-[#0B0D17] text-slate-100 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex flex-1">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-7xl">
          {activeTab === 'home' && <HomePage setActiveTab={setActiveTab} />}
          {activeTab === 'dashboard' && <DashboardPage stats={stats} recentLogs={logs} onRefresh={refreshData} />}
          {activeTab === 'scanner' && <ScannerPage onMarkAttendance={handleMarkAttendance} />}
          {activeTab === 'enrollment' && <EnrollmentPage onRegisterPerson={handleRegisterPerson} onTrainModel={handleTrainModel} />}
          {activeTab === 'logs' && <LogsPage logs={logs} onDeleteLog={handleDeleteLog} onClearLogs={handleClearLogs} onExport={handleExport} />}
          {activeTab === 'persons' && <PersonsPage persons={persons} onEditPerson={handleEditPerson} onDeletePerson={handleDeletePerson} />}
        </main>
      </div>
    </div>
  );
}
