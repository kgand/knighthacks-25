/**
 * Scores Table Component
 * 
 * Per-cell classification scores with filtering and sorting
 */

import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Search, Download } from "lucide-react";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import { useMemo, useState } from "react";
import { useDashboardStore } from "../../store/dashboardStore";
import { generateMockPipelineEvents } from "../../lib/mockData";

interface CellScore {
  frame_id: string;
  cell: string;
  top1_class: string;
  top1_confidence: number;
  entropy?: number;
}

export function ScoresTable() {
  const [events] = useState(() => generateMockPipelineEvents(50));
  const [globalFilter, setGlobalFilter] = useState("");
  const setSelectedCells = useDashboardStore((s) => s.setSelectedCells);

  // Flatten cell scores from all events
  const data = useMemo(() => {
    const scores: CellScore[] = [];
    events.forEach((event) => {
      event.cell_scores?.forEach((score) => {
        scores.push({
          frame_id: event.frame_id,
          cell: score.cell,
          top1_class: score.top1_class,
          top1_confidence: score.top1_confidence,
          entropy: score.top_k
            ? -score.top_k.reduce(
                (sum, item) =>
                  sum + item.confidence * Math.log2(item.confidence + 0.0001),
                0
              )
            : undefined,
        });
      });
    });
    return scores;
  }, [events]);

  const columnHelper = createColumnHelper<CellScore>();

  const columns = useMemo(
    () => [
      columnHelper.accessor("cell", {
        header: "Cell",
        cell: (info) => (
          <span className="font-mono text-xs font-medium">{info.getValue()}</span>
        ),
      }),
      columnHelper.accessor("top1_class", {
        header: "Piece",
        cell: (info) => {
          const value = info.getValue();
          return (
            <Badge variant={value === "0" ? "outline" : "secondary"} className="text-xs">
              {value === "0" ? "empty" : value}
            </Badge>
          );
        },
      }),
      columnHelper.accessor("top1_confidence", {
        header: "Confidence",
        cell: (info) => {
          const value = info.getValue();
          return (
            <div className="flex items-center gap-2">
              <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${value * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium">{(value * 100).toFixed(1)}%</span>
            </div>
          );
        },
        sortingFn: "basic",
      }),
      columnHelper.accessor("entropy", {
        header: "Entropy",
        cell: (info) => {
          const value = info.getValue();
          return value !== undefined ? (
            <span className="text-xs text-muted-foreground">{value.toFixed(2)}</span>
          ) : (
            <span className="text-xs text-muted-foreground">—</span>
          );
        },
      }),
      columnHelper.accessor("frame_id", {
        header: "Frame",
        cell: (info) => (
          <span className="text-xs text-muted-foreground font-mono">
            {info.getValue().slice(-8)}
          </span>
        ),
      }),
    ],
    [columnHelper]
  );

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      globalFilter,
    },
    onGlobalFilterChange: setGlobalFilter,
  });

  return (
    <Card className="overflow-hidden">
      {/* Header & Search */}
      <div className="p-4 border-b flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Cell Scores</h3>
          <p className="text-xs text-muted-foreground">{data.length} predictions</p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
            <Input
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="Search..."
              className="pl-8 h-8 w-48 text-xs"
            />
          </div>
          <Button variant="outline" size="sm" className="gap-2">
            <Download className="size-3.5" />
            Export
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-auto max-h-[400px]">
        <table className="w-full text-sm">
          <thead className="bg-muted/30 sticky top-0 z-10">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="text-left px-4 py-2 text-xs font-medium text-muted-foreground cursor-pointer hover:bg-muted/50"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="border-t hover:bg-muted/20 cursor-pointer transition-colors"
                onClick={() => setSelectedCells([row.original.cell])}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

