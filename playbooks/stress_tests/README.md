# 🚀 Playbooks Ansible - Tests de Stress IBM i

## 📋 Vue d'ensemble

Suite de playbooks Ansible pour automatiser les tests de performance sur les systèmes IBM i. Ces playbooks permettent de déployer et exécuter des tests de stress CPU et I/O, avec collecte automatique des métriques et génération de rapports.

**Objectif principal :** Valider les performances des systèmes IBM i avant et après des mises à jour (PTFs, upgrades OS, etc.).

## 📦 Contenu

### Phase 1 - Playbooks de Base (Disponibles)

| Playbook | Description | Usage |
|----------|-------------|-------|
| `deploy_stress_tools.yml` | Déploie les scripts Python sur IBM i | Première étape obligatoire |
| `run_cpu_stress.yml` | Exécute des tests de stress CPU | Tests de charge processeur |
| `run_io_stress.yml` | Exécute des tests de stress I/O | Tests de charge disque |

### Phase 2 - Fonctionnalités Avancées (À venir)

- Orchestrateur de tests avec scénarios prédéfinis
- Monitoring continu des performances
- Collecte de baseline avant mise à jour
- Comparaison automatique avant/après
- Génération de rapports HTML

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

## 🔜 Prochaines Fonctionnalités (Phase 2)

- ✨ Playbook orchestrateur avec scénarios prédéfinis
- 📊 Monitoring continu avec graphiques temps réel
- 📈 Comparaison automatique avant/après avec rapport HTML
- 📧 Envoi automatique de rapports par email
- 🎨 Génération de graphiques de performance
- 🔔 Alertes sur dégradation de performance

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