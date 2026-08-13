import React, { useState } from 'react';
import { Users, Edit3, Trash2, Search, UserCheck } from 'lucide-react';

export default function PersonsPage({ persons, onEditPerson, onDeletePerson }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [editingPerson, setEditingPerson] = useState(null);

  const filteredPersons = persons.filter(
    (p) =>
      p.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.department && p.department.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleSaveEdit = (e) => {
    e.preventDefault();
    if (editingPerson && onEditPerson) {
      onEditPerson(editingPerson);
      setEditingPerson(null);
    }
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Registered Members Directory</h2>
          <p className="text-xs text-slate-400">View enrolled students and employees, edit details, or delete records</p>
        </div>

        <div className="relative w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search member..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#141724] border border-[#232740] text-xs text-white focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* MEMBERS DIRECTORY GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredPersons.map((p) => (
          <div key={p.id} className="glass-card glass-card-hover rounded-2xl p-5 border border-[#232740] space-y-4 relative">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-md">
                  {p.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-bold text-white text-base leading-tight">{p.name}</h3>
                  <span className="text-xs font-mono text-cyan-400">{p.id}</span>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => setEditingPerson({ ...p })}
                  className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-600 hover:text-white transition-all"
                  title="Edit details"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => onDeletePerson(p.id)}
                  className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-600 hover:text-white transition-all"
                  title="Delete user"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div className="space-y-1.5 text-xs border-t border-[#232740] pt-3 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">Dept:</span>
                <span className="font-semibold">{p.department || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Role:</span>
                <span className="font-semibold text-emerald-400">{p.role || 'Student'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Email:</span>
                <span className="font-mono text-slate-400 truncate max-w-[180px]">{p.email || 'N/A'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* EDIT MODAL */}
      {editingPerson && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card rounded-2xl p-6 w-full max-w-md border border-[#232740] space-y-5">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Edit3 className="w-5 h-5 text-cyan-400" />
              <span>Edit Details - {editingPerson.id}</span>
            </h3>

            <form onSubmit={handleSaveEdit} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Full Name</label>
                <input
                  type="text"
                  value={editingPerson.name}
                  onChange={(e) => setEditingPerson({ ...editingPerson, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#141724] border border-[#232740] text-xs text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Department</label>
                <input
                  type="text"
                  value={editingPerson.department || ''}
                  onChange={(e) => setEditingPerson({ ...editingPerson, department: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#141724] border border-[#232740] text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Role</label>
                <input
                  type="text"
                  value={editingPerson.role || ''}
                  onChange={(e) => setEditingPerson({ ...editingPerson, role: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#141724] border border-[#232740] text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Email</label>
                <input
                  type="email"
                  value={editingPerson.email || ''}
                  onChange={(e) => setEditingPerson({ ...editingPerson, email: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#141724] border border-[#232740] text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setEditingPerson(null)}
                  className="px-4 py-2 rounded-xl bg-[#151828] text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white shadow-md"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
