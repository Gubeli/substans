import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Settings, 
  Plus, 
  Edit, 
  Save, 
  X, 
  Clock, 
  Users, 
  FileText,
  ArrowRight,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

const MethodologyManager = () => {
  const [methodology, setMethodology] = useState({
    version: "1.0",
    nom: "Méthodologie Substans.ai",
    description: "Méthodologie standard pour les études de conseil stratégique",
    phases: []
  })

  const [editingPhase, setEditingPhase] = useState(null)
  const [newPhase, setNewPhase] = useState({
    nom: '',
    duree_estimee_pct: 0,
    livrables: [],
    agents_principaux: [],
    taches: []
  })

  // Simulation du chargement de la méthodologie
  useEffect(() => {
    // Simulation d'un appel API
    const loadMethodology = async () => {
      const mockMethodology = {
        version: "1.0",
        nom: "Méthodologie Substans.ai",
        description: "Méthodologie standard pour les études de conseil stratégique",
        phases: [
          {
            id: 1,
            nom: "Sélection Stratégique et Cadrage",
            duree_estimee_pct: 10,
            livrables: ["Note de cadrage", "Proposition de mission détaillée"],
            agents_principaux: ["Senior Advisor", "AVS"],
            taches: [
              "Veille stratégique continue",
              "Application de la grille de sélection des sujets",
              "Analyse préliminaire",
              "Session de cadrage client",
              "Rédaction de la proposition de mission"
            ]
          },
          {
            id: 2,
            nom: "Collecte et Validation des Données",
            duree_estimee_pct: 25,
            livrables: ["Base de données structurée", "Rapport de validation des sources"],
            agents_principaux: ["AAD", "Experts Métiers", "Experts Domaines"],
            taches: [
              "Plan de collecte",
              "Collecte multi-sources",
              "Processus de validation rigoureux",
              "Documentation des sources",
              "Structuration de la base de données"
            ]
          },
          {
            id: 3,
            nom: "Analyse Approfondie et Synthèse",
            duree_estimee_pct: 30,
            livrables: ["Rapport d'analyse intermédiaire", "Synthèses thématiques"],
            agents_principaux: ["AAD", "ARR", "Experts Métiers", "Experts Domaines"],
            taches: [
              "Analyse quantitative et qualitative",
              "Mobilisation des experts pour interprétation",
              "Synthèse et structuration des insights",
              "Validation intermédiaire client"
            ]
          },
          {
            id: 4,
            nom: "Recommandations Stratégiques et Storytelling",
            duree_estimee_pct: 15,
            livrables: ["Plan de recommandations", "Storyboard de l'étude"],
            agents_principaux: ["Senior Advisor", "ARR"],
            taches: [
              "Développement des recommandations actionnables",
              "Analyse d'impact",
              "Construction du storytelling",
              "Validation des recommandations avec le client"
            ]
          },
          {
            id: 5,
            nom: "Production et Diffusion",
            duree_estimee_pct: 15,
            livrables: ["Étude finale (web interactif, PDF)", "Executive Summary", "Présentation"],
            agents_principaux: ["ARR", "AGC"],
            taches: [
              "Rédaction et mise en forme",
              "Production multi-format",
              "Contrôle qualité final",
              "Diffusion stratégique"
            ]
          },
          {
            id: 6,
            nom: "Suivi et Capitalisation",
            duree_estimee_pct: 5,
            livrables: ["Rapport de mission", "Mise à jour de la base de connaissances"],
            agents_principaux: ["Senior Advisor", "ASM", "AGC"],
            taches: [
              "Plan de suivi client",
              "Session de feedback client",
              "Capitalisation des connaissances",
              "Amélioration continue de la méthodologie"
            ]
          }
        ]
      }
      setMethodology(mockMethodology)
    }

    loadMethodology()
  }, [])

  const handleSavePhase = (phaseId, updatedPhase) => {
    setMethodology(prev => ({
      ...prev,
      phases: prev.phases.map(phase => 
        phase.id === phaseId ? { ...phase, ...updatedPhase } : phase
      )
    }))
    setEditingPhase(null)
    
    // Simulation de sauvegarde
    console.log(`✅ Phase ${phaseId} mise à jour:`, updatedPhase)
  }

  const handleAddPhase = () => {
    if (newPhase.nom) {
      const newId = Math.max(...methodology.phases.map(p => p.id)) + 1
      const phaseToAdd = {
        ...newPhase,
        id: newId,
        livrables: newPhase.livrables.filter(l => l.trim()),
        agents_principaux: newPhase.agents_principaux.filter(a => a.trim()),
        taches: newPhase.taches.filter(t => t.trim())
      }
      
      setMethodology(prev => ({
        ...prev,
        phases: [...prev.phases, phaseToAdd]
      }))
      
      setNewPhase({
        nom: '',
        duree_estimee_pct: 0,
        livrables: [],
        agents_principaux: [],
        taches: []
      })
      
      console.log(`✅ Nouvelle phase ajoutée:`, phaseToAdd)
    }
  }

  const handleDeletePhase = (phaseId) => {
    setMethodology(prev => ({
      ...prev,
      phases: prev.phases.filter(phase => phase.id !== phaseId)
    }))
    console.log(`🗑️ Phase ${phaseId} supprimée`)
  }

  const PhaseEditor = ({ phase, onSave, onCancel }) => {
    const [editedPhase, setEditedPhase] = useState(phase)

    return (
      <Card className="border-2 border-blue-200">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-lg">Édition - Phase {phase.id}</CardTitle>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => onSave(phase.id, editedPhase)}>
                <Save className="h-4 w-4 mr-1" />
                Sauvegarder
              </Button>
              <Button size="sm" variant="outline" onClick={onCancel}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Nom de la Phase</Label>
            <Input
              value={editedPhase.nom}
              onChange={(e) => setEditedPhase({...editedPhase, nom: e.target.value})}
            />
          </div>
          
          <div>
            <Label>Durée Estimée (%)</Label>
            <Input
              type="number"
              value={editedPhase.duree_estimee_pct}
              onChange={(e) => setEditedPhase({...editedPhase, duree_estimee_pct: parseInt(e.target.value)})}
            />
          </div>
          
          <div>
            <Label>Livrables (un par ligne)</Label>
            <Textarea
              value={editedPhase.livrables.join('\n')}
              onChange={(e) => setEditedPhase({...editedPhase, livrables: e.target.value.split('\n')})}
              rows={3}
            />
          </div>
          
          <div>
            <Label>Agents Principaux (un par ligne)</Label>
            <Textarea
              value={editedPhase.agents_principaux.join('\n')}
              onChange={(e) => setEditedPhase({...editedPhase, agents_principaux: e.target.value.split('\n')})}
              rows={2}
            />
          </div>
          
          <div>
            <Label>Tâches (une par ligne)</Label>
            <Textarea
              value={editedPhase.taches.join('\n')}
              onChange={(e) => setEditedPhase({...editedPhase, taches: e.target.value.split('\n')})}
              rows={4}
            />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Gestion de la Méthodologie</h2>
          <p className="text-gray-600">Version {methodology.version} - {methodology.nom}</p>
        </div>
        
        <Dialog>
          <DialogTrigger asChild>
            <Button className="bg-green-600 hover:bg-green-700">
              <Plus className="h-4 w-4 mr-2" />
              Ajouter une Phase
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Ajouter une Nouvelle Phase</DialogTitle>
              <DialogDescription>
                Créez une nouvelle phase dans la méthodologie substans.ai
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Nom de la Phase</Label>
                <Input
                  value={newPhase.nom}
                  onChange={(e) => setNewPhase({...newPhase, nom: e.target.value})}
                  placeholder="Ex: Validation Éthique et Conformité"
                />
              </div>
              
              <div>
                <Label>Durée Estimée (%)</Label>
                <Input
                  type="number"
                  value={newPhase.duree_estimee_pct}
                  onChange={(e) => setNewPhase({...newPhase, duree_estimee_pct: parseInt(e.target.value)})}
                  placeholder="5"
                />
              </div>
              
              <div>
                <Label>Livrables (un par ligne)</Label>
                <Textarea
                  value={newPhase.livrables.join('\n')}
                  onChange={(e) => setNewPhase({...newPhase, livrables: e.target.value.split('\n')})}
                  placeholder="Rapport de conformité&#10;Analyse des risques éthiques"
                  rows={3}
                />
              </div>
              
              <div>
                <Label>Agents Principaux (un par ligne)</Label>
                <Textarea
                  value={newPhase.agents_principaux.join('\n')}
                  onChange={(e) => setNewPhase({...newPhase, agents_principaux: e.target.value.split('\n')})}
                  placeholder="Senior Advisor&#10;Expert RSE"
                  rows={2}
                />
              </div>
              
              <div>
                <Label>Tâches (une par ligne)</Label>
                <Textarea
                  value={newPhase.taches.join('\n')}
                  onChange={(e) => setNewPhase({...newPhase, taches: e.target.value.split('\n')})}
                  placeholder="Analyse des risques éthiques&#10;Validation réglementaire&#10;Contrôle de conformité"
                  rows={4}
                />
              </div>
              
              <Button onClick={handleAddPhase} className="w-full">
                Ajouter la Phase
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Vue d'ensemble */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Vue d'Ensemble de la Méthodologie
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{methodology.phases.length}</div>
              <div className="text-sm text-gray-600">Phases</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {methodology.phases.reduce((sum, phase) => sum + phase.duree_estimee_pct, 0)}%
              </div>
              <div className="text-sm text-gray-600">Durée Totale</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {methodology.phases.reduce((sum, phase) => sum + phase.livrables.length, 0)}
              </div>
              <div className="text-sm text-gray-600">Livrables</div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {methodology.phases.map((phase, index) => (
              <div key={phase.id} className="flex items-center">
                <Badge variant="outline" className="px-3 py-1">
                  {phase.nom} ({phase.duree_estimee_pct}%)
                </Badge>
                {index < methodology.phases.length - 1 && (
                  <ArrowRight className="h-4 w-4 mx-2 text-gray-400" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Liste des phases */}
      <div className="space-y-4">
        {methodology.phases.map((phase) => (
          <div key={phase.id}>
            {editingPhase === phase.id ? (
              <PhaseEditor
                phase={phase}
                onSave={handleSavePhase}
                onCancel={() => setEditingPhase(null)}
              />
            ) : (
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-bold">
                          Phase {phase.id}
                        </span>
                        {phase.nom}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-4 mt-2">
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {phase.duree_estimee_pct}% du temps
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {phase.agents_principaux.length} agents
                        </span>
                        <span className="flex items-center gap-1">
                          <FileText className="h-4 w-4" />
                          {phase.livrables.length} livrables
                        </span>
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingPhase(phase.id)}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Modifier
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeletePhase(phase.id)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="livrables" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="livrables">Livrables</TabsTrigger>
                      <TabsTrigger value="agents">Agents</TabsTrigger>
                      <TabsTrigger value="taches">Tâches</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="livrables" className="space-y-2">
                      {phase.livrables.map((livrable, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{livrable}</span>
                        </div>
                      ))}
                    </TabsContent>
                    
                    <TabsContent value="agents" className="space-y-2">
                      <div className="flex flex-wrap gap-2">
                        {phase.agents_principaux.map((agent, idx) => (
                          <Badge key={idx} variant="secondary">
                            {agent}
                          </Badge>
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="taches" className="space-y-2">
                      {phase.taches.map((tache, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-blue-500" />
                          <span className="text-sm">{tache}</span>
                        </div>
                      ))}
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default MethodologyManager

