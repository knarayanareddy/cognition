"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/team", label: "Team Heatmap", icon: "🗺️" },
  { href: "/scenarios", label: "Demo Scenarios", icon: "🎭" },
  { href: "/interventions", label: "Intervention Log", icon: "⚡" },
  { href: "/privacy", label: "Privacy & Data", icon: "🔒" },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold">CLB</span>
            <span className="text-xs text-gray-500">v1.0</span>
          </div>
          <div className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                  pathname === item.href
                    ? "bg-gray-800 text-white"
                    : "text-gray-400 hover:text-white hover:bg-gray-800/50"
                }`}
              >
                <span className="mr-1.5">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
