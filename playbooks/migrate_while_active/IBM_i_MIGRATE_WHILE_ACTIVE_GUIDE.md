# Guide de Configuration IBM i Migrate While Active

## Table des Matières
1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Architecture et Concepts](#architecture-et-concepts)
4. [Préparation des Partitions](#préparation-des-partitions)
5. [Configuration Réseau](#configuration-réseau)
6. [Configuration du Stockage](#configuration-du-stockage)
7. [Configuration de la Réplication](#configuration-de-la-réplication)
8. [Procédure de Migration](#procédure-de-migration)
9. [Tests et Validation](#tests-et-validation)
10. [Dépannage](#dépannage)

---

## Introduction

**IBM i Migrate While Active** est une fonctionnalité qui permet de migrer une partition IBM i d'un serveur Power à un autre avec un temps d'arrêt minimal (généralement quelques minutes). Cette technologie utilise PowerVM Live Partition Mobility (LPM) combinée avec la réplication de données en temps réel.

### Avantages
- Temps d'arrêt minimal (2-5 minutes typiquement)
- Migration transparente pour les utilisateurs
- Pas de perte de données
- Possibilité de migration entre différents modèles Power
- Idéal pour la maintenance matérielle, les mises à niveau ou la consolidation

### Cas d'Usage
- Migration vers un nouveau serveur Power
- Consolidation de datacenters
- Maintenance matérielle planifiée
- Équilibrage de charge entre serveurs
- Disaster Recovery et Business Continuity

---

## Prérequis

### 1. Prérequis Matériels

#### Serveur Source (Origine)
- **Modèle**: Power7 ou supérieur
- **Firmware**: Niveau minimum 7.6 ou supérieur
- **HMC**: Version 8.8.6 ou supérieure (recommandé: V9 ou V10)
- **Processeurs**: Compatible avec le serveur cible
- **Mémoire**: Suffisante pour la partition à migrer
- **Réseau**: Adaptateurs réseau redondants (recommandé)

#### Serveur Cible (Destination)
- **Modèle**: Power7 ou supérieur (même génération ou supérieure)
- **Firmware**: Niveau égal ou supérieur au serveur source
- **HMC**: Même version ou supérieure que le serveur source
- **Processeurs**: Compatibles avec le serveur source
- **Mémoire**: Capacité égale ou supérieure à la partition source
- **Stockage**: Capacité suffisante pour accueillir les données

#### Réseau de Migration
- **Bande passante**: Minimum 10 Gbps recommandé (1 Gbps minimum)
- **Latence**: < 5ms entre les serveurs (recommandé < 2ms)
- **VLAN dédié**: Pour le trafic de migration (recommandé)
- **Redondance**: Liens réseau multiples pour la haute disponibilité

#### Stockage
- **SAN**: Fibre Channel ou iSCSI
- **Type**: Stockage partagé ou réplication de stockage
- **Capacité**: Espace suffisant sur le système cible
- **Performance**: IOPS suffisants pour la réplication

### 2. Prérequis Logiciels

#### IBM i (Partition Source et Cible)
- **Version**: IBM i 7.2 ou supérieur (recommandé: 7.4 ou 7.5)
- **PTF Groups**: 
  - SF99722 (Technology Refresh)
  - SF99713 (Hiper Group)
  - SF99368 (PowerHA Group) si utilisé
- **Licences**: 
  - 5770-SS1 (IBM i Base)
  - 5770-TC1 (TCP/IP Connectivity)
  - 5770-XE1 (PowerHA pour réplication - optionnel)
  - 5770-DG1 (HTTP Server - pour monitoring)

#### PowerVM
- **Version**: PowerVM 2.2.6 ou supérieur
- **VIOS**: Version 2.2.6.30 ou supérieure sur les deux serveurs
- **Shared Ethernet Adapter (SEA)**: Configuré et fonctionnel
- **Virtual I/O**: Configuré correctement

#### HMC (Hardware Management Console)
- **Version**: V9R1M10 ou supérieur (recommandé: V10)
- **Connectivité**: Accès réseau aux deux serveurs Power
- **Certificats**: Certificats SSL valides
- **Utilisateur**: Profil avec droits d'administration

### 3. Prérequis Réseau

#### Configuration IP
```
Partition Source:
- IP Production: 192.168.1.10/24
- IP Réplication: 10.0.1.10/24
- Gateway: 192.168.1.1
- DNS: 192.168.1.2, 192.168.1.3

Partition Cible:
- IP Production: 192.168.1.11/24 (temporaire, deviendra 192.168.1.10)
- IP Réplication: 10.0.1.11/24
- Gateway: 192.168.1.1
- DNS: 192.168.1.2, 192.168.1.3

Réseau de Migration:
- VLAN dédié: VLAN 100
- Subnet: 10.0.2.0/24
- MTU: 9000 (Jumbo Frames recommandé)
```

#### Ports Requis
- **TCP 449**: AS-400 Remote Command
- **TCP 8470-8476**: IBM i Access
- **TCP 9470-9476**: IBM i Access SSL
- **TCP 2005**: PowerHA
- **TCP 3000-3010**: Réplication de données
- **TCP 22**: SSH (pour Ansible)
- **TCP 23**: Telnet (si utilisé)

### 4. Prérequis Sécurité

#### Comptes Utilisateurs
```
Partition Source:
- QSECOFR ou équivalent avec *ALLOBJ, *IOSYSCFG
- Profil de service: QSRVBAS
- Profil de réplication: REPLUSER (à créer)

Partition Cible:
- QSECOFR ou équivalent
- Profil de service: QSRVBAS
- Profil de réplication: REPLUSER (à créer)
```

#### Niveau de Sécurité
- **QSECURITY**: Niveau 40 ou 50 (recommandé: 40)
- **QRETSVRSEC**: *YES
- **QALWUSRDMN**: *ALL (pour les tests, ajuster en production)
- **QPWDEXPITV**: Configurer selon politique

#### Certificats SSL
- Certificats valides pour les communications sécurisées
- Certificate Store configuré
- Digital Certificate Manager (DCM) configuré

### 5. Prérequis Stockage

#### Configuration Disques
```
Partition Source:
- ASP 1 (System): 200 GB minimum
- ASP 2-32 (User): Selon besoins
- IASP (optionnel): Pour isolation des données

Partition Cible:
- Capacité égale ou supérieure
- Même configuration ASP recommandée
- Disques pré-alloués
```

#### Performance Stockage
- **IOPS**: Minimum 5000 IOPS pour la réplication
- **Latence**: < 10ms
- **Throughput**: Minimum 500 MB/s

### 6. Prérequis Sauvegarde

#### Avant Migration
- **Sauvegarde complète système**: SAVLIB LIB(*ALLUSR)
- **Sauvegarde configuration**: SAVCFG
- **Sauvegarde sécurité**: SAVSECDTA
- **Export PTF**: WRKPTFGRP puis sauvegarder la liste
- **Documentation**: Configuration réseau, utilisateurs, jobs

#### Point de Restauration
- Sauvegarde datée de moins de 24h
- Testée et validée
- Stockée hors du système à migrer

---

## Architecture et Concepts

### 1. Vue d'Ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         HMC (Management)                         │
│                    Version 9 ou supérieure                       │
└────────────────┬───────────────────────────┬────────────────────┘
                 │                           │
                 │                           │
    ┌────────────▼──────────────┐  ┌────────▼───────────────┐
    │   Serveur Power Source    │  │  Serveur Power Cible   │
    │      (Origine)            │  │    (Destination)       │
    │                           │  │                        │
    │  ┌─────────────────────┐  │  │  ┌──────────────────┐ │
    │  │  VIOS 1 (Primary)   │  │  │  │  VIOS 1 (Primary)│ │
    │  │  - SEA Config       │  │  │  │  - SEA Config    │ │
    │  │  - Virtual SCSI     │  │  │  │  - Virtual SCSI  │ │
    │  └─────────────────────┘  │  │  └──────────────────┘ │
    │                           │  │                        │
    │  ┌─────────────────────┐  │  │  ┌──────────────────┐ │
    │  │  VIOS 2 (Secondary) │  │  │  │  VIOS 2 (Second.)│ │
    │  │  - SEA Config       │  │  │  │  - SEA Config    │ │
    │  │  - Virtual SCSI     │  │  │  │  - Virtual SCSI  │ │
    │  └─────────────────────┘  │  │  └──────────────────┘ │
    │                           │  │                        │
    │  ┌─────────────────────┐  │  │  ┌──────────────────┐ │
    │  │  Partition IBM i    │  │  │  │ Partition IBM i  │ │
    │  │  (Source)           │  │  │  │ (Cible)          │ │
    │  │  - IP: 192.168.1.10 │──┼──┼─▶│ IP: 192.168.1.11 │ │
    │  │  - Répl: 10.0.1.10  │  │  │  │ Répl: 10.0.1.11  │ │
    │  └─────────────────────┘  │  │  └──────────────────┘ │
    └───────────┬───────────────┘  └──────────┬─────────────┘
                │                             │
                │                             │
    ┌───────────▼─────────────────────────────▼─────────────┐
    │              Réseau de Production                      │
    │              VLAN 10: 192.168.1.0/24                   │
    └────────────────────────────────────────────────────────┘
    
    ┌────────────────────────────────────────────────────────┐
    │              Réseau de Réplication                     │
    │              VLAN 100: 10.0.1.0/24                     │
    │              (Dédié, 10 Gbps recommandé)               │
    └────────────────────────────────────────────────────────┘
    
    ┌────────────────────────────────────────────────────────┐
    │              Stockage SAN                              │
    │              - Fibre Channel ou iSCSI                  │
    │              - Réplication synchrone/asynchrone        │
    └────────────────────────────────────────────────────────┘
```

### 2. Flux de Migration

```
Phase 1: Préparation (J-7 à J-1)
├── Vérification des prérequis
├── Configuration réseau de réplication
├── Synchronisation initiale des données
└── Tests de connectivité

Phase 2: Réplication Active (J-1 à J-Day)
├── Réplication continue des données
├── Monitoring de la synchronisation
├── Validation de l'intégrité
└── Préparation finale

Phase 3: Migration (J-Day)
├── Arrêt des applications (2-5 minutes)
├── Synchronisation finale
├── Basculement de la partition
├── Vérification de l'état
└── Redémarrage des applications

Phase 4: Validation (J+1)
├── Tests fonctionnels
├── Validation des performances
├── Monitoring intensif
└── Documentation
```

### 3. Types de Réplication

#### Réplication Synchrone
- **Avantage**: RPO = 0 (aucune perte de données)
- **Inconvénient**: Impact sur les performances
- **Usage**: Distances courtes (< 100 km), applications critiques

#### Réplication Asynchrone
- **Avantage**: Moins d'impact sur les performances
- **Inconvénient**: RPO > 0 (perte potentielle de quelques secondes)
- **Usage**: Distances longues, applications moins critiques

---

## Préparation des Partitions

### 1. Vérification de la Partition Source

#### Étape 1.1: Vérifier la Version et les PTFs

```bash
# Se connecter à la partition source
ssh qsecofr@192.168.1.10

# Vérifier la version IBM i
DSPSFWRSC

# Vérifier les PTF Groups installés
WRKPTFGRP

# Vérifier les PTFs critiques
GO PTF
  Option 10 (Display PTF status)
```

**Commandes CL à exécuter:**
```cl
/* Afficher les informations système */
DSPSYSVAL SYSVAL(QMODEL)
DSPSYSVAL SYSVAL(QSRLNBR)
DSPSYSVAL SYSVAL(QVERSION)

/* Vérifier l'espace disque */
WRKSYSSTS
WRKDSKSTS

/* Vérifier les ASP */
WRKSYSSTS
  Option 2 (Disk status)

/* Lister les bibliothèques utilisateur */
DSPLIB LIB(*ALLUSR)
```

#### Étape 1.2: Vérifier la Configuration Réseau

```cl
/* Afficher les interfaces réseau */
WRKTCPIFC

/* Afficher les routes */
WRKTCPRTE

/* Afficher la configuration TCP/IP */
DSPTCPIFC

/* Vérifier les lignes de communication */
WRKLIND

/* Afficher les descriptions de ligne */
WRKHDWRSC *CMN
```

**Documenter:**
- Adresses IP de toutes les interfaces
- Masques de sous-réseau
- Passerelles par défaut
- Serveurs DNS
- Routes statiques
- VLANs configurés

#### Étape 1.3: Inventaire des Ressources

```cl
/* Lister les utilisateurs */
DSPUSRPRF USRPRF(*ALL) OUTPUT(*PRINT)

/* Lister les bibliothèques */
DSPLIB LIB(*ALLUSR) OUTPUT(*PRINT)

/* Lister les fichiers de spool */
WRKSPLF

/* Lister les jobs actifs */
WRKACTJOB

/* Lister les subsystèmes */
WRKSBS

/* Lister les files d'attente de jobs */
WRKJOBQ

/* Lister les files d'attente de sortie */
WRKOUTQ
```

#### Étape 1.4: Vérifier la Sécurité

```cl
/* Afficher le niveau de sécurité */
DSPSYSVAL SYSVAL(QSECURITY)

/* Vérifier les valeurs de sécurité */
DSPSYSVAL SYSVAL(QRETSVRSEC)
DSPSYSVAL SYSVAL(QALWUSRDMN)
DSPSYSVAL SYSVAL(QPWDEXPITV)

/* Afficher les autorisations */
DSPAUTUSR

/* Vérifier les objets avec autorisation publique */
DSPPUBAUT OBJ(*ALL)
```

### 2. Préparation de la Partition Cible

#### Étape 2.1: Installation IBM i

Si la partition cible n'a pas encore IBM i installé:

```
1. Créer la partition LPAR via HMC
   - Allouer les ressources (CPU, mémoire)
   - Configurer les adaptateurs virtuels
   - Définir le profil de partition

2. Installer IBM i depuis le média
   - Démarrer en mode D (Installation)
   - Suivre l'assistant d'installation
   - Configurer les paramètres de base

3. Appliquer les PTFs
   - Installer les mêmes PTF Groups que la source
   - Redémarrer si nécessaire
```

#### Étape 2.2: Configuration de Base

```cl
/* Configurer le nom système */
CHGNETA SYSNAME(IBMICIBLE)

/* Configurer TCP/IP */
CFGTCP
  Option 1 (Work with TCP/IP interfaces)
  
/* Ajouter une interface */
ADDTCPIFC INTNETADR('192.168.1.11') 
          LIND(ETHLINE) 
          SUBNETMASK('255.255.255.0')

/* Ajouter une route par défaut */
ADDTCPRTE RTEDEST(*DFTROUTE) 
          NEXTHOP('192.168.1.1')

/* Configurer DNS */
CHGTCPDMN DMNNAME('votredomaine.com') 
          DNSSVR('192.168.1.2' '192.168.1.3')

/* Démarrer TCP/IP */
STRTCP
```

#### Étape 2.3: Créer les Utilisateurs de Réplication

```cl
/* Sur la partition SOURCE */
CRTUSRPRF USRPRF(REPLUSER) 
          PASSWORD(VotreMotDePasse123!) 
          USRCLS(*SECOFR) 
          TEXT('Utilisateur de réplication') 
          SPCAUT(*ALLOBJ *IOSYSCFG *SECADM)

/* Sur la partition CIBLE */
CRTUSRPRF USRPRF(REPLUSER) 
          PASSWORD(VotreMotDePasse123!) 
          USRCLS(*SECOFR) 
          TEXT('Utilisateur de réplication') 
          SPCAUT(*ALLOBJ *IOSYSCFG *SECADM)
```

### 3. Configuration du Stockage

#### Étape 3.1: Vérifier l'Espace Disque

```cl
/* Sur la partition SOURCE */
WRKDSKSTS

/* Calculer l'espace total utilisé */
RTVDSKINF TYPE(*TOTAL)

/* Afficher les détails des ASP */
WRKSYSSTS
  Option 2 (Disk status)
```

**Documenter:**
- Taille totale de chaque ASP
- Espace utilisé
- Espace disponible
- Nombre de disques
- Configuration RAID

#### Étape 3.2: Préparer le Stockage Cible

```cl
/* Sur la partition CIBLE */
/* Vérifier que l'espace disponible est suffisant */
WRKDSKSTS

/* Si nécessaire, ajouter des disques via HMC */
/* Puis les configurer dans IBM i */
CFGDEVASP ASPDEV(ASP02) ACTION(*ADD)
```

---

## Configuration Réseau

### 1. Configuration du Réseau de Production

#### Étape 1.1: Configuration sur la Partition Source

```cl
/* Vérifier la configuration actuelle */
WRKTCPIFC

/* Si nécessaire, modifier l'interface */
CHGTCPIFC INTNETADR('192.168.1.10') 
          LIND(ETHLINE) 
          SUBNETMASK('255.255.255.0')

/* Vérifier la connectivité */
PING RMTSYS('192.168.1.1')
PING RMTSYS('192.168.1.2')
```

#### Étape 1.2: Configuration sur la Partition Cible

```cl
/* Configurer l'interface de production */
ADDTCPIFC INTNETADR('192.168.1.11') 
          LIND(ETHLINE) 
          SUBNETMASK('255.255.255.0')

/* Ajouter la route par défaut */
ADDTCPRTE RTEDEST(*DFTROUTE) 
          NEXTHOP('192.168.1.1')

/* Démarrer l'interface */
STRTCPIFC INTNETADR('192.168.1.11')

/* Vérifier la connectivité */
PING RMTSYS('192.168.1.1')
PING RMTSYS('192.168.1.10')
```

### 2. Configuration du Réseau de Réplication

#### Étape 2.1: Créer une Ligne Dédiée (Source)

```cl
/* Créer une description de ligne Ethernet */
CRTLINETH LIND(REPLLINE) 
          RSRCNAME(CMN05) 
          LINESPEED(10G) 
          DUPLEX(*FULL) 
          TEXT('Ligne de réplication')

/* Varier ON la ligne */
VRYCFG CFGOBJ(REPLLINE) CFGTYPE(*LIN) STATUS(*ON)

/* Ajouter l'interface de réplication */
ADDTCPIFC INTNETADR('10.0.1.10') 
          LIND(REPLLINE) 
          SUBNETMASK('255.255.255.0') 
          TEXT('Interface de réplication')

/* Démarrer l'interface */
STRTCPIFC INTNETADR('10.0.1.10')
```

#### Étape 2.2: Créer une Ligne Dédiée (Cible)

```cl
/* Créer une description de ligne Ethernet */
CRTLINETH LIND(REPLLINE) 
          RSRCNAME(CMN05) 
          LINESPEED(10G) 
          DUPLEX(*FULL) 
          TEXT('Ligne de réplication')

/* Varier ON la ligne */
VRYCFG CFGOBJ(REPLLINE) CFGTYPE(*LIN) STATUS(*ON)

/* Ajouter l'interface de réplication */
ADDTCPIFC INTNETADR('10.0.1.11') 
          LIND(REPLLINE) 
          SUBNETMASK('255.255.255.0') 
          TEXT('Interface de réplication')

/* Démarrer l'interface */
STRTCPIFC INTNETADR('10.0.1.11')
```

#### Étape 2.3: Tester la Connectivité de Réplication

```cl
/* Depuis la partition SOURCE */
PING RMTSYS('10.0.1.11') NBRPKT(100)

/* Depuis la partition CIBLE */
PING RMTSYS('10.0.1.10') NBRPKT(100)

/* Tester la bande passante (optionnel) */
/* Utiliser iperf3 ou un outil similaire */
```

### 3. Configuration des Jumbo Frames (Recommandé)

```cl
/* Sur les deux partitions */
CHGTCPIFC INTNETADR('10.0.1.10') 
          MTU(9000)

/* Redémarrer l'interface */
ENDTCPIFC INTNETADR('10.0.1.10')
STRTCPIFC INTNETADR('10.0.1.10')

/* Vérifier */
DSPTCPIFC INTNETADR('10.0.1.10')
```

---

## Configuration de la Réplication

### 1. Choix de la Méthode de Réplication

#### Option A: PowerHA SystemMirror (Recommandé)

**Avantages:**
- Réplication en temps réel
- Gestion automatique des erreurs
- Monitoring intégré
- Support IBM

**Installation:**
```cl
/* Installer PowerHA (5770-XE1) */
GO LICPGM
  Option 11 (Install licensed programs)
  
/* Sélectionner 5770-XE1 */
```

#### Option B: Réplication au Niveau Stockage

**Avantages:**
- Indépendant d'IBM i
- Performance élevée
- Gestion centralisée

**Configuration:**
- Dépend du fournisseur de stockage (IBM, Dell, NetApp, etc.)
- Configurer via l'interface du SAN

### 2. Configuration PowerHA (Option A)

#### Étape 2.1: Installation sur les Deux Partitions

```cl
/* Sur SOURCE et CIBLE */
RSTLICPGM LICPGM(5770XE1) 
          DEV(*SAVF) 
          SAVF(QGPL/XE1SAVF)

/* Vérifier l'installation */
DSPLICPGM LICPGM(5770XE1)
```

#### Étape 2.2: Configuration du Cluster

```cl
/* Sur la partition SOURCE */
/* Créer le cluster */
CRTCLU CLUSTER(MIGRCLUSTER) 
       NODE(IBMISOURCE IBMICIBLE) 
       TEXT('Cluster de migration')

/* Ajouter le nœud source */
ADDCLUNODE CLUSTER(MIGRCLUSTER) 
           NODE(IBMISOURCE) 
           INTNETADR('10.0.1.10')

/* Démarrer le cluster */
STRCLUNOD CLUSTER(MIGRCLUSTER) NODE(IBMISOURCE)
```

```cl
/* Sur la partition CIBLE */
/* Ajouter le nœud cible */
ADDCLUNODE CLUSTER(MIGRCLUSTER) 
           NODE(IBMICIBLE) 
           INTNETADR('10.0.1.11')

/* Démarrer le cluster */
STRCLUNOD CLUSTER(MIGRCLUSTER) NODE(IBMICIBLE)
```

#### Étape 2.3: Configuration de la Réplication

```cl
/* Sur la partition SOURCE */
/* Créer un groupe de ressources */
CRTCRG CRG(MIGRATIONCRG) 
       CLUSTER(MIGRCLUSTER) 
       CRGTYPE(*DEV) 
       TEXT('Groupe de réplication pour migration')

/* Ajouter les bibliothèques à répliquer */
ADDCRGDEVE CRG(MIGRATIONCRG) 
           CLUSTER(MIGRCLUSTER) 
           RCYDMN(*DEV) 
           DEV(ASP01)

/* Démarrer la réplication */
STRCRG CRG(MIGRATIONCRG) 
       CLUSTER(MIGRCLUSTER)
```

### 3. Synchronisation Initiale

#### Étape 3.1: Sauvegarder la Partition Source

```cl
/* Sauvegarder toutes les bibliothèques utilisateur */
SAVLIB LIB(*ALLUSR) 
       DEV(*SAVF) 
       SAVF(QGPL/ALLUSRSAVF) 
       CLEAR(*ALL)

/* Sauvegarder la configuration */
SAVCFG DEV(*SAVF) 
       SAVF(QGPL/CFGSAVF)

/* Sauvegarder les données de sécurité */
SAVSECDTA DEV(*SAVF) 
          SAVF(QGPL/SECSAVF)
```

#### Étape 3.2: Transférer vers la Partition Cible

```cl
/* Depuis la partition SOURCE */
/* Utiliser FTP pour transférer les SAVF */
FTP RMTSYS('192.168.1.11')
  User: REPLUSER
  Password: VotreMotDePasse123!
  
  bin
  put QGPL/ALLUSRSAVF QGPL/ALLUSRSAVF
  put QGPL/CFGSAVF QGPL/CFGSAVF
  put QGPL/SECSAVF QGPL/SECSAVF
  quit
```

#### Étape 3.3: Restaurer sur la Partition Cible

```cl
/* Sur la partition CIBLE */
/* Restaurer les bibliothèques */
RSTLIB SAVLIB(*ALLUSR) 
       DEV(*SAVF) 
       SAVF(QGPL/ALLUSRSAVF)

/* Restaurer la configuration */
RSTCFG DEV(*SAVF) 
       SAVF(QGPL/CFGSAVF)

/* Restaurer les données de sécurité */
RSTSECDTA DEV(*SAVF) 
          SAVF(QGPL/SECSAVF)
```

---

## Procédure de Migration

### 1. Phase de Préparation (J-1)

#### Étape 1.1: Vérifications Finales

```cl
/* Sur la partition SOURCE */
/* Vérifier l'état de la réplication */
WRKCLU CLUSTER(MIGRCLUSTER)
WRKCRG CRG(MIGRATIONCRG)

/* Vérifier la synchronisation */
DSPCRGSTS CRG(MIGRATIONCRG)

/* Vérifier les jobs actifs */
WRKACTJOB

/* Vérifier les files d'attente */
WRKJOBQ
WRKOUTQ
```

#### Étape 1.2: Communication

- Informer tous les utilisateurs de la fenêtre de migration
- Envoyer un email de rappel
- Afficher un message sur le système

```cl
/* Envoyer un message à tous les utilisateurs */
SNDBRKMSG MSG('ATTENTION: Migration système prévue demain à 20h00. Durée estimée: 30 minutes. Merci de sauvegarder votre travail.') 
          TOMSGQ(*ALLWS)
```

### 2. Phase de Migration (J-Day)

#### Étape 2.1: Arrêt Contrôlé des Applications (T-30 min)

```cl
/* Envoyer un avertissement final */
SNDBRKMSG MSG('ATTENTION: Migration système dans 30 minutes. Merci de terminer votre travail et de vous déconnecter.') 
          TOMSGQ(*ALLWS)

/* Attendre 30 minutes */

/* Envoyer un dernier avertissement */
SNDBRKMSG MSG('Migration système dans 5 minutes. Déconnexion imminente.') 
          TOMSGQ(*ALLWS)
```

#### Étape 2.2: Arrêt des Subsystèmes (T-5 min)

```cl
/* Arrêter les subsystèmes applicatifs */
ENDSBS SBS(QBATCH) OPTION(*IMMED)
ENDSBS SBS(QCMN) OPTION(*IMMED)
ENDSBS SBS(QINTER) OPTION(*IMMED)

/* Vérifier qu'il ne reste que les subsystèmes système */
WRKSBS

/* Arrêter les serveurs TCP/IP */
ENDTCPSVR SERVER(*ALL)
```

#### Étape 2.3: Synchronisation Finale (T-0)

```cl
/* Forcer une synchronisation finale */
CHGCRG CRG(MIGRATIONCRG) 
       CLUSTER(MIGRCLUSTER) 
       ACTION(*SYNC)

/* Attendre la fin de la synchronisation */
DSPCRGSTS CRG(MIGRATIONCRG)

/* Vérifier qu'il n'y a plus de différences */
```

#### Étape 2.4: Basculement via HMC

**Sur la HMC:**

1. Se connecter à la HMC
2. Naviguer vers: Systems Management > Servers
3. Sélectionner le serveur source
4. Clic droit sur la partition IBM i source
5. Sélectionner: Operations > Migrate Partition
6. Suivre l'assistant:
   - Sélectionner le serveur cible
   - Vérifier les ressources
   - Valider la configuration réseau
   - Lancer la migration

**Commandes HMC (CLI):**
```bash
# Se connecter à la HMC
ssh hscroot@hmc-hostname

# Lister les partitions
lssyscfg -r lpar -m serveur-source

# Migrer la partition
migrlpar -o m -m serveur-source -t serveur-cible \
         -p partition-ibmi --id partition-id

# Suivre la progression
lsmigr -m serveur-source -p partition-ibmi
```

#### Étape 2.5: Vérification Post-Migration (T+5 min)

```cl
/* Sur la partition CIBLE (maintenant active) */
/* Vérifier l'état du système */
WRKSYSSTS

/* Vérifier les ASP */
WRKDSKSTS

/* Vérifier les interfaces réseau */
WRKTCPIFC

/* Démarrer TCP/IP si nécessaire */
STRTCP

/* Vérifier la connectivité */
PING RMTSYS('192.168.1.1')
```

#### Étape 2.6: Redémarrage des Applications (T+10 min)

```cl
/* Démarrer les subsystèmes */
STRSBS SBSD(QINTER)
STRSBS SBSD(QBATCH)
STRSBS SBSD(QCMN)

/* Démarrer les serveurs TCP/IP */
STRTCPSVR SERVER(*ALL)

/* Vérifier les jobs actifs */
WRKACTJOB

/* Envoyer un message de confirmation */
SNDBRKMSG MSG('Migration terminée avec succès. Le système est de nouveau opérationnel.') 
          TOMSGQ(*ALLWS)
```

### 3. Changement d'Adresse IP (Si nécessaire)

Si la partition cible doit prendre l'adresse IP de la source:

```cl
/* Arrêter l'interface actuelle */
ENDTCPIFC INTNETADR('192.168.1.11')

/* Supprimer l'interface */
RMVTCPIFC INTNETADR('192.168.1.11')

/* Ajouter la nouvelle interface avec l'IP de production */
ADDTCPIFC INTNETADR('192.168.1.10') 
          LIND(ETHLINE) 
          SUBNETMASK('255.255.255.0')

/* Démarrer l'interface */
STRTCPIFC INTNETADR('192.168.1.10')

/* Vérifier */
WRKTCPIFC
PING RMTSYS('192.168.1.1')
```

---

## Tests et Validation

### 1. Tests Fonctionnels

#### Test 1.1: Connectivité Réseau

```cl
/* Tester la connectivité externe */
PING RMTSYS('8.8.8.8') NBRPKT(10)

/* Tester la résolution DNS */
PING RMTSYS('www.ibm.com')

/* Tester FTP */
FTP RMTSYS('ftp.ibm.com')

/* Tester HTTP */
/* Depuis un navigateur, accéder à http://192.168.1.10:2001 */
```

#### Test 1.2: Accès Utilisateurs

```cl
/* Vérifier que les utilisateurs peuvent se connecter */
/* Demander à quelques utilisateurs de test de se connecter */

/* Vérifier les profils utilisateurs */
DSPUSRPRF USRPRF(TESTUSER)

/* Vérifier les autorisations */
DSPAUTUSR USRPRF(TESTUSER)
```

#### Test 1.3: Applications

```cl
/* Lancer les applications critiques */
/* Vérifier qu'elles fonctionnent correctement */

/* Vérifier les bibliothèques */
DSPLIB LIB(APPLIB)

/* Vérifier les fichiers de données */
DSPFD FILE(APPLIB/DATAFILE)

/* Exécuter des requêtes SQL de test */
RUNSQLSTM SRCFILE(QGPL/QSQLSRC) SRCMBR(TESTQRY)
```

### 2. Tests de Performance

#### Test 2.1: Performance CPU

```cl
/* Vérifier l'utilisation CPU */
WRKSYSSTS

/* Lancer un job de test intensif */
SBMJOB CMD(CALL PGM(CPUINTENSIVE)) JOB(CPUTEST)

/* Monitorer pendant 5 minutes */
WRKACTJOB
```

#### Test 2.2: Performance Disque

```cl
/* Vérifier les I/O disque */
WRKDSKSTS

/* Lancer un test d'I/O */
SBMJOB CMD(CALL PGM(IOTEST)) JOB(IOTEST)

/* Monitorer les performances */
WRKSYSSTS
```

#### Test 2.3: Performance Réseau

```bash
# Depuis un client, tester la latence
ping -c 100 192.168.1.10

# Tester le débit
# Utiliser iperf3 ou un outil similaire
iperf3 -c 192.168.1.10 -t 60
```

### 3. Validation des Données

#### Test 3.1: Intégrité des Données

```cl
/* Comparer les checksums des fichiers critiques */
/* Créer un programme CL pour calculer les checksums */

/* Vérifier le nombre d'enregistrements */
DSPFD FILE(APPLIB/CUSTOMER) TYPE(*MBR)

/* Comparer avec la source (si encore accessible) */
```

#### Test 3.2: Cohérence des Bibliothèques

```cl
/* Lister toutes les bibliothèques */
DSPLIB LIB(*ALLUSR) OUTPUT(*PRINT)

/* Comparer avec la liste de la source */

/* Vérifier les objets dans les bibliothèques critiques */
DSPOBJD OBJ(APPLIB/*ALL) OBJTYPE(*ALL) OUTPUT(*PRINT)
```

### 4. Monitoring Post-Migration

#### Monitoring Jour 1 (J+0)

```cl
/* Créer un job de monitoring */
SBMJOB CMD(CALL PGM(QGPL/MONITOR)) 
       JOB(POSTMIGMON) 
       JOBD(QGPL/MONJOBD)

/* Vérifier toutes les heures: */
- WRKSYSSTS (CPU, mémoire, I/O)
- WRKACTJOB (jobs actifs)
- WRKTCPSTS (connexions réseau)
- DSPLOG (messages système)
```

#### Monitoring Semaine 1 (J+1 à J+7)

```cl
/* Vérifier quotidiennement: */
- Performance globale
- Messages d'erreur
- Utilisation des ressources
- Feedback utilisateurs

/* Créer des rapports quotidiens */
CALL PGM(QGPL/DAILYREPORT)
```

---

## Dépannage

### 1. Problèmes Courants

#### Problème 1: Échec de la Migration HMC

**Symptômes:**
- La migration s'arrête avec une erreur
- Message: "Migration failed - incompatible resources"

**Solutions:**
```
1. Vérifier la compatibilité des ressources:
   - Processeurs compatibles
   - Mémoire suffisante
   - Adaptateurs virtuels configurés

2. Vérifier les logs HMC:
   - /var/hsc/log/hmc.log
   - Rechercher les erreurs spécifiques

3. Vérifier la connectivité réseau entre serveurs:
   - Ping entre les VIOS
   - Vérifier les VLANs

4. Redémarrer la migration:
   - Annuler la migration en cours
   - Corriger les problèmes identifiés
   - Relancer la migration
```

#### Problème 2: Perte de Connectivité Réseau

**Symptômes:**
- Impossible de se connecter à la partition après migration
- Ping ne répond pas

**Solutions:**
```cl
/* Depuis la console HMC */
/* Se connecter en mode console */

/* Vérifier l'état des interfaces */
WRKTCPIFC

/* Vérifier que TCP/IP est démarré */
NETSTAT *IFC

/* Si TCP/IP n'est pas démarré */
STRTCP

/* Vérifier les lignes de communication */
WRKLIND

/* Varier ON les lignes si nécessaire */
VRYCFG CFGOBJ(ETHLINE) CFGTYPE(*LIN) STATUS(*ON)

/* Redémarrer l'interface */
ENDTCPIFC INTNETADR('192.168.1.10')
STRTCPIFC INTNETADR('192.168.1.10')
```

#### Problème 3: Problèmes de Performance

**Symptômes:**
- Système lent après migration
- Temps de réponse élevés

**Solutions:**
```cl
/* Vérifier l'utilisation des ressources */
WRKSYSSTS

/* Vérifier les jobs actifs */
WRKACTJOB

/* Identifier les jobs consommant beaucoup de CPU */
WRKACTJOB SBS(*ALL) CPU(*GT 50)

/* Vérifier les I/O disque */
WRKDSKSTS

/* Vérifier la configuration des pools de mémoire */
WRKSHRPOOL

/* Ajuster si nécessaire */
CHGSHRPOOL POOL(*MACHINE) SIZE(2000)
```

#### Problème 4: Données Manquantes

**Symptômes:**
- Bibliothèques ou fichiers manquants
- Données incomplètes

**Solutions:**
```cl
/* Vérifier les bibliothèques */
DSPLIB LIB(*ALLUSR)

/* Comparer avec la liste de la source */

/* Si des bibliothèques manquent, restaurer depuis la sauvegarde */
RSTLIB SAVLIB(MISSINGLIB) 
       DEV(*SAVF) 
       SAVF(QGPL/ALLUSRSAVF)

/* Vérifier l'intégrité des fichiers */
CHKOBJ OBJ(APPLIB/*ALL) OBJTYPE(*FILE)

/* Reconstruire les index si nécessaire */
RGZPFM FILE(APPLIB/DATAFILE)
```

### 2. Procédure de Rollback

Si la migration échoue et qu'il faut revenir à la partition source:

#### Étape 1: Arrêter la Partition Cible

```cl
/* Sur la partition CIBLE */
/* Arrêter tous les subsystèmes */
ENDSBS SBS(*ALL) OPTION(*IMMED)

/* Arrêter le système */
PWRDWNSYS OPTION(*IMMED) DELAY(0)
```

#### Étape 2: Redémarrer la Partition Source

```
1. Via HMC, activer la partition source
2. Démarrer la partition en mode normal
3. Vérifier que tout fonctionne
```

#### Étape 3: Restaurer la Configuration Réseau

```cl
/* Sur la partition SOURCE */
/* Vérifier les interfaces réseau */
WRKTCPIFC

/* Redémarrer TCP/IP si nécessaire */
STRTCP

/* Vérifier la connectivité */
PING RMTSYS('192.168.1.1')
```

#### Étape 4: Redémarrer les Applications

```cl
/* Démarrer les subsystèmes */
STRSBS SBSD(QINTER)
STRSBS SBSD(QBATCH)
STRSBS SBSD(QCMN)

/* Démarrer les serveurs */
STRTCPSVR SERVER(*ALL)

/* Informer les utilisateurs */
SNDBRKMSG MSG('Le système est de nouveau opérationnel sur le serveur d origine.') 
          TOMSGQ(*ALLWS)
```

### 3. Contacts et Support

#### Support IBM
- **Téléphone**: 0800 426 426 (France)
- **Web**: https://www.ibm.com/support
- **Severité 1**: Disponible 24/7

#### Documentation
- IBM i Information Center: https://www.ibm.com/docs/en/i
- PowerVM Documentation: https://www.ibm.com/docs/en/powervm
- HMC Documentation: https://www.ibm.com/docs/en/power-systems

#### Logs à Collecter pour le Support
```cl
/* Collecter les logs système */
DMPJOBLOG JOB(*) OUTPUT(*PRINT)

/* Collecter les logs de communication */
DSPLOG LOG(QHST) OUTPUT(*PRINT)

/* Collecter les informations système */
PRTSYSINF OUTPUT(*PRINT)

/* Collecter les informations de configuration */
PRTCFGSTS CFGTYPE(*ALL) OUTPUT(*PRINT)
```

---

## Annexes

### Annexe A: Checklist de Migration

```
□ Prérequis
  □ Versions IBM i compatibles
  □ PTFs installés
  □ Espace disque suffisant
  □ Réseau configuré
  □ Sauvegardes à jour

□ Préparation (J-7)
  □ Vérification de la partition source
  □ Installation de la partition cible
  □ Configuration du réseau de réplication
  □ Tests de connectivité

□ Synchronisation (J-3)
  □ Sauvegarde complète de la source
  □ Transfert vers la cible
  □ Restauration sur la cible
  □ Configuration de la réplication
  □ Synchronisation initiale

□ Validation (J-1)
  □ Vérification de la synchronisation
  □ Tests de connectivité
  □ Communication aux utilisateurs
  □ Préparation de la fenêtre de migration

□ Migration (J-Day)
  □ Avertissement utilisateurs (T-30 min)
  □ Arrêt des applications (T-5 min)
  □ Synchronisation finale (T-0)
  □ Migration HMC
  □ Vérification post-migration (T+5 min)
  □ Redémarrage des applications (T+10 min)
  □ Tests fonctionnels (T+15 min)

□ Post-Migration (J+1)
  □ Monitoring intensif
  □ Tests de performance
  □ Validation des données
  □ Feedback utilisateurs
  □ Documentation
```

### Annexe B: Commandes Utiles

```cl
/* Commandes de diagnostic */
WRKSYSSTS          /* État du système */
WRKACTJOB          /* Jobs actifs */
WRKDSKSTS          /* État des disques */
WRKTCPIFC          /* Interfaces réseau */
WRKTCPSTS          /* Statistiques TCP/IP */
DSPLOG             /* Journal système */
DSPMSG QSYSOPR     /* Messages opérateur */

/* Commandes de configuration */
CFGTCP             /* Configuration TCP/IP */
WRKLIND            /* Lignes de communication */
WRKSBS             /* Subsystèmes */
WRKJOBQ            /* Files d'attente de jobs */

/* Commandes de sauvegarde */
SAVLIB             /* Sauvegarder bibliothèques */
SAVCFG             /* Sauvegarder configuration */
SAVSECDTA          /* Sauvegarder sécurité */
SAVSYS             /* Sauvegarder système */

/* Commandes de restauration */
RSTLIB             /* Restaurer bibliothèques */
RSTCFG             /* Restaurer configuration */
RSTSECDTA          /* Restaurer sécurité */
RSTSYS             /* Restaurer système */

/* Commandes PowerHA */
CRTCLU             /* Créer cluster */
ADDCLUNODE         /* Ajouter nœud */
STRCLUNOD          /* Démarrer nœud */
CRTCRG             /* Créer groupe de réplication */
STRCRG             /* Démarrer réplication */
WRKCLU             /* Travailler avec cluster */
WRKCRG             /* Travailler avec groupe de réplication */
```

### Annexe C: Scripts Ansible

Voir le répertoire `playbooks/migrate_while_active/` pour les playbooks Ansible automatisant certaines tâches.

### Annexe D: Glossaire

- **ASP**: Auxiliary Storage Pool - Pool de stockage auxiliaire
- **CRG**: Cluster Resource Group - Groupe de ressources de cluster
- **HMC**: Hardware Management Console - Console de gestion matérielle
- **IASP**: Independent Auxiliary Storage Pool - Pool de stockage auxiliaire indépendant
- **LPAR**: Logical Partition - Partition logique
- **LPM**: Live Partition Mobility - Mobilité de partition en direct
- **PowerHA**: Solution de haute disponibilité d'IBM
- **PowerVM**: Technologie de virtualisation d'IBM
- **PTF**: Program Temporary Fix - Correctif temporaire de programme
- **RPO**: Recovery Point Objective - Objectif de point de récupération
- **RTO**: Recovery Time Objective - Objectif de temps de récupération
- **SEA**: Shared Ethernet Adapter - Adaptateur Ethernet partagé
- **VIOS**: Virtual I/O Server - Serveur d'E/S virtuel

---

## Conclusion

La migration IBM i While Active est une procédure complexe mais bien maîtrisée qui permet de migrer une partition IBM i avec un temps d'arrêt minimal. En suivant ce guide étape par étape et en respectant tous les prérequis, vous devriez pouvoir réaliser une migration réussie.

**Points clés à retenir:**
1. La préparation est essentielle - ne pas précipiter
2. Tester la connectivité réseau avant la migration
3. Avoir des sauvegardes à jour
4. Communiquer avec les utilisateurs
5. Avoir un plan de rollback
6. Monitorer intensivement après la migration

**Recommandations:**
- Effectuer une migration de test dans un environnement non-production
- Planifier la migration pendant une fenêtre de maintenance
- Avoir le support IBM disponible pendant la migration
- Documenter toutes les étapes et les résultats

Pour toute question ou assistance, n'hésitez pas à contacter le support IBM ou votre partenaire IBM.

---

**Document créé le**: 2025-12-17  
**Version**: 1.0  
**Auteur**: IBM i Technical Team  
**Dernière mise à jour**: 2025-12-17