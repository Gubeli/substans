import React, { useState, useEffect } from 'react';

const SystemManagement = () => {
  const [activeManagementTab, setActiveManagementTab] = useState('systems');
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [showSystemDialog, setShowSystemDialog] = useState(false);

  const systemCategories = {
    core: {
      name: 'Systèmes Core',
      systems: [
        { id: 'core_engine', name: 'Substans Core Engine', status: 'running', cpu: 15, memory: 2.1, version: '3.0.0' },
        { id: 'orchestrator', name: 'System Orchestrator', status: 'running', cpu: 8, memory: 1.5, version: '3.0.0' },
        { id: 'ml_engine', name: 'ML Engine', status: 'running', cpu: 25, memory: 3.2, version: '3.0.0' },
        { id: 'monitor', name: 'System Monitor', status: 'running', cpu: 5, memory: 0.8, version: '3.0.0' }
      ]
    },
    specialized: {
      name: 'Systèmes Spécialisés',
      systems: [
        { id: 'knowledge_base', name: 'Knowledge Base Sémantique', status: 'running', cpu: 12, memory: 2.8, version: '3.0.0' },
        { id: 'methodology', name: 'Methodology Adaptive', status: 'running', cpu: 7, memory: 1.2, version: '3.0.0' },
        { id: 'predictive', name: 'Intelligence Prédictive', status: 'running', cpu: 18, memory: 2.5, version: '3.0.0' },
        { id: 'trends', name: 'Trend Detection', status: 'running', cpu: 10, memory: 1.8, version: '3.0.0' }
      ]
    },
    management: {
      name: 'Gestion & Missions',
      systems: [
        { id: 'mission_manager', name: 'Mission Lifecycle Manager', status: 'running', cpu: 14, memory: 2.3, version: '3.0.0' },
        { id: 'quality', name: 'Quality Assurance System', status: 'running', cpu: 9, memory: 1.6, version: '3.0.0' },
        { id: 'analytics', name: 'Performance Analytics', status: 'running', cpu: 11, memory: 2.0, version: '3.0.0' },
        { id: 'resources', name: 'Resource Allocator', status: 'running', cpu: 6, memory: 1.1, version: '3.0.0' }
      ]
    },
    integration: {
      name: 'Intégration',
      systems: [
        { id: 'api_gateway', name: 'API Gateway', status: 'running', cpu: 13, memory: 1.9, version: '3.0.0' },
        { id: 'notifications', name: 'Notification Engine', status: 'running', cpu: 4, memory: 0.7, version: '3.0.0' },
        { id: 'documentation', name: 'Documentation Generator', status: 'running', cpu: 3, memory: 0.5, version: '3.0.0' }
      ]
    },
    security: {
      name: 'Sécurité',
      systems: [
        { id: 'security_manager', name: 'Security Manager', status: 'running', cpu: 16, memory: 2.4, version: '3.0.0' },
        { id: 'rbac', name: 'RBAC System', status: 'running', cpu: 5, memory: 0.9, version: '3.0.0' },
        { id: 'audit', name: 'Audit System', status: 'running', cpu: 8, memory: 1.3, version: '3.0.0' },
        { id: 'encryption', name: 'Encryption System', status: 'running', cpu: 12, memory: 1.7, version: '3.0.0' }
      ]
    }
  };

  const agents = {
    consultants: [
      { id: 'avs', name: 'Agent Veille Stratégique', status: 'active', performance: 95, missions: 23 },
      { id: 'aad', name: 'Agent Analyse Données', status: 'active', performance: 98, missions: 31 },
      { id: 'agc', name: 'Agent Gestion Connaissances', status: 'active', performance: 94, missions: 18 },
      { id: 'apc', name: 'Agent Proposition Commerciale', status: 'active', performance: 96, missions: 27 },
      { id: 'arr', name: 'Agent Rédaction Rapports', status: 'active', performance: 93, missions: 35 },
      { id: 'asm', name: 'Agent Suivi Mission', status: 'active', performance: 97, missions: 42 },
      { id: 'amo', name: 'Agent Méthodes & Outils', status: 'active', performance: 95, missions: 19 }
    ],
    experts_metiers: [
      { id: 'ess', name: 'Expert Semi-conducteurs', status: 'active', performance: 96, missions: 15 },
      { id: 'ebf', name: 'Expert Banque Finance', status: 'active', performance: 94, missions: 22 },
      { id: 'ea', name: 'Expert Assurance', status: 'active', performance: 92, missions: 13 },
      { id: 'eddi', name: 'Expert Données Digitales Intelligence', status: 'active', performance: 98, missions: 28 },
      { id: 'efs', name: 'Expert Finance & M&A', status: 'active', performance: 97, missions: 21 }
    ],
    experts_domaines: [
      { id: 'eia', name: 'Expert Intelligence Artificielle', status: 'active', performance: 99, missions: 34 },
      { id: 'ecyber', name: 'Expert Cybersécurité', status: 'active', performance: 97, missions: 26 },
      { id: 'ec', name: 'Expert Cloud', status: 'active', performance: 95, missions: 29 },
      { id: 'edata', name: 'Expert Data', status: 'active', performance: 96, missions: 31 },
      { id: 'elrd', name: 'Expert Législations Réglementations Digitales', status: 'active', performance: 94, missions: 17 }
    ]
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'stopped':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
      case 'active':
        return '🟢';
      case 'warning':
        return '🟡';
      case 'error':
        return '🔴';
      case 'stopped':
        return '⚪';
      default:
        return '⚪';
    }
  };

  const handleSystemAction = (system, action) => {
    console.log(`Action ${action} sur le système ${system.name}`);
    // Ici on implémenterait les actions réelles
  };

  return (
    <div className="space-y-6">
      {/* Header Management */}
      <div className="bg-gradient-to-r from-gray-900 to-slate-900 text-white p-6 rounded-lg">
        <h1 className="text-3xl font-bold">Pilotage Plateforme Enterprise</h1>
        <p className="text-gray-200 mt-2">Gestion et monitoring des 47 systèmes opérationnels</p>
      </div>

      {/* Onglets Management */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'systems', name: 'Systèmes Core', icon: '⚙️' },
              { id: 'agents', name: 'Agents (32)', icon: '🤖' },
              { id: 'monitoring', name: 'Monitoring', icon: '📊' },
              { id: 'configuration', name: 'Configuration', icon: '🔧' },
              { id: 'maintenance', name: 'Maintenance', icon: '🛠️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveManagementTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeManagementTab === tab.id
                    ? 'border-gray-500 text-gray-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Systèmes Core */}
          {activeManagementTab === 'systems' && (
            <div className="space-y-6">
              {Object.entries(systemCategories).map(([categoryId, category]) => (
                <div key={categoryId} className="border rounded-lg">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                  </div>
                  
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {category.systems.map((system) => (
                        <div key={system.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center">
                              <span className="mr-2">{getStatusIcon(system.status)}</span>
                              <h4 className="font-semibold text-gray-900">{system.name}</h4>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(system.status)}`}>
                              {system.status}
                            </span>
                          </div>
                          
                          <div className="space-y-2 text-sm text-gray-600">
                            <div className="flex justify-between">
                              <span>CPU:</span>
                              <span>{system.cpu}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Mémoire:</span>
                              <span>{system.memory} GB</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Version:</span>
                              <span>{system.version}</span>
                            </div>
                          </div>
                          
                          <div className="mt-4 flex space-x-2">
                            <button 
                              onClick={() => {
                                setSelectedSystem(system);
                                setShowSystemDialog(true);
                              }}
                              className="flex-1 bg-gray-600 text-white px-3 py-2 rounded text-sm hover:bg-gray-700 transition-colors"
                            >
                              Détails
                            </button>
                            <button 
                              onClick={() => handleSystemAction(system, 'restart')}
                              className="flex-1 border border-gray-300 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-50 transition-colors"
                            >
                              Redémarrer
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Agents */}
          {activeManagementTab === 'agents' && (
            <div className="space-y-6">
              {Object.entries(agents).map(([categoryId, agentList]) => (
                <div key={categoryId} className="border rounded-lg">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {categoryId === 'consultants' ? 'Agents Consultants (7)' :
                       categoryId === 'experts_metiers' ? 'Experts Métiers (11)' :
                       'Experts Domaines (14)'}
                    </h3>
                  </div>
                  
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {agentList.map((agent) => (
                        <div key={agent.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center">
                              <span className="mr-2">{getStatusIcon(agent.status)}</span>
                              <h4 className="font-medium text-gray-900 text-sm">{agent.name}</h4>
                            </div>
                          </div>
                          
                          <div className="space-y-2 text-sm text-gray-600">
                            <div className="flex justify-between">
                              <span>Performance:</span>
                              <span className="font-semibold text-green-600">{agent.performance}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Missions:</span>
                              <span>{agent.missions}</span>
                            </div>
                          </div>
                          
                          <div className="mt-3">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full" 
                                style={{ width: `${agent.performance}%` }}
                              ></div>
                            </div>
                          </div>
                          
                          <div className="mt-4 flex space-x-2">
                            <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-xs hover:bg-blue-700 transition-colors">
                              Configurer
                            </button>
                            <button className="flex-1 border border-gray-300 text-gray-700 px-3 py-2 rounded text-xs hover:bg-gray-50 transition-colors">
                              Logs
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Monitoring */}
          {activeManagementTab === 'monitoring' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Métriques Système */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Métriques Système</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>CPU Global</span>
                        <span>12%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '12%' }}></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Mémoire</span>
                        <span>34%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '34%' }}></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Disque</span>
                        <span>18%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '18%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Alertes */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Alertes Actives</h3>
                  <div className="space-y-3">
                    <div className="flex items-center text-sm">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      <span>Tous les systèmes opérationnels</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      <span>32 agents actifs</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      <span>Performance optimale</span>
                    </div>
                  </div>
                </div>

                {/* Statistiques */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Statistiques</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Uptime:</span>
                      <span className="font-semibold text-green-600">99.95%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Requêtes/min:</span>
                      <span className="font-semibold">1,247</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Missions actives:</span>
                      <span className="font-semibold">5</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Utilisateurs:</span>
                      <span className="font-semibold">12</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Graphiques de monitoring */}
              <div className="border rounded-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Monitoring Temps Réel</h3>
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <div className="text-4xl mb-2">📊</div>
                    <p>Graphiques de monitoring</p>
                    <p className="text-sm">CPU, Mémoire, Réseau, Performance</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Configuration */}
          {activeManagementTab === 'configuration' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Configuration Générale */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Configuration Générale</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Niveau de Log
                      </label>
                      <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                        <option>INFO</option>
                        <option>DEBUG</option>
                        <option>WARNING</option>
                        <option>ERROR</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Threads Pool Size
                      </label>
                      <input 
                        type="number" 
                        defaultValue="20" 
                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Cache TTL (minutes)
                      </label>
                      <input 
                        type="number" 
                        defaultValue="30" 
                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                      />
                    </div>
                  </div>
                </div>

                {/* Configuration Sécurité */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Configuration Sécurité</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Niveau de Sécurité
                      </label>
                      <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                        <option>Standard</option>
                        <option>Élevé</option>
                        <option>Maximum</option>
                        <option>Top Secret</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Rotation des Clés (jours)
                      </label>
                      <input 
                        type="number" 
                        defaultValue="30" 
                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                      />
                    </div>
                    
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        defaultChecked 
                        className="mr-2"
                      />
                      <label className="text-sm text-gray-700">
                        Audit automatique activé
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                  Annuler
                </button>
                <button className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
                  Sauvegarder
                </button>
              </div>
            </div>
          )}

          {/* Maintenance */}
          {activeManagementTab === 'maintenance' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Actions de Maintenance */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Actions de Maintenance</h3>
                  <div className="space-y-3">
                    <button className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors text-left">
                      <div className="flex items-center">
                        <span className="mr-3">🔄</span>
                        <div>
                          <div className="font-medium">Redémarrer Tous les Systèmes</div>
                          <div className="text-sm text-blue-100">Redémarrage complet de la plateforme</div>
                        </div>
                      </div>
                    </button>
                    
                    <button className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors text-left">
                      <div className="flex items-center">
                        <span className="mr-3">💾</span>
                        <div>
                          <div className="font-medium">Sauvegarde Complète</div>
                          <div className="text-sm text-green-100">Backup de tous les systèmes et données</div>
                        </div>
                      </div>
                    </button>
                    
                    <button className="w-full bg-yellow-600 text-white px-4 py-3 rounded-lg hover:bg-yellow-700 transition-colors text-left">
                      <div className="flex items-center">
                        <span className="mr-3">🧹</span>
                        <div>
                          <div className="font-medium">Nettoyage Cache</div>
                          <div className="text-sm text-yellow-100">Vider tous les caches système</div>
                        </div>
                      </div>
                    </button>
                    
                    <button className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors text-left">
                      <div className="flex items-center">
                        <span className="mr-3">🔍</span>
                        <div>
                          <div className="font-medium">Diagnostic Complet</div>
                          <div className="text-sm text-purple-100">Analyse complète de la plateforme</div>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Planification */}
                <div className="border rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Maintenance Programmée</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-sm">Sauvegarde Quotidienne</div>
                        <div className="text-xs text-gray-600">Tous les jours à 02:00</div>
                      </div>
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Actif</span>
                    </div>
                    
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-sm">Nettoyage Logs</div>
                        <div className="text-xs text-gray-600">Hebdomadaire - Dimanche 01:00</div>
                      </div>
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Actif</span>
                    </div>
                    
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-sm">Mise à jour Sécurité</div>
                        <div className="text-xs text-gray-600">Mensuel - 1er de chaque mois</div>
                      </div>
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Actif</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dialog Détails Système */}
      {showSystemDialog && selectedSystem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Détails - {selectedSystem.name}</h3>
              <button 
                onClick={() => setShowSystemDialog(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Informations Générales */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Informations Générales</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Statut:</span>
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getStatusColor(selectedSystem.status)}`}>
                      {selectedSystem.status}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Version:</span>
                    <span className="ml-2 font-medium">{selectedSystem.version}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">CPU:</span>
                    <span className="ml-2 font-medium">{selectedSystem.cpu}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Mémoire:</span>
                    <span className="ml-2 font-medium">{selectedSystem.memory} GB</span>
                  </div>
                </div>
              </div>

              {/* Métriques */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Métriques de Performance</h4>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Utilisation CPU</span>
                      <span>{selectedSystem.cpu}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${selectedSystem.cpu}%` }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Utilisation Mémoire</span>
                      <span>{Math.round(selectedSystem.memory * 10)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{ width: `${selectedSystem.memory * 10}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Actions Disponibles</h4>
                <div className="grid grid-cols-2 gap-3">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Redémarrer
                  </button>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                    Sauvegarder
                  </button>
                  <button className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors">
                    Logs
                  </button>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                    Configuration
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end mt-6">
              <button 
                onClick={() => setShowSystemDialog(false)}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemManagement;

