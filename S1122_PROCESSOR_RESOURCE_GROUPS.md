# Processor Resource Groups sur IBM Power S1122

## Vue d'ensemble

Les **Processor Resource Groups** (PRG) sont une fonctionnalité matérielle des serveurs IBM Power qui permet de partitionner physiquement les processeurs en groupes distincts pour optimiser les performances et l'isolation des workloads.

### Système S1122 - Caractéristiques

- **Modèle**: IBM Power S1022s/S1022/S1024 (famille Scale Out)
- **Processeur**: Power11
- **Configuration typique**: 4 à 8 cœurs
- **Sockets**: 1 socket (single-socket system)
- **SMT**: SMT8 (8 threads par cœur)
- **Mémoire**: 16 GB à 256 GB

---

## Qu'est-ce qu'un Processor Resource Group ?

Un **Processor Resource Group (PRG)** est un regroupement logique de cœurs de processeur au niveau du firmware qui permet de :

- **Isoler les workloads** : Séparer physiquement les charges de travail critiques
- **Optimiser les performances** : Réduire la contention sur les caches L2/L3
- **Améliorer la prévisibilité** : Garantir des performances constantes
- **Faciliter le licensing** : Gérer les licences logicielles par groupe de processeurs

---

## Architecture des PRG sur S1122

### Configuration Single-Socket (S1122)

```
┌─────────────────────────────────────────────────────────┐
│              IBM Power S1122 - Single Socket            │
│                    Power11 Processor                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Processor Resource Group 0 (PRG0)        │  │
│  │              (Default Group)                      │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  Core 0  │  Core 1  │  Core 2  │  Core 3         │  │
│  │  SMT8    │  SMT8    │  SMT8    │  SMT8           │  │
│  │  (8 thr) │  (8 thr) │  (8 thr) │  (8 thr)        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Processor Resource Group 1 (PRG1)        │  │
│  │           (Optional - if configured)              │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  Core 4  │  Core 5  │  Core 6  │  Core 7         │  │
│  │  SMT8    │  SMT8    │  SMT8    │  SMT8           │  │
│  │  (8 thr) │  (8 thr) │  (8 thr) │  (8 thr)        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Shared L3 Cache per Group                              │
│  Memory Controllers                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration des PRG sur S1122

### Configuration par défaut

Sur un S1122 avec 8 cœurs, la configuration par défaut est :

```
PRG 0 (Default): Tous les 8 cœurs
- Cœurs: 0-7
- Threads: 64 (8 cœurs × 8 threads SMT8)
- Usage: Toutes les partitions LPAR
```

### Configuration recommandée pour isolation

Pour un environnement avec isolation des workloads :

```
PRG 0 (Production):
- Cœurs: 0-3 (4 cœurs)
- Threads: 32 (4 × 8 SMT8)
- Usage: Partitions de production critiques
- Priorité: Haute

PRG 1 (Non-Production):
- Cœurs: 4-7 (4 cœurs)
- Threads: 32 (4 × 8 SMT8)
- Usage: Développement, test, batch
- Priorité: Normale
```

---

## Configuration via HMC (Hardware Management Console)

### Étape 1: Accéder à la configuration du système

1. Se connecter à la HMC
2. Naviguer vers : **Systems Management** → **Servers** → [Votre S1122]
3. Sélectionner : **Configuration** → **Processor Resource Groups**

### Étape 2: Créer un nouveau PRG

```
HMC GUI:
1. Clic droit sur le système → Properties
2. Onglet "Processor Resource Groups"
3. Cliquer sur "Add"

Configuration PRG1:
- Name: PRG_PRODUCTION
- Processor Cores: 0,1,2,3
- Mode: Dedicated
- Description: Production workloads
```

### Étape 3: Assigner des LPARs aux PRG

```
HMC GUI:
1. Sélectionner la LPAR
2. Properties → Processor
3. Processor Resource Group: PRG_PRODUCTION
4. Activer
```

---

## Configuration via HMC CLI

### Créer un PRG

```bash
# Lister les PRG existants
lssyscfg -r sys -m <system_name> -F name,proc_resource_groups

