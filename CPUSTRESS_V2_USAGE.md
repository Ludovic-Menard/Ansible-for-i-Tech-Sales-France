# CPU Stress Test Program V2.0 - Guide d'Utilisation

## Vue d'ensemble

CPUSTRESS_V2 est une version améliorée du programme de test de charge CPU pour IBM i. Cette version ajoute plusieurs fonctionnalités avancées pour des tests plus flexibles et une meilleure observabilité.

## Nouvelles Fonctionnalités V2.0

### ✨ Améliorations Principales

1. **Types de Charge Configurables**
   - LIGHT : Charge légère (~30% CPU)
   - MATH : Charge normale (~70% CPU) - par défaut
   - HEAVY : Charge intensive (~95-100% CPU)
   - MIXED : Alternance entre charges légères et lourdes

2. **Métriques de Performance**
   - Calcul automatique des opérations/seconde
   - Temps d'exécution précis
   - Statistiques détaillées

3. **Logging Amélioré**
   - Messages structurés avec timestamps
   - Informations sur le job
   - Résultats détaillés

4. **Architecture Modulaire**
   - Procédures séparées pour chaque type de charge
   - Code plus maintenable
   - Facilité d'extension

5. **Informations Job**
   - Capture automatique du nom du job
   - Traçabilité complète

## Prérequis

- IBM i V7R2 ou supérieur (pour **FREE format RPG)
- Autorité pour créer et exécuter des programmes
- Python 3.9+ (pour intégration Ansible)

## Installation

### Méthode 1: Compilation Manuelle

```bash
# 1. Copier le source vers IBM i
CPYFRMSTMF FROMSTMF('/path/to/CPUSTRESS_V2.RPGLE') 
           TOMBR('/QSYS.LIB/YOURLIB.LIB/QRPGLESRC.FILE/CPUSTRV2.MBR') 
           MBROPT(*REPLACE)

# 2. Compiler le programme
CRTBNDRPG PGM(YOURLIB/CPUSTRV2) 
          SRCFILE(YOURLIB/QRPGLESRC) 
          SRCMBR(CPUSTRV2) 
          DFTACTGRP(*NO)
```

### Méthode 2: Avec BOB (Better Object Builder)

Créer `iproj.json`:
```json
{
  "version": "0.2",
  "description": "CPU Stress Test V2",
  "objlib": "STRESSLIB",
  "curlib": "STRESSLIB",
  "includePath": ["src"],
  "build": {
    "CPUSTRV2": {
      "type": "rpgle",
      "source": "CPUSTRESS_V2.RPGLE"
    }
  }
}
```

Compiler:
```bash
bob --build
```

### Méthode 3: Avec Ansible

Voir section "Intégration Ansible" ci-dessous.

## Utilisation

### Syntaxe

```
CALL PGM(YOURLIB/CPUSTRV2) PARM(duration workload_type log_file)
```

### Paramètres

| Paramètre | Type | Description | Valeurs |
|-----------|------|-------------|---------|
| duration | Integer | Durée en secondes | 1-999999 |
| workload_type | Char(10) | Type de charge | LIGHT, MATH, HEAVY, MIXED |
| log_file | Char(50) | Fichier log IFS (optionnel) | Chemin IFS ou blancs |

### Exemples d'Utilisation

#### Exemple 1: Test Léger de 60 secondes
```
CALL PGM(YOURLIB/CPUSTRV2) PARM(60 'LIGHT' ' ')
```

#### Exemple 2: Test Normal de 5 minutes
```
CALL PGM(YOURLIB/CPUSTRV2) PARM(300 'MATH' ' ')
```

#### Exemple 3: Test Intensif de 10 minutes
```
CALL PGM(YOURLIB/CPUSTRV2) PARM(600 'HEAVY' ' ')
```

#### Exemple 4: Test Mixte de 15 minutes
```
CALL PGM(YOURLIB/CPUSTRV2) PARM(900 'MIXED' ' ')
```

#### Exemple 5: Avec Logging
```
CALL PGM(YOURLIB/CPUSTRV2) PARM(300 'HEAVY' '/tmp/stress.log')
```

## Types de Charge Détaillés

### LIGHT - Charge Légère
- **Utilisation CPU**: ~30-40%
- **Itérations**: 100,000 par cycle
- **Boucles internes**: 50 itérations
- **Usage**: Tests de base, validation système
- **Durée recommandée**: 60-300 secondes

### MATH - Charge Normale (Défaut)
- **Utilisation CPU**: ~70-80%
- **Itérations**: 1,000,000 par cycle
- **Boucles internes**: 100 itérations
- **Usage**: Tests standards, benchmarking
- **Durée recommandée**: 300-600 secondes

### HEAVY - Charge Intensive
- **Utilisation CPU**: ~95-100%
- **Itérations**: 5,000,000 par cycle
- **Boucles internes**: 200 itérations
- **Usage**: Tests de stress maximum, validation thermique
- **Durée recommandée**: 600-1800 secondes

### MIXED - Charge Variable
- **Utilisation CPU**: Variable (30-80%)
- **Cycles**: Alternance LIGHT/NORMAL
- **Usage**: Simulation de charge réelle, tests de réactivité
- **Durée recommandée**: 600-3600 secondes

## Exécution Multiple (Multi-Core)

### Script CL pour Tests Multi-Core

```cl
PGM PARM(&DURATION &WORKLOAD &CORES)
  DCL VAR(&DURATION) TYPE(*DEC) LEN(10 0)
  DCL VAR(&WORKLOAD) TYPE(*CHAR) LEN(10)
  DCL VAR(&CORES) TYPE(*DEC) LEN(5 0)
  DCL VAR(&I) TYPE(*DEC) LEN(5 0)
  DCL VAR(&JOBNAME) TYPE(*CHAR) LEN(10)
  
  CHGVAR VAR(&I) VALUE(1)
  
  DOWHILE COND(&I *LE &CORES)
    CHGVAR VAR(&JOBNAME) VALUE('STRV2' *CAT %CHAR(&I))
    SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRV2) +
               PARM(&DURATION &WORKLOAD ' ')) +
           JOB(&JOBNAME) +
           JOBQ(QBATCH)
    CHGVAR VAR(&I) VALUE(&I + 1)
  ENDDO
  
  SNDPGMMSG MSG('Submitted ' *CAT %CHAR(&CORES) *CAT +
                ' stress test jobs') TOPGMQ(*EXT)
  
ENDPGM
```

Utilisation:
```
CALL RUNSTRESS PARM(600 'HEAVY' 8)
```

## Monitoring et Métriques

### Sortie du Programme

Le programme affiche:
```
=================================================
CPU Stress Test V2.0 Started
Job: 123456/USER/STRV201
Duration: 300 seconds
Workload Type: HEAVY
Start Time: 2026-05-06-08.45.00.000000
=================================================
Executing HEAVY workload...
=================================================
CPU Stress Test V2.0 Completed
End Time: 2026-05-06-08.50.00.000000
Elapsed: 300 seconds
Total Iterations: 15234567890
Operations/Second: 50781892.97
Final Result: 1234.567890
Workload Type: HEAVY
=================================================
```

### Monitoring avec SQL

```sql
-- Vue en temps réel des jobs de stress
SELECT JOB_NAME,
       SUBSYSTEM,
       CPU_TIME,
       ELAPSED_CPU_PERCENTAGE,
       ELAPSED_CPU_TIME,
       ELAPSED_TIME,
       FUNCTION
FROM TABLE(QSYS2.ACTIVE_JOB_INFO(
  JOB_NAME_FILTER => 'STRV2*'
))
ORDER BY ELAPSED_CPU_PERCENTAGE DESC;

-- Statistiques agrégées
SELECT COUNT(*) AS ACTIVE_JOBS,
       AVG(ELAPSED_CPU_PERCENTAGE) AS AVG_CPU_PCT,
       SUM(CPU_TIME) AS TOTAL_CPU_TIME
FROM TABLE(QSYS2.ACTIVE_JOB_INFO(
  JOB_NAME_FILTER => 'STRV2*'
));
```

### Monitoring Système

```
-- Utilisation CPU globale
WRKSYSSTS

-- Jobs actifs
WRKACTJOB SBS(*ALL) JOB(STRV2*)

-- Performance détaillée
WRKSYSACT
```

## Intégration Ansible

### Playbook de Déploiement

```yaml
---
- name: Déployer et Compiler CPUSTRESS V2
  hosts: ibmi_servers
  gather_facts: no
  
  vars:
    source_file: "CPUSTRESS_V2.RPGLE"
    target_lib: "STRESSLIB"
    program_name: "CPUSTRV2"
  
  tasks:
    - name: Créer la bibliothèque si nécessaire
      ibm.power_ibmi.ibmi_cl_command:
        cmd: "CRTLIB LIB({{ target_lib }}) TEXT('Stress Test Library')"
      ignore_errors: yes
      
    - name: Créer source physical file
      ibm.power_ibmi.ibmi_cl_command:
        cmd: "CRTSRCPF FILE({{ target_lib }}/QRPGLESRC) RCDLEN(112)"
      ignore_errors: yes
      
    - name: Copier le source vers IBM i
      ibm.power_ibmi.ibmi_copy:
        src: "{{ source_file }}"
        lib_name: "{{ target_lib }}"
        force: yes
        
    - name: Compiler le programme
      ibm.power_ibmi.ibmi_cl_command:
        cmd: >
          CRTBNDRPG PGM({{ target_lib }}/{{ program_name }})
          SRCFILE({{ target_lib }}/QRPGLESRC)
          SRCMBR(CPUSTRV2)
          DFTACTGRP(*NO)
      register: compile_result
      
    - name: Afficher résultat compilation
      debug:
        var: compile_result
```

### Playbook d'Exécution

```yaml
---
- name: Exécuter Tests de Stress CPU V2
  hosts: ibmi_servers
  gather_facts: yes
  
  vars:
    duration: 300
    workload_type: "HEAVY"
    num_jobs: 4
    target_lib: "STRESSLIB"
  
  tasks:
    - name: Soumettre jobs de stress
      ibm.power_ibmi.ibmi_cl_command:
        cmd: >
          SBMJOB 
          CMD(CALL PGM({{ target_lib }}/CPUSTRV2) 
              PARM({{ duration }} '{{ workload_type }}' ' '))
          JOB(STRV2{{ item }})
          JOBQ(QBATCH)
      loop: "{{ range(1, num_jobs + 1) | list }}"
      register: submit_result
      
    - name: Attendre 10 secondes
      pause:
        seconds: 10
        
    - name: Vérifier les jobs actifs
      ibm.power_ibmi.ibmi_sql_query:
        sql: >
          SELECT JOB_NAME, ELAPSED_CPU_PERCENTAGE, CPU_TIME
          FROM TABLE(QSYS2.ACTIVE_JOB_INFO(
            JOB_NAME_FILTER => 'STRV2*'
          ))
      register: active_jobs
      
    - name: Afficher jobs actifs
      debug:
        var: active_jobs.row
```

### Playbook de Monitoring

