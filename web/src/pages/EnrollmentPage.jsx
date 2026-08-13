import React, { useState } from 'react';
import { UserPlus, Camera, Upload, Cpu, CheckCircle2, Sparkles } from 'lucide-react';

export default function EnrollmentPage({ onRegisterPerson, onTrainModel }) {
  const [personId, setPersonId] = useState('');
  const [name, setName] = useState('');
  const [department, setDepartment] = useState('');
  const [role, setRole] = useState('Student');
  const [email, setEmail] = useState('');

  const [sampleCount, setSampleCount] = useState(0);
  const [statusMsg, setStatusMsg] = useState('');
  const [isTraining, setIsTraining] = useState(false);

  const handleSubmitForm = (e) => {
    e.preventDefault();
    if (!personId || !name) {
      alert('Please enter both Person ID and Full Name.');
      return;
    }
    onRegisterPerson({
      id: personId,
      name,
      department,
      role,
      email,
      created_at: new Date().toISOString().split('T')[0]
    });
    setSampleCount(20);
    setStatusMsg(`✅ Captured 20 face samples for ${name} (${personId}).`);
  };

  const handleTrain = () => {
    setIsTraining(true);
    setTimeout(() => {
      onTrainModel();
      setIsTraining(false);
      alert('⚙️ Face Recognition Machine Learning Model Trained Successfully!');
    }, 1500);
  };

  return (
    <div className="space-y-6 pb-10">
      <div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight">Member Enrollment & AI Training</h2>
        <p className="text-xs text-slate-400">Register new students or employees, capture face photo samples, and train the LBPH model</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* FORM CARD */}
        <div className="glass-card rounded-2xl p-6 space-y-5 border border-[#232740]">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-cyan-400" />
            <span>Registration Profile Form</span>
          </h3>

          <form onSubmit={handleSubmitForm} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Person ID / Roll No (Required)</label>
              <input
                type="text"
                placeholder="e.g., EMP001"
                value={personId}
                onChange={(e) => setPersonId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#141724] border border-[#232740] text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Full Name (Required)</label>
              <input
                type="text"
                placeholder="e.g., John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#141724] border border-[#232740] text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Department</label>
                <input
                  type="text"
                  placeholder="e.g., Computer Science"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#141724] border border-[#232740] text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#141724] border border-[#232740] text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
                >
                  <option value="Student">Student</option>
                  <option value="Employee">Employee</option>
                  <option value="Faculty">Faculty</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Email Address</label>
              <input
                type="email"
                placeholder="e.g., john@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#141724] border border-[#232740] text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-bold text-sm shadow-lg shadow-blue-500/20 hover:brightness-110 transition-all pt-3"
            >
              <Camera className="w-4 h-4" />
              <span>Capture Face Photo Samples</span>
            </button>
          </form>
        </div>

        {/* PHOTO CAPTURE & MODEL TRAINING CARD */}
        <div className="glass-card rounded-2xl p-6 space-y-6 flex flex-col justify-between border border-[#232740]">
          <div className="space-y-4">
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <Cpu className="w-5 h-5 text-purple-400" />
              <span>Face Sample Capture & Model Training</span>
            </h3>

            <div className="p-4 rounded-xl bg-[#141724] border border-[#232740] space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                <span>Samples Count:</span>
                <span className="text-cyan-400 font-bold">{sampleCount} / 20</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-gradient-to-r from-cyan-500 to-blue-600 h-full transition-all duration-300" style={{ width: `${(sampleCount / 20) * 100}%` }} />
              </div>
              {statusMsg && <p className="text-xs text-emerald-400 font-medium">{statusMsg}</p>}
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={handleTrain}
              disabled={isTraining}
              className={`w-full flex items-center justify-center gap-2 py-4 rounded-xl text-white font-bold text-sm shadow-lg transition-all ${
                isTraining ? 'bg-slate-700 cursor-not-allowed' : 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:brightness-110 shadow-emerald-500/20'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>{isTraining ? 'Training LBPH Model...' : '⚙️ Train Face Recognition Model'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