# Créer un nouveau PRG
chsyscfg -r sys -m <system_name> \
  -i "proc_resource_group_name=PRG_PRODUCTION,\
      proc_resource_group_cores=0-3"

# Créer un second PRG
chsyscfg -r sys -m <system_name> \
  -i "proc_resource_group_name=PRG_NONPROD,\
      proc_resource_group_cores=4-7"
```

### Assigner une LPAR à un PRG

```bash
# Modifier une LPAR pour utiliser un PRG spécifique
chsyscfg -r lpar -m <system_name> \
  -i "name=<lpar_name>,\
      proc_resource_group=PRG_PRODUCTION"

# Vérifier l'assignation
lssyscfg -r lpar -m <system_name> \
  --filter "lpar_names=<lpar_name>" \
  -F name,proc_resource_group
```

### Afficher la configuration des PRG

```bash
# Détails complets des PRG
lshwres -r proc -m <system_name> --level sys \
  -F proc_resource_group_name,proc_resource_group_cores

# Afficher les LPARs par PRG
lshwres -r proc -m <system_name> --level lpar \
  -F lpar_name,proc_resource_group
```

---

## Scénarios de configuration pour S1122

### Scénario 1: Production isolée (4+4)

**Objectif**: Isoler complètement la production du reste

```
┌─────────────────────────────────────────┐
│ PRG 0 - PRODUCTION (Cœurs 0-3)         │
├─────────────────────────────────────────┤
│ LPAR: PROD_IBMI                         │
│ - 3.5 cœurs dédiés                      │
│ - 28 GB RAM                             │
│ - Priorité: 255                         │
│ - Applications critiques                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRG 1 - NON-PROD (Cœurs 4-7)           │
├─────────────────────────────────────────┤
│ LPAR: DEV_IBMI (2.0 cœurs)             │
│ LPAR: TEST_IBMI (1.5 cœurs)            │
│ LPAR: VIOS (0.5 cœurs)                 │
│ - Mode partagé                          │
│ - 20 GB RAM total                       │
└─────────────────────────────────────────┘
```

**Configuration HMC**:
```bash
# PRG Production
chsyscfg -r sys -m S1122_PROD \
  -i "proc_resource_group_name=PRG_PRODUCTION,\
      proc_resource_group_cores=0-3"

# PRG Non-Production
chsyscfg -r sys -m S1122_PROD \
  -i "proc_resource_group_name=PRG_NONPROD,\
      proc_resource_group_cores=4-7"

# Assigner LPAR Production
chsyscfg -r lpar -m S1122_PROD \
  -i "name=PROD_IBMI,\
      proc_resource_group=PRG_PRODUCTION,\
      desired_procs=4,\
      min_procs=3,\
      max_procs=4,\
      proc_mode=ded"
