import React, { useState, useMemo } from "react";
import { cn } from "@/lib/utils";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./Table";
import { Input } from "./Input";
import { Button } from "./Button";
import { Skeleton } from "./Skeleton";
import { EmptyState } from "./EmptyState";
import { Search, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

export interface Column<T> {
  key?: string;
  accessorKey?: string;
  header: string;
  accessor?: (item: T) => any;
  render?: (item: T) => React.ReactNode;
  cell?: (item: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  isLoading?: boolean;
  searchPlaceholder?: string;
  searchableKey?: string;
  pageSize?: number;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyMessage?: string;
  emptyAction?: React.ReactNode;
  rowKey?: (item: T, idx?: number) => string;
  onRowClick?: (item: T) => void;
  actions?: React.ReactNode;
  className?: string;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  isLoading = false,
  searchPlaceholder = "Search records...",
  searchableKey,
  pageSize = 10,
  emptyTitle = "No records found",
  emptyDescription = "There are currently no items matching your criteria.",
  emptyMessage,
  emptyAction,
  rowKey = (item: T, idx?: number) => (item && item.id ? String(item.id) : String(idx ?? 0)),
  onRowClick,
  actions,
  className,
}: DataTableProps<T>) {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [currentPage, setCurrentPage] = useState(1);

  // Search filter
  const filteredData = useMemo(() => {
    if (!searchQuery.trim()) return data;
    const q = searchQuery.toLowerCase().trim();
    return data.filter((item) => {
      if (searchableKey && item[searchableKey] !== undefined) {
        return String(item[searchableKey]).toLowerCase().includes(q);
      }
      return Object.values(item).some((val) =>
        String(val ?? "").toLowerCase().includes(q)
      );
    });
  }, [data, searchQuery, searchableKey]);

  // Sorting
  const sortedData = useMemo(() => {
    if (!sortKey) return filteredData;
    const col = columns.find((c) => c.key === sortKey);
    return [...filteredData].sort((a, b) => {
      const valA = col?.accessor ? col.accessor(a) : a[sortKey];
      const valB = col?.accessor ? col.accessor(b) : b[sortKey];

      if (valA === valB) return 0;
      if (valA === null || valA === undefined) return 1;
      if (valB === null || valB === undefined) return -1;

      const compare = valA > valB ? 1 : -1;
      return sortDirection === "asc" ? compare : -compare;
    });
  }, [filteredData, sortKey, sortDirection, columns]);

  // Pagination
  const totalPages = Math.ceil(sortedData.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else {
        setSortKey(null);
        setSortDirection("asc");
      }
    } else {
      setSortKey(key);
      setSortDirection("asc");
    }
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Top Search & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative max-w-sm w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            placeholder={searchPlaceholder}
            className="w-full bg-slate-900/60 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
          />
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      {/* Table Surface */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 backdrop-blur-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : paginatedData.length === 0 ? (
          <div className="py-12">
            <EmptyState
              title={emptyTitle}
              description={emptyMessage || emptyDescription}
              action={emptyAction}
            />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((col) => {
                  const colKey = col.key || col.accessorKey || col.header;
                  return (
                    <TableHead
                      key={colKey}
                      className={cn(
                        col.sortable && "cursor-pointer select-none hover:text-slate-200 transition-colors",
                        col.className
                      )}
                      onClick={() => col.sortable && handleSort(colKey)}
                    >
                      <div className="flex items-center gap-1.5">
                        <span>{col.header}</span>
                        {col.sortable && (
                          <span className="text-slate-500">
                            {sortKey === colKey ? (
                              sortDirection === "asc" ? (
                                <ArrowUp className="w-3.5 h-3.5 text-brand-400" />
                              ) : (
                                <ArrowDown className="w-3.5 h-3.5 text-brand-400" />
                              )
                            ) : (
                              <ArrowUpDown className="w-3.5 h-3.5 opacity-50" />
                            )}
                          </span>
                        )}
                      </div>
                    </TableHead>
                  );
                })}
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedData.map((item, idx) => (
                <TableRow
                  key={rowKey(item, idx)}
                  onClick={() => onRowClick && onRowClick(item)}
                  className={cn(onRowClick && "cursor-pointer hover:bg-slate-800/60")}
                >
                  {columns.map((col) => {
                    const colKey = col.key || col.accessorKey || col.header;
                    return (
                      <TableCell key={colKey} className={col.className}>
                        {col.render
                          ? col.render(item)
                          : col.cell
                          ? col.cell(item)
                          : col.accessor
                          ? col.accessor(item)
                          : item[colKey] !== undefined && item[colKey] !== null
                          ? String(item[colKey])
                          : "-"}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {/* Pagination Bar */}
        {!isLoading && sortedData.length > 0 && (
          <div className="px-4 py-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <div>
              Showing{" "}
              <span className="font-semibold text-slate-200">
                {(currentPage - 1) * pageSize + 1}
              </span>{" "}
              to{" "}
              <span className="font-semibold text-slate-200">
                {Math.min(currentPage * pageSize, sortedData.length)}
              </span>{" "}
              of <span className="font-semibold text-slate-200">{sortedData.length}</span>{" "}
              results
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                disabled={currentPage === 1}
                className="h-7 px-2 text-xs"
              >
                <ChevronLeft className="w-3.5 h-3.5 mr-1" />
                Previous
              </Button>
              <span className="px-2 font-medium text-slate-300">
                {currentPage} / {totalPages}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                disabled={currentPage >= totalPages}
                className="h-7 px-2 text-xs"
              >
                Next
                <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
