/**
 * Pipeline Stepper Component
 * 
 * Visual stepper showing: Raw → Grid Fit → Crops → Classify → Boardstate
 */

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Loader2 } from "lucide-react";
import type { PipelineStage, PipelineStageInfo } from "../../types";

const stages: PipelineStageInfo[] = [
  {
    stage: "raw",
    label: "Raw Frame",
    description: "Camera capture",
  },
  {
    stage: "board_detect",
    label: "Board Detection",
    description: "Corner detection & perspective",
  },
  {
    stage: "grid_fit",
    label: "Grid Fit",
    description: "8×8 cell mapping",
  },
  {
    stage: "crop",
    label: "Piece Crops",
    description: "64 cell extractions",
  },
  {
    stage: "classify",
    label: "Classification",
    description: "Piece recognition",
  },
  {
    stage: "validate",
    label: "Validation",
    description: "FEN generation",
  },
  {
    stage: "complete",
    label: "Complete",
    description: "Board state ready",
  },
];

export function PipelineStepper() {
  // Mock current stage (in real implementation, this comes from selected frame)
  const currentStage: PipelineStage = "classify";

  const getCurrentStageIndex = () => {
    return stages.findIndex((s) => s.stage === currentStage);
  };

  const getStageStatus = (index: number) => {
    const current = getCurrentStageIndex();
    if (index < current) return "complete";
    if (index === current) return "processing";
    return "pending";
  };

  return (
    <div className="space-y-6">
      {/* Stepper */}
      <Card className="p-6">
        <h3 className="text-sm font-semibold mb-6">Pipeline Stages</h3>

        <div className="flex items-center justify-between">
          {stages.map((stage, index) => {
            const status = getStageStatus(index);
            const isLast = index === stages.length - 1;

            return (
              <div key={stage.stage} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  {/* Icon */}
                  <div
                    className={`
                    size-10 rounded-full flex items-center justify-center transition-all
                    ${
                      status === "complete"
                        ? "bg-primary text-primary-foreground"
                        : status === "processing"
                        ? "bg-primary/20 text-primary animate-pulse"
                        : "bg-muted text-muted-foreground"
                    }
                  `}
                  >
                    {status === "complete" && <Check className="size-5" />}
                    {status === "processing" && <Loader2 className="size-5 animate-spin" />}
                    {status === "pending" && <div className="size-2 rounded-full bg-current" />}
                  </div>

                  {/* Label */}
                  <div className="mt-3 text-center">
                    <p className="text-xs font-medium">{stage.label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {stage.description}
                    </p>
                    {stage.timing_ms && (
                      <Badge variant="outline" className="text-xs mt-1">
                        {stage.timing_ms.toFixed(1)}ms
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Connector */}
                {!isLast && (
                  <div className="flex-1 h-[2px] bg-border mx-4 relative">
                    {status === "complete" && (
                      <div className="absolute inset-0 bg-primary" />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Debug Artifacts Grid */}
      <Card className="p-6">
        <h3 className="text-sm font-semibold mb-4">Debug Artifacts</h3>
        <div className="grid grid-cols-3 gap-4">
          <DebugArtifactCard
            title="Raw Frame"
            description="Original camera capture"
          />
          <DebugArtifactCard
            title="Board Detection"
            description="Corner keypoints & warp"
          />
          <DebugArtifactCard
            title="Cell Crops"
            description="64 piece extractions"
          />
        </div>
      </Card>
    </div>
  );
}

function DebugArtifactCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="aspect-video bg-muted flex items-center justify-center">
        <p className="text-xs text-muted-foreground">No frame selected</p>
      </div>
      <div className="p-3 border-t">
        <p className="text-xs font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

