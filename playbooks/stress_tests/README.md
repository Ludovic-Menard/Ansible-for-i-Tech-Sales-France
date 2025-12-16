# 🚀 Playbooks Ansible - Tests de Stress IBM i

## 📋 Vue d'ensemble

Suite de playbooks Ansible pour automatiser les tests de performance sur les systèmes IBM i. Ces playbooks permettent de déployer et exécuter des tests de stress CPU et I/O, avec collecte automatique des métriques et génération de rapports.

**Objectif principal :** Valider les performances des systèmes IBM i avant et après des mises à jour (PTFs, upgrades OS, etc.).

## 📦 Contenu

### Phase 1 - Playbooks de Base ✅

| Playbook | Description | Usage |
|----------|-------------|-------|
| `deploy_stress_tools.yml` | Déploie les scripts Python sur IBM i | Première étape obligatoire |
| `run_cpu_stress.yml` | Exécute des tests de stress CPU | Tests de charge processeur |
| `run_io_stress.yml` | Exécute des tests de stress I/O | Tests de charge disque |

### Phase 2 - Fonctionnalités Avancées ✅

| Playbook | Description | Usage |
|----------|-------------|-------|
| `run_monitoring.yml` | Monitoring continu des performances | Collecte métriques temps réel |
| `run_orchestrator.yml` | Orchestrateur avec scénarios prédéfinis | Tests combinés CPU + I/O |
| `collect_baseline.yml` | Collecte baseline avant mise à jour | Référence de performance |
| `compare_results.yml` | Compare baseline vs validation | Analyse des différences |
| `main_performance_validation.yml` | **Workflow complet automatisé** | **Validation bout-en-bout** |

### Templates

| Template | Description |
|----------|-------------|
| `performance_report.html.j2` | Rapport HTML visuel avec graphiques |

## 🔧 Prérequis

### Sur le Serveur de Contrôle Ansible

- Ansible 2.9 ou supérieur
- Python 3.6+
- Accès SSH aux serveurs IBM i

### Sur les Serveurs IBM i

- IBM i V7R2 ou supérieur
- Python 3 installé (`/QOpenSys/pkgs/bin/python3`)
- Package `psutil` (sera installé automatiquement)
- Accès SSH configuré
- Espace disque suffisant pour les tests

## 📥 Installation

### 1. Cloner le Projet

```bash
cd /path/to/Ansible-for-i-Tech-Sales-France
```

### 2. Configurer l'Inventaire

Copiez et adaptez le fichier d'inventaire exemple :

```bash
cd playbooks/stress_tests
cp inventory_example.ini inventory.ini
```

Éditez `inventory.ini` avec vos serveurs IBM i :

```ini
[ibmi_stress_test]
ibmi-prod.example.com ansible_host=192.168.1.10

[ibmi_stress_test:vars]
ansible_user=QSECOFR
ansible_ssh_pass=your_password
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
```

**⚠️ Sécurité :** Utilisez plutôt des clés SSH ou Ansible Vault pour les mots de passe.

### 3. Personnaliser les Variables

Éditez `vars.yml` pour ajuster les paramètres de test :

```yaml
# Durée des tests
cpu_test_duration: 300  # 5 minutes
io_test_duration: 300   # 5 minutes

# Intensité CPU
cpu_cores: 4
cpu_intensity: "high"

# Configuration I/O
io_processes: 2
io_file_size_mb: 100
io_operation: "mixed"
```

### 4. Tester la Connexion

```bash
ansible -i inventory.ini ibmi_stress_test -m ping
```

Résultat attendu :
```
ibmi-prod.example.com | SUCCESS => {
    "ping": "pong"
}
```

## 🚀 Utilisation

### Workflow Complet

#### Étape 1 : Déploiement des Outils

Déployez les scripts Python sur tous les serveurs IBM i :

```bash
ansible-playbook -i inventory.ini deploy_stress_tools.yml
```

**Ce que fait ce playbook :**
- ✅ Vérifie les prérequis (Python, pip)
- ✅ Crée la structure de répertoires
- ✅ Copie les scripts Python
- ✅ Installe les dépendances (psutil)
- ✅ Vérifie le déploiement

**Durée estimée :** 2-5 minutes

#### Étape 2 : Test de Stress CPU

