"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Layers, Library, BellRing, FileText, Activity } from "lucide-react"

const navigation = [
  { name: "Tableau de Bord", href: "/dashboard", icon: LayoutDashboard },
  { name: "Thématiques", href: "/dashboard/thematics", icon: Layers },
  { name: "Sources", href: "/dashboard/sources", icon: Library },
  { name: "Alertes", href: "/dashboard/alerts", icon: BellRing },
  { name: "Articles", href: "/dashboard/articles", icon: FileText },
  { name: "Signaux Faibles", href: "/dashboard/signals", icon: Activity },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col w-64 border-r border-border bg-card h-full min-h-screen">
      <div className="p-6">
        <div className="flex items-center space-x-2">
          <Activity className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold tracking-tight">VeilleAI</span>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-4 py-4">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href)
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${
                isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <Icon className={`mr-3 h-5 w-5 flex-shrink-0 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
