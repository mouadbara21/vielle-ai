"use client"

import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CheckCircle2, Clock } from "lucide-react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const loadAlerts = async () => {
    try {
      const data = await fetchApi("/alerts/")
      setAlerts(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAlerts()
  }, [])

  const markAsRead = async (id: number) => {
    try {
      await fetchApi(`/alerts/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_read: true }),
      })
      loadAlerts()
    } catch (e) {
      console.error(e)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Alertes</h1>
        <p className="text-muted-foreground mt-2">Fil d'actualité des alertes de veille détectées par l'IA.</p>
      </div>

      <div className="space-y-4">
        {loading ? (
          <div>Chargement des alertes...</div>
        ) : alerts.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              Aucune alerte pour le moment.
            </CardContent>
          </Card>
        ) : (
          alerts.map(alert => (
            <Card key={alert.id} className={alert.is_read ? "opacity-70" : "border-l-4 border-l-primary"}>
              <CardHeader className="py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className={getPriorityColor(alert.priority) + " text-white border-0"}>
                      {alert.priority}
                    </Badge>
                    <Badge variant="secondary">{alert.type}</Badge>
                    {alert.ai_score > 0.8 && (
                      <Badge className="bg-purple-600 hover:bg-purple-700">IA ({alert.ai_score.toFixed(2)})</Badge>
                    )}
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="mr-1 h-3 w-3" />
                    {format(new Date(alert.created_at), "PPP à p", { locale: fr })}
                  </div>
                </div>
                <CardTitle className="text-lg mt-2">{alert.title}</CardTitle>
                <CardDescription>{alert.description}</CardDescription>
              </CardHeader>
              <CardFooter className="py-3 flex justify-end bg-muted/50 rounded-b-lg">
                {!alert.is_read && (
                  <Button variant="outline" size="sm" onClick={() => markAsRead(alert.id)}>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Marquer comme lue
                  </Button>
                )}
              </CardFooter>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
