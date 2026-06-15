import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { CheckCircle, Clock, AlertCircle } from "lucide-react";

interface Phase {
  id: number;
  name: string;
  description: string;
  status: "pending" | "processing" | "completed" | "error";
  progress: number;
}

interface ProcessingPipelineProps {
  isProcessing?: boolean;
  onComplete?: () => void;
}

export default function ProcessingPipeline({ isProcessing = false, onComplete }: ProcessingPipelineProps) {
  const [phases, setPhases] = useState<Phase[]>([
    {
      id: 1,
      name: "Ingesta y Pseudonimización",
      description: "Reading DICOM metadata and destructive pseudonymization of PHI tags",
      status: "pending",
      progress: 0,
    },
    {
      id: 2,
      name: "Localización de Texto",
      description: "Detecting and segmenting sensitive text with binary mask generation",
      status: "pending",
      progress: 0,
    },
    {
      id: 3,
      name: "Inpainting Médico",
      description: "Surgical reconstruction of marked regions using CNN/GAN models",
      status: "pending",
      progress: 0,
    },
    {
      id: 4,
      name: "Validación de Inocuidad",
      description: "PSNR/SSIM certification and diagnostic safety verification",
      status: "pending",
      progress: 0,
    },
  ]);

  useEffect(() => {
    if (!isProcessing) return;

    let currentPhase = 0;
    const phaseInterval = setInterval(() => {
      if (currentPhase < phases.length) {
        setPhases((prev) => {
          const updated = [...prev];
          if (updated[currentPhase].status === "pending") {
            updated[currentPhase].status = "processing";
          } else if (updated[currentPhase].progress < 100) {
            updated[currentPhase].progress += Math.random() * 40;
            if (updated[currentPhase].progress >= 100) {
              updated[currentPhase].progress = 100;
              updated[currentPhase].status = "completed";
              currentPhase++;
            }
          }
          return updated;
        });
      } else {
        clearInterval(phaseInterval);
        onComplete?.();
      }
    }, 600);

    return () => clearInterval(phaseInterval);
  }, [isProcessing, phases.length, onComplete]);

  return (
    <Card className="p-6 bg-card">
      <h2 className="text-lg font-semibold text-foreground mb-6">Processing Pipeline</h2>

      <div className="space-y-4">
        {phases.map((phase, index) => (
          <div key={phase.id}>
            {/* Phase card */}
            <div className="flex items-start gap-4 p-4 bg-muted rounded-lg border border-border">
              {/* Status icon */}
              <div className="flex-shrink-0 mt-1">
                {phase.status === "completed" && (
                  <CheckCircle className="w-6 h-6 text-green-500" />
                )}
                {phase.status === "processing" && (
                  <div className="w-6 h-6 rounded-full border-2 border-accent border-t-transparent animate-spin" />
                )}
                {phase.status === "pending" && (
                  <Clock className="w-6 h-6 text-muted-foreground" />
                )}
                {phase.status === "error" && (
                  <AlertCircle className="w-6 h-6 text-red-500" />
                )}
              </div>

              {/* Phase info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-foreground">Phase {phase.id}: {phase.name}</h3>
                  <span className="text-xs px-2 py-1 rounded-full bg-accent/10 text-accent font-medium">
                    {phase.status === "completed" && "✓ Completed"}
                    {phase.status === "processing" && "Processing..."}
                    {phase.status === "pending" && "Pending"}
                    {phase.status === "error" && "Error"}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{phase.description}</p>

                {/* Progress bar */}
                {(phase.status === "processing" || phase.status === "completed") && (
                  <div className="w-full bg-border rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-accent h-full rounded-full transition-all duration-300"
                      style={{ width: `${phase.progress}%` }}
                    />
                  </div>
                )}
              </div>

              {/* Progress percentage */}
              {phase.status === "processing" && (
                <div className="flex-shrink-0 text-right">
                  <p className="text-sm font-semibold text-accent">{Math.round(phase.progress)}%</p>
                </div>
              )}
            </div>

            {/* Connector line */}
            {index < phases.length - 1 && (
              <div className="flex justify-center py-2">
                <div className="w-1 h-6 bg-border rounded-full" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-muted rounded-lg border border-border">
        <p className="text-sm text-foreground font-medium mb-2">Pipeline Status</p>
        <div className="grid grid-cols-4 gap-2 text-xs">
          {phases.map((phase) => (
            <div key={phase.id} className="text-center">
              <p className="text-muted-foreground">Phase {phase.id}</p>
              <p className="font-semibold text-foreground">
                {phase.status === "completed" && "✓"}
                {phase.status === "processing" && "⟳"}
                {phase.status === "pending" && "○"}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="mt-4 p-3 bg-muted rounded-lg text-xs text-muted-foreground">
        <p>• Each phase is executed sequentially for data integrity</p>
        <p>• All processing occurs locally in Edge Mode (Zero-Trust)</p>
        <p>• Estimated total time: 2-5 minutes per study</p>
      </div>
    </Card>
  );
}
