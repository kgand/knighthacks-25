/**
 * Debug Workbench Component
 * 
 * Timeline + Tabbed detail views for pipeline debugging
 */

import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Activity } from "lucide-react";
import { Timeline } from "./Timeline";
import { ScoresTable } from "./ScoresTable";
import { PipelineStepper } from "./PipelineStepper";
import { useDashboardStore } from "../../store/dashboardStore";

export function DebugWorkbench() {
  const activeTab = useDashboardStore((s) => s.activeTab);
  const setActiveTab = useDashboardStore((s) => s.setActiveTab);

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b">
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <Activity className="size-4" />
          Debugging Workbench
        </h2>
      </div>

      {/* Timeline */}
      <div className="p-4 border-b">
        <Timeline />
      </div>

      {/* Tabbed Details */}
      <div className="flex-1 overflow-hidden p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
          <TabsList className="mb-4">
            <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
            <TabsTrigger value="scores">Scores</TabsTrigger>
            <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
            <TabsTrigger value="boardstate">Boardstate</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-auto">
            <TabsContent value="pipeline" className="mt-0">
              <PipelineStepper />
            </TabsContent>

            <TabsContent value="scores" className="mt-0">
              <ScoresTable />
            </TabsContent>

            <TabsContent value="heatmap" className="mt-0">
              <Card className="p-6">
                <div className="text-center text-muted-foreground">
                  <p>Heatmap visualization coming soon</p>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="boardstate" className="mt-0">
              <Card className="p-6">
                <div className="text-center text-muted-foreground">
                  <p>Boardstate viewer coming soon</p>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="alerts" className="mt-0">
              <Card className="p-6">
                <div className="text-center text-muted-foreground">
                  <p>Alerts panel coming soon</p>
                </div>
              </Card>
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}