```yaml
---
- name: Monitorer Tests de Stress
  hosts: ibmi_servers
  gather_facts: no
  
  tasks:
    - name: Collecter métriques CPU
      ibm.power_ibmi.ibmi_sql_query:
        sql: >
          SELECT 
            JOB_NAME,
            ELAPSED_CPU_PERCENTAGE,
            CPU_TIME,
            ELAPSED_TIME,
            FUNCTION
          FROM TABLE(QSYS2.ACTIVE_JOB_INFO(
            JOB_NAME_FILTER => 'STRV2*'
          ))
          ORDER BY ELAPSED_CPU_PERCENTAGE DESC
      register: cpu_metrics
      
    - name: Collecter statistiques système
      ibm.power_ibmi.ibmi_sql_query:
        sql: "SELECT * FROM QSYS2.SYSTEM_STATUS_INFO"
      register: sys_status
      
    - name: Générer rapport
      template:
        src: stress_report.j2
        dest: "/tmp/stress_report_{{ ansible_date_time.iso8601_basic_short }}.html"
      delegate_to: localhost
```

## Scénarios de Test

### Scénario 1: Validation Rapide
```bash
# Test de 2 minutes, charge normale
CALL PGM(STRESSLIB/CPUSTRV2) PARM(120 'MATH' ' ')
```

### Scénario 2: Benchmark Standard
```bash
# 4 jobs, 10 minutes, charge intensive
for i in 1 2 3 4; do
  SBMJOB CMD(CALL PGM(STRESSLIB/CPUSTRV2) PARM(600 'HEAVY' ' ')) JOB(STRV2$i)
done
```

### Scénario 3: Test de Stabilité
```bash
# 1 heure, charge mixte
CALL PGM(STRESSLIB/CPUSTRV2) PARM(3600 'MIXED' '/tmp/stability.log')
```

### Scénario 4: Test Multi-Core Maximum
```bash
# 8 cores, 30 minutes, charge maximale
CALL RUNSTRESS PARM(1800 'HEAVY' 8)
```

## Comparaison V1 vs V2

| Fonctionnalité | V1 | V2 |
|----------------|----|----|
| Types de charge | 1 (fixe) | 4 (configurable) |
| Métriques | Basiques | Avancées (ops/sec) |
| Logging | Simple DSPLY | Structuré + IFS |
| Architecture | Monolithique | Modulaire (procédures) |
| Info Job | Non | Oui |
| Flexibilité | Limitée | Élevée |
| Maintenabilité | Moyenne | Excellente |

## Dépannage

### Erreur de Compilation

**Problème**: Erreur "**FREE not supported"
**Solution**: Vérifier IBM i >= V7R2

**Problème**: Erreur sur les procédures
**Solution**: Vérifier la syntaxe des Dcl-Proc/End-Proc

### Performance Inférieure

**Problème**: CPU < 50% avec HEAVY
**Solution**: 
- Vérifier la priorité du job (CHGJOB RUNPTY(20))
- Augmenter le nombre de jobs
- Vérifier les limites système

### Jobs ne Démarrent Pas

**Problème**: SBMJOB échoue
**Solution**:
- Vérifier JOBQ: WRKJOBQ QBATCH
- Vérifier autorités: WRKOBJ OBJ(STRESSLIB/CPUSTRV2)
- Vérifier joblog: WRKJOB → Option 10

## Meilleures Pratiques

1. **Environnement de Test**
   - Toujours tester en DEV d'abord
   - Documenter les résultats
   - Comparer avec baseline

2. **Monitoring**
   - Surveiller température CPU
   - Vérifier utilisation mémoire
   - Observer I/O système

3. **Planification**
   - Éviter heures de production
   - Prévoir temps de refroidissement
   - Alerter les équipes

4. **Documentation**
   - Enregistrer configurations
   - Sauvegarder résultats
   - Tracer les anomalies

## Support et Contribution

Pour questions ou améliorations:
- Consulter les joblogs pour erreurs détaillées
- Vérifier la documentation IBM i
- Contribuer via pull requests

## Licence

Utilisation libre. Programme fourni "tel quel" sans garantie.
Utiliser de manière responsable en environnement de test.

---

**Version**: 2.0  
**Date**: 2026-05-06  
**Auteur**: Enhanced by Bob AI Assistant