Exécutez un test de charge CPU :

```bash
ansible-playbook -i inventory.ini run_cpu_stress.yml
```

**Ce que fait ce playbook :**
- ✅ Collecte les métriques baseline
- ✅ Exécute le test de stress CPU
- ✅ Collecte les métriques post-test
- ✅ Calcule les statistiques
- ✅ Sauvegarde les résultats localement

**Durée :** Selon `cpu_test_duration` (défaut: 5 minutes)

#### Étape 3 : Test de Stress I/O

Exécutez un test de charge disque :

```bash
ansible-playbook -i inventory.ini run_io_stress.yml
```

**Ce que fait ce playbook :**
- ✅ Vérifie l'espace disque disponible
- ✅ Collecte les métriques baseline
- ✅ Exécute le test de stress I/O
- ✅ Calcule les débits lecture/écriture
- ✅ Nettoie les fichiers de test
- ✅ Sauvegarde les résultats

**Durée :** Selon `io_test_duration` (défaut: 5 minutes)

### Exemples d'Utilisation Avancée

#### Exécuter sur un Serveur Spécifique

```bash
ansible-playbook -i inventory.ini run_cpu_stress.yml --limit ibmi-prod.example.com
```

#### Surcharger les Variables

```bash
# Test CPU intensif sur 8 cœurs pendant 10 minutes
ansible-playbook -i inventory.ini run_cpu_stress.yml \
  --extra-vars "cpu_cores=8 cpu_intensity=extreme cpu_test_duration=600"

# Test I/O avec 4 processus et fichiers de 200 MB
ansible-playbook -i inventory.ini run_io_stress.yml \
  --extra-vars "io_processes=4 io_file_size_mb=200"
```

#### Mode Verbeux pour Débogage

```bash
ansible-playbook -i inventory.ini deploy_stress_tools.yml -vvv
```

#### Exécuter Uniquement Certaines Étapes (Tags)

```bash
# Vérifier uniquement les prérequis
ansible-playbook -i inventory.ini deploy_stress_tools.yml --tags check

# Exécuter uniquement le test sans collecte baseline
ansible-playbook -i inventory.ini run_cpu_stress.yml --tags execute

# Voir uniquement le résumé
ansible-playbook -i inventory.ini run_cpu_stress.yml --tags summary
```

## 📊 Résultats et Métriques

### Emplacement des Résultats

Les résultats sont sauvegardés dans deux emplacements :

**Sur le serveur IBM i :**
```
/tmp/ibmi_stress_tests/
├── results/
│   ├── cpu_stress_ibmi-prod_20241216T143000.json
│   └── io_stress_ibmi-prod_20241216T144500.json
└── logs/
    ├── cpu_stress_ibmi-prod_20241216T143000.log
    └── io_stress_ibmi-prod_20241216T144500.log
```

**Localement (sur le serveur Ansible) :**
```
playbooks/stress_tests/results/
├── cpu_stress_ibmi-prod_20241216T143000.json
├── cpu_stress_ibmi-prod_20241216T143000.log
├── io_stress_ibmi-prod_20241216T144500.json
└── io_stress_ibmi-prod_20241216T144500.log
```

### Format des Résultats

Les fichiers JSON contiennent :

**Pour les tests CPU :**
```json
{
  "hostname": "ibmi-prod.example.com",
  "test_type": "cpu_stress",
  "timestamp": "2024-12-16T14:30:00Z",
  "parameters": {
    "duration": 300,
    "cores": 4,
    "intensity": "high"
  },
  "baseline_metrics": {
    "cpu_percent_total": 15.2,
    "load_average": [1.5, 1.3, 1.2]
  },
  "post_test_metrics": {
    "cpu_percent_total": 85.7,
    "load_average": [4.2, 3.8, 2.5]
  },
  "success": true
}
```

**Pour les tests I/O :**
```json
{
  "hostname": "ibmi-prod.example.com",
  "test_type": "io_stress",
  "timestamp": "2024-12-16T14:45:00Z",
  "parameters": {
    "duration": 300,
    "processes": 2,
    "file_size_mb": 100,
    "operation": "mixed"
  },
  "io_statistics": {
    "bytes_read": 10737418240,
    "bytes_written": 10737418240,
    "read_throughput_mbps": 68.5,
    "write_throughput_mbps": 68.5,
    "total_data_gb": 20.0
  },
  "success": true
}
```

## 🎯 Cas d'Usage : Validation Avant/Après Mise à Jour

### Scénario Complet

#### 1. Collecte Baseline (Avant Mise à Jour)

```bash
# Déployer les outils
ansible-playbook -i inventory.ini deploy_stress_tools.yml

# Exécuter les tests baseline
ansible-playbook -i inventory.ini run_cpu_stress.yml \
  --extra-vars "cpu_test_duration=600"

ansible-playbook -i inventory.ini run_io_stress.yml \
  --extra-vars "io_test_duration=600"

# Sauvegarder les résultats
cp results/cpu_stress_*.json results/baseline_cpu.json
cp results/io_stress_*.json results/baseline_io.json
```

#### 2. Appliquer la Mise à Jour

```bash
# Appliquer les PTFs ou effectuer l'upgrade
# (Utilisez vos playbooks de mise à jour existants)
```

#### 3. Tests de Validation (Après Mise à Jour)

```bash
# Exécuter les mêmes tests
ansible-playbook -i inventory.ini run_cpu_stress.yml \
  --extra-vars "cpu_test_duration=600"

ansible-playbook -i inventory.ini run_io_stress.yml \
  --extra-vars "io_test_duration=600"

# Sauvegarder les résultats
cp results/cpu_stress_*.json results/validation_cpu.json
cp results/io_stress_*.json results/validation_io.json
```

#### 4. Comparaison Manuelle (Pour l'instant)

```bash
# Comparer les fichiers JSON
diff results/baseline_cpu.json results/validation_cpu.json
diff results/baseline_io.json results/validation_io.json
```

**Note :** La Phase 2 inclura un playbook automatique de comparaison avec génération de rapport HTML.

## 🔍 Interprétation des Résultats

### Métriques CPU

| Métrique | Bon | Acceptable | Préoccupant |
|----------|-----|------------|-------------|
| CPU moyen pendant test | 80-95% | 60-80% | < 60% ou > 95% |
| Load average | < nb_cores | < nb_cores * 1.5 | > nb_cores * 2 |
| Augmentation post-MAJ | < 5% | 5-10% | > 10% |

### Métriques I/O

| Métrique | Bon | Acceptable | Préoccupant |
|----------|-----|------------|-------------|
| Débit lecture | > 100 MB/s | 50-100 MB/s | < 50 MB/s |
| Débit écriture | > 80 MB/s | 40-80 MB/s | < 40 MB/s |
| Dégradation post-MAJ | < 10% | 10-20% | > 20% |

**Note :** Ces valeurs sont indicatives et dépendent de votre matériel.

## 🛠️ Dépannage

### Problème : "Script not deployed"

**Solution :**
```bash
ansible-playbook -i inventory.ini deploy_stress_tools.yml
```

### Problème : "psutil not found"

**Solution :**
```bash
# Sur IBM i
ssh user@ibmi-host
pip3 install psutil
```

### Problème : "Permission denied"

**Solution :**
```bash
# Vérifier les permissions
ansible -i inventory.ini ibmi_stress_test -m shell \
  -a "ls -la /tmp/ibmi_stress_tests"

# Corriger si nécessaire
ansible -i inventory.ini ibmi_stress_test -m shell \
  -a "chmod -R 755 /tmp/ibmi_stress_tests"
```

### Problème : "Disk space full"

**Solution :**
```bash
# Vérifier l'espace disque
ansible -i inventory.ini ibmi_stress_test -m shell \
  -a "df -h /tmp"

# Nettoyer les anciens fichiers
ansible -i inventory.ini ibmi_stress_test -m shell \
  -a "rm -rf /tmp/ibmi_io_stress/*"
```

### Problème : Test trop lent ou système non responsive

**Solution :** Réduire l'intensité des tests
```bash
ansible-playbook -i inventory.ini run_cpu_stress.yml \
  --extra-vars "cpu_cores=2 cpu_intensity=medium cpu_test_duration=120"
```

## 📚 Variables Disponibles

Consultez `vars.yml` pour la liste complète. Principales variables :

### Tests CPU
- `cpu_test_duration`: Durée en secondes (défaut: 300)
- `cpu_cores`: Nombre de cœurs (défaut: 4)
- `cpu_intensity`: low, medium, high, extreme (défaut: high)