```

### Scénario 2: Multi-tenant (2+3+3)

**Objectif**: Trois environnements clients isolés

```
┌─────────────────────────────────────────┐
│ PRG 0 - CLIENT_A (Cœurs 0-1)           │
│ - 2 cœurs dédiés                        │
│ - 16 GB RAM                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRG 1 - CLIENT_B (Cœurs 2-4)           │
│ - 3 cœurs dédiés                        │
│ - 24 GB RAM                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRG 2 - CLIENT_C (Cœurs 5-7)           │
│ - 3 cœurs dédiés                        │
│ - 24 GB RAM                             │
└─────────────────────────────────────────┘
```

### Scénario 3: Licensing optimization (6+2)

**Objectif**: Minimiser les coûts de licence logicielle

```
┌─────────────────────────────────────────┐
│ PRG 0 - LICENSED (Cœurs 0-5)           │
│ - Applications avec licence par cœur    │
│ - Oracle, SAP, etc.                     │
│ - 6 cœurs = licence pour 6 cœurs        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRG 1 - UNLICENSED (Cœurs 6-7)         │
│ - Applications open source              │
│ - Outils de monitoring                  │
│ - Pas de coût de licence                │
└─────────────────────────────────────────┘
```

---

## Avantages des PRG sur S1122

### 1. Isolation des performances

- **Cache L3 dédié** : Chaque PRG a accès à son propre cache L3
- **Pas de contention** : Les workloads ne se disputent pas les ressources
- **Performances prévisibles** : Latence constante

### 2. Optimisation des coûts

- **Licensing par PRG** : Payer uniquement pour les cœurs utilisés
- **Exemple** : Oracle sur 4 cœurs au lieu de 8 = 50% d'économie

### 3. Sécurité et compliance

- **Isolation physique** : Séparation matérielle des données
- **Audit facilité** : Traçabilité par PRG
- **Conformité réglementaire** : RGPD, PCI-DSS, etc.

### 4. Flexibilité

- **Reconfiguration dynamique** : Modifier les PRG sans redémarrage système
- **Migration de LPARs** : Déplacer entre PRG selon les besoins

---

## Limitations et considérations

### Limitations du S1122

1. **Single Socket** : Tous les cœurs sont sur le même socket
   - Pas de séparation NUMA réelle
   - Partage du contrôleur mémoire

2. **Nombre de PRG** : Maximum 8 PRG par système
   - Recommandé : 2-4 PRG pour simplicité

3. **Granularité** : Minimum 1 cœur par PRG
   - Ne peut pas diviser un cœur entre PRG

### Considérations de performance

1. **Overhead minimal** : < 1% de perte de performance
2. **Cache L3** : Partagé au niveau du chip, mais optimisé par PRG
3. **Memory bandwidth** : Partagé entre tous les PRG

---

## Monitoring des PRG

### Via HMC

```bash
# Performance par PRG
lslparutil -r proc -m <system_name> \
  --filter "resource_type=proc_resource_group"

# Utilisation CPU par PRG
lshwres -r proc -m <system_name> --level sys \
  -F proc_resource_group_name,curr_avail_proc_units
```

### Via IBM i (dans la LPAR)

```cl
/* Afficher le PRG assigné */
DSPSYSVAL SYSVAL(QPRCRSGRP)

/* Performance du processeur */
WRKSYSSTS

/* Détails des processeurs */
WRKHDWRSC TYPE(*PRC)
```

### Métriques clés

1. **CPU Utilization par PRG** : < 85% recommandé
2. **Cache Miss Rate** : Doit être stable
3. **Thread Contention** : Surveiller avec SMT8
4. **Memory Bandwidth** : Vérifier la saturation

---

## Migration et changement de PRG

### Procédure de migration d'une LPAR

```bash
# 1. Arrêter la LPAR
chsysstate -r lpar -m <system_name> \
  -o shutdown -n <lpar_name> --immed

# 2. Modifier l'assignation PRG
chsyscfg -r lpar -m <system_name> \
  -i "name=<lpar_name>,\
      proc_resource_group=PRG_NEW"

# 3. Redémarrer la LPAR
chsysstate -r lpar -m <system_name> \
  -o on -n <lpar_name>

# 4. Vérifier
lssyscfg -r lpar -m <system_name> \
  --filter "lpar_names=<lpar_name>" \
  -F name,proc_resource_group,state
```

### Migration à chaud (Live Partition Mobility)

**Note** : Le changement de PRG nécessite généralement un redémarrage de la LPAR. LPM entre PRG n'est pas supporté sur le même système.

---

## Bonnes pratiques

### 1. Planification initiale

- ✅ Définir les workloads critiques
- ✅ Calculer les besoins en cœurs
- ✅ Prévoir 10-20% de marge
- ✅ Documenter la configuration

### 2. Naming convention

```
PRG_PRODUCTION    : Production critique
PRG_BATCH         : Traitements batch
PRG_DEV           : Développement
PRG_TEST          : Tests et QA
PRG_INFRA         : Infrastructure (VIOS, monitoring)
```

### 3. Allocation des ressources

```
Production    : 40-50% des cœurs
Batch         : 20-30% des cœurs
Dev/Test      : 15-25% des cœurs
Infrastructure: 5-10% des cœurs
```

### 4. Monitoring continu

- Surveiller l'utilisation CPU par PRG
- Ajuster selon les besoins réels
- Réévaluer trimestriellement

---

## Dépannage

### Problème : LPAR ne démarre pas après changement de PRG

```bash
# Vérifier la configuration
lssyscfg -r lpar -m <system_name> \
  --filter "lpar_names=<lpar_name>" \
  -F name,proc_resource_group,state,rmc_state

