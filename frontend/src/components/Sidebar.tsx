"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  UploadCloud, 
  BarChart3, 
  AlertTriangle, 
  LineChart, 
  Bot, 
  FileText, 
  Settings 
} from "lucide-react";
import { cn } from "@/lib/utils";

const routes = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard", color: "text-sky-500" },
  { label: "Upload Data", icon: UploadCloud, href: "/upload", color: "text-violet-500" },
  { label: "Analytics", icon: BarChart3, href: "/analytics", color: "text-pink-700" },
  { label: "Anomalies", icon: AlertTriangle, href: "/anomalies", color: "text-orange-700" },
  { label: "Forecast", icon: LineChart, href: "/forecast", color: "text-emerald-500" },
  { label: "AI Analyst", icon: Bot, href: "/ai-analyst", color: "text-blue-500" },
  { label: "Reports", icon: FileText, href: "/reports", color: "text-gray-500" },
  { label: "Settings", icon: Settings, href: "/settings", color: "text-gray-500" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col h-full bg-slate-900 text-white w-64 p-4">
      <div className="px-3 py-2 flex-1">
        <Link href="/" className="flex items-center pl-3 mb-14">
          <div className="relative w-8 h-8 mr-4 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">A</span>
          </div>
          <h1 className="text-2xl font-bold text-white">AquaSense</h1>
        </Link>
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-white hover:bg-white/10 rounded-lg transition",
                pathname === route.href ? "text-white bg-white/10" : "text-zinc-400"
              )}
            >
              <div className="flex items-center flex-1">
                <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                {route.label}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
