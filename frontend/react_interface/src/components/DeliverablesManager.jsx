import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { 
  FileText, 
  BarChart3, 
  Presentation, 
  FileSpreadsheet,
  Image,
  Plus,
  Edit,
  Trash2
} from 'lucide-react'

const DeliverablesManager = ({ mission, onUpdateMission }) => {
  const [showAddDeliverable, setShowAddDeliverable] = useState(false)
  const [newDeliverable, setNewDeliverable] = useState({
    nom: '',
    type: '',
    format: '',
    taille_estimee: '',
    description: '',
    contenu: '',
    style: '',
    phase: ''
  })

  // Livrables prédéfinis selon méthodologie substans.ai
  const livrablesPredefined = {
    "diagnostic_strategique": {
      nom: "Diagnostic Stratégique",
      type: "document",
      format: "md",
      taille_estimee: "25-35 pages",
      description: "Analyse approfondie de la situation actuelle, forces/faiblesses, opportunités/menaces",
      contenu: "Executive Summary, Analyse interne, Analyse externe, Positionnement concurrentiel, Enjeux critiques",
      style: "Analytique, factuel, structuré avec graphiques et tableaux",
      phase: "Phase 1"
    },
    "vision_strategique": {
      nom: "Vision Stratégique 2030",
      type: "document",
      format: "md",
      taille_estimee: "20-30 pages",
      description: "Définition de la vision, ambitions et orientations stratégiques",
      contenu: "Vision 2030, Ambitions, Piliers stratégiques, Objectifs, Roadmap macro",
      style: "Inspirant, prospectif, orienté action avec visuels impactants",
      phase: "Phase 2"
    },
    "business_plan": {
      nom: "Business Plan Détaillé",
      type: "spreadsheet",
      format: "xlsx",
      taille_estimee: "40-50 pages + modèles Excel",
      description: "Projections financières, modèles économiques, plan de financement",
      contenu: "P&L 5 ans, Cash-flow, Bilans prévisionnels, Hypothèses, Scénarios, ROI",
      style: "Rigoureux, détaillé, avec modèles financiers dynamiques",
      phase: "Phase 3"
    },
    "plan_execution": {
      nom: "Plan d'Exécution",
      type: "document",
      format: "md",
      taille_estimee: "30-40 pages",
      description: "Roadmap d'implémentation, organisation, gouvernance",
      contenu: "Roadmap détaillée, Organisation cible, Gouvernance, Risques, Planning",
      style: "Opérationnel, actionnable, avec timelines et responsabilités",
      phase: "Phase 4"
    },
    "proposition_commerciale": {
      nom: "Proposition Commerciale",
      type: "document",
      format: "md",
      taille_estimee: "15-25 pages",
      description: "Offre commerciale structurée pour présentation client",
      contenu: "Contexte, Approche, Livrables, Planning, Équipe, Tarification",
      style: "Commercial, persuasif, professionnel avec visuels attractifs",
      phase: "Pré-mission"
    },
    "analyse_concurrentielle": {
      nom: "Analyse Concurrentielle",
      type: "document",
      format: "md",
      taille_estimee: "20-25 pages",
      description: "Étude approfondie du paysage concurrentiel et positionnement",
      contenu: "Mapping concurrentiel, Benchmarks, Forces/faiblesses, Opportunités",
      style: "Analytique, comparatif, avec matrices et graphiques",
      phase: "Phase 1"
    },
    "presentation_executive": {
      nom: "Présentation Executive",
      type: "presentation",
      format: "pptx",
      taille_estimee: "25-35 slides",
      description: "Synthèse exécutive pour comité de direction",
      contenu: "Messages clés, Recommandations, Next steps, Appendices",
      style: "Synthétique, impactant, orienté décision avec visuels forts",
      phase: "Phase 4"
    },
    "etude_marche": {
      nom: "Étude de Marché",
      type: "document",
      format: "md",
      taille_estimee: "30-40 pages",
      description: "Analyse approfondie du marché, tendances, opportunités",
      contenu: "Taille marché, Segmentation, Tendances, Drivers, Prévisions",
      style: "Analytique, prospectif, avec données quantitatives et qualitatives",
      phase: "Phase 1"
    }
  }

  const handleAddPredefinedDeliverable = (key) => {
    const deliverable = livrablesPredefined[key]
    const newDel = {
      id: Date.now(),
      ...deliverable,
      statut: "À produire",
      progression: 0,
      iterations: [],
      feedback: []
    }
    
    const updatedMission = {
      ...mission,
      livrables: [...(mission.livrables || []), newDel]
    }
    onUpdateMission(updatedMission)
  }

  const handleAddCustomDeliverable = () => {
    if (newDeliverable.nom && newDeliverable.type) {
      const customDel = {
        id: Date.now(),
        ...newDeliverable,
        statut: "À produire",
        progression: 0,
        iterations: [],
        feedback: []
      }
      
      const updatedMission = {
        ...mission,
        livrables: [...(mission.livrables || []), customDel]
      }
      onUpdateMission(updatedMission)
      setNewDeliverable({
        nom: '',
        type: '',
        format: '',
        taille_estimee: '',
        description: '',
        contenu: '',
        style: '',
        phase: ''
      })
      setShowAddDeliverable(false)
    }
  }

  const getDeliverableIcon = (type) => {
    switch(type) {
      case 'document': return <FileText className="h-4 w-4" />
      case 'spreadsheet': return <FileSpreadsheet className="h-4 w-4" />
      case 'presentation': return <Presentation className="h-4 w-4" />
      case 'chart': return <BarChart3 className="h-4 w-4" />
      case 'image': return <Image className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  const getStatusColor = (statut) => {
    switch(statut) {
      case 'À produire': return 'bg-gray-500'
      case 'En cours': return 'bg-blue-500'
      case 'En révision': return 'bg-yellow-500'
      case 'Terminé': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Livrables de la Mission</h3>
        <div className="flex gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Plus className="h-4 w-4 mr-1" />
                Livrables Prédéfinis
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Livrables Prédéfinis - Méthodologie substans.ai</DialogTitle>
                <DialogDescription>
                  Sélectionnez les livrables standards selon notre méthodologie éprouvée
                </DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(livrablesPredefined).map(([key, deliverable]) => (
                  <Card key={key} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm flex items-center gap-2">
                          {getDeliverableIcon(deliverable.type)}
                          {deliverable.nom}
                        </CardTitle>
                        <Badge variant="outline" className="text-xs">
                          {deliverable.phase}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-xs text-gray-600 mb-2">{deliverable.description}</p>
                      <div className="space-y-1 text-xs">
                        <div><strong>Taille:</strong> {deliverable.taille_estimee}</div>
                        <div><strong>Format:</strong> {deliverable.format.toUpperCase()}</div>
                        <div><strong>Style:</strong> {deliverable.style}</div>
                      </div>
                      <Button 
                        size="sm" 
                        className="w-full mt-3"
                        onClick={() => handleAddPredefinedDeliverable(key)}
                      >
                        Ajouter à la Mission
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={showAddDeliverable} onOpenChange={setShowAddDeliverable}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-1" />
                Livrable Personnalisé
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Créer un Livrable Personnalisé</DialogTitle>
                <DialogDescription>
                  Définissez un livrable spécifique pour cette mission
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="nom">Nom du livrable</Label>
                  <Input
                    id="nom"
                    value={newDeliverable.nom}
                    onChange={(e) => setNewDeliverable({...newDeliverable, nom: e.target.value})}
                    placeholder="Ex: Analyse de faisabilité technique"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="type">Type</Label>
                    <Select value={newDeliverable.type} onValueChange={(value) => setNewDeliverable({...newDeliverable, type: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Type de livrable" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="document">Document</SelectItem>
                        <SelectItem value="spreadsheet">Tableur</SelectItem>
                        <SelectItem value="presentation">Présentation</SelectItem>
                        <SelectItem value="chart">Graphique</SelectItem>
                        <SelectItem value="image">Image</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="format">Format</Label>
                    <Select value={newDeliverable.format} onValueChange={(value) => setNewDeliverable({...newDeliverable, format: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Format de fichier" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="md">Markdown</SelectItem>
                        <SelectItem value="pdf">PDF</SelectItem>
                        <SelectItem value="docx">Word</SelectItem>
                        <SelectItem value="xlsx">Excel</SelectItem>
                        <SelectItem value="pptx">PowerPoint</SelectItem>
                        <SelectItem value="jpg">Image JPG</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newDeliverable.description}
                    onChange={(e) => setNewDeliverable({...newDeliverable, description: e.target.value})}
                    placeholder="Décrivez l'objectif et le contenu du livrable..."
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="contenu">Contenu attendu</Label>
                  <Textarea
                    id="contenu"
                    value={newDeliverable.contenu}
                    onChange={(e) => setNewDeliverable({...newDeliverable, contenu: e.target.value})}
                    placeholder="Détaillez les sections et éléments à inclure..."
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="style">Style et ton</Label>
                  <Input
                    id="style"
                    value={newDeliverable.style}
                    onChange={(e) => setNewDeliverable({...newDeliverable, style: e.target.value})}
                    placeholder="Ex: Analytique, commercial, technique..."
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowAddDeliverable(false)}>
                    Annuler
                  </Button>
                  <Button onClick={handleAddCustomDeliverable}>
                    Créer le Livrable
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Liste des livrables de la mission */}
      <div className="space-y-4">
        {(mission.livrables || []).map((livrable) => (
          <Card key={livrable.id}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  {getDeliverableIcon(livrable.type)}
                  {livrable.nom}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Badge className={`${getStatusColor(livrable.statut)} text-white`}>
                    {livrable.statut}
                  </Badge>
                  <Badge variant="outline">{livrable.format?.toUpperCase()}</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-3">{livrable.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mb-3">
                <div><strong>Taille:</strong> {livrable.taille_estimee}</div>
                <div><strong>Phase:</strong> {livrable.phase}</div>
                <div><strong>Style:</strong> {livrable.style}</div>
                <div><strong>Progression:</strong> {livrable.progression || 0}%</div>
              </div>

              {livrable.contenu && (
                <div className="mb-3">
                  <strong className="text-xs">Contenu attendu:</strong>
                  <p className="text-xs text-gray-600 mt-1">{livrable.contenu}</p>
                </div>
              )}

              <div className="flex gap-2">
                <Button size="sm" variant="outline">
                  <Edit className="h-3 w-3 mr-1" />
                  Modifier
                </Button>
                <Button size="sm" variant="outline">
                  Itérer
                </Button>
                {livrable.statut === 'Terminé' && (
                  <Button size="sm">
                    Consulter
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
        
        {(!mission.livrables || mission.livrables.length === 0) && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Aucun livrable défini pour cette mission</p>
            <p className="text-sm">Ajoutez des livrables prédéfinis ou personnalisés</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DeliverablesManager

