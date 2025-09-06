#!/usr/bin/env python3
"""
Documentation Generator - Substans.AI Enterprise
Génération automatique de documentation technique et utilisateur
"""

import os
import ast
import inspect
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from collections import defaultdict
import markdown
from jinja2 import Environment, FileSystemLoader

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FunctionDoc:
    """Documentation d'une fonction"""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, Any]]
    return_type: str
    return_description: str
    examples: List[str]
    decorators: List[str]
    line_number: int
    complexity: str  # 'simple', 'medium', 'complex'
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ClassDoc:
    """Documentation d'une classe"""
    name: str
    docstring: str
    methods: List[FunctionDoc]
    attributes: List[Dict[str, Any]]
    inheritance: List[str]
    line_number: int
    is_dataclass: bool
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['methods'] = [method.to_dict() for method in self.methods]
        return data

@dataclass
class ModuleDoc:
    """Documentation d'un module"""
    name: str
    path: str
    docstring: str
    classes: List[ClassDoc]
    functions: List[FunctionDoc]
    imports: List[str]
    constants: List[Dict[str, Any]]
    line_count: int
    complexity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['classes'] = [cls.to_dict() for cls in self.classes]
        data['functions'] = [func.to_dict() for func in self.functions]
        return data

@dataclass
class APIEndpointDoc:
    """Documentation d'un endpoint API"""
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Dict[str, Any]
    responses: Dict[str, Dict[str, Any]]
    examples: List[Dict[str, Any]]
    authentication: str
    rate_limit: str
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class DocumentationGenerator:
    """Générateur de documentation automatique"""
    
    def __init__(self, project_root: str, output_dir: str = "docs"):
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuration des templates
        self.template_dir = self.output_dir / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
        # Créer les templates par défaut
        self._create_default_templates()
        
        # Environnement Jinja2
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # Patterns pour l'analyse
        self.docstring_patterns = {
            'parameters': r'(?:Args?|Parameters?):\s*(.*?)(?=Returns?:|Raises?:|Examples?:|$)',
            'returns': r'Returns?:\s*(.*?)(?=Raises?:|Examples?:|$)',
            'examples': r'Examples?:\s*(.*?)(?=Args?|Parameters?|Returns?:|Raises?:|$)',
            'raises': r'Raises?:\s*(.*?)(?=Args?|Parameters?|Returns?:|Examples?:|$)'
        }
        
        logger.info(f"Documentation Generator initialisé pour {project_root}")
    
    def _create_default_templates(self):
        """Crée les templates par défaut"""
        
        # Template pour la documentation de module
        module_template = """# {{ module.name }}

{{ module.docstring }}

**Chemin:** `{{ module.path }}`  
**Lignes de code:** {{ module.line_count }}  
**Score de complexité:** {{ "%.2f"|format(module.complexity_score) }}

## Imports

{% for import in module.imports %}
- `{{ import }}`
{% endfor %}

{% if module.constants %}
## Constantes

{% for constant in module.constants %}
### {{ constant.name }}
- **Type:** {{ constant.type }}
- **Valeur:** `{{ constant.value }}`
- **Description:** {{ constant.description }}
{% endfor %}
{% endif %}

{% if module.classes %}
## Classes

{% for class in module.classes %}
### {{ class.name }}

{{ class.docstring }}

**Ligne:** {{ class.line_number }}  
**Héritage:** {% for parent in class.inheritance %}{{ parent }}{% if not loop.last %}, {% endif %}{% endfor %}  
**Dataclass:** {{ "Oui" if class.is_dataclass else "Non" }}

{% if class.attributes %}
#### Attributs

{% for attr in class.attributes %}
- **{{ attr.name }}** ({{ attr.type }}): {{ attr.description }}
{% endfor %}
{% endif %}

{% if class.methods %}
#### Méthodes

{% for method in class.methods %}
##### {{ method.name }}

```python
{{ method.signature }}
```

{{ method.docstring }}

{% if method.parameters %}
**Paramètres:**
{% for param in method.parameters %}
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}
{% endif %}

{% if method.return_description %}
**Retourne:** {{ method.return_description }}
{% endif %}

{% if method.examples %}
**Exemples:**
{% for example in method.examples %}
```python
{{ example }}
```
{% endfor %}
{% endif %}

**Complexité:** {{ method.complexity }}

{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if module.functions %}
## Fonctions

{% for function in module.functions %}
### {{ function.name }}

```python
{{ function.signature }}
```

{{ function.docstring }}

{% if function.parameters %}
**Paramètres:**
{% for param in function.parameters %}
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}
{% endif %}

{% if function.return_description %}
**Retourne:** {{ function.return_description }}
{% endif %}

{% if function.examples %}
**Exemples:**
{% for example in function.examples %}
```python
{{ example }}
```
{% endfor %}
{% endif %}

**Complexité:** {{ function.complexity }}

{% endfor %}
{% endif %}

---
*Documentation générée automatiquement le {{ generation_date }}*
"""
        
        with open(self.template_dir / "module.md", "w", encoding="utf-8") as f:
            f.write(module_template)
        
        # Template pour l'index
        index_template = """# Documentation Substans.AI

Documentation technique générée automatiquement.

**Généré le:** {{ generation_date }}  
**Version:** {{ version }}

## Vue d'ensemble

- **Modules analysés:** {{ stats.total_modules }}
- **Classes totales:** {{ stats.total_classes }}
- **Fonctions totales:** {{ stats.total_functions }}
- **Lignes de code:** {{ stats.total_lines }}
- **Score de complexité moyen:** {{ "%.2f"|format(stats.avg_complexity) }}

## Modules

{% for module in modules %}
### [{{ module.name }}]({{ module.name|replace(".", "_") }}.md)

{{ module.docstring[:200] }}{% if module.docstring|length > 200 %}...{% endif %}

- **Classes:** {{ module.classes|length }}
- **Fonctions:** {{ module.functions|length }}
- **Lignes:** {{ module.line_count }}
- **Complexité:** {{ "%.2f"|format(module.complexity_score) }}

{% endfor %}

## API Endpoints

{% for endpoint in api_endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

{{ endpoint.description }}

**Tags:** {% for tag in endpoint.tags %}{{ tag }}{% if not loop.last %}, {% endif %}{% endfor %}  
**Authentification:** {{ endpoint.authentication }}  
**Rate Limit:** {{ endpoint.rate_limit }}

{% endfor %}

## Architecture

```mermaid
graph TB
    A[Substans Core Engine] --> B[System Orchestrator]
    A --> C[ML Engine]
    A --> D[System Monitor]
    
    B --> E[Mission Lifecycle Manager]
    B --> F[Quality Assurance]
    B --> G[Performance Analytics]
    
    C --> H[Knowledge Base Semantic]
    C --> I[Predictive Intelligence]
    C --> J[Trend Detection]
    
    D --> K[API Gateway]
    D --> L[Notification Engine]
    D --> M[Resource Allocator]
```

---
*Documentation générée automatiquement par Substans.AI Documentation Generator*
"""
        
        with open(self.template_dir / "index.md", "w", encoding="utf-8") as f:
            f.write(index_template)
        
        # Template pour l'API
        api_template = """# API Documentation

{% for endpoint in endpoints %}
## {{ endpoint.method }} {{ endpoint.path }}

{{ endpoint.description }}

**Tags:** {% for tag in endpoint.tags %}{{ tag }}{% if not loop.last %}, {% endif %}{% endfor %}  
**Authentification:** {{ endpoint.authentication }}  
**Rate Limit:** {{ endpoint.rate_limit }}

{% if endpoint.parameters %}
### Paramètres

{% for param in endpoint.parameters %}
- **{{ param.name }}** ({{ param.type }}){% if param.required %} *requis*{% endif %}: {{ param.description }}
{% endfor %}
{% endif %}

{% if endpoint.request_body %}
### Corps de la requête

```json
{{ endpoint.request_body | tojson(indent=2) }}
```
{% endif %}

### Réponses

{% for code, response in endpoint.responses.items() %}
#### {{ code }}

{{ response.description }}

```json
{{ response.schema | tojson(indent=2) }}
```
{% endfor %}

{% if endpoint.examples %}
### Exemples

{% for example in endpoint.examples %}
#### {{ example.title }}

**Requête:**
```bash
curl -X {{ endpoint.method }} "{{ example.request.url }}" \\
{% for header, value in example.request.headers.items() %}
  -H "{{ header }}: {{ value }}" \\
{% endfor %}
{% if example.request.body %}
  -d '{{ example.request.body | tojson }}'
{% endif %}
```

**Réponse:**
```json
{{ example.response | tojson(indent=2) }}
```
{% endfor %}
{% endif %}

---

{% endfor %}
"""
        
        with open(self.template_dir / "api.md", "w", encoding="utf-8") as f:
            f.write(api_template)
    
    def analyze_python_file(self, file_path: Path) -> ModuleDoc:
        """Analyse un fichier Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parser AST
            tree = ast.parse(content)
            
            # Extraire les informations
            module_name = file_path.stem
            module_docstring = ast.get_docstring(tree) or ""
            
            # Analyser les imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # Analyser les constantes
            constants = []
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constants.append({
                                'name': target.id,
                                'type': type(ast.literal_eval(node.value) if isinstance(node.value, (ast.Constant, ast.Str, ast.Num)) else 'unknown').__name__,
                                'value': ast.get_source_segment(content, node.value) or 'N/A',
                                'description': 'Constante du module'
                            })
            
            # Analyser les classes
            classes = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_doc = self._analyze_class(node, content)
                    classes.append(class_doc)
            
            # Analyser les fonctions
            functions = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_doc = self._analyze_function(node, content)
                    functions.append(func_doc)
            
            # Calculer la complexité
            line_count = len(content.splitlines())
            complexity_score = self._calculate_complexity(tree)
            
            return ModuleDoc(
                name=module_name,
                path=str(file_path.relative_to(self.project_root)),
                docstring=module_docstring,
                classes=classes,
                functions=functions,
                imports=imports,
                constants=constants,
                line_count=line_count,
                complexity_score=complexity_score
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse fichier {file_path}: {e}")
            return ModuleDoc(
                name=file_path.stem,
                path=str(file_path),
                docstring=f"Erreur d'analyse: {e}",
                classes=[],
                functions=[],
                imports=[],
                constants=[],
                line_count=0,
                complexity_score=0.0
            )
    
    def _analyze_class(self, node: ast.ClassDef, content: str) -> ClassDoc:
        """Analyse une classe"""
        class_name = node.name
        docstring = ast.get_docstring(node) or ""
        line_number = node.lineno
        
        # Vérifier si c'est une dataclass
        is_dataclass = any(
            isinstance(decorator, ast.Name) and decorator.id == 'dataclass'
            for decorator in node.decorator_list
        )
        
        # Analyser l'héritage
        inheritance = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance.append(base.id)
            elif isinstance(base, ast.Attribute):
                inheritance.append(f"{base.value.id}.{base.attr}")
        
        # Analyser les attributs
        attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_name = item.target.id
                attr_type = ast.get_source_segment(content, item.annotation) or 'Any'
                attributes.append({
                    'name': attr_name,
                    'type': attr_type,
                    'description': 'Attribut de classe'
                })
        
        # Analyser les méthodes
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._analyze_function(item, content)
                methods.append(method_doc)
        
        return ClassDoc(
            name=class_name,
            docstring=docstring,
            methods=methods,
            attributes=attributes,
            inheritance=inheritance,
            line_number=line_number,
            is_dataclass=is_dataclass
        )
    
    def _analyze_function(self, node: ast.FunctionDef, content: str) -> FunctionDoc:
        """Analyse une fonction"""
        func_name = node.name
        docstring = ast.get_docstring(node) or ""
        line_number = node.lineno
        
        # Extraire la signature
        signature = f"def {func_name}("
        args = []
        
        # Arguments positionnels
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.get_source_segment(content, arg.annotation)}"
            args.append(arg_str)
        
        # Arguments avec valeurs par défaut
        defaults = node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                idx = len(args) - len(defaults) + i
                if idx >= 0:
                    default_value = ast.get_source_segment(content, default) or 'None'
                    args[idx] += f" = {default_value}"
        
        signature += ", ".join(args) + ")"
        
        # Type de retour
        return_type = ""
        if node.returns:
            return_type = ast.get_source_segment(content, node.returns) or ""
            signature += f" -> {return_type}"
        
        # Parser la docstring
        parameters, return_description, examples = self._parse_docstring(docstring)
        
        # Analyser les décorateurs
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.value.id}.{decorator.attr}")
        
        # Calculer la complexité
        complexity = self._calculate_function_complexity(node)
        
        return FunctionDoc(
            name=func_name,
            signature=signature,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            return_description=return_description,
            examples=examples,
            decorators=decorators,
            line_number=line_number,
            complexity=complexity
        )
    
    def _parse_docstring(self, docstring: str) -> tuple:
        """Parse une docstring pour extraire les informations"""
        parameters = []
        return_description = ""
        examples = []
        
        if not docstring:
            return parameters, return_description, examples
        
        # Extraire les paramètres
        params_match = re.search(self.docstring_patterns['parameters'], docstring, re.DOTALL | re.IGNORECASE)
        if params_match:
            params_text = params_match.group(1).strip()
            for line in params_text.split('\n'):
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    param_name = parts[0].strip()
                    param_desc = parts[1].strip()
                    
                    # Extraire le type s'il est présent
                    param_type = "Any"
                    if '(' in param_name and ')' in param_name:
                        type_match = re.search(r'\(([^)]+)\)', param_name)
                        if type_match:
                            param_type = type_match.group(1)
                            param_name = re.sub(r'\([^)]+\)', '', param_name).strip()
                    
                    parameters.append({
                        'name': param_name,
                        'type': param_type,
                        'description': param_desc
                    })
        
        # Extraire la description de retour
        returns_match = re.search(self.docstring_patterns['returns'], docstring, re.DOTALL | re.IGNORECASE)
        if returns_match:
            return_description = returns_match.group(1).strip()
        
        # Extraire les exemples
        examples_match = re.search(self.docstring_patterns['examples'], docstring, re.DOTALL | re.IGNORECASE)
        if examples_match:
            examples_text = examples_match.group(1).strip()
            # Diviser par blocs de code
            code_blocks = re.findall(r'```python\n(.*?)\n```', examples_text, re.DOTALL)
            examples.extend(code_blocks)
        
        return parameters, return_description, examples
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calcule le score de complexité d'un module"""
        complexity = 0
        
        for node in ast.walk(tree):
            # Complexité cyclomatique
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 1
            elif isinstance(node, ast.ClassDef):
                complexity += 2
        
        # Normaliser par rapport au nombre de lignes
        total_nodes = len(list(ast.walk(tree)))
        return complexity / max(total_nodes, 1) * 100
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> str:
        """Calcule la complexité d'une fonction"""
        complexity = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
        
        if complexity <= 2:
            return "simple"
        elif complexity <= 5:
            return "medium"
        else:
            return "complex"
    
    def generate_module_documentation(self, modules: List[ModuleDoc]) -> Dict[str, str]:
        """Génère la documentation des modules"""
        docs = {}
        
        template = self.jinja_env.get_template("module.md")
        
        for module in modules:
            doc_content = template.render(
                module=module,
                generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            filename = f"{module.name.replace('.', '_')}.md"
            docs[filename] = doc_content
        
        return docs
    
    def generate_index_documentation(self, modules: List[ModuleDoc], 
                                   api_endpoints: List[APIEndpointDoc] = None) -> str:
        """Génère la documentation d'index"""
        # Calculer les statistiques
        stats = {
            'total_modules': len(modules),
            'total_classes': sum(len(m.classes) for m in modules),
            'total_functions': sum(len(m.functions) for m in modules),
            'total_lines': sum(m.line_count for m in modules),
            'avg_complexity': sum(m.complexity_score for m in modules) / len(modules) if modules else 0
        }
        
        template = self.jinja_env.get_template("index.md")
        
        return template.render(
            modules=modules,
            api_endpoints=api_endpoints or [],
            stats=stats,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            version="1.0.0"
        )
    
    def generate_api_documentation(self, endpoints: List[APIEndpointDoc]) -> str:
        """Génère la documentation API"""
        template = self.jinja_env.get_template("api.md")
        
        return template.render(
            endpoints=endpoints,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def scan_project(self, extensions: List[str] = None) -> List[ModuleDoc]:
        """Scanne le projet pour analyser tous les fichiers"""
        if extensions is None:
            extensions = ['.py']
        
        modules = []
        
        for ext in extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                # Ignorer certains dossiers
                if any(part.startswith('.') or part in ['__pycache__', 'node_modules', 'venv', 'env'] 
                      for part in file_path.parts):
                    continue
                
                if ext == '.py':
                    module_doc = self.analyze_python_file(file_path)
                    modules.append(module_doc)
        
        return modules
    
    def generate_full_documentation(self, include_api: bool = False) -> Dict[str, str]:
        """Génère la documentation complète du projet"""
        logger.info("Début de la génération de documentation")
        
        # Scanner le projet
        modules = self.scan_project()
        
        # Générer la documentation des modules
        module_docs = self.generate_module_documentation(modules)
        
        # Générer l'index
        api_endpoints = []
        if include_api:
            # Ici, on pourrait analyser les endpoints API depuis le code
            # Pour l'instant, on utilise des exemples
            api_endpoints = self._extract_api_endpoints()
        
        index_doc = self.generate_index_documentation(modules, api_endpoints)
        
        # Combiner tous les documents
        all_docs = {'index.md': index_doc}
        all_docs.update(module_docs)
        
        if include_api and api_endpoints:
            api_doc = self.generate_api_documentation(api_endpoints)
            all_docs['api.md'] = api_doc
        
        logger.info(f"Documentation générée: {len(all_docs)} fichiers")
        return all_docs
    
    def _extract_api_endpoints(self) -> List[APIEndpointDoc]:
        """Extrait les endpoints API du code (exemple)"""
        # Ici, on pourrait analyser le code pour extraire les endpoints Flask/FastAPI
        # Pour l'instant, on retourne des exemples
        return [
            APIEndpointDoc(
                path="/api/v1/missions",
                method="GET",
                description="Récupère la liste des missions",
                parameters=[
                    {"name": "status", "type": "string", "required": False, "description": "Filtre par statut"},
                    {"name": "limit", "type": "integer", "required": False, "description": "Nombre maximum de résultats"}
                ],
                request_body={},
                responses={
                    "200": {
                        "description": "Liste des missions",
                        "schema": {"missions": "array", "total": "integer"}
                    },
                    "401": {
                        "description": "Non autorisé",
                        "schema": {"error": "string"}
                    }
                },
                examples=[
                    {
                        "title": "Récupérer toutes les missions",
                        "request": {
                            "url": "/api/v1/missions",
                            "headers": {"Authorization": "Bearer your_api_key"}
                        },
                        "response": {
                            "missions": [
                                {"id": "mission_001", "title": "Analyse Bull", "status": "completed"}
                            ],
                            "total": 1
                        }
                    }
                ],
                authentication="Bearer Token",
                rate_limit="100 req/min",
                tags=["missions"]
            )
        ]
    
    def save_documentation(self, docs: Dict[str, str]):
        """Sauvegarde la documentation sur disque"""
        for filename, content in docs.items():
            file_path = self.output_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Documentation sauvegardée: {file_path}")
        
        # Créer un fichier de métadonnées
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'files_count': len(docs),
            'generator_version': '1.0.0',
            'project_root': str(self.project_root)
        }
        
        with open(self.output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le générateur
    generator = DocumentationGenerator(
        project_root="/home/ubuntu/substans_ai_megacabinet",
        output_dir="/home/ubuntu/substans_ai_megacabinet/docs"
    )
    
    # Générer la documentation complète
    docs = generator.generate_full_documentation(include_api=True)
    
    # Sauvegarder
    generator.save_documentation(docs)
    
    print(f"Documentation générée dans {generator.output_dir}")
    print(f"Fichiers créés: {list(docs.keys())}")
    
    # Afficher les statistiques
    modules = generator.scan_project()
    total_classes = sum(len(m.classes) for m in modules)
    total_functions = sum(len(m.functions) for m in modules)
    total_lines = sum(m.line_count for m in modules)
    
    print(f"\nStatistiques du projet:")
    print(f"- Modules: {len(modules)}")
    print(f"- Classes: {total_classes}")
    print(f"- Fonctions: {total_functions}")
    print(f"- Lignes de code: {total_lines}")
    print(f"- Complexité moyenne: {sum(m.complexity_score for m in modules) / len(modules):.2f}")