### Tests I/O
- `io_test_duration`: Durée en secondes (défaut: 300)
- `io_processes`: Nombre de processus (défaut: 2)
- `io_file_size_mb`: Taille fichiers en MB (défaut: 100)
- `io_operation`: read, write, mixed (défaut: mixed)

### Chemins
- `remote_test_dir`: Répertoire sur IBM i (défaut: /tmp/ibmi_stress_tests)
- `local_results_dir`: Répertoire local (défaut: ./results)

### Comportement
- `cleanup_after_test`: Nettoyer après test (défaut: true)
- `check_dependencies`: Vérifier dépendances (défaut: true)

## 🚀 Workflow Complet de Validation (Phase 2)

### Playbook Principal : `main_performance_validation.yml`

Ce playbook orchestre automatiquement tout le processus de validation de performance :

```bash
ansible-playbook -i inventory.ini main_performance_validation.yml
```

**Workflow en 5 phases :**

1. **Phase 1 - Collecte Baseline** : Capture l'état de performance avant mise à jour
2. **Phase 2 - Pause** : Temps pour appliquer les PTFs/mises à jour
3. **Phase 3 - Tests de Validation** : Exécute les tests après mise à jour
4. **Phase 4 - Comparaison** : Analyse les différences de performance
5. **Phase 5 - Rapport HTML** : Génère un rapport visuel professionnel

### Utilisation des Playbooks Avancés

#### 1. Monitoring Continu

Surveiller les performances en temps réel pendant les tests :

```bash
# Monitoring pendant 10 minutes
ansible-playbook -i inventory.ini run_monitoring.yml \
  --extra-vars "monitor_duration=600"

# Monitoring continu (arrêt manuel avec Ctrl+C)
ansible-playbook -i inventory.ini run_monitoring.yml
```

**Résultat :** Fichier JSONL avec métriques horodatées (CPU, mémoire, disque, réseau)

#### 2. Orchestrateur de Tests

Exécuter des scénarios prédéfinis combinant CPU + I/O + monitoring :

```bash
# Lister les scénarios disponibles
ansible-playbook -i inventory.ini run_orchestrator.yml --tags info

# Exécuter un scénario prédéfini
ansible-playbook -i inventory.ini run_orchestrator.yml \
  --extra-vars "orchestrator_scenario=demo_standard"

# Scénarios disponibles :
#   - demo_light      : Test léger (2 min)
#   - demo_standard   : Test standard (5 min)
#   - demo_intensive  : Test intensif (10 min)
#   - cpu_only        : CPU uniquement
#   - io_only         : I/O uniquement
#   - full_stress     : Stress complet (15 min)
```

#### 3. Collecte de Baseline

Capturer l'état de référence avant une mise à jour :

```bash
# Baseline avec nom personnalisé
ansible-playbook -i inventory.ini collect_baseline.yml \
  --extra-vars "baseline_name=before_ptf_SI12345"

# Baseline automatique avec horodatage
ansible-playbook -i inventory.ini collect_baseline.yml
```

**Contenu de la baseline :**
- Informations système (OS, CPU, mémoire)
- Métriques actuelles (CPU, mémoire, disque, réseau)
- Tests rapides de performance (30s CPU + 30s I/O)

#### 4. Comparaison des Résultats

Comparer deux baselines pour détecter les changements :

```bash
ansible-playbook -i inventory.ini compare_results.yml \
  --extra-vars "baseline_file=results/baseline_before.json validation_file=results/baseline_after.json"
```

**Analyse automatique :**
- ✅ Calcul des différences (absolues et pourcentages)
- ✅ Évaluation selon seuils configurables
- ✅ Génération de recommandations
- ✅ Statut global : OK / ATTENTION / DÉGRADÉ

### Workflow Complet Recommandé

#### Scénario : Validation PTF

```bash
# 1. Déployer les outils (une seule fois)
ansible-playbook -i inventory.ini deploy_stress_tools.yml

# 2. Workflow complet automatisé
ansible-playbook -i inventory.ini main_performance_validation.yml
```

**Le playbook va :**
1. Collecter la baseline automatiquement
2. Vous demander d'appliquer les PTFs
3. Exécuter les tests de validation
4. Comparer les résultats
5. Générer un rapport HTML professionnel

