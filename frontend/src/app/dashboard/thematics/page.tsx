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
import { Plus, Pencil, Trash2, Layers, FileText, BellRing, FolderOpen } from "lucide-react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"

interface Thematic {
  id: number
  name: string
  color: string
  description: string | null
  access_portal: string
  access_admin: string
  created_at: string
  source_count: number
  document_count: number
  alert_count: number
}

const PRESET_COLORS = [
  "#3B82F6", "#8B5CF6", "#EC4899", "#EF4444", "#F97316",
  "#EAB308", "#22C55E", "#14B8A6", "#06B6D4", "#6366F1",
  "#D946EF", "#F43F5E", "#0EA5E9", "#10B981", "#A855F7",
]

export default function ThematicsPage() {
  const [thematics, setThematics] = useState<Thematic[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingThematic, setEditingThematic] = useState<Thematic | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    color: "#3B82F6",
    description: "",
    access_portal: "public",
    access_admin: "private",
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  const loadThematics = async () => {
    try {
      const data = await fetchApi("/thematics/")
      setThematics(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadThematics()
  }, [])

  const resetForm = () => {
    setFormData({ name: "", color: "#3B82F6", description: "", access_portal: "public", access_admin: "private" })
    setEditingThematic(null)
    setError("")
  }

  const openCreate = () => {
    resetForm()
    setDialogOpen(true)
  }

  const openEdit = (t: Thematic) => {
    setEditingThematic(t)
    setFormData({
      name: t.name,
      color: t.color,
      description: t.description || "",
      access_portal: t.access_portal,
      access_admin: t.access_admin,
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    if (!formData.name.trim()) {
      setError("Le nom est requis.")
      return
    }
    setSaving(true)
    setError("")
    try {
      if (editingThematic) {
        await fetchApi(`/thematics/${editingThematic.id}`, {
          method: "PUT",
          body: JSON.stringify(formData),
        })
      } else {
        await fetchApi("/thematics/", {
          method: "POST",
          body: JSON.stringify(formData),
        })
      }
      setDialogOpen(false)
      resetForm()
      loadThematics()
    } catch (err: any) {
      setError(err.message || "Erreur lors de la sauvegarde.")
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer cette thématique ? Cette action est irréversible.")) return
    try {
      await fetchApi(`/thematics/${id}`, { method: "DELETE" })
      loadThematics()
    } catch (err: any) {
      alert(err.message || "Erreur lors de la suppression.")
    }
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex items-center space-x-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">Chargement des thématiques...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Thématiques</h1>
          <p className="text-muted-foreground mt-2">
            Organisez votre veille par domaines thématiques.
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm() }}>
          <DialogTrigger render={<Button onClick={openCreate} className="gap-2" />}>
            <Plus className="h-4 w-4" />
            Nouvelle Thématique
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>{editingThematic ? "Modifier la Thématique" : "Créer une Thématique"}</DialogTitle>
              <DialogDescription>
                {editingThematic
                  ? "Modifiez les informations de cette thématique."
                  : "Ajoutez une nouvelle thématique pour organiser votre veille."}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="thematic-name">Nom *</Label>
                <Input
                  id="thematic-name"
                  placeholder="Ex: Cybersécurité, IA Générative..."
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="thematic-description">Description</Label>
                <Input
                  id="thematic-description"
                  placeholder="Description optionnelle..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Couleur</Label>
                <div className="flex flex-wrap gap-2">
                  {PRESET_COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      className={`h-8 w-8 rounded-full border-2 transition-all hover:scale-110 ${
                        formData.color === color ? "border-foreground scale-110 ring-2 ring-foreground/20" : "border-transparent"
                      }`}
                      style={{ backgroundColor: color }}
                      onClick={() => setFormData({ ...formData, color })}
                    />
                  ))}
                  <Input
                    type="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    className="h-8 w-8 cursor-pointer rounded-full p-0 border-0"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Accès Portail</Label>
                  <Select value={formData.access_portal} onValueChange={(v) => setFormData({ ...formData, access_portal: v as string })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">Public</SelectItem>
                      <SelectItem value="restricted">Restreint</SelectItem>
                      <SelectItem value="private">Privé</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Accès Admin</Label>
                  <Select value={formData.access_admin} onValueChange={(v) => setFormData({ ...formData, access_admin: v as string })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">Public</SelectItem>
                      <SelectItem value="restricted">Restreint</SelectItem>
                      <SelectItem value="private">Privé</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              {error && <p className="text-sm text-red-500 font-medium">{error}</p>}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? "Enregistrement..." : (editingThematic ? "Mettre à jour" : "Créer")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-l-4" style={{ borderLeftColor: "#3B82F6" }}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Thématiques</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{thematics.length}</div>
          </CardContent>
        </Card>
        <Card className="border-l-4" style={{ borderLeftColor: "#22C55E" }}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Sources Totales</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{thematics.reduce((acc, t) => acc + t.source_count, 0)}</div>
          </CardContent>
        </Card>
        <Card className="border-l-4" style={{ borderLeftColor: "#EAB308" }}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Alertes Actives</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{thematics.reduce((acc, t) => acc + t.alert_count, 0)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Thematics Grid */}
      {thematics.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Layers className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-semibold mb-1">Aucune thématique</h3>
            <p className="text-muted-foreground mb-4">Créez votre première thématique pour commencer la veille.</p>
            <Button onClick={openCreate} className="gap-2">
              <Plus className="h-4 w-4" />
              Créer une Thématique
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {thematics.map((t) => (
            <Card key={t.id} className="group relative overflow-hidden hover:shadow-lg transition-all duration-300">
              {/* Color stripe */}
              <div className="absolute top-0 left-0 right-0 h-1" style={{ backgroundColor: t.color }} />
              <CardHeader className="pt-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: t.color + "20" }}>
                      <Layers className="h-5 w-5" style={{ color: t.color }} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{t.name}</CardTitle>
                      {t.description && (
                        <CardDescription className="mt-1 line-clamp-2">{t.description}</CardDescription>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center p-2 rounded-md bg-muted/50">
                    <FolderOpen className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
                    <p className="text-lg font-bold">{t.source_count}</p>
                    <p className="text-xs text-muted-foreground">Sources</p>
                  </div>
                  <div className="text-center p-2 rounded-md bg-muted/50">
                    <FileText className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
                    <p className="text-lg font-bold">{t.document_count}</p>
                    <p className="text-xs text-muted-foreground">Documents</p>
                  </div>
                  <div className="text-center p-2 rounded-md bg-muted/50">
                    <BellRing className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
                    <p className="text-lg font-bold">{t.alert_count}</p>
                    <p className="text-xs text-muted-foreground">Alertes</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="text-xs">{t.access_portal}</Badge>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(t.created_at), "d MMM yyyy", { locale: fr })}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEdit(t)}>
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive" onClick={() => handleDelete(t.id)}>
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