# Vérifier que le PRG existe
lshwres -r proc -m <system_name> --level sys \
  -F proc_resource_group_name

# Réassigner au PRG par défaut
chsyscfg -r lpar -m <system_name> \
  -i "name=<lpar_name>,proc_resource_group=default"
```

### Problème : Performance dégradée après création de PRG

```bash
# Vérifier la distribution des cœurs
lshwres -r proc -m <system_name> --level sys

# Vérifier l'utilisation
lslparutil -r proc -m <system_name> \
  --filter "resource_type=proc_resource_group" \
  -s 300 -i 60

# Ajuster si nécessaire
chsyscfg -r sys -m <system_name> \
  -i "proc_resource_group_name=PRG_PRODUCTION,\
      proc_resource_group_cores=0-4"
```

---

## Exemple complet : Configuration S1122 pour production

### Configuration système

```bash
#!/bin/bash
# Configuration PRG pour S1122 - 8 cœurs

SYSTEM="S1122_PROD"

# Créer PRG Production (4 cœurs)
chsyscfg -r sys -m $SYSTEM \
  -i "proc_resource_group_name=PRG_PRODUCTION,\
      proc_resource_group_cores=0-3"

# Créer PRG Non-Production (3 cœurs)
chsyscfg -r sys -m $SYSTEM \
  -i "proc_resource_group_name=PRG_NONPROD,\
      proc_resource_group_cores=4-6"

# Créer PRG Infrastructure (1 cœur)
chsyscfg -r sys -m $SYSTEM \
  -i "proc_resource_group_name=PRG_INFRA,\
      proc_resource_group_cores=7"

# Configurer LPAR Production
chsyscfg -r lpar -m $SYSTEM \
  -i "name=PROD_IBMI,\
      proc_resource_group=PRG_PRODUCTION,\
      desired_procs=3.5,\
      min_procs=3,\
      max_procs=4,\
      proc_mode=ded,\
      desired_mem=32768,\
      min_mem=24576,\
      max_mem=40960"

# Configurer LPAR Dev
chsyscfg -r lpar -m $SYSTEM \
  -i "name=DEV_IBMI,\
      proc_resource_group=PRG_NONPROD,\
      desired_procs=2,\
      min_procs=1,\
      max_procs=3,\
      proc_mode=shared,\
      uncap_weight=128,\
      desired_mem=16384"

# Configurer VIOS
chsyscfg -r lpar -m $SYSTEM \
  -i "name=VIOS1,\
      proc_resource_group=PRG_INFRA,\
      desired_procs=0.5,\
      min_procs=0.5,\
      max_procs=1,\
      proc_mode=shared,\
      desired_mem=8192"

# Vérifier la configuration
echo "=== Configuration PRG ==="
lshwres -r proc -m $SYSTEM --level sys \
  -F proc_resource_group_name,proc_resource_group_cores

echo "=== LPARs par PRG ==="
lshwres -r proc -m $SYSTEM --level lpar \
  -F lpar_name,proc_resource_group,curr_procs
```

---

## Ressources et documentation

### Documentation IBM

- **Redbook**: PowerVM Best Practices
- **Knowledge Center**: Processor Resource Groups
- **Power Systems Performance Guide**

### Outils de gestion

- **HMC GUI**: Interface graphique
- **HMC CLI**: Scripts d'automatisation
- **PowerVC**: Gestion cloud privé
- **Ansible**: Automatisation (via HMC REST API)

---

## Conclusion

Les **Processor Resource Groups** sur S1122 permettent de :

✅ **Isoler physiquement** les workloads critiques  
✅ **Optimiser les coûts** de licensing logiciel  
✅ **Améliorer les performances** par réduction de la contention  
✅ **Faciliter la gestion** multi-tenant  
✅ **Garantir la conformité** réglementaire

**Recommandation pour S1122** : Commencer avec 2 PRG (Production + Non-Production) et ajuster selon les besoins mesurés.