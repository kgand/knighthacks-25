/**
 * Timeline Component
 * 
 * Multi-series time chart with brush/zoom for pipeline metrics
 */

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from "recharts";
import { useDashboardStore } from "../../store/dashboardStore";
import { generateMockPipelineEvents } from "../../lib/mockData";
import { useState, useMemo } from "react";

export function Timeline() {
  const [events] = useState(() => generateMockPipelineEvents(300));
  const setTimeWindow = useDashboardStore((s) => s.setTimeWindow);

  // Transform events to chart data
  const chartData = useMemo(() => {
    return events.map((event) => {
      const totalLatency = event.stage_timings
        ? Object.values(event.stage_timings).reduce((a, b) => a + b, 0)
        : 0;

      const avgConfidence =
        event.cell_scores && event.cell_scores.length > 0
          ? event.cell_scores.reduce((sum, cell) => sum + cell.top1_confidence, 0) /
            event.cell_scores.length
          : 0;

      return {
        timestamp: event.timestamp,
        time_label: new Date(event.timestamp).toLocaleTimeString(),
        latency_ms: Math.round(totalLatency),
        num_detections: event.cell_scores?.length || 0,
        avg_confidence: Math.round(avgConfidence * 100),
        has_anomaly: event.anomalies && event.anomalies.length > 0 ? 100 : 0,
      };
    });
  }, [events]);

  const stats = useMemo(() => {
    if (chartData.length === 0) return null;
    const avgLatency =
      chartData.reduce((sum, d) => sum + d.latency_ms, 0) / chartData.length;
    const maxLatency = Math.max(...chartData.map((d) => d.latency_ms));
    const anomalyCount = chartData.filter((d) => d.has_anomaly > 0).length;
    return { avgLatency, maxLatency, anomalyCount };
  }, [chartData]);

  const handleBrushChange = (brushData: any) => {
    if (brushData && brushData.startIndex !== undefined && brushData.endIndex !== undefined) {
      const startTime = chartData[brushData.startIndex].timestamp;
      const endTime = chartData[brushData.endIndex].timestamp;
      setTimeWindow(startTime, endTime);
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold">Pipeline Metrics Timeline</h3>
          <p className="text-xs text-muted-foreground">{chartData.length} frames tracked</p>
        </div>

        {stats && (
          <div className="flex gap-3">
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Avg Latency</p>
              <p className="text-sm font-medium">{stats.avgLatency.toFixed(1)}ms</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Max Latency</p>
              <p className="text-sm font-medium">{stats.maxLatency}ms</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Anomalies</p>
              <Badge variant={stats.anomalyCount > 0 ? "destructive" : "outline"}>
                {stats.anomalyCount}
              </Badge>
            </div>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
          <XAxis
            dataKey="time_label"
            tick={{ fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--background)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />

          <Line
            type="monotone"
            dataKey="latency_ms"
            stroke="hsl(var(--chart-1))"
            strokeWidth={2}
            dot={false}
            name="Latency (ms)"
          />
          <Line
            type="monotone"
            dataKey="avg_confidence"
            stroke="hsl(var(--chart-2))"
            strokeWidth={2}
            dot={false}
            name="Avg Confidence (%)"
          />
          <Line
            type="monotone"
            dataKey="num_detections"
            stroke="hsl(var(--chart-3))"
            strokeWidth={2}
            dot={false}
            name="# Detections"
          />

          <Brush
            dataKey="time_label"
            height={30}
            stroke="hsl(var(--primary))"
            onChange={handleBrushChange}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

