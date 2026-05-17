"use client"

import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Activity, TrendingUp, Sparkles, Filter, Link2 } from "lucide-react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from "recharts"

interface Signal {
  id: number
  thematic_id: number
  type: string
  description: string
  confidence: number
  trend_data: any
  detected_at: string
}

const mockSignals: Signal[] = [
  {
    id: 1,
    thematic_id: 1,
    type: "trend",
    description: "Augmentation soudaine des mentions de 'RAG' (Retrieval-Augmented Generation) dans les publications technologiques.",
    confidence: 0.92,
    detected_at: new Date(Date.now() - 3600000 * 24 * 2).toISOString(),
    trend_data: { 
      keywords: ["RAG", "LLM", "Vector DB", "Embeddings"],
      series: [
        { date: "Lun", count: 12 }, { date: "Mar", count: 18 },
        { date: "Mer", count: 15 }, { date: "Jeu", count: 35 },
        { date: "Ven", count: 52 }, { date: "Sam", count: 48 }, { date: "Dim", count: 65 }
      ]
    }
  },
  {
    id: 2,
    thematic_id: 2,
    type: "novelty",
    description: "Nouveau cluster de documents détecté autour de 'Green IT' et 'Taxonomie Européenne'. Sémantique inhabituelle.",
    confidence: 0.78,
    detected_at: new Date(Date.now() - 3600000 * 5).toISOString(),
    trend_data: { 
      keywords: ["Green IT", "CSRD", "Directive Européenne"],
      series: []
    }
  },
  {
    id: 3,
    thematic_id: 1,
    type: "trend",
    description: "Émergence du terme 'Agentic AI' en remplacement de 'Autonomous Agents'.",
    confidence: 0.85,
    detected_at: new Date(Date.now() - 3600000 * 24 * 5).toISOString(),
    trend_data: {
      keywords: ["Agentic AI", "Agents", "LangChain", "AutoGPT"],
      series: [
        { date: "10/04", count: 5 }, { date: "11/04", count: 8 },
        { date: "12/04", count: 20 }, { date: "13/04", count: 45 },
        { date: "14/04", count: 38 }, { date: "15/04", count: 60 }
      ]
    }
  }
]

export default function SignalsPage() {
  const [signals, setSignals] = useState<Signal[]>(mockSignals)
  const [loading, setLoading] = useState(false) // Use true when integrating API

  /*
  // uncomment when backend /signals is ready
  useEffect(() => {
    const loadSignals = async () => {
      try {
        const data = await fetchApi("/signals/")
        setSignals(data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    loadSignals()
  }, [])
  */

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex items-center space-x-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">Analyse des tendances en cours...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Signaux Faibles & Tendances</h1>
          <p className="text-muted-foreground mt-2">
            Vue consolidée des anomalies et émergences détectées par nos modèles non-supervisés (Clustering et Timeseries).
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Signals List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            Signaux Récents
          </h2>
          {signals.map((signal) => (
            <Card key={signal.id} className="hover:border-purple-500/50 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="outline" className={signal.type === 'trend' ? "text-blue-500 border-blue-500/30 bg-blue-500/10" : "text-amber-500 border-amber-500/30 bg-amber-500/10"}>
                    {signal.type === 'trend' ? (
                      <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> Tendance</span>
                    ) : (
                      <span className="flex items-center gap-1"><Sparkles className="h-3 w-3" /> Nouveauté</span>
                    )}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(signal.detected_at), "d MMM à HH:mm", { locale: fr })}
                  </span>
                </div>
                <CardDescription className="text-foreground text-sm font-medium">
                  {signal.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {signal.trend_data.keywords.map((kw: string) => (
                      <Badge key={kw} variant="secondary" className="text-xs">{kw}</Badge>
                    ))}
                  </div>
                  <div className="flex items-center gap-1 text-xs font-semibold text-purple-600 bg-purple-100 dark:bg-purple-900/30 px-2 py-1 rounded-md">
                    <Activity className="h-3 w-3" />
                    Confidence: {(signal.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Panel */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Visualisation</h2>
          
          {signals.filter(s => s.type === 'trend' && s.trend_data.series.length > 0).map(signal => (
            <Card key={`chart-${signal.id}`}>
              <CardHeader>
                <CardTitle className="text-base text-muted-foreground flex justify-between">
                  <span>Évolution : {signal.trend_data.keywords[0]}</span>
                  <Activity className="h-4 w-4" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] w-full mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={signal.trend_data.series}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#88888833" />
                      <XAxis 
                        dataKey="date" 
                        stroke="#888888" 
                        fontSize={12} 
                        tickLine={false} 
                        axisLine={false} 
                      />
                      <YAxis 
                        stroke="#888888" 
                        fontSize={12} 
                        tickLine={false} 
                        axisLine={false} 
                      />
                      <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="count" 
                        stroke="#8B5CF6" 
                        strokeWidth={3}
                        dot={{ r: 4, strokeWidth: 2 }}
                        activeDot={{ r: 6, strokeWidth: 0 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
