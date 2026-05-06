# CPUSTRESS V2 - Playbooks Ansible

## Vue d'ensemble

Ce répertoire contient les playbooks Ansible pour déployer, exécuter et monitorer le programme de stress test CPU V2 sur les serveurs IBM i.

## Structure des Fichiers

```
playbooks/stress_tests/
├── deploy_cpustress_v2.yml      # Déploiement et compilation
├── run_cpustress_v2.yml         # Exécution des tests
├── monitor_cpustress_v2.yml     # Monitoring en temps réel
└── README_CPUSTRESS_V2.md       # Cette documentation
```

## Prérequis

### Sur le Serveur de Contrôle Ansible

- Ansible Core 2.15+
- Collection `ibm.power_ibmi` installée
- Python 3.9+
- Accès SSH aux serveurs IBM i cibles

### Sur les Serveurs IBM i Cibles

- IBM i V7R2 ou supérieur
- SSH activé et configuré
- Python 3.9+ installé
- Autorités appropriées pour créer bibliothèques et programmes

## Installation Rapide

### 1. Déployer le Programme

```bash
# Déployer sur tous les serveurs
ansible-playbook playbooks/stress_tests/deploy_cpustress_v2.yml

# Déployer sur un serveur spécifique
ansible-playbook playbooks/stress_tests/deploy_cpustress_v2.yml -l ibmi-prod-01

# Avec variables personnalisées
ansible-playbook playbooks/stress_tests/deploy_cpustress_v2.yml \
  -e "target_lib=MYLIB" \
  -e "program_name=MYSTRESS"
```

### 2. Exécuter un Test

```bash
# Test standard (5 minutes, charge normale, 4 jobs)
ansible-playbook playbooks/stress_tests/run_cpustress_v2.yml

# Test personnalisé
ansible-playbook playbooks/stress_tests/run_cpustress_v2.yml \
  -e "duration=600" \
  -e "workload_type=HEAVY" \
  -e "num_jobs=8"
```

### 3. Monitorer les Tests

```bash
# Monitoring ponctuel
ansible-playbook playbooks/stress_tests/monitor_cpustress_v2.yml

# Monitoring avec rapport
ansible-playbook playbooks/stress_tests/monitor_cpustress_v2.yml \
  -e "report_file=/tmp/my_report.html"
```

## Playbooks Détaillés

### deploy_cpustress_v2.yml

**Objectif**: Déployer et compiler CPUSTRESS V2 sur les serveurs IBM i

**Variables**:
- `source_file`: Chemin du fichier source RPG (défaut: `../../CPUSTRESS_V2.RPGLE`)
- `target_lib`: Bibliothèque cible (défaut: `STRESSLIB`)
- `program_name`: Nom du programme (défaut: `CPUSTRV2`)
- `member_name`: Nom du membre source (défaut: `CPUSTRV2`)

**Tâches**:
1. Vérification/création de la bibliothèque
2. Création du source physical file
3. Copie du source vers IBM i
4. Compilation du programme
5. Vérification du programme compilé

**Exemple**:
```bash
ansible-playbook deploy_cpustress_v2.yml \
  -e "target_lib=PRODLIB" \
  -e "program_name=CPUSTRESS" \
  -l production_servers
```

### run_cpustress_v2.yml

**Objectif**: Exécuter des tests de stress CPU avec configuration flexible

**Variables**:
- `duration`: Durée en secondes (défaut: `300`)
- `workload_type`: Type de charge - `LIGHT`, `MATH`, `HEAVY`, `MIXED` (défaut: `MATH`)
- `num_jobs`: Nombre de jobs parallèles (défaut: `4`)
- `job_prefix`: Préfixe des noms de jobs (défaut: `STRV2`)
- `log_file`: Fichier log IFS (défaut: ` ` - pas de log)

**Tâches**:
1. Vérification du programme
2. Collecte des métriques de base
3. Soumission des jobs de stress
4. Vérification des jobs actifs
5. Monitoring initial

**Exemples**:

```bash
# Test léger de 2 minutes
ansible-playbook run_cpustress_v2.yml \
  -e "duration=120" \
  -e "workload_type=LIGHT" \
  -e "num_jobs=2"

# Test intensif de 30 minutes sur 8 cores
ansible-playbook run_cpustress_v2.yml \
  -e "duration=1800" \
  -e "workload_type=HEAVY" \
  -e "num_jobs=8"

# Test mixte avec logging
ansible-playbook run_cpustress_v2.yml \
  -e "duration=600" \
  -e "workload_type=MIXED" \
  -e "num_jobs=4" \
  -e "log_file=/tmp/stress.log"
```

### monitor_cpustress_v2.yml

**Objectif**: Surveiller les tests en cours et collecter les métriques

**Variables**:
- `job_prefix`: Préfixe des jobs à monitorer (défaut: `STRV2`)
- `monitoring_interval`: Intervalle entre checks (défaut: `10` secondes)
- `report_file`: Fichier rapport HTML (défaut: `/tmp/stress_report_<timestamp>.html`)

**Métriques Collectées**:
- Utilisation CPU système
- Capacité CPU
- Utilisation ASP
- Jobs actifs
- Utilisation mémoire
- Statistiques par job (CPU%, temps, I/O)

**Tâches**:
1. Collecte métriques système
2. Liste des jobs de stress actifs
3. Calcul statistiques agrégées
4. Vérification jobs terminés
5. Génération rapport HTML

**Exemples**:

```bash
# Monitoring simple
ansible-playbook monitor_cpustress_v2.yml

# Monitoring avec rapport personnalisé
ansible-playbook monitor_cpustress_v2.yml \
  -e "report_file=/reports/stress_$(date +%Y%m%d_%H%M%S).html"

# Monitoring de jobs spécifiques
ansible-playbook monitor_cpustress_v2.yml \
  -e "job_prefix=MYTEST"
```

## Scénarios d'Utilisation

### Scénario 1: Validation Rapide

Test rapide pour vérifier que tout fonctionne:

```bash
# 1. Déployer
ansible-playbook deploy_cpustress_v2.yml -l test_server

# 2. Test de 2 minutes
ansible-playbook run_cpustress_v2.yml \
  -e "duration=120" \
  -e "workload_type=LIGHT" \
  -e "num_jobs=1" \
  -l test_server

# 3. Vérifier
ansible-playbook monitor_cpustress_v2.yml -l test_server
```

### Scénario 2: Benchmark Standard

Test standard pour benchmarking:

```bash
# 1. Déployer sur tous les serveurs
ansible-playbook deploy_cpustress_v2.yml

# 2. Test de 10 minutes, charge normale, 4 cores
ansible-playbook run_cpustress_v2.yml \
  -e "duration=600" \
  -e "workload_type=MATH" \
  -e "num_jobs=4"

# 3. Monitorer pendant le test
ansible-playbook monitor_cpustress_v2.yml

# 4. Attendre la fin et collecter résultats
sleep 600
ansible-playbook monitor_cpustress_v2.yml
```

### Scénario 3: Test de Stress Maximum

Test intensif pour validation de capacité:

```bash
# 1. Déployer
ansible-playbook deploy_cpustress_v2.yml -l production_servers

# 2. Test de 30 minutes, charge maximale, 8 cores
ansible-playbook run_cpustress_v2.yml \
  -e "duration=1800" \
  -e "workload_type=HEAVY" \
  -e "num_jobs=8" \
  -l production_servers

# 3. Monitoring continu (dans un autre terminal)
watch -n 30 "ansible-playbook monitor_cpustress_v2.yml -l production_servers"
```

### Scénario 4: Test de Stabilité

Test longue durée avec charge variable:

```bash
# Test de 2 heures avec charge mixte
ansible-playbook run_cpustress_v2.yml \
  -e "duration=7200" \
  -e "workload_type=MIXED" \
  -e "num_jobs=6" \
  -e "log_file=/tmp/stability_test.log"
```

### Scénario 5: Comparaison Avant/Après Migration

```bash
# Avant migration
ansible-playbook run_cpustress_v2.yml \
  -e "duration=600" \
  -e "workload_type=MATH" \
  -e "num_jobs=4" \
  -l old_server

ansible-playbook monitor_cpustress_v2.yml \
  -e "report_file=/reports/before_migration.html" \
  -l old_server

# Après migration
ansible-playbook deploy_cpustress_v2.yml -l new_server

ansible-playbook run_cpustress_v2.yml \
  -e "duration=600" \
  -e "workload_type=MATH" \
  -e "num_jobs=4" \
  -l new_server

ansible-playbook monitor_cpustress_v2.yml \
  -e "report_file=/reports/after_migration.html" \
  -l new_server
```

