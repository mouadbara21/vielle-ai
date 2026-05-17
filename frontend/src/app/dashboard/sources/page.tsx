"use client"

import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Plus, Pencil, Trash2, Globe, Rss, Play, RefreshCw,
  CheckCircle2, XCircle, AlertTriangle, Clock, Library, ExternalLink
} from "lucide-react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"

interface Source {
  id: number
  folder_id: number
  name: string
  url: string
  type: string
  crawl_frequency: string
  status: string
  last_crawled_at: string | null
  error_count: number
  created_at: string
}

const getStatusConfig = (status: string) => {
  switch (status) {
    case "active": return { label: "Active", icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" }
    case "error": return { label: "Erreur", icon: XCircle, color: "text-red-500", bg: "bg-red-500/10" }
    case "paused": return { label: "En pause", icon: AlertTriangle, color: "text-yellow-500", bg: "bg-yellow-500/10" }
    default: return { label: "Inactive", icon: Clock, color: "text-gray-500", bg: "bg-gray-500/10" }
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case "rss": return Rss
    case "web": return Globe
    default: return Globe
  }
}

const getFrequencyLabel = (freq: string) => {
  switch (freq) {
    case "realtime": return "Temps réel"
    case "hourly": return "Horaire"
    case "daily": return "Quotidien"
    case "weekly": return "Hebdomadaire"
    default: return freq
  }
}

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingSource, setEditingSource] = useState<Source | null>(null)
  const [statusFilter, setStatusFilter] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [folders, setFolders] = useState<{ id: number; label: string }[]>([])
  const [formData, setFormData] = useState({
    name: "",
    url: "",
    type: "web",
    crawl_frequency: "daily",
    folder_id: 1,
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  const loadSources = async () => {
    try {
      const params = statusFilter !== "all" ? `?status_filter=${statusFilter}` : ""
      const data = await fetchApi(`/sources/${params}`)
      setSources(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadFolders = async () => {
    try {
      const data = await fetchApi("/thematics/all/folders")
      setFolders(data)
      if (data.length > 0 && !editingSource) {
        setFormData(prev => ({ ...prev, folder_id: data[0].id }))
      }
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    loadSources()
    loadFolders()
  }, [statusFilter])

  const filteredSources = sources.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.url.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const resetForm = () => {
    setFormData({ name: "", url: "", type: "web", crawl_frequency: "daily", folder_id: 1 })
    setEditingSource(null)
    setError("")
  }

  const openCreate = () => {
    resetForm()
    setDialogOpen(true)
  }

  const openEdit = (s: Source) => {
    setEditingSource(s)
    setFormData({
      name: s.name,
      url: s.url,
      type: s.type,
      crawl_frequency: s.crawl_frequency,
      folder_id: s.folder_id,
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    if (!formData.name.trim() || !formData.url.trim()) {
      setError("Le nom et l'URL sont requis.")
      return
    }
    setSaving(true)
    setError("")
    try {
      if (editingSource) {
        await fetchApi(`/sources/${editingSource.id}`, {
          method: "PUT",
          body: JSON.stringify(formData),
        })
      } else {
        await fetchApi("/sources/", {
          method: "POST",
          body: JSON.stringify(formData),
        })
      }
      setDialogOpen(false)
      resetForm()
      loadSources()
    } catch (err: any) {
      setError(err.message || "Erreur lors de la sauvegarde.")
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Supprimer cette source ? Les documents collectés seront conservés.")) return
    try {
      await fetchApi(`/sources/${id}`, { method: "DELETE" })
      loadSources()
    } catch (err: any) {
      alert(err.message || "Erreur lors de la suppression.")
    }
  }

  const triggerCrawl = async (id: number) => {
    try {
      await fetchApi(`/sources/${id}/crawl`, { method: "POST" })
      alert("Crawl déclenché avec succès !")
    } catch (err: any) {
      alert(err.message || "Erreur lors du déclenchement du crawl.")
    }
  }

  const statusCounts = {
    all: sources.length,
    active: sources.filter(s => s.status === "active").length,
    error: sources.filter(s => s.status === "error").length,
    paused: sources.filter(s => s.status === "paused").length,
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex items-center space-x-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">Chargement des sources...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sources</h1>
          <p className="text-muted-foreground mt-2">
            Gérez les sources web à surveiller et leurs paramètres de collecte.
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm() }}>
          <DialogTrigger render={<Button onClick={openCreate} className="gap-2" />}>
            <Plus className="h-4 w-4" />
            Ajouter une Source
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>{editingSource ? "Modifier la Source" : "Ajouter une Source"}</DialogTitle>
              <DialogDescription>
                {editingSource
                  ? "Modifiez les paramètres de cette source."
                  : "Configurez une nouvelle source à surveiller."}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="source-name">Nom *</Label>
                <Input
                  id="source-name"
                  placeholder="Ex: Le Monde - Tech, Reuters AI..."
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="source-url">URL *</Label>
                <Input
                  id="source-url"
                  type="url"
                  placeholder="https://example.com/tech"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select value={formData.type} onValueChange={(v) => setFormData({ ...formData, type: v as string })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="web">Site Web</SelectItem>
                      <SelectItem value="rss">Flux RSS</SelectItem>
                      <SelectItem value="api">API</SelectItem>
                      <SelectItem value="social">Réseaux Sociaux</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Fréquence de collecte</Label>
                  <Select value={formData.crawl_frequency} onValueChange={(v) => setFormData({ ...formData, crawl_frequency: v as string })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="realtime">Temps réel</SelectItem>
                      <SelectItem value="hourly">Horaire</SelectItem>
                      <SelectItem value="daily">Quotidien</SelectItem>
                      <SelectItem value="weekly">Hebdomadaire</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Dossier / Thématique *</Label>
                <Select
                  value={formData.folder_id.toString()}
                  onValueChange={(v) => setFormData({ ...formData, folder_id: parseInt(v || "0") })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un dossier" />
                  </SelectTrigger>
                  <SelectContent>
                    {folders.map((f) => (
                      <SelectItem key={f.id} value={f.id.toString()}>
                        {f.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {folders.length === 0 && (
                  <p className="text-xs text-yellow-500">
                    Aucun dossier trouvé. Créez d'abord une thématique et ses partitions/dossiers.
                  </p>
                )}
              </div>
              {error && <p className="text-sm text-red-500 font-medium">{error}</p>}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? "Enregistrement..." : (editingSource ? "Mettre à jour" : "Ajouter")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Row */}
      <div className="grid gap-4 md:grid-cols-4">
        {([
          { key: "all", label: "Total", icon: Library, color: "#3B82F6" },
          { key: "active", label: "Actives", icon: CheckCircle2, color: "#22C55E" },
          { key: "error", label: "En Erreur", icon: XCircle, color: "#EF4444" },
          { key: "paused", label: "En Pause", icon: AlertTriangle, color: "#EAB308" },
        ] as const).map(({ key, label, icon: Icon, color }) => (
          <Card
            key={key}
            className={`cursor-pointer transition-all hover:shadow-md ${statusFilter === key ? "ring-2 ring-primary" : ""}`}
            onClick={() => setStatusFilter(key)}
          >
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="text-2xl font-bold">{statusCounts[key]}</p>
              </div>
              <div className="h-10 w-10 rounded-full flex items-center justify-center" style={{ backgroundColor: color + "20" }}>
                <Icon className="h-5 w-5" style={{ color }} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Search */}
      <div className="flex items-center space-x-4">
        <Input
          placeholder="Rechercher une source par nom ou URL..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-md"
        />
        <Button variant="outline" size="icon" onClick={loadSources}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Sources Table */}
      {filteredSources.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Library className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-semibold mb-1">Aucune source trouvée</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery ? "Aucune source ne correspond à votre recherche." : "Ajoutez votre première source pour commencer la collecte."}
            </p>
            {!searchQuery && (
              <Button onClick={openCreate} className="gap-2">
                <Plus className="h-4 w-4" />
                Ajouter une Source
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[300px]">Source</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Fréquence</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Dernier Crawl</TableHead>
                <TableHead>Erreurs</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSources.map((source) => {
                const statusConfig = getStatusConfig(source.status)
                const StatusIcon = statusConfig.icon
                const TypeIcon = getTypeIcon(source.type)
                return (
                  <TableRow key={source.id} className="group">
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <div className="h-9 w-9 rounded-md bg-muted flex items-center justify-center flex-shrink-0">
                          <TypeIcon className="h-4 w-4 text-muted-foreground" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium truncate">{source.name}</p>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-muted-foreground hover:text-primary truncate flex items-center gap-1"
                          >
                            {source.url.replace(/https?:\/\//, "").substring(0, 40)}...
                            <ExternalLink className="h-3 w-3 flex-shrink-0" />
                          </a>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">{source.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{getFrequencyLabel(source.crawl_frequency)}</span>
                    </TableCell>
                    <TableCell>
                      <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${statusConfig.bg} ${statusConfig.color}`}>
                        <StatusIcon className="h-3 w-3" />
                        {statusConfig.label}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">
                        {source.last_crawled_at
                          ? format(new Date(source.last_crawled_at), "d MMM à HH:mm", { locale: fr })
                          : "Jamais"
                        }
                      </span>
                    </TableCell>
                    <TableCell>
                      {source.error_count > 0 ? (
                        <Badge variant="destructive" className="text-xs">{source.error_count}</Badge>
                      ) : (
                        <span className="text-xs text-muted-foreground">0</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="icon" className="h-8 w-8" title="Déclencher un crawl" onClick={() => triggerCrawl(source.id)}>
                          <Play className="h-3.5 w-3.5 text-green-500" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEdit(source)}>
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive" onClick={() => handleDelete(source.id)}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </Card>
      )}
    </div>
  )
}
