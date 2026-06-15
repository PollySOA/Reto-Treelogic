import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LogOut, Shield, Activity } from "lucide-react";
import { getLoginUrl } from "@/const";
import { ReactNode } from "react";

interface IdoniaLayoutProps {
  children: ReactNode;
  title?: string;
}

export default function IdoniaLayout({ children, title = "Medical Deidentification" }: IdoniaLayoutProps) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-blue-950">
      {/* Header with Idonia branding - Medical Theme */}
      <header className="border-b border-blue-200 dark:border-blue-800 bg-gradient-to-r from-white to-blue-50 dark:from-slate-900 dark:to-blue-950/50 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo y branding médico */}
            <div className="flex items-center gap-4">
              {/* Idonia Logo con tema médico */}
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-green-500 rounded-full border-2 border-white dark:border-slate-900 flex items-center justify-center">
                  <Shield className="w-3 h-3 text-white" />
                </div>
              </div>
              
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-700 to-cyan-700 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent">
                  Idonia Health
                </h1>
                <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                  Medical Image Deidentification Platform
                </p>
              </div>
            </div>

            {/* Compliance badges */}
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 rounded-lg border border-green-300 dark:border-green-700">
                <Shield className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="text-xs font-semibold text-green-700 dark:text-green-300">RGPD</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 rounded-lg border border-blue-300 dark:border-blue-700">
                <Shield className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-xs font-semibold text-blue-700 dark:text-blue-300">AI Act</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-100 dark:bg-purple-900/30 rounded-lg border border-purple-300 dark:border-purple-700">
                <Activity className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span className="text-xs font-semibold text-purple-700 dark:text-purple-300">Zero-Trust</span>
              </div>
            </div>

            {/* User info and logout */}
            <div className="flex items-center gap-4">
              {user ? (
                <>
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-100">{user.name || user.email}</p>
                    <p className="text-xs text-blue-600 dark:text-blue-400">{user.role}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => logout()}
                    className="text-blue-600 hover:text-blue-700 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900/50"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </>
              ) : (
                <div className="px-3 py-1.5 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-md border border-green-300 dark:border-green-700">
                  <span className="text-xs font-semibold text-green-700 dark:text-green-300 flex items-center gap-1">
                    <Shield className="w-3 h-3" />
                    Demo Mode • Edge Local
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

      {/* Footer médico */}
      <footer className="border-t border-blue-200 dark:border-blue-800 bg-white dark:bg-slate-900 py-4">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-600 dark:text-slate-400">
            <p>© 2026 Idonia Health. Cumplimiento normativo RGPD & AI Act.</p>
            <p className="flex items-center gap-1">
              <Shield className="w-3 h-3" />
              Procesamiento Edge Local • Zero-Trust Architecture
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
