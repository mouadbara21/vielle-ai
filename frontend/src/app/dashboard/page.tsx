"use client"

import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, BellRing, FileText, Layers, Library, Users } from "lucide-react"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await fetchApi("/dashboard/stats")
        setStats(data)
      } catch (err: any) {
        setError("Impossible de charger les statistiques du tableau de bord.")
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  if (loading) return <div className="flex h-full items-center justify-center">Chargement...</div>
  if (error) return <div className="text-red-500">{error}</div>
  if (!stats) return null

  const chartData = [
    { name: "Nouveaux Docs", total: stats.alerts.by_type?.new_document || 0 },
    { name: "Mots-Clés", total: stats.alerts.by_type?.keyword_match || 0 },
    { name: "Signaux", total: stats.alerts.by_type?.weak_signal || 0 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Tableau de Bord</h1>
        <p className="text-muted-foreground mt-2">Bienvenue sur votre espace de veille intelligente.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sources Actives</CardTitle>
            <Library className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.sources?.active || 0}</div>
            <p className="text-xs text-muted-foreground">
              Sur un total de {stats.sources?.total || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents Collectés</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.documents || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertes Non Lues</CardTitle>
            <BellRing className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.alerts?.unread || 0}</div>
            <p className="text-xs text-muted-foreground">
              Total historique : {stats.alerts?.total || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Signaux Faibles</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.signals || 0}</div>
            <p className="text-xs text-muted-foreground">Tendances détectées par l'IA</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Répartition des Alertes Récentes</CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                <Tooltip />
                <Bar dataKey="total" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Sources en Erreur</CardTitle>
            <CardDescription>
              {stats.sources?.error || 0} sources nécessitent votre attention.
            </CardDescription>
          </CardHeader>
          <CardContent>
             {/* Simple message for MVP. Should list the errors. */}
             {stats.sources?.error > 0 ? (
               <div className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md">
                 Certaines sources rencontrent des erreurs (CAPTCHA, 403, 404). Vérifiez la configuration.
               </div>
             ) : (
               <div className="p-4 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-md">
                 Toutes les sources actives fonctionnent correctement.
               </div>
             )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
