import { useRef, useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { ZoomIn, ZoomOut, RotateCw, Download } from "lucide-react";

interface MedicalImageViewerProps {
  originalImage?: string;
  processedImage?: string;
  title?: string;
}

export default function MedicalImageViewer({
  originalImage,
  processedImage,
  title = "Medical Image Viewer",
}: MedicalImageViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [splitPosition, setSplitPosition] = useState(50);
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [originalImg, setOriginalImg] = useState<HTMLImageElement | null>(null);
  const [processedImg, setProcessedImg] = useState<HTMLImageElement | null>(null);

  // Función para descargar la imagen desidentificada
  const handleDownloadProcessedImage = async () => {
    if (!processedImage) {
      alert("No hay imagen desidentificada para descargar");
      return;
    }

    try {
      // Si la imagen es una data URL (base64), descargar directamente
      if (processedImage.startsWith('data:')) {
        const link = document.createElement('a');
        link.href = processedImage;
        link.download = `treelogic_phi_removed_${new Date().toISOString().slice(0, 10)}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Si es una URL, fetch y descargar
        const response = await fetch(processedImage);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `treelogic_phi_removed_${new Date().toISOString().slice(0, 10)}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Error al descargar imagen:", error);
      alert("Error al descargar la imagen. Por favor, intente de nuevo.");
    }
  };

  // Load images
  useEffect(() => {
    if (originalImage) {
      const img = new Image();
      img.onload = () => setOriginalImg(img);
      img.src = originalImage;
    }
    if (processedImage) {
      const img = new Image();
      img.onload = () => setProcessedImg(img);
      img.src = processedImage;
    }
  }, [originalImage, processedImage]);

  // Draw canvas with split-screen
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Clear canvas
    ctx.fillStyle = "#f5f5f5";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Calculate image dimensions with zoom and rotation
    const maxWidth = canvas.width / 2;
    const maxHeight = canvas.height;

    if (originalImg) {
      const scale = Math.min(maxWidth / originalImg.width, maxHeight / originalImg.height) * zoom;
      const x = (maxWidth - originalImg.width * scale) / 2;
      const y = (canvas.height - originalImg.height * scale) / 2;

      ctx.save();
      ctx.translate(x + (originalImg.width * scale) / 2, y + (originalImg.height * scale) / 2);
      ctx.rotate((rotation * Math.PI) / 180);
      ctx.drawImage(originalImg, -originalImg.width * scale / 2, -originalImg.height * scale / 2, originalImg.width * scale, originalImg.height * scale);
      ctx.restore();
    }

    // Draw split line
    const splitX = (canvas.width * splitPosition) / 100;
    ctx.strokeStyle = "#0ea5e9";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(splitX, 0);
    ctx.lineTo(splitX, canvas.height);
    ctx.stroke();

    // Draw processed image on right side
    if (processedImg) {
      ctx.save();
      ctx.beginPath();
      ctx.rect(splitX, 0, canvas.width - splitX, canvas.height);
      ctx.clip();

      const scale = Math.min(maxWidth / processedImg.width, maxHeight / processedImg.height) * zoom;
      const x = splitX + (maxWidth - processedImg.width * scale) / 2;
      const y = (canvas.height - processedImg.height * scale) / 2;

      ctx.translate(x + (processedImg.width * scale) / 2, y + (processedImg.height * scale) / 2);
      ctx.rotate((rotation * Math.PI) / 180);
      ctx.drawImage(processedImg, -processedImg.width * scale / 2, -processedImg.height * scale / 2, processedImg.width * scale, processedImg.height * scale);
      ctx.restore();
    }

    // Draw labels
    ctx.fillStyle = "#0ea5e9";
    ctx.font = "12px sans-serif";
    ctx.fillText("Original", 10, 25);
    ctx.fillText("Deidentified", splitX + 10, 25);
  }, [originalImg, processedImg, splitPosition, zoom, rotation]);

  return (
    <Card className="p-6 bg-card">
      <h2 className="text-lg font-semibold text-foreground mb-4">{title}</h2>

      {/* Canvas viewer */}
      <div className="bg-muted rounded-lg overflow-hidden mb-4 border border-border">
        <canvas
          ref={canvasRef}
          className="w-full h-96 cursor-move"
          onMouseMove={(e) => {
            if (e.buttons === 1) {
              const rect = canvasRef.current?.getBoundingClientRect();
              if (rect) {
                const newPos = ((e.clientX - rect.left) / rect.width) * 100;
                setSplitPosition(Math.max(0, Math.min(100, newPos)));
              }
            }
          }}
        />
      </div>

      {/* Split position slider */}
      <div className="mb-4">
        <label className="text-sm font-medium text-foreground mb-2 block">Split Position</label>
        <Slider
          value={[splitPosition]}
          onValueChange={(val) => setSplitPosition(val[0])}
          min={0}
          max={100}
          step={1}
          className="w-full"
        />
        <p className="text-xs text-muted-foreground mt-1">{splitPosition.toFixed(0)}%</p>
      </div>

      {/* Controls */}
      <div className="flex gap-2 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setZoom(Math.min(3, zoom + 0.2))}
          className="gap-2"
        >
          <ZoomIn className="w-4 h-4" />
          Zoom In
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setZoom(Math.max(0.5, zoom - 0.2))}
          className="gap-2"
        >
          <ZoomOut className="w-4 h-4" />
          Zoom Out
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setRotation((rotation + 90) % 360)}
          className="gap-2"
        >
          <RotateCw className="w-4 h-4" />
          Rotate
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setZoom(1);
            setRotation(0);
            setSplitPosition(50);
          }}
          className="gap-2"
        >
          Reset
        </Button>
        <div className="ml-auto" />
        <Button
          size="sm"
          onClick={handleDownloadProcessedImage}
          disabled={!processedImage}
          className="gap-2 bg-green-600 hover:bg-green-700 text-white"
        >
          <Download className="w-4 h-4" />
          Descargar PHI Removed
        </Button>
      </div>

      {/* Info - Medical Theme */}
      <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-lg border border-green-200 dark:border-green-800">
        <div className="flex items-start gap-2">
          <Download className="w-4 h-4 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-green-800 dark:text-green-200">
            <p className="font-semibold mb-1">📥 Descarga segura de imagen desidentificada</p>
            <p>• Arrastra la línea divisoria para comparar Original vs. PHI Removed</p>
            <p>• Usa zoom y rotación para inspección detallada</p>
            <p>• El botón "Descargar PHI Removed" exporta solo la imagen anónima en formato PNG</p>
            <p>• La imagen descargada cumple con RGPD Artículo 9 y AI Act</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
