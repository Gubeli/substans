import React, { useState, useEffect } from 'react';
import './App.css';
import EnterpriseDashboard from './components/EnterpriseDashboard';
import ReportingSystem from './components/ReportingSystem';
import SystemManagement from './components/SystemManagement';

function App() {
  const [activeTab, setActiveTab] = useState('enterprise');
  const [enterpriseData, setEnterpriseData] = useState({
    overview: {
      version: '3.0.0',
      environment: 'enterprise',
      uptime: 99.95,
      performance_score: 94.2,
      security_score: 98.5,
      compliance_score: 96.8
    },
    systems: {
      total: 47,
      active: 47,
      warning: 0,
      error: 0
    },
    metrics: {
      total_missions: 127,
      active_missions: 5,
      total_users: 45,
      active_users: 12,
      system_uptime: 99.95,
      performance_score: 94.2,
      security_score: 98.5,
      compliance_score: 96.8
    },
    alerts: [],
    recent_activities: []
  });

  // Simulation de données temps réel
  useEffect(() => {
    const interval = setInterval(() => {
      setEnterpriseData(prev => ({
        ...prev,
        metrics: {
          ...prev.metrics,
          active_users: Math.floor(Math.random() * 5) + 10,
          performance_score: 94.2 + (Math.random() - 0.5) * 2
        }
      }));
    }, 30000); // Mise à jour toutes les 30 secondes

    return () => clearInterval(interval);
  }, []);

  const handleRefreshData = () => {
    // Simulation du rafraîchissement des données
    setEnterpriseData(prev => ({
      ...prev,
      overview: {
        ...prev.overview,
        uptime: 99.95 + (Math.random() - 0.5) * 0.1,
        performance_score: 94.2 + (Math.random() - 0.5) * 2,
        security_score: 98.5 + (Math.random() - 0.5) * 1,
        compliance_score: 96.8 + (Math.random() - 0.5) * 1
      }
    }));
  };

  const tabs = [
    {
      id: 'enterprise',
      name: 'Dashboard Enterprise',
      icon: '🏢',
      description: 'Vue d\'ensemble de la plateforme'
    },
    {
      id: 'systems',
      name: 'Pilotage Systèmes',
      icon: '⚙️',
      description: 'Gestion des 47 systèmes'
    },
    {
      id: 'reporting',
      name: 'Reporting & Analytics',
      icon: '📊',
      description: 'Rapports et analyses'
    },
    {
      id: 'agents',
      name: 'Agents (32)',
      icon: '🤖',
      description: 'Gestion des agents experts'
    },
    {
      id: 'missions',
      name: 'Missions',
      icon: '📋',
      description: 'Gestion des missions'
    },
    {
      id: 'intelligence',
      name: 'Intelligence',
      icon: '🧠',
      description: 'Veille et intelligence'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header Enterprise */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-full mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-gray-900">
                Substans.AI Enterprise v{enterpriseData.overview.version}
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">
                  {enterpriseData.systems.active}/{enterpriseData.systems.total} systèmes actifs
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Uptime: <span className="font-semibold text-green-600">{enterpriseData.overview.uptime}%</span>
              </div>
              <div className="text-sm text-gray-600">
                Performance: <span className="font-semibold text-blue-600">{enterpriseData.overview.performance_score.toFixed(1)}%</span>
              </div>
              <button 
                onClick={handleRefreshData}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Actualiser"
              >
                🔄
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-full mx-auto px-6">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </div>
                <div className="text-xs text-gray-400 mt-1">{tab.description}</div>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-full mx-auto px-6 py-6">
        {activeTab === 'enterprise' && (
          <EnterpriseDashboard 
            enterpriseData={enterpriseData} 
            onRefresh={handleRefreshData}
          />
        )}
        
        {activeTab === 'systems' && (
          <SystemManagement />
        )}
        
        {activeTab === 'reporting' && (
          <ReportingSystem />
        )}
        
        {activeTab === 'agents' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white p-6 rounded-lg">
              <h1 className="text-3xl font-bold">Gestion des Agents Experts</h1>
              <p className="text-blue-200 mt-2">32 agents experts opérationnels - Performance moyenne: 96.2%</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Agents Consultants */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Agents Consultants (7)</h2>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {[
                      'Agent Veille Stratégique',
                      'Agent Analyse Données', 
                      'Agent Gestion Connaissances',
                      'Agent Proposition Commerciale',
                      'Agent Rédaction Rapports',
                      'Agent Suivi Mission',
                      'Agent Méthodes & Outils'
                    ].map((agent, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium">{agent}</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                          Actif
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Experts Métiers */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Experts Métiers (11)</h2>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {[
                      'Expert Semi-conducteurs',
                      'Expert Banque Finance',
                      'Expert Assurance',
                      'Expert Données Digitales Intelligence',
                      'Expert Finance & M&A'
                    ].map((expert, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium">{expert}</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                          Actif
                        </span>
                      </div>
                    ))}
                    <div className="text-xs text-gray-500 mt-2 text-center">+ 6 autres experts</div>
                  </div>
                </div>
              </div>

              {/* Experts Domaines */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Experts Domaines (14)</h2>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {[
                      'Expert Intelligence Artificielle',
                      'Expert Cybersécurité',
                      'Expert Cloud',
                      'Expert Data',
                      'Expert Législations Réglementations'
                    ].map((expert, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium">{expert}</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                          Actif
                        </span>
                      </div>
                    ))}
                    <div className="text-xs text-gray-500 mt-2 text-center">+ 9 autres experts</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'missions' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-900 to-blue-900 text-white p-6 rounded-lg">
              <h1 className="text-3xl font-bold">Gestion des Missions</h1>
              <p className="text-purple-200 mt-2">127 missions terminées - 5 missions actives - Taux de succès: 98.5%</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Mission Bull */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Vision, plan stratégique et BP</h3>
                  <p className="text-sm text-gray-600">Client: Bull</p>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Progression:</span>
                      <span className="font-semibold text-green-600">100%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Statut:</span>
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                        Terminée
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Livrables:</span>
                      <span className="font-semibold">3 documents</span>
                    </div>
                  </div>
                  <div className="mt-4 flex space-x-2">
                    <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 transition-colors">
                      Voir Détails
                    </button>
                    <button className="flex-1 border border-gray-300 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-50 transition-colors">
                      Livrables
                    </button>
                  </div>
                </div>
              </div>

              {/* Nouvelles missions */}
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white rounded-lg shadow-md">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Mission {i}</h3>
                    <p className="text-sm text-gray-600">Client: En attente</p>
                  </div>
                  <div className="p-6">
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span>Progression:</span>
                        <span className="font-semibold text-gray-600">0%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-gray-300 h-2 rounded-full" style={{ width: '0%' }}></div>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Statut:</span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                          En attente
                        </span>
                      </div>
                    </div>
                    <div className="mt-4">
                      <button className="w-full bg-indigo-600 text-white px-3 py-2 rounded text-sm hover:bg-indigo-700 transition-colors">
                        Nouvelle Mission
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'intelligence' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-900 to-teal-900 text-white p-6 rounded-lg">
              <h1 className="text-3xl font-bold">Intelligence & Veille Quotidienne</h1>
              <p className="text-green-200 mt-2">290 sources surveillées - 24 rapports quotidiens - Dernière mise à jour: 06:00</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Intelligence Quotidienne */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Intelligence Quotidienne</h3>
                  <p className="text-sm text-gray-600">Synthèse des 32 agents experts</p>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Rapports générés:</span>
                      <span className="font-semibold text-blue-600">24</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Sources surveillées:</span>
                      <span className="font-semibold text-green-600">290</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Dernière collecte:</span>
                      <span className="font-semibold">06:00</span>
                    </div>
                  </div>
                  <div className="mt-4">
                    <button className="w-full bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 transition-colors">
                      Consulter Intelligence
                    </button>
                  </div>
                </div>
              </div>

              {/* Génération de Contenu */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Génération de Contenu</h3>
                  <p className="text-sm text-gray-600">LinkedIn, Twitter, Instagram, Facebook</p>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Contenus générés:</span>
                      <span className="font-semibold text-purple-600">156</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Planifiés:</span>
                      <span className="font-semibold text-orange-600">23</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Plateformes:</span>
                      <span className="font-semibold">4</span>
                    </div>
                  </div>
                  <div className="mt-4">
                    <button className="w-full bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700 transition-colors">
                      Gérer Contenu
                    </button>
                  </div>
                </div>
              </div>

              {/* Tendances Détectées */}
              <div className="bg-white rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Tendances Détectées</h3>
                  <p className="text-sm text-gray-600">Analyse prédictive et patterns</p>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Tendances actives:</span>
                      <span className="font-semibold text-red-600">12</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Alertes critiques:</span>
                      <span className="font-semibold text-yellow-600">3</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Prédictions:</span>
                      <span className="font-semibold text-blue-600">8</span>
                    </div>
                  </div>
                  <div className="mt-4">
                    <button className="w-full bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 transition-colors">
                      Analyser Tendances
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-full mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              Substans.AI Enterprise v{enterpriseData.overview.version} - 
              <span className="ml-1">47 systèmes opérationnels</span>
            </div>
            <div className="flex items-center space-x-4">
              <span>Performance: {enterpriseData.overview.performance_score.toFixed(1)}%</span>
              <span>Sécurité: {enterpriseData.overview.security_score.toFixed(1)}%</span>
              <span>Uptime: {enterpriseData.overview.uptime.toFixed(2)}%</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

