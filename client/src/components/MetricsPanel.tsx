import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, AlertCircle, ChevronDown, ChevronUp, Activity, Shield, Stethoscope, FileCheck } from "lucide-react";

interface Microservice {
  name: string;
  status: "online" | "offline" | "processing";
  description: string;
}

interface MetricsPanelProps {
  psnr?: number;
  ssim?: number;
  pseudonymizationHash?: string;
  detectedClasses?: Record<string, number>;
  microservices?: Microservice[];
}

export default function MetricsPanel({
  psnr = 42.5,
  ssim = 0.995,
  pseudonymizationHash = "7f3a8c9e2b1d5f6a",
  detectedClasses = { name: 2, id: 1, age: 1, date: 1, time: 0 },
  microservices = [
    { name: "Ingesta", status: "online", description: "DICOM Processor" },
    { name: "Inferencia", status: "online", description: "Text Locator & Inpainter" },
    { name: "Drive", status: "online", description: "Medical Drive" },
    { name: "Validador", status: "online", description: "Quality Validator" },
  ],
}: MetricsPanelProps) {
  const ssimStatus = ssim >= 0.99 ? "pass" : "warning";
  const psnrStatus = psnr >= 40 ? "pass" : "warning";

  // Estado de expansión para cada columna
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    quality: false,
    compliance: false,
    services: false,
    phi: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Quality Metrics Card - EXPANDIBLE */}
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 border-blue-200 dark:border-blue-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100">Métricas de Calidad</h2>
              <p className="text-xs text-blue-700 dark:text-blue-300">Integridad de tejido sano</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleSection("quality")}
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            {expandedSections.quality ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </Button>
        </div>

        {/* Vista compacta */}
        {!expandedSections.quality && (
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-medium text-blue-700 dark:text-blue-300">PSNR</p>
                {psnrStatus === "pass" ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                )}
              </div>
              <p className="text-xl font-bold text-blue-900 dark:text-blue-100">{psnr.toFixed(1)} dB</p>
            </div>
            <div className="p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-medium text-blue-700 dark:text-blue-300">SSIM</p>
                {ssimStatus === "pass" ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                )}
              </div>
              <p className="text-xl font-bold text-blue-900 dark:text-blue-100">{ssim.toFixed(4)}</p>
            </div>
          </div>
        )}

        {/* Vista expandida */}
        {expandedSections.quality && (
          <div className="space-y-4 animate-in fade-in duration-300">
            {/* PSNR Metric */}
            <div className="p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  PSNR (Peak Signal-to-Noise Ratio)
                </label>
                {psnrStatus === "pass" ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-yellow-500" />
                )}
              </div>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{psnr.toFixed(2)} dB</p>
              <p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
                📊 Umbral mínimo: 40 dB
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                ℹ️ Mide la relación señal/ruido. Valores altos indican preservación óptima del tejido sano.
              </p>
            </div>

            {/* SSIM Metric */}
            <div className="p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  SSIM (Structural Similarity Index)
                </label>
                {ssimStatus === "pass" ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-yellow-500" />
                )}
              </div>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{ssim.toFixed(4)}</p>
              <p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
                📊 Umbral mínimo: ≥0.99 (AI Act)
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                ℹ️ Compara estructura, luminancia y contraste. Valor próximo a 1.0 = preservación perfecta.
              </p>
            </div>

            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg text-xs text-blue-800 dark:text-blue-200">
              <strong>🔬 Interpretación clínica:</strong> Estas métricas garantizan que el tejido sano permanece sin alteraciones tras la desidentificación.
            </div>
          </div>
        )}
      </Card>

      {/* Compliance & Security Card - EXPANDIBLE */}
      <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border-green-200 dark:border-green-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <Shield className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-green-900 dark:text-green-100">Cumplimiento Normativo</h2>
              <p className="text-xs text-green-700 dark:text-green-300">RGPD & AI Act</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleSection("compliance")}
            className="text-green-600 hover:text-green-700 dark:text-green-400"
          >
            {expandedSections.compliance ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </Button>
        </div>

        {/* Vista compacta */}
        {!expandedSections.compliance && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-green-200 dark:border-green-800">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-green-900 dark:text-green-100">✅ AI Act Compliant</p>
                <p className="text-xs text-green-700 dark:text-green-300">Procesamiento local (Zero-Trust)</p>
              </div>
            </div>
            <div className="p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-xs font-medium text-green-700 dark:text-green-300 mb-1">Hash Pseudonimización</p>
              <p className="font-mono text-xs text-green-900 dark:text-green-100 break-all">{pseudonymizationHash}</p>
            </div>
          </div>
        )}

        {/* Vista expandida */}
        {expandedSections.compliance && (
          <div className="space-y-4 animate-in fade-in duration-300">
            {/* RGPD Compliance */}
            <div className="p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <label className="text-sm font-semibold text-green-900 dark:text-green-100">
                  RGPD Artículo 9 - Categorías Especiales
                </label>
              </div>
              <p className="text-xs text-green-700 dark:text-green-300 mt-2">
                ✓ Datos de salud protegidos<br />
                ✓ Seudonimización irreversible<br />
                ✓ Garantía de derecho al olvido
              </p>
            </div>

            {/* AI Act Compliance */}
            <div className="p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <label className="text-sm font-semibold text-green-900 dark:text-green-100">
                  EU AI Act - Sistema de Alto Riesgo
                </label>
              </div>
              <p className="text-xs text-green-700 dark:text-green-300 mt-2">
                ✓ Validación de calidad (SSIM ≥0.99)<br />
                ✓ Trazabilidad de decisiones algorítmicas<br />
                ✓ Transparencia en procesamiento médico
              </p>
            </div>

            {/* Security Mode */}
            <div className="p-4 bg-green-100 dark:bg-green-900/30 rounded-lg border border-green-300 dark:border-green-700">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-5 h-5 text-green-600" />
                <label className="text-sm font-semibold text-green-900 dark:text-green-100">
                  Modo Edge Seguro (Zero-Trust)
                </label>
              </div>
              <p className="text-xs text-green-700 dark:text-green-300">
                🔒 Todo el procesamiento ocurre localmente sin exportación de datos.<br />
                🛡️ No hay transferencia de PHI a servidores externos.
              </p>
            </div>

            {/* Pseudonymization Hash */}
            <div className="p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-green-200 dark:border-green-800">
              <label className="text-sm font-medium text-green-900 dark:text-green-100 block mb-2">
                Token de Pseudonimización
              </label>
              <p className="font-mono text-xs text-green-700 dark:text-green-300 break-all bg-green-50 dark:bg-green-950/50 p-2 rounded">
                {pseudonymizationHash}
              </p>
              <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                🔐 Hash SHA-256 irreversible para auditoría sin re-identificación.
              </p>
            </div>
          </div>
        )}
      </Card>

      {/* Microservices Status Card - EXPANDIBLE */}
      <Card className="p-6 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20 border-purple-200 dark:border-purple-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <Stethoscope className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-purple-900 dark:text-purple-100">Estado del Pipeline</h2>
              <p className="text-xs text-purple-700 dark:text-purple-300">Microservicios médicos</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleSection("services")}
            className="text-purple-600 hover:text-purple-700 dark:text-purple-400"
          >
            {expandedSections.services ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </Button>
        </div>

        {/* Vista compacta */}
        {!expandedSections.services && (
          <div className="grid grid-cols-2 gap-3">
            {microservices.map((service) => (
              <div key={service.name} className="flex items-center gap-2 p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-purple-200 dark:border-purple-800">
                {service.status === "online" && (
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse flex-shrink-0" />
                )}
                {service.status === "processing" && (
                  <div className="w-2 h-2 rounded-full border-2 border-purple-500 border-t-transparent animate-spin flex-shrink-0" />
                )}
                {service.status === "offline" && (
                  <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                )}
                <p className="text-xs font-medium text-purple-900 dark:text-purple-100 truncate">{service.name}</p>
              </div>
            ))}
          </div>
        )}

        {/* Vista expandida */}
        {expandedSections.services && (
          <div className="space-y-3 animate-in fade-in duration-300">
            {microservices.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-purple-200 dark:border-purple-800">
                <div className="flex-1">
                  <p className="text-sm font-medium text-purple-900 dark:text-purple-100">{service.name}</p>
                  <p className="text-xs text-purple-700 dark:text-purple-300 mt-1">{service.description}</p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  {service.status === "online" && (
                    <>
                      <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-xs font-medium text-green-600 dark:text-green-400">Online</span>
                    </>
                  )}
                  {service.status === "processing" && (
                    <>
                      <div className="w-3 h-3 rounded-full border-2 border-purple-500 border-t-transparent animate-spin" />
                      <span className="text-xs font-medium text-purple-600 dark:text-purple-400">Procesando</span>
                    </>
                  )}
                  {service.status === "offline" && (
                    <>
                      <div className="w-3 h-3 rounded-full bg-red-500" />
                      <span className="text-xs font-medium text-red-600 dark:text-red-400">Offline</span>
                    </>
                  )}
                </div>
              </div>
            ))}
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg text-xs text-purple-800 dark:text-purple-200">
              <strong>⚡ Pipeline médico:</strong> Todos los servicios operan en modo edge local sin comunicación externa.
            </div>
          </div>
        )}
      </Card>

      {/* Detected PHI Classes Card - EXPANDIBLE */}
      <Card className="p-6 bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-950/20 dark:to-rose-950/20 border-red-200 dark:border-red-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <FileCheck className="w-5 h-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-red-900 dark:text-red-100">Datos PHI Detectados</h2>
              <p className="text-xs text-red-700 dark:text-red-300">Información protegida de salud</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleSection("phi")}
            className="text-red-600 hover:text-red-700 dark:text-red-400"
          >
            {expandedSections.phi ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </Button>
        </div>

        {/* Vista compacta */}
        {!expandedSections.phi && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(detectedClasses).map(([className, count]) => (
              <div key={className} className="p-3 bg-white/60 dark:bg-black/20 rounded-lg border border-red-200 dark:border-red-800 text-center">
                <p className="text-xs font-medium text-red-700 dark:text-red-300 uppercase mb-1">{className}</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">{count}</p>
              </div>
            ))}
          </div>
        )}

        {/* Vista expandida */}
        {expandedSections.phi && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(detectedClasses).map(([className, count]) => (
                <div key={className} className="p-4 bg-white/80 dark:bg-black/30 rounded-lg border border-red-200 dark:border-red-800">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-red-900 dark:text-red-100 uppercase">{className}</p>
                    <Badge variant="destructive" className="text-xs">
                      {count}
                    </Badge>
                  </div>
                  <p className="text-xs text-red-700 dark:text-red-300">
                    {className === "name" && "📛 Nombres de pacientes"}
                    {className === "id" && "🆔 Números de identificación"}
                    {className === "age" && "🎂 Edades registradas"}
                    {className === "date" && "📅 Fechas de estudio"}
                    {className === "time" && "🕐 Horas de adquisición"}
                  </p>
                </div>
              ))}
            </div>

            <div className="p-4 bg-red-100 dark:bg-red-900/30 rounded-lg border border-red-300 dark:border-red-700">
              <p className="text-xs font-semibold text-red-900 dark:text-red-100 mb-2">
                🔍 Detección Multi-Pass OCR
              </p>
              <ul className="text-xs text-red-700 dark:text-red-300 space-y-1">
                <li>✓ Preprocesamiento CLAHE + Sharpening + Binarización</li>
                <li>✓ Múltiples configuraciones de EasyOCR por imagen</li>
                <li>✓ Detección en zonas críticas (esquinas superiores)</li>
                <li>✓ Clasificación heurística PHI vs. metadata clínica</li>
                <li>✓ Todas las instancias marcadas para inpainting adaptativo</li>
              </ul>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
