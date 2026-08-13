import React, { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
} from '@tanstack/react-table';
import { Search, Download, Trash2, ArrowUpDown, FileSpreadsheet, FileText, Globe, RefreshCw } from 'lucide-react';

export default function LogsPage({ logs, onDeleteLog, onClearLogs, onExport }) {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);

  // TanStack Table Column Definitions
  const columns = useMemo(
    () => [
      {
        accessorKey: 'id',
        header: 'Log ID',
        cell: (info) => <span className="font-mono text-cyan-400 font-bold">#{info.getValue()}</span>,
      },
      {
        accessorKey: 'person_id',
        header: 'Person ID',
        cell: (info) => <span className="font-mono text-slate-300">{info.getValue()}</span>,
      },
      {
        accessorKey: 'name',
        header: 'Full Name',
        cell: (info) => <span className="font-bold text-white">{info.getValue()}</span>,
      },
      {
        accessorKey: 'department',
        header: 'Department',
        cell: (info) => <span className="text-slate-400">{info.getValue() || 'N/A'}</span>,
      },
      {
        accessorKey: 'date',
        header: 'Date',
        cell: (info) => <span className="font-mono text-slate-300">{info.getValue()}</span>,
      },
      {
        accessorKey: 'time_in',
        header: 'Time In',
        cell: (info) => <span className="font-mono text-emerald-400 font-medium">{info.getValue()}</span>,
      },
      {
        accessorKey: 'time_out',
        header: 'Time Out',
        cell: (info) => <span className="font-mono text-slate-400">{info.getValue() || '--'}</span>,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info) => {
          const val = info.getValue();
          return (
            <span
              className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${
                val === 'Present'
                  ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-950/80 text-amber-400 border border-amber-500/30'
              }`}
            >
              {val}
            </span>
          );
        },
      },
      {
        accessorKey: 'confidence',
        header: 'Match %',
        cell: (info) => <span className="font-semibold text-slate-200">{info.getValue()}%</span>,
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => (
          <button
            onClick={() => onDeleteLog(row.original.id)}
            className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white transition-all"
            title="Delete this log"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        ),
      },
    ],
    [onDeleteLog]
  );

  const table = useReactTable({
    data: logs,
    columns,
    state: {
      globalFilter,
      sorting,
    },
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-extrabold text-white tracking-tight">Attendance Logs</h2>
            <span className="px-2.5 py-0.5 text-xs font-bold bg-cyan-950 border border-cyan-500/30 text-cyan-400 rounded-full">
              TanStack Table Engine
            </span>
          </div>
          <p className="text-xs text-slate-400">Searchable, sortable attendance records table with export and bulk management</p>
        </div>

        {/* EXPORT BUTTONS */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onExport('excel')}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md transition-all"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Export Excel</span>
          </button>
          <button
            onClick={() => onExport('csv')}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-md transition-all"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => onExport('html')}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold shadow-md transition-all"
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Export HTML</span>
          </button>
        </div>
      </div>

      {/* FILTER & SEARCH BAR */}
      <div className="glass-card rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 border border-[#232740]">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by Name or Person ID..."
            value={globalFilter ?? ''}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#141724] border border-[#232740] text-xs text-white focus:outline-none focus:border-cyan-500"
          />
        </div>

        <button
          onClick={onClearLogs}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-600 hover:text-white text-xs font-bold transition-all"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear All Logs</span>
        </button>
      </div>

      {/* TANSTACK TABLE CONTAINER */}
      <div className="glass-card rounded-2xl p-4 overflow-hidden border border-[#232740]">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#1E2235] text-slate-200 uppercase font-bold text-[11px] rounded-lg">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} className="p-3 cursor-pointer select-none" onClick={header.column.getToggleSortingHandler()}>
                      <div className="flex items-center gap-1.5">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && <ArrowUpDown className="w-3 h-3 text-slate-500" />}
                      </div>
                    </th>
                  ))}
                </tr>
              ))}
            </thead>

            <tbody className="divide-y divide-[#232740]">
              {table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="hover:bg-[#1D2138] transition-colors">
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="p-3">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length} className="p-6 text-center text-slate-400">
                    No attendance logs match the current query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* PAGINATION */}
        <div className="flex items-center justify-between pt-4 mt-4 border-t border-[#232740] text-xs text-slate-400">
          <div>
            Page <span className="font-bold text-white">{table.getState().pagination.pageIndex + 1}</span> of{' '}
            <span className="font-bold text-white">{table.getPageCount() || 1}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="px-3 py-1.5 rounded-lg bg-[#141724] border border-[#232740] hover:text-white disabled:opacity-40"
            >
              Previous
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="px-3 py-1.5 rounded-lg bg-[#141724] border border-[#232740] hover:text-white disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