## Intégration avec BOB

Pour utiliser BOB (Better Object Builder) au lieu de la compilation directe:

1. Créer `iproj.json` sur le serveur IBM i:
```json
{
  "version": "0.2",
  "description": "CPU Stress Test V2",
  "objlib": "STRESSLIB",
  "build": {
    "CPUSTRV2": {
      "type": "rpgle",
      "source": "CPUSTRESS_V2.RPGLE"
    }
  }
}
```

2. Modifier le playbook pour utiliser BOB:
```yaml
- name: Compiler avec BOB
  ansible.builtin.shell: |
    cd /home/project
    bob --build
  args:
    executable: /QOpenSys/pkgs/bin/bash
```

## Dépannage

### Problème: Programme non trouvé

**Erreur**: `Program STRESSLIB/CPUSTRV2 not found`

**Solution**:
```bash
# Vérifier le déploiement
ansible-playbook deploy_cpustress_v2.yml -v

# Vérifier sur le serveur
ansible ibmi_servers -m ibm.power_ibmi.ibmi_cl_command \
  -a "cmd='WRKOBJ OBJ(STRESSLIB/CPUSTRV2) OBJTYPE(*PGM)'"
```

### Problème: Jobs ne démarrent pas

**Erreur**: Jobs soumis mais pas actifs

**Solution**:
```bash
# Vérifier la job queue
ansible ibmi_servers -m ibm.power_ibmi.ibmi_cl_command \
  -a "cmd='WRKJOBQ JOBQ(QBATCH)'"

# Vérifier les joblogs
ansible ibmi_servers -m ibm.power_ibmi.ibmi_sql_query \
  -a "sql='SELECT * FROM TABLE(QSYS2.JOBLOG_INFO(\"STRV2*\"))'"
```

### Problème: CPU faible

**Symptôme**: CPU < 50% avec workload HEAVY

**Solution**:
- Augmenter le nombre de jobs
- Vérifier la priorité des jobs
- Vérifier les limites système

```bash
# Changer la priorité
ansible ibmi_servers -m ibm.power_ibmi.ibmi_cl_command \
  -a "cmd='CHGJOB JOB(STRV2*) RUNPTY(20)'"
```

## Meilleures Pratiques

1. **Toujours tester en DEV d'abord**
   ```bash
   ansible-playbook deploy_cpustress_v2.yml -l dev_servers
   ```

2. **Utiliser des tags pour exécution sélective**
   ```yaml
   tasks:
     - name: Tâche importante
       tags: [deploy, critical]
   ```

3. **Sauvegarder les rapports**
   ```bash
   ansible-playbook monitor_cpustress_v2.yml \
     -e "report_file=/archives/stress_$(date +%Y%m%d).html"
   ```

4. **Documenter les tests**
   - Enregistrer la configuration
   - Sauvegarder les résultats
   - Noter les observations

5. **Nettoyer après les tests**
   ```bash
   # Arrêter tous les jobs de stress
   ansible ibmi_servers -m ibm.power_ibmi.ibmi_cl_command \
     -a "cmd='ENDJOB JOB(STRV2*) OPTION(*IMMED)'"
   ```

## Support

Pour questions ou problèmes:
1. Vérifier les joblogs sur IBM i
2. Exécuter les playbooks en mode verbose (`-vvv`)
3. Consulter la documentation IBM i Ansible
4. Vérifier les logs Ansible

## Ressources

- [Documentation CPUSTRESS V2](../../CPUSTRESS_V2_USAGE.md)
- [Collection IBM Power IBMi](https://galaxy.ansible.com/ibm/power_ibmi)
- [Documentation Ansible](https://docs.ansible.com/)
- [IBM i Open Source](https://ibmi-oss-docs.readthedocs.io/)

---

**Version**: 1.0  
**Date**: 2026-05-06  
**Auteur**: Enhanced by Bob AI Assistant