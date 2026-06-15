import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LogOut, Shield, Activity } from "lucide-react";
import { getLoginUrl } from "@/const";
import { ReactNode } from "react";

interface TreelogicLayoutProps {
  children: ReactNode;
  title?: string;
}

export default function TreelogicLayout({ children, title = "Medical Deidentification" }: TreelogicLayoutProps) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-slate-950">
      {/* Header with Treelogic branding - Corporate Theme */}
      <header className="border-b border-gray-200 dark:border-gray-800 bg-black dark:bg-slate-900 shadow-lg">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo Treelogic */}
            <div className="flex items-center gap-4">
              {/* Treelogic Logo corporativo */}
              <div className="flex items-center gap-3">
                <img 
                  src="/treelogic-logo.svg" 
                  alt="Treelogic Logo" 
                  className="h-10 w-auto"
                  onError={(e) => {
                    // Fallback: mostrar texto si falla la imagen
                    e.currentTarget.style.display = 'none';
                    const textFallback = document.createElement('span');
                    textFallback.className = 'text-2xl font-bold text-orange-500';
                    textFallback.textContent = 'Treelogic';
                    e.currentTarget.parentElement?.appendChild(textFallback);
                  }}
                />
              </div>
              
              <div className="border-l border-gray-700 pl-4 hidden md:block">
                <p className="text-sm text-orange-500 font-semibold">
                  Desidentificación Visual de Imágenes Médicas
                </p>
                <p className="text-xs text-gray-400">
                  Computer Vision · Hackathon 30h
                </p>
              </div>
            </div>

            {/* Compliance badges - Treelogic style */}
            <div className="hidden lg:flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-900 dark:bg-gray-800 rounded border border-gray-700">
                <Shield className="w-3.5 h-3.5 text-green-500" />
                <span className="text-xs font-medium text-green-400">RGPD</span>
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-900 dark:bg-gray-800 rounded border border-gray-700">
                <Shield className="w-3.5 h-3.5 text-orange-500" />
                <span className="text-xs font-medium text-orange-400">AI Act</span>
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-900 dark:bg-gray-800 rounded border border-gray-700">
                <Activity className="w-3.5 h-3.5 text-orange-500" />
                <span className="text-xs font-medium text-orange-400">Zero-Trust</span>
              </div>
            </div>

            {/* User info and logout */}
            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium text-white">{user.name || user.email}</p>
                    <p className="text-xs text-gray-400">{user.role}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => logout()}
                    className="text-orange-500 hover:text-orange-400 hover:bg-gray-900"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </>
              ) : (
                <div className="px-2.5 py-1 bg-gray-900 rounded border border-gray-700">
                  <span className="text-xs font-medium text-green-400 flex items-center gap-1.5">
                    <Shield className="w-3 h-3" />
                    Demo • Local
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer corporativo Treelogic */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-slate-900 py-4">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-gray-600 dark:text-gray-400">
            <p>© 2026 <span className="text-orange-600 dark:text-orange-500 font-semibold">Treelogic</span>. Cumplimiento normativo RGPD & AI Act.</p>
            <p className="flex items-center gap-1">
              <Shield className="w-3 h-3 text-green-600" />
              Procesamiento Edge Local • Zero-Trust Architecture
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
