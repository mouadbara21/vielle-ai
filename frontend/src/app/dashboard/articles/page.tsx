"use client"

import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/api"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Plus, Pencil, Trash2, Send, Eye, FileText, Clock, CheckCircle2,
  Archive, Globe, Lock, Tag, X
} from "lucide-react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"

interface Article {
  id: number
  thematic_id: number
  alert_id: number | null
  title: string
  content: string | null
  summary: string | null
  status: string
  language: string
  author_id: number | null
  tags: string[]
  visibility: string
  created_at: string
  published_at: string | null
}

interface Thematic {
  id: number
  name: string
  color: string
}

const getStatusConfig = (status: string) => {
  switch (status) {
    case "published": return { label: "Publié", icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10", badgeVariant: "default" as const }
    case "draft": return { label: "Brouillon", icon: Clock, color: "text-yellow-500", bg: "bg-yellow-500/10", badgeVariant: "secondary" as const }
    case "archived": return { label: "Archivé", icon: Archive, color: "text-gray-500", bg: "bg-gray-500/10", badgeVariant: "outline" as const }
    default: return { label: status, icon: FileText, color: "text-gray-500", bg: "bg-gray-500/10", badgeVariant: "outline" as const }
  }
}

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [thematics, setThematics] = useState<Thematic[]>([])
  const [loading, setLoading] = useState(true)
  const [currentTab, setCurrentTab] = useState("all")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingArticle, setEditingArticle] = useState<Article | null>(null)
  const [viewingArticle, setViewingArticle] = useState<Article | null>(null)
  const [tagInput, setTagInput] = useState("")
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    summary: "",
    thematic_id: 0,
    language: "fr",
    tags: [] as string[],
    visibility: "public",
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  const loadArticles = async () => {
    try {
      const statusParam = currentTab !== "all" ? `?status_filter=${currentTab}` : ""
      const data = await fetchApi(`/articles/${statusParam}`)
      setArticles(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadThematics = async () => {
    try {
      const data = await fetchApi("/thematics/")
      setThematics(data)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    loadThematics()
  }, [])

  useEffect(() => {
    setLoading(true)
    loadArticles()
  }, [currentTab])

  const resetForm = () => {
    setFormData({ title: "", content: "", summary: "", thematic_id: 0, language: "fr", tags: [], visibility: "public" })
    setEditingArticle(null)
    setTagInput("")
    setError("")
  }

  const openCreate = () => {
    resetForm()
    if (thematics.length > 0) {
      setFormData(f => ({ ...f, thematic_id: thematics[0].id }))
    }
    setDialogOpen(true)
  }

  const openEdit = (a: Article) => {
    setEditingArticle(a)
    setFormData({
      title: a.title,
      content: a.content || "",
      summary: a.summary || "",
      thematic_id: a.thematic_id,
      language: a.language,
      tags: a.tags || [],
      visibility: a.visibility,
    })
    setDialogOpen(true)
  }

  const addTag = () => {
    const tag = tagInput.trim()
    if (tag && !formData.tags.includes(tag)) {
      setFormData({ ...formData, tags: [...formData.tags, tag] })
    }
    setTagInput("")
  }

  const removeTag = (tag: string) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) })
  }

  const handleSave = async () => {
    if (!formData.title.trim()) {
      setError("Le titre est requis.")
      return
    }
    if (!formData.thematic_id) {
      setError("La thématique est requise.")
      return
    }
    setSaving(true)
    setError("")
    try {
      if (editingArticle) {
        await fetchApi(`/articles/${editingArticle.id}`, {
          method: "PUT",
          body: JSON.stringify({
            title: formData.title,
            content: formData.content,
            summary: formData.summary,
            tags: formData.tags,
            visibility: formData.visibility,
          }),
        })
      } else {
        await fetchApi("/articles/", {
          method: "POST",
          body: JSON.stringify(formData),
        })
      }
      setDialogOpen(false)
      resetForm()
      loadArticles()
    } catch (err: any) {
      setError(err.message || "Erreur lors de la sauvegarde.")
    } finally {
      setSaving(false)
    }
  }

  const handlePublish = async (id: number) => {
    try {
      await fetchApi(`/articles/${id}`, {
        method: "PUT",
        body: JSON.stringify({ status: "published" }),
      })
      loadArticles()
    } catch (err: any) {
      alert(err.message || "Erreur lors de la publication.")
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Supprimer cet article ? Cette action est irréversible.")) return
    try {
      await fetchApi(`/articles/${id}`, { method: "DELETE" })
      loadArticles()
    } catch (err: any) {
      alert(err.message || "Erreur lors de la suppression.")
    }
  }

  const getThematicName = (id: number) => thematics.find(t => t.id === id)?.name || "—"
  const getThematicColor = (id: number) => thematics.find(t => t.id === id)?.color || "#888"

  const statusCounts = {
    all: articles.length,
    draft: articles.filter(a => a.status === "draft").length,
    published: articles.filter(a => a.status === "published").length,
    archived: articles.filter(a => a.status === "archived").length,
  }

  if (loading && articles.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex items-center space-x-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">Chargement des articles...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Articles</h1>
          <p className="text-muted-foreground mt-2">
            Rédigez, publiez et diffusez vos articles de veille.
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm() }}>
          <DialogTrigger render={<Button onClick={openCreate} className="gap-2" />}>
            <Plus className="h-4 w-4" />
            Nouvel Article
          </DialogTrigger>
          <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingArticle ? "Modifier l'Article" : "Créer un Article"}</DialogTitle>
              <DialogDescription>
                {editingArticle ? "Modifiez le contenu de cet article." : "Rédigez un nouvel article de veille."}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="article-title">Titre *</Label>
                <Input
                  id="article-title"
                  placeholder="Titre de l'article..."
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Thématique *</Label>
                  <Select
                    value={formData.thematic_id?.toString()}
                    onValueChange={(v) => setFormData({ ...formData, thematic_id: parseInt(v as string) })}
                  >
                    <SelectTrigger><SelectValue placeholder="Choisir..." /></SelectTrigger>
                    <SelectContent>
                      {thematics.map(t => (
                        <SelectItem key={t.id} value={t.id.toString()}>
                          <span className="flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: t.color }} />
                            {t.name}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Visibilité</Label>
                  <Select value={formData.visibility} onValueChange={(v) => setFormData({ ...formData, visibility: v as string })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public"><span className="flex items-center gap-2"><Globe className="h-3 w-3" />Public</span></SelectItem>
                      <SelectItem value="private"><span className="flex items-center gap-2"><Lock className="h-3 w-3" />Privé</span></SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="article-summary">Résumé</Label>
                <Input
                  id="article-summary"
                  placeholder="Résumé court de l'article..."
                  value={formData.summary}
                  onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="article-content">Contenu</Label>
                <textarea
                  id="article-content"
                  placeholder="Rédigez le contenu de l'article ici..."
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows={10}
                  className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y"
                />
              </div>
              <div className="space-y-2">
                <Label>Tags</Label>
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Ajouter un tag..."
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag() } }}
                    className="flex-1"
                  />
                  <Button type="button" variant="outline" size="sm" onClick={addTag}>
                    <Tag className="h-3 w-3 mr-1" />
                    Ajouter
                  </Button>
                </div>
                {formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {formData.tags.map(tag => (
                      <Badge key={tag} variant="secondary" className="gap-1 pr-1">
                        {tag}
                        <button onClick={() => removeTag(tag)} className="ml-1 rounded-full hover:bg-muted-foreground/20 p-0.5">
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
              {error && <p className="text-sm text-red-500 font-medium">{error}</p>}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? "Enregistrement..." : (editingArticle ? "Mettre à jour" : "Créer le brouillon")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Tabs */}
      <Tabs value={currentTab} onValueChange={setCurrentTab}>
        <TabsList>
          <TabsTrigger value="all" className="gap-2">
            Tous <Badge variant="secondary" className="ml-1 text-xs">{statusCounts.all}</Badge>
          </TabsTrigger>
          <TabsTrigger value="draft" className="gap-2">
            Brouillons <Badge variant="secondary" className="ml-1 text-xs">{statusCounts.draft}</Badge>
          </TabsTrigger>
          <TabsTrigger value="published" className="gap-2">
            Publiés <Badge variant="secondary" className="ml-1 text-xs">{statusCounts.published}</Badge>
          </TabsTrigger>
          <TabsTrigger value="archived" className="gap-2">
            Archivés <Badge variant="secondary" className="ml-1 text-xs">{statusCounts.archived}</Badge>
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Article Detail View Dialog */}
      <Dialog open={!!viewingArticle} onOpenChange={(open) => { if (!open) setViewingArticle(null) }}>
        <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
          {viewingArticle && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-2 mb-2">
                  <Badge style={{ backgroundColor: getThematicColor(viewingArticle.thematic_id) + "20", color: getThematicColor(viewingArticle.thematic_id) }}>
                    {getThematicName(viewingArticle.thematic_id)}
                  </Badge>
                  <Badge variant={getStatusConfig(viewingArticle.status).badgeVariant}>
                    {getStatusConfig(viewingArticle.status).label}
                  </Badge>
                </div>
                <DialogTitle className="text-xl">{viewingArticle.title}</DialogTitle>
                <DialogDescription>
                  Créé le {format(new Date(viewingArticle.created_at), "PPP à p", { locale: fr })}
                  {viewingArticle.published_at && (
                    <> · Publié le {format(new Date(viewingArticle.published_at), "PPP à p", { locale: fr })}</>
                  )}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                {viewingArticle.summary && (
                  <div className="p-3 rounded-md bg-muted/50 italic text-sm">
                    {viewingArticle.summary}
                  </div>
                )}
                <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                  {viewingArticle.content || "Aucun contenu."}
                </div>
                {viewingArticle.tags?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-2 border-t">
                    {viewingArticle.tags.map(tag => (
                      <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Articles List */}
      {articles.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <FileText className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-semibold mb-1">Aucun article</h3>
            <p className="text-muted-foreground mb-4">
              {currentTab === "all"
                ? "Créez votre premier article à partir d'une alerte ou manuellement."
                : `Aucun article ${currentTab === "draft" ? "en brouillon" : currentTab === "published" ? "publié" : "archivé"}.`
              }
            </p>
            <Button onClick={openCreate} className="gap-2">
              <Plus className="h-4 w-4" />
              Créer un Article
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => {
            const statusConf = getStatusConfig(article.status)
            const StatusIcon = statusConf.icon
            return (
              <Card key={article.id} className="group flex flex-col hover:shadow-lg transition-all duration-300">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span
                        className="h-2 w-2 rounded-full flex-shrink-0"
                        style={{ backgroundColor: getThematicColor(article.thematic_id) }}
                      />
                      <span className="text-xs text-muted-foreground">{getThematicName(article.thematic_id)}</span>
                    </div>
                    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${statusConf.bg} ${statusConf.color}`}>
                      <StatusIcon className="h-3 w-3" />
                      {statusConf.label}
                    </div>
                  </div>
                  <CardTitle className="text-base line-clamp-2 leading-snug">{article.title}</CardTitle>
                  {article.summary && (
                    <CardDescription className="line-clamp-2 mt-1.5">{article.summary}</CardDescription>
                  )}
                </CardHeader>
                <CardContent className="flex-1 pb-3">
                  {article.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {article.tags.slice(0, 4).map(tag => (
                        <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
                      ))}
                      {article.tags.length > 4 && (
                        <Badge variant="outline" className="text-xs">+{article.tags.length - 4}</Badge>
                      )}
                    </div>
                  )}
                </CardContent>
                <CardFooter className="pt-3 border-t flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(article.created_at), "d MMM yyyy", { locale: fr })}
                  </span>
                  <div className="flex items-center space-x-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" title="Voir" onClick={() => setViewingArticle(article)}>
                      <Eye className="h-3.5 w-3.5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7" title="Modifier" onClick={() => openEdit(article)}>
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    {article.status === "draft" && (
                      <Button variant="ghost" size="icon" className="h-7 w-7 text-green-500 hover:text-green-500" title="Publier" onClick={() => handlePublish(article.id)}>
                        <Send className="h-3.5 w-3.5" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" title="Supprimer" onClick={() => handleDelete(article.id)}>
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardFooter>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