**Résultat :** Rapport HTML dans `reports/report_validation_YYYYMMDD_HHMMSS.html`

#### Scénario : Validation en Deux Temps

Si vous préférez contrôler chaque étape :

```bash
# Étape 1 : Avant la mise à jour
ansible-playbook -i inventory.ini collect_baseline.yml \
  --extra-vars "baseline_name=before_ptf_SI12345"

# Étape 2 : Appliquer les PTFs manuellement
# ... (vos commandes de mise à jour)

# Étape 3 : Après la mise à jour
ansible-playbook -i inventory.ini main_performance_validation.yml \
  --tags phase3,phase4,phase5 \
  --extra-vars "baseline_file=results/baseline_before_ptf_SI12345.json"
```

### Rapport HTML Généré

Le rapport HTML inclut :

📊 **Résumé Exécutif**
- Statut global avec code couleur
- Métriques clés (CPU, mémoire, disque)
- Changements en pourcentage

📈 **Comparaison Détaillée**
- Tableaux avant/après
- Calculs de différences
- Barres de progression visuelles

⚠️ **Recommandations**
- Alertes automatiques si dégradation
- Actions suggérées
- Seuils configurables

🖥️ **Informations Système**
- Configuration matérielle
- Version OS
- Dates de collecte

**Exemple de visualisation :**
```
open reports/report_validation_20241216_143000.html
```

### Configuration des Seuils d'Alerte

Dans `vars.yml`, ajustez les seuils selon vos besoins :

```yaml
performance_thresholds:
  cpu_degradation_warning: 10      # Alerte si CPU +10%
  cpu_degradation_critical: 20     # Critique si CPU +20%
  io_degradation_warning: 15       # Alerte si I/O +15%
  io_degradation_critical: 30      # Critique si I/O +30%
  memory_increase_warning: 20      # Alerte si mémoire +20%
  memory_increase_critical: 40     # Critique si mémoire +40%
```

### Scénarios d'Utilisation Avancés

#### 1. Tests Parallèles sur Plusieurs Serveurs

```bash
# Tester tous les serveurs du groupe en parallèle
ansible-playbook -i inventory.ini main_performance_validation.yml \
  --forks 5
```

#### 2. Tests Personnalisés

```bash
# CPU intensif + I/O léger
ansible-playbook -i inventory.ini run_cpu_stress.yml \
  --extra-vars "cpu_cores=8 cpu_intensity=extreme cpu_test_duration=600"

ansible-playbook -i inventory.ini run_io_stress.yml \
  --extra-vars "io_processes=1 io_file_size_mb=50 io_test_duration=300"
```

#### 3. Monitoring Pendant les Tests

Terminal 1 :
```bash
ansible-playbook -i inventory.ini run_monitoring.yml \
  --extra-vars "monitor_duration=900"
```

Terminal 2 :
```bash
ansible-playbook -i inventory.ini run_orchestrator.yml \
  --extra-vars "orchestrator_scenario=demo_intensive"
```

### Analyse des Métriques Collectées

Les fichiers JSONL de monitoring peuvent être analysés :

```bash
# Afficher toutes les métriques
cat results/metrics_*.jsonl | jq .

# Extraire uniquement les valeurs CPU
cat results/metrics_*.jsonl | jq '.cpu.percent'

# Calculer la moyenne CPU
cat results/metrics_*.jsonl | jq -s 'map(.cpu.percent) | add/length'

# Trouver le pic de mémoire
cat results/metrics_*.jsonl | jq -s 'map(.memory.percent) | max'
```

## 📞 Support

Pour toute question ou problème :

1. Vérifiez les logs : `playbooks/stress_tests/results/*.log`
2. Exécutez en mode verbeux : `-vvv`
3. Consultez la documentation IBM i
4. Contactez l'équipe IBM Tech Sales France

## 📄 Licence

Ces playbooks sont fournis à des fins de validation de performance. Utilisez-les de manière responsable et uniquement dans des environnements de test ou avec autorisation.

---

**Version :** 1.0 (Phase 1)  
**Date :** Décembre 2024  
**Auteur :** IBM Tech Sales France  
**Projet :** Ansible for IBM i - Tech Sales France