import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import TreelogicLayout from "@/components/TreelogicLayout";
import DocumentUploadWidget from "@/components/DocumentUploadWidget";
import ProcessingPipeline from "@/components/ProcessingPipeline";
import MetricsPanel from "@/components/MetricsPanel";
import MedicalImageViewer from "@/components/MedicalImageViewer";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";

interface AnonymizationResult {
  status: string;
  metrics: {
    ssim: number;
    psnr: number;
    healthy_changed_pixels: number;
  };
  ai_act_compliant: boolean;
  clean_image_url: string;
  original_image_url: string;
  bboxes: Array<{
    box: number[];
    text: string;
    class: string;
    confidence: number;
  }>;
}

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState("upload");
  const [result, setResult] = useState<AnonymizationResult | null>(null);

  const handleProcessingComplete = (data: AnonymizationResult) => {
    setResult(data);
    setActiveTab("metrics");
  };

  // Compute detected classes from bboxes
  const detectedClasses = result
    ? result.bboxes.reduce((acc, bbox) => {
        acc[bbox.class] = (acc[bbox.class] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    : { name: 0, id: 0, age: 0, date: 0, time: 0 };

  // For medical hackathon: skip authentication, show app directly
  // Uncomment the block below to enable authentication:
  /*
  if (!isAuthenticated) {
    return (
      <TreelogicLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto text-center">
            <h1 className="text-3xl font-bold text-foreground mb-4">Bienvenido a Treelogic</h1>
            <p className="text-muted-foreground mb-8">
              Medical Image Deidentification Platform with Secure Edge Mode (Zero-Trust)
            </p>
            <Button asChild size="lg" className="w-full">
              <a href={getLoginUrl()}>Sign In to Continue</a>
            </Button>
          </div>
        </div>
      </TreelogicLayout>
    );
  }
  */

  return (
    <TreelogicLayout>
      <div className="container mx-auto px-4 py-8">
        {/* Main tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="upload">Upload</TabsTrigger>
            <TabsTrigger value="processing">Processing</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="viewer">Viewer</TabsTrigger>
          </TabsList>

          {/* Upload Tab */}
          <TabsContent value="upload" className="space-y-6">
            <DocumentUploadWidget onProcessingComplete={handleProcessingComplete} />
            <Card className="p-6 bg-card">
              <h3 className="text-lg font-semibold text-foreground mb-4">Processing Instructions</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>1. Upload a PNG radiograph or DICOM file</li>
                <li>2. The system will automatically process through all 4 phases</li>
                <li>3. Monitor progress in the Processing tab</li>
                <li>4. Review metrics and quality indicators</li>
                <li>5. Compare original and deidentified images in the Viewer</li>
              </ul>
            </Card>
          </TabsContent>

          {/* Processing Tab */}
          <TabsContent value="processing" className="space-y-6">
            <div className="flex gap-4 mb-6">
              <Button
                onClick={() => setIsProcessing(true)}
                disabled={isProcessing}
                size="lg"
              >
                {isProcessing ? "Processing..." : "Start Processing"}
              </Button>
              <Button
                variant="outline"
                onClick={() => setIsProcessing(false)}
                disabled={!isProcessing}
                size="lg"
              >
                Cancel
              </Button>
            </div>
            <ProcessingPipeline
              isProcessing={isProcessing}
              onComplete={() => {
                setIsProcessing(false);
                setActiveTab("metrics");
              }}
            />
          </TabsContent>

          {/* Metrics Tab */}
          <TabsContent value="metrics" className="space-y-6">
            {result ? (
              <>
                <MetricsPanel
                  psnr={result.metrics.psnr}
                  ssim={result.metrics.ssim}
                  pseudonymizationHash={`AI Act: ${result.ai_act_compliant ? '✅ Compliant' : '❌ Non-compliant'}`}
                  detectedClasses={detectedClasses}
                  microservices={[
                    { name: "OCR Detector", status: "online", description: "EasyOCR + Heuristic Classifier" },
                    { name: "Inpainter", status: "online", description: "Navier-Stokes Anonymizer" },
                    { name: "Validator", status: "online", description: `SSIM: ${result.metrics.ssim.toFixed(4)}, HP: ${result.metrics.healthy_changed_pixels}` },
                    { name: "Storage", status: "online", description: "Local Edge Processing" },
                  ]}
                />
                <Card className="p-6 bg-card">
                  <h3 className="text-lg font-semibold mb-4">PHI Detections ({result.bboxes.length})</h3>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {result.bboxes.map((bbox, idx) => (
                      <div key={idx} className="p-3 bg-muted rounded-lg text-sm">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="font-semibold text-red-600">{bbox.class.toUpperCase()}</span>
                            <span className="text-muted-foreground ml-2">→ "{bbox.text}"</span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {(bbox.confidence * 100).toFixed(1)}% conf
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Box: [{bbox.box.join(', ')}]
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </>
            ) : (
              <Card className="p-12 text-center bg-card">
                <p className="text-muted-foreground">No processing results yet. Upload an image to start.</p>
              </Card>
            )}
          </TabsContent>

          {/* Viewer Tab */}
          <TabsContent value="viewer" className="space-y-6">
            {result ? (
              <MedicalImageViewer
                title="Medical Image Comparison - PHI Removed vs Original"
                originalImage={result.original_image_url}
                processedImage={result.clean_image_url}
              />
            ) : (
              <Card className="p-12 text-center bg-card">
                <p className="text-muted-foreground">No images to display. Upload and process an image first.</p>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </TreelogicLayout>
  );
}
