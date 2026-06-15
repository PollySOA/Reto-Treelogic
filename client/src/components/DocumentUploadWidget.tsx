import { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Upload, File, X, CheckCircle, AlertCircle, FileImage, Activity } from "lucide-react";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  progress: number;
  status: "uploading" | "completed" | "error";
  error?: string;
}

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

interface DocumentUploadWidgetProps {
  onProcessingComplete?: (result: AnonymizationResult) => void;
}

export default function DocumentUploadWidget({ onProcessingComplete }: DocumentUploadWidgetProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    processFiles(e.dataTransfer.files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processFiles(e.target.files);
    }
  };

  const processFiles = async (fileList: FileList) => {
    const newFiles: UploadedFile[] = [];
    
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      if (file.type === "image/png" || file.type === "application/dicom" || file.name.endsWith(".dcm") || file.name.endsWith(".png")) {
        const uploadedFile: UploadedFile = {
          id: `${Date.now()}-${i}`,
          name: file.name,
          size: file.size,
          type: file.type || "application/dicom",
          progress: 0,
          status: "uploading",
        };
        newFiles.push(uploadedFile);
        setFiles((prev) => [...prev, uploadedFile]);

        // Real upload to backend
        try {
          const formData = new FormData();
          formData.append('file', file);

          // Update progress
          setFiles((prev) =>
            prev.map((f) => (f.id === uploadedFile.id ? { ...f, progress: 50 } : f))
          );

          const response = await fetch('/api/python/api/v1/anonymize', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }

          const result: AnonymizationResult = await response.json();
          
          // Complete
          setFiles((prev) =>
            prev.map((f) => (f.id === uploadedFile.id ? { ...f, progress: 100, status: "completed" } : f))
          );

          // Notify parent component
          if (onProcessingComplete) {
            onProcessingComplete(result);
          }

        } catch (error) {
          console.error('Upload error:', error);
          setFiles((prev) =>
            prev.map((f) => 
              f.id === uploadedFile.id 
                ? { ...f, progress: 0, status: "error", error: error instanceof Error ? error.message : 'Upload failed' } 
                : f
            )
          );
        }
      }
    }
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-white to-blue-50 dark:from-slate-900 dark:to-blue-950/30 border-blue-200 dark:border-blue-800">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
          <FileImage className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100">Cargar Imágenes Médicas</h2>
          <p className="text-xs text-blue-600 dark:text-blue-400">Radiografías • PNG • DICOM</p>
        </div>
      </div>

      {/* Drag and drop area - Medical Theme */}
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          isDragging 
            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/50 scale-[1.02]" 
            : "border-blue-300 dark:border-blue-700 bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-950/20 dark:to-cyan-950/20"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="relative mb-4">
          <Upload className="w-12 h-12 mx-auto text-blue-500 dark:text-blue-400" />
          <div className="absolute -bottom-1 -right-[calc(50%-1.5rem)] w-6 h-6 bg-green-500 rounded-full border-2 border-white dark:border-slate-900 flex items-center justify-center">
            <Activity className="w-3 h-3 text-white" />
          </div>
        </div>
        <h3 className="text-base font-semibold text-blue-900 dark:text-blue-100 mb-2">
          Arrastra imágenes médicas aquí
        </h3>
        <p className="text-xs text-blue-700 dark:text-blue-300 mb-4">
          o haz clic para seleccionar archivos PNG o DICOM
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          className="border-blue-300 text-blue-700 hover:bg-blue-100 dark:border-blue-700 dark:text-blue-300 dark:hover:bg-blue-900/50"
        >
          Seleccionar Archivos
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".png,.dcm,.dicom,image/png,application/dicom"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-3">
            📋 Archivos Cargados ({files.length})
          </h3>
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.id} className="flex items-center gap-3 p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <File className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100 truncate">{file.name}</p>
                  <p className="text-xs text-blue-600 dark:text-blue-400">{formatFileSize(file.size)}</p>
                  {file.status === "uploading" && (
                    <div className="mt-2">
                      <Progress value={file.progress} className="h-1.5 bg-blue-100 dark:bg-blue-900" />
                      <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                        Procesando... {Math.round(file.progress)}%
                      </p>
                    </div>
                  )}
                  {file.error && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">❌ {file.error}</p>
                  )}
                </div>
                {file.status === "completed" && (
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                )}
                {file.status === "error" && (
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                )}
                {file.status === "uploading" && (
                  <div className="w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin flex-shrink-0" />
                )}
                <button
                  onClick={() => removeFile(file.id)}
                  className="p-1 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded transition-colors"
                >
                  <X className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info - Medical Theme */}
      <div className="mt-4 p-4 bg-gradient-to-r from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-2">
          <Activity className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-blue-800 dark:text-blue-200">
            <p className="font-semibold mb-2">🏥 Procesamiento médico seguro:</p>
            <ul className="space-y-1">
              <li>✓ Formatos soportados: PNG, DICOM (.dcm)</li>
              <li>✓ Detección multi-pass OCR con preprocesamiento avanzado</li>
              <li>✓ Metadata limpiada y seudonimizada automáticamente</li>
              <li>✓ Procesamiento en modo Edge local (Zero-Trust)</li>
              <li>✓ Imagen desidentificada descargable en pestaña Viewer</li>
            </ul>
          </div>
        </div>
      </div>
    </Card>
  );
}
