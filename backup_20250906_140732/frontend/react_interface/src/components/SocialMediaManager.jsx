import React, { useState, useEffect } from 'react';

const SocialMediaManager = () => {
  const [activeTab, setActiveTab] = useState('generator');
  const [selectedPlatform, setSelectedPlatform] = useState('linkedin');
  const [contentType, setContentType] = useState('insight');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState([]);
  const [contentCalendar, setContentCalendar] = useState(null);
  const [selectedIntelligence, setSelectedIntelligence] = useState(null);

  // Données d'intelligence simulées
  const intelligenceData = [
    {
      id: "INTEL_001",
      title: "JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen",
      summary: "L'Europe franchit une étape historique avec JUPITER, premier supercalculateur exascale européen",
      sector: "HPC",
      confidence: 0.95,
      market_size: "€2.3B",
      growth_rate: "+180%",
      expert: "Expert Semi-conducteurs (ESS)"
    },
    {
      id: "INTEL_002", 
      title: "Nvidia annonce Blackwell B200 - 20x plus puissant que H100",
      summary: "Nouvelle génération d'accélérateurs IA révolutionnaire",
      sector: "IA",
      confidence: 0.92,
      market_size: "€45B",
      growth_rate: "+250%",
      expert: "Expert Digital Data IA (EDDI)"
    },
    {
      id: "INTEL_003",
      title: "La BCE lance l'euro numérique en phase pilote",
      summary: "Transformation du système financier européen",
      sector: "Finance",
      confidence: 0.89,
      market_size: "€1.2T",
      growth_rate: "+85%",
      expert: "Expert Banque Finance (EBF)"
    }
  ];

  // Configuration des plateformes
  const platforms = {
    linkedin: {
      name: "LinkedIn",
      icon: "💼",
      color: "blue",
      contentTypes: [
        { id: "insight", name: "Insight Professionnel" },
        { id: "market_update", name: "Mise à jour Marché" },
        { id: "tech_breakthrough", name: "Breakthrough Technologique" }
      ]
    },
    twitter: {
      name: "Twitter/X", 
      icon: "🐦",
      color: "sky",
      contentTypes: [
        { id: "thread", name: "Thread" },
        { id: "single_tweet", name: "Tweet Simple" },
        { id: "quote_tweet", name: "Quote Tweet" }
      ]
    },
    instagram: {
      name: "Instagram",
      icon: "📸", 
      color: "pink",
      contentTypes: [
        { id: "post", name: "Post Feed" },
        { id: "story", name: "Story" },
        { id: "reel", name: "Reel" }
      ]
    },
    facebook: {
      name: "Facebook",
      icon: "👥",
      color: "blue",
      contentTypes: [
        { id: "post", name: "Post" },
        { id: "story", name: "Story" },
        { id: "video", name: "Vidéo" }
      ]
    }
  };

  const generateContent = async () => {
    if (!selectedIntelligence) {
      alert("Veuillez sélectionner une source d'intelligence");
      return;
    }

    setIsGenerating(true);
    
    // Simulation de génération de contenu
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const newContent = {
      id: `${selectedPlatform.toUpperCase()}_${Date.now()}`,
      platform: selectedPlatform,
      type: contentType,
      title: `${platforms[selectedPlatform].contentTypes.find(t => t.id === contentType)?.name} - ${selectedIntelligence.title}`,
      content: generateMockContent(selectedPlatform, contentType, selectedIntelligence),
      status: "draft",
      created_at: new Date().toISOString(),
      scheduled_for: null,
      engagement_score: Math.random() * 0.3 + 0.7, // 0.7-1.0
      estimated_metrics: generateMockMetrics(selectedPlatform),
      source_intelligence: selectedIntelligence.id
    };
    
    setGeneratedContent(prev => [newContent, ...prev]);
    setIsGenerating(false);
  };

  const generateMockContent = (platform, type, intelligence) => {
    const templates = {
      linkedin: {
        insight: `🔍 Analyse exclusive : ${intelligence.title}

Nos algorithmes d'IA révèlent une opportunité stratégique majeure dans le secteur ${intelligence.sector}.

📊 Données clés :
• Croissance: ${intelligence.growth_rate}
• Taille marché: ${intelligence.market_size}
• Niveau de confiance: ${Math.round(intelligence.confidence * 100)}%

💡 Ce que cela signifie pour vous :
• Nouvelles opportunités de revenus identifiées
• Transformation des processus métier nécessaire
• Avantage concurrentiel temporaire disponible

🎯 Actions recommandées :
• Évaluer l'impact sur votre roadmap
• Identifier les partenariats stratégiques
• Planifier les investissements nécessaires

Qu'en pensez-vous ? Partagez votre expérience en commentaire 👇

#Innovation #${intelligence.sector} #DigitalTransformation #TechTrends #BusinessStrategy`,

        market_update: `📈 MISE À JOUR MARCHÉ - ${intelligence.sector}

${intelligence.summary}

🔢 Chiffres marquants :
• Croissance: ${intelligence.growth_rate}
• Marché: ${intelligence.market_size}
• Confiance: ${Math.round(intelligence.confidence * 100)}%

🎯 Impact sur votre business :
Transformation accélérée des modèles économiques et nouvelles opportunités de différenciation.

🚀 Opportunités identifiées :
• Automatisation intelligente
• Nouveaux modèles économiques
• Avantage concurrentiel durable

💬 Votre avis ? Comment votre entreprise se positionne-t-elle face à ces évolutions ?

#MarketTrends #${intelligence.sector} #BusinessStrategy #Innovation`
      },
      
      twitter: {
        thread: `🧵 THREAD - ${intelligence.title.substring(0, 50)}...

1/🚀 Alerte tendance : ${intelligence.summary}

2/📊 Les chiffres : ${intelligence.growth_rate} de croissance, marché de ${intelligence.market_size}

3/💡 L'insight clé : Cette évolution va redéfinir les règles du jeu dans les 18 prochains mois

4/🎯 Impact : Transformation des modèles économiques et nouvelles opportunités business

5/🔮 Prédiction : Adoption massive d'ici 2025, les early adopters prendront l'avantage

6/🎬 Conclusion : Le futur se dessine maintenant. Qui sera prêt ?

Vous avez aimé ce thread ?
🔄 RT pour partager
❤️ Like si utile
💬 Vos thoughts ?

#${intelligence.sector.toLowerCase()} #innovation #tech`
      },
      
      instagram: {
        post: `🚀 ${intelligence.title.substring(0, 30)}...

[Image: Infographie moderne montrant l'évolution technologique]

${intelligence.summary.substring(0, 100)}...

💡 Retenez : Cette innovation va transformer votre secteur

🔥 Suivez @substans.ai pour plus d'insights tech !

.
.
.
#innovation #technology #${intelligence.sector.toLowerCase()} #future #business #startup #entrepreneur #digitaltransformation #tech #ai #data #insights #trends`
      }
    };
    
    return templates[platform]?.[type] || `Contenu généré pour ${platform} - ${type}`;
  };

  const generateMockMetrics = (platform) => {
    const baseMetrics = {
      linkedin: {
        estimated_reach: `${Math.floor(Math.random() * 15000 + 5000):,}`,
        estimated_likes: Math.floor(Math.random() * 500 + 100),
        estimated_comments: Math.floor(Math.random() * 50 + 10),
        estimated_shares: Math.floor(Math.random() * 25 + 5),
        estimated_value: `€${Math.floor(Math.random() * 2000 + 1500):,}`
      },
      twitter: {
        estimated_reach: `${Math.floor(Math.random() * 10000 + 2000):,}`,
        estimated_likes: Math.floor(Math.random() * 300 + 50),
        estimated_retweets: Math.floor(Math.random() * 75 + 15),
        estimated_replies: Math.floor(Math.random() * 30 + 5),
        estimated_value: `€${Math.floor(Math.random() * 1500 + 800):,}`
      },
      instagram: {
        estimated_reach: `${Math.floor(Math.random() * 8000 + 1500):,}`,
        estimated_likes: Math.floor(Math.random() * 400 + 80),
        estimated_comments: Math.floor(Math.random() * 40 + 8),
        estimated_saves: Math.floor(Math.random() * 20 + 4),
        estimated_value: `€${Math.floor(Math.random() * 1800 + 1000):,}`
      }
    };
    
    return baseMetrics[platform] || baseMetrics.linkedin;
  };

  const scheduleContent = (contentId, datetime) => {
    setGeneratedContent(prev => 
      prev.map(content => 
        content.id === contentId 
          ? { ...content, scheduled_for: datetime, status: "scheduled" }
          : content
      )
    );
  };

  const publishContent = (contentId) => {
    setGeneratedContent(prev => 
      prev.map(content => 
        content.id === contentId 
          ? { ...content, status: "published", published_at: new Date().toISOString() }
          : content
      )
    );
  };

  const createContentCalendar = () => {
    // Simulation de création de calendrier éditorial
    const calendar = {};
    const today = new Date();
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];
      
      calendar[dateStr] = {
        date: dateStr,
        day_of_week: date.toLocaleDateString('fr-FR', { weekday: 'long' }),
        content_planned: Math.floor(Math.random() * 4) + 1,
        platforms: ['linkedin', 'twitter', 'instagram'].slice(0, Math.floor(Math.random() * 3) + 1)
      };
    }
    
    setContentCalendar(calendar);
  };

  useEffect(() => {
    createContentCalendar();
  }, []);

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">📱 Social Media Manager</h2>
            <p className="text-purple-100 mt-1">Génération automatisée de contenu pour tous vos réseaux sociaux</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{generatedContent.length}</div>
            <div className="text-purple-100 text-sm">Contenus générés</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'generator', label: '🤖 Générateur', icon: '🤖' },
          { id: 'calendar', label: '📅 Calendrier', icon: '📅' },
          { id: 'content', label: '📚 Bibliothèque', icon: '📚' },
          { id: 'analytics', label: '📊 Analytics', icon: '📊' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Générateur de contenu */}
      {activeTab === 'generator' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Configuration */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">⚙️ Configuration</h3>
            
            {/* Sélection de la plateforme */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Plateforme</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(platforms).map(([key, platform]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedPlatform(key)}
                      className={`p-3 rounded-lg border text-left transition-colors ${
                        selectedPlatform === key
                          ? `bg-${platform.color}-50 border-${platform.color}-300 text-${platform.color}-700`
                          : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{platform.icon}</span>
                        <span className="font-medium">{platform.name}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Type de contenu */}
              <div>
                <label className="block text-sm font-medium mb-2">Type de contenu</label>
                <select 
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2"
                >
                  {platforms[selectedPlatform]?.contentTypes.map(type => (
                    <option key={type.id} value={type.id}>{type.name}</option>
                  ))}
                </select>
              </div>

              {/* Source d'intelligence */}
              <div>
                <label className="block text-sm font-medium mb-2">Source d'intelligence</label>
                <select 
                  value={selectedIntelligence?.id || ''}
                  onChange={(e) => setSelectedIntelligence(intelligenceData.find(i => i.id === e.target.value))}
                  className="w-full border rounded-lg px-3 py-2"
                >
                  <option value="">Sélectionner une source...</option>
                  {intelligenceData.map(intel => (
                    <option key={intel.id} value={intel.id}>
                      {intel.title.substring(0, 50)}...
                    </option>
                  ))}
                </select>
              </div>

              {/* Aperçu de l'intelligence sélectionnée */}
              {selectedIntelligence && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900">{selectedIntelligence.title}</h4>
                  <p className="text-sm text-blue-700 mt-1">{selectedIntelligence.summary}</p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-blue-600">
                    <span>Secteur: {selectedIntelligence.sector}</span>
                    <span>Confiance: {Math.round(selectedIntelligence.confidence * 100)}%</span>
                    <span>Expert: {selectedIntelligence.expert}</span>
                  </div>
                </div>
              )}

              {/* Bouton de génération */}
              <button
                onClick={generateContent}
                disabled={isGenerating || !selectedIntelligence}
                className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? '🔄 Génération en cours...' : '🚀 Générer le contenu'}
              </button>
            </div>
          </div>

          {/* Aperçu du contenu généré */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">👁️ Aperçu</h3>
            
            {generatedContent.length > 0 ? (
              <div className="space-y-4">
                {generatedContent.slice(0, 1).map(content => (
                  <div key={content.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{platforms[content.platform]?.icon}</span>
                        <span className="font-medium">{platforms[content.platform]?.name}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          content.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                          content.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {content.status}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">
                        Score: {(content.engagement_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <div className="bg-gray-50 rounded p-3 mb-3">
                      <pre className="whitespace-pre-wrap text-sm font-mono">
                        {content.content.substring(0, 300)}...
                      </pre>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Portée estimée:</span>
                        <span className="font-medium ml-1">{content.estimated_metrics.estimated_reach}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Valeur estimée:</span>
                        <span className="font-medium ml-1 text-green-600">{content.estimated_metrics.estimated_value}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <div className="text-4xl mb-2">📝</div>
                <p>Aucun contenu généré pour le moment</p>
                <p className="text-sm">Configurez les paramètres et cliquez sur "Générer"</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Calendrier éditorial */}
      {activeTab === 'calendar' && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold">📅 Calendrier Éditorial</h3>
            <button 
              onClick={createContentCalendar}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              🔄 Actualiser
            </button>
          </div>
          
          {contentCalendar && (
            <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
              {Object.entries(contentCalendar).map(([date, dayData]) => (
                <div key={date} className="border rounded-lg p-4">
                  <div className="text-center mb-3">
                    <div className="font-semibold">{dayData.day_of_week}</div>
                    <div className="text-sm text-gray-600">{new Date(date).getDate()}</div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-center">
                      <span className="text-lg font-bold text-purple-600">{dayData.content_planned}</span>
                      <div className="text-xs text-gray-600">contenus</div>
                    </div>
                    
                    <div className="flex justify-center space-x-1">
                      {dayData.platforms.map(platform => (
                        <span key={platform} className="text-sm">
                          {platforms[platform]?.icon}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Bibliothèque de contenu */}
      {activeTab === 'content' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">📚 Bibliothèque de Contenu</h3>
            <div className="flex space-x-2">
              <select className="border rounded px-3 py-1 text-sm">
                <option>Toutes plateformes</option>
                <option>LinkedIn</option>
                <option>Twitter</option>
                <option>Instagram</option>
              </select>
              <select className="border rounded px-3 py-1 text-sm">
                <option>Tous statuts</option>
                <option>Brouillon</option>
                <option>Programmé</option>
                <option>Publié</option>
              </select>
            </div>
          </div>

          <div className="grid gap-4">
            {generatedContent.map(content => (
              <div key={content.id} className="bg-white border rounded-lg p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{platforms[content.platform]?.icon}</span>
                      <span className="font-medium">{platforms[content.platform]?.name}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        content.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                        content.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {content.status}
                      </span>
                      <span className="text-xs text-gray-500">
                        Score: {(content.engagement_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <h4 className="font-medium mb-2">{content.title}</h4>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {content.content.substring(0, 150)}...
                    </p>
                    
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Portée:</span>
                        <div className="font-medium">{content.estimated_metrics.estimated_reach}</div>
                      </div>
                      <div>
                        <span className="text-gray-600">Engagement:</span>
                        <div className="font-medium">{content.estimated_metrics.estimated_likes} likes</div>
                      </div>
                      <div>
                        <span className="text-gray-600">Valeur:</span>
                        <div className="font-medium text-green-600">{content.estimated_metrics.estimated_value}</div>
                      </div>
                      <div>
                        <span className="text-gray-600">Créé:</span>
                        <div className="font-medium">{new Date(content.created_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2 ml-4">
                    <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                      👁️ Voir
                    </button>
                    {content.status === 'draft' && (
                      <>
                        <button 
                          onClick={() => scheduleContent(content.id, new Date(Date.now() + 3600000).toISOString())}
                          className="px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700"
                        >
                          📅 Programmer
                        </button>
                        <button 
                          onClick={() => publishContent(content.id)}
                          className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                        >
                          🚀 Publier
                        </button>
                      </>
                    )}
                    <button className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700">
                      ✏️ Éditer
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics */}
      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg border p-6">
            <h4 className="font-medium text-gray-600 mb-2">Total Contenus</h4>
            <div className="text-3xl font-bold text-blue-600">{generatedContent.length}</div>
            <div className="text-sm text-green-600">+12% ce mois</div>
          </div>
          
          <div className="bg-white rounded-lg border p-6">
            <h4 className="font-medium text-gray-600 mb-2">Engagement Moyen</h4>
            <div className="text-3xl font-bold text-green-600">
              {generatedContent.length > 0 
                ? (generatedContent.reduce((acc, c) => acc + c.engagement_score, 0) / generatedContent.length * 100).toFixed(1)
                : 0}%
            </div>
            <div className="text-sm text-green-600">+5.2% ce mois</div>
          </div>
          
          <div className="bg-white rounded-lg border p-6">
            <h4 className="font-medium text-gray-600 mb-2">Valeur Générée</h4>
            <div className="text-3xl font-bold text-purple-600">
              €{generatedContent.length * 2000:,}
            </div>
            <div className="text-sm text-green-600">+18% ce mois</div>
          </div>
          
          <div className="bg-white rounded-lg border p-6">
            <h4 className="font-medium text-gray-600 mb-2">Plateformes Actives</h4>
            <div className="text-3xl font-bold text-orange-600">4</div>
            <div className="text-sm text-gray-600">LinkedIn, Twitter, Instagram, Facebook</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialMediaManager;

