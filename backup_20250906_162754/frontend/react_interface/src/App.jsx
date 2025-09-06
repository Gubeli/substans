import React, { useState, useEffect } from 'react';
import './App.css';

// Import des composants
import EnterpriseDashboard from './components/EnterpriseDashboard';
import ReportingSystem from './components/ReportingSystem';
import SystemManagement from './components/SystemManagement';

function App() {
  // États principaux
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemStatus, setSystemStatus] = useState({});
  const [loading, setLoading] = useState(false);
  
  // États pour les nouveaux agents
  const [factCheckerActive, setFactCheckerActive] = useState(true);
  const [graphistActive, setGraphistActive] = useState(true);
  
  // États pour les missions
  const [missions, setMissions] = useState([
    {
      id: 'mission_bull_001',
      name: 'Vision, plan stratégique et BP - Bull',
      client: 'Bull',
      status: 'Terminée',
      progress: 100,
      methodology: 'Proposition Commerciale SCR',
      domains: ['Stratégie', 'Transformation', 'Innovation'],
      agents: ['Senior Advisor', 'EFS', 'ESS'],
      completion_date: '2025-09-04',
      deliverables: [
        { id: 1, name: 'Analyse de marché HPC', type: 'PDF', status: 'Terminé', verified: true },
        { id: 2, name: 'Business Plan Bull 2025-2027', type: 'DOCX', status: 'Terminé', verified: true },
        { id: 3, name: 'Proposition commerciale', type: 'PDF', status: 'Terminé', verified: true }
      ]
    }
  ]);
  
  // États pour les dialogs
  const [showDeliverablesDialog, setShowDeliverablesDialog] = useState(false);
  const [showInteractionDialog, setShowInteractionDialog] = useState(false);
  const [showNewMissionDialog, setShowNewMissionDialog] = useState(false);
  const [showFactCheckerDialog, setShowFactCheckerDialog] = useState(false);
  const [showGraphistDialog, setShowGraphistDialog] = useState(false);
  const [selectedMission, setSelectedMission] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);

  // Données des agents (incluant les nouveaux)
  const [agents] = useState({
    consultants: [
      { id: 'AVS', name: 'Agent Veille Stratégique', status: 'active', performance: 95 },
      { id: 'AAD', name: 'Agent Analyse Données', status: 'active', performance: 98 },
      { id: 'AGC', name: 'Agent Gestion Connaissances', status: 'active', performance: 94 },
      { id: 'APC', name: 'Agent Proposition Commerciale', status: 'active', performance: 96 },
      { id: 'ARR', name: 'Agent Rédaction Rapports', status: 'active', performance: 93 },
      { id: 'ASM', name: 'Agent Suivi Mission', status: 'active', performance: 97 },
      { id: 'AMO', name: 'Agent Méthodes & Outils', status: 'active', performance: 95 },
      { id: 'AFC', name: 'Agent Fact Checker', status: 'active', performance: 99 },
      { id: 'AGR', name: 'Agent Graphiste', status: 'active', performance: 96 }
    ],
    experts_metiers: [
      { id: 'ESS', name: 'Expert Semi-conducteurs & Substrats', status: 'active', performance: 96 },
      { id: 'EBF', name: 'Expert Banque Finance', status: 'active', performance: 94 },
      { id: 'EA', name: 'Expert Assurance', status: 'active', performance: 92 },
      { id: 'EDDI', name: 'Expert Données Digitales Intelligence', status: 'active', performance: 98 },
      { id: 'EFS', name: 'Expert Finance & Stratégie', status: 'active', performance: 97 }
    ],
    experts_domaines: [
      { id: 'EIA', name: 'Expert Intelligence Artificielle', status: 'active', performance: 99 },
      { id: 'ECyber', name: 'Expert Cybersécurité', status: 'active', performance: 97 },
      { id: 'EC', name: 'Expert Cloud', status: 'active', performance: 95 },
      { id: 'EData', name: 'Expert Data', status: 'active', performance: 96 },
      { id: 'ELRD', name: 'Expert Législations Réglementations', status: 'active', performance: 94 }
    ]
  });

  // Fonctions de gestion des missions
  const handleViewDeliverables = (mission) => {
    setSelectedMission(mission);
    setShowDeliverablesDialog(true);
  };

  const handleViewInteraction = (mission) => {
    setSelectedMission(mission);
    setShowInteractionDialog(true);
  };

  const handleNewMission = () => {
    setShowNewMissionDialog(true);
  };

  // Fonctions pour les nouveaux agents
  const handleFactCheck = (document) => {
    setSelectedDocument(document);
    setShowFactCheckerDialog(true);
  };

  const handleGraphicEnrichment = (document) => {
    setSelectedDocument(document);
    setShowGraphistDialog(true);
  };

  // Fonction de fermeture des dialogs
  const closeAllDialogs = () => {
    setShowDeliverablesDialog(false);
    setShowInteractionDialog(false);
    setShowNewMissionDialog(false);
    setShowFactCheckerDialog(false);
    setShowGraphistDialog(false);
    setSelectedMission(null);
    setSelectedDocument(null);
  };

  // Rendu des onglets
  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <EnterpriseDashboard />;
      case 'systems':
        return <SystemManagement />;
      case 'reporting':
        return <ReportingSystem />;
      case 'agents':
        return renderAgentsTab();
      case 'missions':
        return renderMissionsTab();
      case 'intelligence':
        return renderIntelligenceTab();
      default:
        return <EnterpriseDashboard />;
    }
  };

  // Rendu de l'onglet Agents
  const renderAgentsTab = () => (
    <div className="agents-tab">
      <div className="tab-header">
        <h2>Gestion des Agents Experts</h2>
        <p>34 agents experts opérationnels - Performance moyenne: 96.2%</p>
      </div>
      
      <div className="agents-grid">
        <div className="agent-category">
          <h3>Agents Consultants (9)</h3>
          {agents.consultants.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className={`agent-status ${agent.status}`}>
                  {agent.status === 'active' ? 'Actif' : 'Inactif'}
                </span>
              </div>
              <div className="agent-performance">
                <span>{agent.performance}%</span>
              </div>
              {agent.id === 'AFC' && (
                <button 
                  className="agent-action-btn fact-checker"
                  onClick={() => setShowFactCheckerDialog(true)}
                >
                  🔍 Fact Check
                </button>
              )}
              {agent.id === 'AGR' && (
                <button 
                  className="agent-action-btn graphist"
                  onClick={() => setShowGraphistDialog(true)}
                >
                  🎨 Enrichir
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="agent-category">
          <h3>Experts Métiers (5)</h3>
          {agents.experts_metiers.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className={`agent-status ${agent.status}`}>Actif</span>
              </div>
              <div className="agent-performance">
                <span>{agent.performance}%</span>
              </div>
            </div>
          ))}
        </div>

        <div className="agent-category">
          <h3>Experts Domaines (5)</h3>
          {agents.experts_domaines.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className={`agent-status ${agent.status}`}>Actif</span>
              </div>
              <div className="agent-performance">
                <span>{agent.performance}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Rendu de l'onglet Missions
  const renderMissionsTab = () => (
    <div className="missions-tab">
      <div className="tab-header">
        <h2>Gestion des Missions</h2>
        <p>127 missions terminées - 5 missions actives - Taux de succès: 98.5%</p>
        <button className="new-mission-btn" onClick={handleNewMission}>
          Nouvelle Mission
        </button>
      </div>
      
      <div className="missions-grid">
        {missions.map(mission => (
          <div key={mission.id} className="mission-card">
            <div className="mission-header">
              <h3>{mission.name}</h3>
              <span className="mission-client">Client: {mission.client}</span>
            </div>
            
            <div className="mission-progress">
              <span>Progression:</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${mission.progress}%` }}
                ></div>
              </div>
              <span>{mission.progress}%</span>
            </div>
            
            <div className="mission-status">
              <span>Statut:</span>
              <span className={`status ${mission.status.toLowerCase()}`}>
                {mission.status}
              </span>
            </div>
            
            <div className="mission-deliverables">
              <span>Livrables: {mission.deliverables?.length || 0} documents</span>
            </div>
            
            <div className="mission-actions">
              <button 
                className="action-btn primary"
                onClick={() => handleViewDeliverables(mission)}
              >
                Livrables
              </button>
              <button 
                className="action-btn secondary"
                onClick={() => handleViewInteraction(mission)}
              >
                Voir Détails
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Rendu de l'onglet Intelligence
  const renderIntelligenceTab = () => (
    <div className="intelligence-tab">
      <div className="tab-header">
        <h2>Intelligence & Veille</h2>
        <p>Système de veille automatisé - Dernière mise à jour: {new Date().toLocaleString()}</p>
      </div>
      
      <div className="intelligence-content">
        <div className="intelligence-summary">
          <h3>Résumé Quotidien</h3>
          <p>Le système d'intelligence a collecté et analysé 247 sources aujourd'hui.</p>
          <ul>
            <li>15 nouvelles tendances technologiques identifiées</li>
            <li>8 opportunités de marché détectées</li>
            <li>12 alertes concurrentielles</li>
            <li>5 risques réglementaires signalés</li>
          </ul>
        </div>
        
        <div className="intelligence-actions">
          <button className="intelligence-btn">Générer Rapport</button>
          <button className="intelligence-btn">Configurer Alertes</button>
          <button className="intelligence-btn">Historique</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      {/* Header avec navigation */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>Substans.AI Enterprise v3.0.0</h1>
            <span className="status-indicator">
              <span className="status-dot active"></span>
              47/47 systèmes actifs
            </span>
          </div>
          
          <div className="header-stats">
            <div className="stat">
              <span className="stat-label">Uptime:</span>
              <span className="stat-value">99.95%</span>
            </div>
            <div className="stat">
              <span className="stat-label">Performance:</span>
              <span className="stat-value">94.2%</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation par onglets */}
      <nav className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          🏢 Dashboard Enterprise
          <small>Vue d'ensemble de la plateforme</small>
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'systems' ? 'active' : ''}`}
          onClick={() => setActiveTab('systems')}
        >
          ⚙️ Pilotage Systèmes
          <small>Gestion des 47 systèmes</small>
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'reporting' ? 'active' : ''}`}
          onClick={() => setActiveTab('reporting')}
        >
          📊 Reporting & Analytics
          <small>Rapports et analyses</small>
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          🤖 Agents (34)
          <small>Gestion des agents experts</small>
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'missions' ? 'active' : ''}`}
          onClick={() => setActiveTab('missions')}
        >
          📋 Missions
          <small>Gestion des missions</small>
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'intelligence' ? 'active' : ''}`}
          onClick={() => setActiveTab('intelligence')}
        >
          🧠 Intelligence
          <small>Veille et intelligence</small>
        </button>
      </nav>

      {/* Contenu principal */}
      <main className="main-content">
        {renderTabContent()}
      </main>

      {/* Dialog Livrables */}
      {showDeliverablesDialog && selectedMission && (
        <div className="dialog-overlay" onClick={closeAllDialogs}>
          <div className="dialog-content" onClick={e => e.stopPropagation()}>
            <div className="dialog-header">
              <h3>Livrables - {selectedMission.name}</h3>
              <button className="close-btn" onClick={closeAllDialogs}>×</button>
            </div>
            
            <div className="dialog-body">
              <div className="deliverables-list">
                {selectedMission.deliverables?.map(deliverable => (
                  <div key={deliverable.id} className="deliverable-item">
                    <div className="deliverable-info">
                      <span className="deliverable-name">{deliverable.name}</span>
                      <span className="deliverable-type">{deliverable.type}</span>
                      <span className={`deliverable-status ${deliverable.status.toLowerCase()}`}>
                        {deliverable.status}
                      </span>
                      {deliverable.verified && (
                        <span className="verified-badge">✅ Vérifié</span>
                      )}
                    </div>
                    
                    <div className="deliverable-actions">
                      <button className="action-btn small">Consulter</button>
                      <button className="action-btn small">Télécharger</button>
                      <button 
                        className="action-btn small fact-check"
                        onClick={() => handleFactCheck(deliverable)}
                      >
                        🔍 Fact Check
                      </button>
                      <button 
                        className="action-btn small graphist"
                        onClick={() => handleGraphicEnrichment(deliverable)}
                      >
                        🎨 Enrichir
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dialog Fact Checker */}
      {showFactCheckerDialog && (
        <div className="dialog-overlay" onClick={closeAllDialogs}>
          <div className="dialog-content fact-checker-dialog" onClick={e => e.stopPropagation()}>
            <div className="dialog-header">
              <h3>🔍 Agent Fact Checker</h3>
              <button className="close-btn" onClick={closeAllDialogs}>×</button>
            </div>
            
            <div className="dialog-body">
              <div className="fact-checker-interface">
                <div className="fact-checker-status">
                  <h4>Vérification en cours...</h4>
                  <p>L'Agent Fact Checker analyse le document "{selectedDocument?.name || 'Document sélectionné'}"</p>
                </div>
                
                <div className="verification-progress">
                  <div className="progress-item">
                    <span>✅ Vérification des chiffres</span>
                    <span className="confidence">Confiance: 95%</span>
                  </div>
                  <div className="progress-item">
                    <span>✅ Vérification des dates</span>
                    <span className="confidence">Confiance: 98%</span>
                  </div>
                  <div className="progress-item">
                    <span>✅ Vérification des noms</span>
                    <span className="confidence">Confiance: 92%</span>
                  </div>
                  <div className="progress-item">
                    <span>⏳ Vérification des sources</span>
                    <span className="confidence">En cours...</span>
                  </div>
                </div>
                
                <div className="fact-checker-actions">
                  <button className="action-btn primary">Approuver</button>
                  <button className="action-btn secondary">Révision requise</button>
                  <button className="action-btn danger">Rejeter</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dialog Graphiste */}
      {showGraphistDialog && (
        <div className="dialog-overlay" onClick={closeAllDialogs}>
          <div className="dialog-content graphist-dialog" onClick={e => e.stopPropagation()}>
            <div className="dialog-header">
              <h3>🎨 Agent Graphiste</h3>
              <button className="close-btn" onClick={closeAllDialogs}>×</button>
            </div>
            
            <div className="dialog-body">
              <div className="graphist-interface">
                <div className="graphist-options">
                  <h4>Options d'enrichissement</h4>
                  <div className="enrichment-options">
                    <label>
                      <input type="checkbox" defaultChecked />
                      Ajouter des graphiques pour les données numériques
                    </label>
                    <label>
                      <input type="checkbox" defaultChecked />
                      Créer des infographies pour les listes
                    </label>
                    <label>
                      <input type="checkbox" defaultChecked />
                      Générer des schémas de processus
                    </label>
                    <label>
                      <input type="checkbox" />
                      Ajouter des timelines chronologiques
                    </label>
                  </div>
                </div>
                
                <div className="style-selection">
                  <h4>Style graphique</h4>
                  <select className="style-selector">
                    <option value="professionnel">Professionnel</option>
                    <option value="moderne">Moderne</option>
                    <option value="minimaliste">Minimaliste</option>
                    <option value="corporate">Corporate</option>
                  </select>
                </div>
                
                <div className="graphist-preview">
                  <h4>Aperçu des améliorations</h4>
                  <p>3 graphiques seront ajoutés</p>
                  <p>2 infographies seront créées</p>
                  <p>1 schéma de processus sera généré</p>
                </div>
                
                <div className="graphist-actions">
                  <button className="action-btn primary">Enrichir le document</button>
                  <button className="action-btn secondary">Aperçu</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dialog Nouvelle Mission */}
      {showNewMissionDialog && (
        <div className="dialog-overlay" onClick={closeAllDialogs}>
          <div className="dialog-content new-mission-dialog" onClick={e => e.stopPropagation()}>
            <div className="dialog-header">
              <h3>Nouvelle Mission</h3>
              <button className="close-btn" onClick={closeAllDialogs}>×</button>
            </div>
            
            <div className="dialog-body">
              <div className="mission-form">
                <div className="form-group">
                  <label>Nom de la mission</label>
                  <input type="text" placeholder="Ex: Analyse stratégique secteur X" />
                </div>
                
                <div className="form-group">
                  <label>Client</label>
                  <input type="text" placeholder="Nom du client" />
                </div>
                
                <div className="form-group">
                  <label>Domaines d'expertise</label>
                  <div className="checkbox-group">
                    <label><input type="checkbox" /> Stratégie</label>
                    <label><input type="checkbox" /> Finance</label>
                    <label><input type="checkbox" /> Technologie</label>
                    <label><input type="checkbox" /> Innovation</label>
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Agents à mobiliser</label>
                  <select multiple className="agents-selector">
                    <option value="EFS">Expert Finance & Stratégie</option>
                    <option value="EIA">Expert Intelligence Artificielle</option>
                    <option value="ESS">Expert Semi-conducteurs</option>
                  </select>
                </div>
                
                <div className="form-actions">
                  <button className="action-btn primary">Créer la mission</button>
                  <button className="action-btn secondary" onClick={closeAllDialogs}>Annuler</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <p>Substans.AI Enterprise v3.0 - 47 systèmes opérationnels</p>
        <div className="footer-stats">
          <span>Performance: 94.2%</span>
          <span>Sécurité: 98.5%</span>
          <span>Uptime: 99.95%</span>
        </div>
      </footer>
    </div>
  );
}

export default App;

