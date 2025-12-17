# Guide de Configuration IBM i Migrate While Active via Navigator for i

## Table des Matières
1. [Introduction à Navigator for i](#introduction-à-navigator-for-i)
2. [Accès et Configuration Initiale](#accès-et-configuration-initiale)
3. [Vérification des Prérequis](#vérification-des-prérequis)
4. [Configuration du Réseau](#configuration-du-réseau)
5. [Configuration du Stockage](#configuration-du-stockage)
6. [Configuration PowerHA SystemMirror](#configuration-powerha-systemmirror)
7. [Monitoring et Validation](#monitoring-et-validation)
8. [Procédure de Migration](#procédure-de-migration)
9. [Dépannage](#dépannage)

---

## Introduction à Navigator for i

**IBM Navigator for i** est l'interface web moderne pour administrer IBM i. Elle remplace System i Navigator (client Windows) et offre une interface intuitive pour gérer tous les aspects du système, y compris la configuration de la réplication pour Migrate While Active.

### Avantages de Navigator for i
- ✅ Interface web accessible depuis n'importe quel navigateur
- ✅ Pas d'installation client nécessaire
- ✅ Interface moderne et intuitive
- ✅ Gestion complète de PowerHA
- ✅ Monitoring en temps réel
- ✅ Tableaux de bord personnalisables

### Prérequis Navigator for i
- IBM i 7.2 ou supérieur
- HTTP Server (5770-DG1) installé et démarré
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)
- Connexion réseau à la partition IBM i

---

## Accès et Configuration Initiale

### 1. Démarrage du HTTP Server

#### Via 5250 (si pas encore démarré)

```
1. Se connecter en 5250
2. Taper: STRTCPSVR SERVER(*HTTP) HTTPSVR(*ADMIN)
3. Attendre le message de confirmation
```

#### Vérifier l'état du serveur

```
WRKACTJOB SBS(QHTTPSVR)
```

### 2. Accès à Navigator for i

#### URL d'accès

```
https://[adresse-ip-ibmi]:2001/navigator

Exemples:
- Partition Source: https://192.168.1.10:2001/navigator
- Partition Cible: https://192.168.1.11:2001/navigator
```

#### Première connexion

1. **Ouvrir le navigateur web**
   - Chrome, Firefox, Edge ou Safari recommandés

2. **Accepter le certificat SSL**
   - Le certificat est auto-signé par défaut
   - Cliquer sur "Avancé" puis "Accepter le risque"

3. **Se connecter**
   ```
   Utilisateur: QSECOFR (ou utilisateur avec *ALLOBJ)
   Mot de passe: [votre mot de passe]
   ```

4. **Page d'accueil**
   - Vous arrivez sur le tableau de bord principal
   - Navigation à gauche avec toutes les fonctions

### 3. Configuration Initiale de Navigator

#### Étape 3.1: Configurer les Préférences

1. **Cliquer sur l'icône utilisateur** (en haut à droite)
2. **Sélectionner "Preferences"**
3. **Configurer:**
   - Langue: Français
   - Fuseau horaire: Europe/Paris
   - Format de date: JJ/MM/AAAA
   - Rafraîchissement automatique: Activé

#### Étape 3.2: Vérifier les Services

1. **Navigation:** IBM i Management > Work Management > Servers
2. **Vérifier que ces serveurs sont démarrés:**
   - QHTTPSVR (HTTP Server)
   - QUSRWRK (User Work)
   - QSYSWRK (System Work)

---

## Vérification des Prérequis

### 1. Informations Système

#### Étape 1.1: Afficher les Informations Système

1. **Navigation:** IBM i Management > System Values
2. **Ou:** Dashboard > System Information

**Informations à noter:**
```
┌─────────────────────────────────────────────────┐
│ System Information                              │
├─────────────────────────────────────────────────┤
│ System Name:        IBMISOURCE                  │
│ Serial Number:      1234567                     │
│ Model:              9009-42A                    │
│ Processor:          POWER9                      │
│ OS Version:         V7R4M0                      │
│ PTF Level:          SI78544                     │
└─────────────────────────────────────────────────┘
```

#### Étape 1.2: Vérifier les PTFs

1. **Navigation:** IBM i Management > Fixes
2. **Cliquer sur:** "PTF Groups"
3. **Vérifier les groupes installés:**
   - SF99722 (Technology Refresh)
   - SF99713 (Hiper Group)
   - SF99368 (PowerHA Group)

**Capture d'écran type:**
```
┌────────────────────────────────────────────────────────────┐
│ PTF Groups                                    [Refresh]    │
├────────────────────────────────────────────────────────────┤
│ Group ID  │ Level  │ Status    │ Release │ Description    │
├───────────┼────────┼───────────┼─────────┼────────────────┤
│ SF99722   │ 23     │ Installed │ V7R4M0  │ Technology...  │
│ SF99713   │ 45     │ Installed │ V7R4M0  │ Hiper Group    │
│ SF99368   │ 12     │ Installed │ V7R4M0  │ PowerHA Group  │
└────────────────────────────────────────────────────────────┘
```

### 2. Vérification du Stockage

#### Étape 2.1: Afficher l'Espace Disque

1. **Navigation:** IBM i Management > Disk Management > Disk Units
2. **Ou:** Dashboard > Storage

**Vue d'ensemble:**
```
┌─────────────────────────────────────────────────────────────┐
│ Disk Storage Overview                                       │
├─────────────────────────────────────────────────────────────┤
│ ASP  │ Total (GB) │ Used (GB) │ Free (GB) │ Used %        │
├──────┼────────────┼───────────┼───────────┼───────────────┤
│ 1    │ 500.00     │ 250.00    │ 250.00    │ 50.0%  ████   │
│ 2    │ 1000.00    │ 300.00    │ 700.00    │ 30.0%  ███    │
└─────────────────────────────────────────────────────────────┘
```

#### Étape 2.2: Détails des ASP

1. **Cliquer sur un ASP** pour voir les détails
2. **Vérifier:**
   - Protection: RAID 5 ou RAID 6
   - État: Active
   - Compression: Activée (recommandé)

### 3. Vérification du Réseau

#### Étape 3.1: Interfaces Réseau

1. **Navigation:** Network > TCP/IP Configuration > IPv4 > Interfaces
2. **Vérifier les interfaces actives**

**Vue des interfaces:**
```
┌──────────────────────────────────────────────────────────────────┐
│ TCP/IP Interfaces                                  [Add] [Refresh]│
├──────────────────────────────────────────────────────────────────┤
│ Interface │ IP Address    │ Subnet Mask     │ Status │ Line     │
├───────────┼───────────────┼─────────────────┼────────┼──────────┤
│ *LOOPBACK │ 127.0.0.1     │ 255.0.0.0       │ Active │ *LOOPBACK│
│ ETHLINE   │ 192.168.1.10  │ 255.255.255.0   │ Active │ ETHLINE  │
└──────────────────────────────────────────────────────────────────┘
```

#### Étape 3.2: Tester la Connectivité

1. **Navigation:** Network > Utilities > Ping
2. **Tester:**
   - Gateway: 192.168.1.1
   - DNS: 192.168.1.2
   - Partition cible: 192.168.1.11

**Interface Ping:**
```
┌─────────────────────────────────────────────────┐
│ Ping Utility                                    │
├─────────────────────────────────────────────────┤
│ Remote System: [192.168.1.11        ]          │
│ Number of Packets: [10  ]                      │
│ Packet Size: [56   ] bytes                     │
│                                                 │
│ [Start Ping]                                   │
│                                                 │
│ Results:                                        │
│ ┌─────────────────────────────────────────────┐│
│ │ PING 192.168.1.11: 56 data bytes           ││
│ │ 64 bytes from 192.168.1.11: icmp_seq=0     ││
│ │   time=0.5 ms                               ││
│ │ 64 bytes from 192.168.1.11: icmp_seq=1     ││
│ │   time=0.4 ms                               ││
│ │ ...                                         ││
│ │ 10 packets transmitted, 10 received, 0%    ││
│ │ packet loss                                 ││
│ └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

## Configuration du Réseau

### 1. Création de l'Interface de Réplication

#### Étape 1.1: Créer une Nouvelle Ligne Ethernet

1. **Navigation:** Network > TCP/IP Configuration > Lines
2. **Cliquer sur:** "Add" (bouton +)
3. **Remplir le formulaire:**

```
┌─────────────────────────────────────────────────────────┐
│ Create Line Description                                 │
├─────────────────────────────────────────────────────────┤
│ Line Description:                                       │
│   Name: [REPLLINE          ]                           │
│   Text: [Ligne de réplication                    ]     │
│                                                         │
│ Resource:                                               │
│   Resource Name: [CMN05    ] [Browse...]               │
│   Line Type: [Ethernet ▼]                              │
│                                                         │
│ Line Speed:                                             │
│   Speed: [10G ▼]                                       │
│   Duplex: [*FULL ▼]                                    │
│                                                         │
│ Advanced Options:                                       │
│   ☑ Auto-start line                                    │
│   ☐ Enable jumbo frames                                │
│   MTU Size: [1500  ] (9000 pour jumbo frames)         │
│                                                         │
│ [Create]  [Cancel]                                     │
└─────────────────────────────────────────────────────────┘
```

4. **Cliquer sur "Create"**
5. **Attendre la confirmation**

#### Étape 1.2: Activer la Ligne

1. **Dans la liste des lignes**, trouver REPLLINE
2. **Clic droit** sur la ligne
3. **Sélectionner:** "Vary On"
4. **Confirmer** l'action

**État après activation:**
```
┌──────────────────────────────────────────────────────────┐
│ Lines                                      [Add] [Refresh]│
├──────────────────────────────────────────────────────────┤
│ Line      │ Resource │ Type     │ Speed │ Status        │
├───────────┼──────────┼──────────┼───────┼───────────────┤
│ ETHLINE   │ CMN04    │ Ethernet │ 10G   │ Active   ✓    │
│ REPLLINE  │ CMN05    │ Ethernet │ 10G   │ Active   ✓    │
└──────────────────────────────────────────────────────────┘
```

### 2. Configuration de l'Interface IP de Réplication

#### Étape 2.1: Ajouter l'Interface

1. **Navigation:** Network > TCP/IP Configuration > IPv4 > Interfaces
2. **Cliquer sur:** "Add" (bouton +)
3. **Remplir le formulaire:**

**Sur la Partition SOURCE:**
```
┌─────────────────────────────────────────────────────────┐
│ Add TCP/IP Interface                                    │
├─────────────────────────────────────────────────────────┤
│ Internet Address:                                       │
│   [10.0.1.10           ]                               │
│                                                         │
│ Line Description:                                       │
│   [REPLLINE ▼]                                         │
│                                                         │
│ Subnet Mask:                                            │
│   [255.255.255.0       ]                               │
│                                                         │
│ Interface Type:                                         │
│   ⦿ Point-to-Point                                     │
│   ○ Broadcast                                          │
│                                                         │
│ Text Description:                                       │
│   [Interface de réplication                      ]     │
│                                                         │
│ Advanced Options:                                       │
│   MTU: [9000  ] (Jumbo Frames)                        │
│   ☑ Auto-start interface                               │
│   ☐ Preferred interface                                │
│                                                         │
│ [Add]  [Cancel]                                        │
└─────────────────────────────────────────────────────────┘
```

**Sur la Partition CIBLE:**
- Même procédure avec IP: 10.0.1.11

4. **Cliquer sur "Add"**
5. **Attendre la confirmation**

#### Étape 2.2: Démarrer l'Interface

1. **Dans la liste des interfaces**, trouver 10.0.1.10
2. **Clic droit** sur l'interface
3. **Sélectionner:** "Start"
4. **Confirmer** l'action

### 3. Configuration des Routes

#### Étape 3.1: Ajouter une Route pour la Réplication

1. **Navigation:** Network > TCP/IP Configuration > IPv4 > Routes
2. **Cliquer sur:** "Add"
3. **Remplir:**

```
┌─────────────────────────────────────────────────────────┐
│ Add Route                                               │
├─────────────────────────────────────────────────────────┤
│ Route Destination:                                      │
│   ⦿ Network                                            │
│   ○ Host                                               │
│   ○ Default                                            │
│                                                         │
│ Destination Address:                                    │
│   [10.0.1.0            ]                               │
│                                                         │
│ Subnet Mask:                                            │
│   [255.255.255.0       ]                               │
│                                                         │
│ Next Hop:                                               │
│   [*DIRECT             ]                               │
│                                                         │
│ Preferred Interface:                                    │
│   [10.0.1.10 ▼]                                        │
│                                                         │
│ [Add]  [Cancel]                                        │
└─────────────────────────────────────────────────────────┘
```

### 4. Test de Connectivité Réseau

#### Étape 4.1: Ping entre Partitions

1. **Navigation:** Network > Utilities > Ping
2. **Tester la réplication:**
   - Source → Cible: 10.0.1.11
   - Cible → Source: 10.0.1.10

#### Étape 4.2: Test de Bande Passante (Optionnel)

1. **Navigation:** Network > Utilities > Network Performance
2. **Configurer un test entre les deux partitions**
3. **Analyser les résultats**

---

## Configuration du Stockage

### 1. Vérification des Disques

#### Étape 1.1: Vue d'Ensemble des Disques

1. **Navigation:** IBM i Management > Disk Management > Disk Units
2. **Vérifier:**
   - Tous les disques sont "Active"
   - Pas d'erreurs
   - Protection configurée (RAID)

**Vue des disques:**
```
┌──────────────────────────────────────────────────────────────────┐
│ Disk Units                                       [Add] [Refresh] │
├──────────────────────────────────────────────────────────────────┤
│ Unit │ Resource │ Type  │ Size (GB) │ ASP │ Status │ Protection │
├──────┼──────────┼───────┼───────────┼─────┼────────┼────────────┤
│ 1    │ DMP01    │ SAS   │ 300       │ 1   │ Active │ RAID 5     │
│ 2    │ DMP02    │ SAS   │ 300       │ 1   │ Active │ RAID 5     │
│ 3    │ DMP03    │ SAS   │ 300       │ 1   │ Active │ RAID 5     │
│ 4    │ DMP04    │ SAS   │ 600       │ 2   │ Active │ RAID 6     │
│ 5    │ DMP05    │ SAS   │ 600       │ 2   │ Active │ RAID 6     │
└──────────────────────────────────────────────────────────────────┘
```

### 2. Configuration des ASP

#### Étape 2.1: Créer un ASP Utilisateur (si nécessaire)

1. **Navigation:** IBM i Management > Disk Management > ASPs
2. **Cliquer sur:** "Add ASP"
3. **Remplir:**

```
┌─────────────────────────────────────────────────────────┐
│ Create Auxiliary Storage Pool                          │
├─────────────────────────────────────────────────────────┤
│ ASP Number:                                             │
│   [2   ] (2-32 pour User ASP)                          │
│                                                         │
│ ASP Type:                                               │
│   ⦿ Basic ASP                                          │
│   ○ Independent ASP (IASP)                             │
│                                                         │
│ Disk Units:                                             │
│   Available Disks:        Selected Disks:              │
│   ┌──────────────┐       ┌──────────────┐             │
│   │ DMP04 (600GB)│  >>>  │              │             │
│   │ DMP05 (600GB)│  <<<  │              │             │
│   │              │       │              │             │
│   └──────────────┘       └──────────────┘             │
│                                                         │
│ Protection:                                             │
│   [RAID 6 ▼]                                           │
│                                                         │
│ [Create]  [Cancel]                                     │
└─────────────────────────────────────────────────────────┘
```

### 3. Monitoring du Stockage

#### Étape 3.1: Configurer les Alertes

1. **Navigation:** IBM i Management > Disk Management > Thresholds
2. **Configurer les seuils:**
   - Avertissement: 80% utilisé
   - Critique: 90% utilisé

```
┌─────────────────────────────────────────────────────────┐
│ Storage Thresholds                                      │
├─────────────────────────────────────────────────────────┤
│ ASP │ Warning (%) │ Critical (%) │ Action              │
├─────┼─────────────┼──────────────┼─────────────────────┤
│ 1   │ [80  ]      │ [90   ]      │ ☑ Send email       │
│ 2   │ [80  ]      │ [90   ]      │ ☑ Send email       │
│                                                         │
│ Email Recipients:                                       │
│   [admin@example.com                              ]    │
│                                                         │
│ [Save]  [Cancel]                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration PowerHA SystemMirror

### 1. Installation de PowerHA

#### Étape 1.1: Vérifier l'Installation

1. **Navigation:** IBM i Management > Licensed Programs
2. **Rechercher:** 5770-XE1 (PowerHA SystemMirror)
3. **Si non installé:**
   - Cliquer sur "Install Licensed Programs"
   - Sélectionner 5770-XE1
   - Suivre l'assistant d'installation

### 2. Configuration du Cluster

#### Étape 2.1: Créer un Nouveau Cluster

1. **Navigation:** High Availability > Clusters
2. **Cliquer sur:** "New Cluster"
3. **Assistant de création:**

**Page 1: Informations de Base**
```
┌─────────────────────────────────────────────────────────┐
│ Create Cluster - Step 1 of 5                           │
├─────────────────────────────────────────────────────────┤
│ Cluster Name:                                           │
│   [MIGRCLUSTER                                    ]    │
│                                                         │
│ Cluster Type:                                           │
│   ⦿ Geographic Mirroring                               │
│   ○ Switchable                                         │
│   ○ Resilient                                          │
│                                                         │
│ Description:                                            │
│   [Cluster pour migration IBM i                   ]    │
│                                                         │
│ [Next >]  [Cancel]                                     │
└─────────────────────────────────────────────────────────┘
```

**Page 2: Nœuds du Cluster**
```
┌─────────────────────────────────────────────────────────┐
│ Create Cluster - Step 2 of 5                           │
├─────────────────────────────────────────────────────────┤
│ Cluster Nodes:                                          │
│                                                         │
│ Primary Node:                                           │
│   System Name: [IBMISOURCE        ]                    │
│   IP Address:  [10.0.1.10         ]                    │
│   Role: Primary                                         │
│                                                         │
│ [Add Node]                                             │
│                                                         │
│ Backup Node:                                            │
│   System Name: [IBMICIBLE         ]                    │
│   IP Address:  [10.0.1.11         ]                    │
│   Role: Backup                                          │
│                                                         │
│ [< Back]  [Next >]  [Cancel]                           │
└─────────────────────────────────────────────────────────┘
```

**Page 3: Configuration Réseau**
```
┌─────────────────────────────────────────────────────────┐
│ Create Cluster - Step 3 of 5                           │
├─────────────────────────────────────────────────────────┤
│ Network Configuration:                                  │
│                                                         │
│ Heartbeat Interface:                                    │
│   Primary:   [10.0.1.10 ▼]                             │
│   Backup:    [10.0.1.11 ▼]                             │
│   Interval:  [1000  ] ms                               │
│   Timeout:   [5000  ] ms                               │
│                                                         │
│ Data Replication Interface:                             │
│   Primary:   [10.0.1.10 ▼]                             │
│   Backup:    [10.0.1.11 ▼]                             │
│   Port:      [3000  ]                                  │
│                                                         │
│ [< Back]  [Next >]  [Cancel]                           │
└─────────────────────────────────────────────────────────┘
```

**Page 4: Options de Réplication**
```
┌─────────────────────────────────────────────────────────┐
│ Create Cluster - Step 4 of 5                           │
├─────────────────────────────────────────────────────────┤
│ Replication Options:                                    │
│                                                         │
│ Replication Mode:                                       │
│   ⦿ Asynchronous (Recommended)                         │
│   ○ Synchronous                                        │
│                                                         │
│ Data to Replicate:                                      │
│   ☑ System ASP (ASP 1)                                 │
│   ☑ User ASP 2                                         │
│   ☐ User ASP 3                                         │
│                                                         │
│ Compression:                                            │
│   ☑ Enable compression                                 │
│   Level: [6 ▼] (1-9)                                   │
│                                                         │
│ [< Back]  [Next >]  [Cancel]                           │
└─────────────────────────────────────────────────────────┘
```

**Page 5: Résumé et Création**
```
┌─────────────────────────────────────────────────────────┐
│ Create Cluster - Step 5 of 5                           │
├─────────────────────────────────────────────────────────┤
│ Summary:                                                │
│                                                         │
│ Cluster Name:     MIGRCLUSTER                          │
│ Type:             Geographic Mirroring                  │
│ Primary Node:     IBMISOURCE (10.0.1.10)               │
│ Backup Node:      IBMICIBLE (10.0.1.11)                │
│ Replication Mode: Asynchronous                          │
│ ASPs to Replicate: 1, 2                                │
│                                                         │
│ ⚠ Warning: Creating the cluster will:                  │
│   - Configure cluster resources                         │
│   - Start replication services                          │
│   - Begin initial synchronization                       │
│                                                         │
│ [< Back]  [Create]  [Cancel]                           │
└─────────────────────────────────────────────────────────┘
```

4. **Cliquer sur "Create"**
5. **Attendre la création** (peut prendre plusieurs minutes)

### 3. Configuration du Groupe de Réplication (CRG)

#### Étape 3.1: Créer un CRG

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Onglet:** "Cluster Resource Groups"
3. **Cliquer sur:** "New CRG"

```
┌─────────────────────────────────────────────────────────┐
│ Create Cluster Resource Group                          │
├─────────────────────────────────────────────────────────┤
│ CRG Name:                                               │
│   [MIGRATIONCRG                                   ]    │
│                                                         │
│ CRG Type:                                               │
│   ⦿ Device CRG (for disk replication)                  │
│   ○ Application CRG                                    │
│   ○ Data CRG                                           │
│                                                         │
│ Description:                                            │
│   [Groupe de réplication pour migration           ]    │
│                                                         │
│ Primary Node:                                           │
│   [IBMISOURCE ▼]                                       │
│                                                         │
│ Backup Nodes:                                           │
│   ☑ IBMICIBLE                                          │
│                                                         │
│ Recovery Domain:                                        │
│   ⦿ All nodes                                          │
│   ○ Selected nodes                                     │
│                                                         │
│ [Create]  [Cancel]                                     │
└─────────────────────────────────────────────────────────┘
```

#### Étape 3.2: Ajouter des Ressources au CRG

1. **Sélectionner le CRG** MIGRATIONCRG
2. **Onglet:** "Resources"
3. **Cliquer sur:** "Add Resources"

```
┌─────────────────────────────────────────────────────────┐
│ Add Resources to CRG                                    │
├─────────────────────────────────────────────────────────┤
│ Resource Type:                                          │
│   ⦿ Disk Units (ASP)                                   │
│   ○ IP Addresses                                       │
│   ○ Applications                                       │
│                                                         │
│ Select ASPs to Replicate:                               │
│   ☑ ASP 1 (System)                                     │
│   ☑ ASP 2 (User Data)                                  │
│   ☐ ASP 3                                              │
│                                                         │
│ Replication Options:                                    │
│   Sync Mode: [Asynchronous ▼]                          │
│   Priority:  [Normal ▼]                                │
│                                                         │
│ [Add]  [Cancel]                                        │
└─────────────────────────────────────────────────────────┘
```

### 4. Démarrage de la Réplication

#### Étape 4.1: Démarrer le Cluster

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Clic droit** sur le cluster
3. **Sélectionner:** "Start Cluster"
4. **Confirmer** l'action

**Progression:**
```
┌─────────────────────────────────────────────────────────┐
│ Starting Cluster                                        │
├─────────────────────────────────────────────────────────┤
│ Progress:                                               │
│ ████████████████████████████████████░░░░░░░░ 80%       │
│                                                         │
│ Current Step:                                           │
│ Starting cluster services on IBMICIBLE...              │
│                                                         │
│ Completed Steps:                                        │
│ ✓ Validating cluster configuration                     │
│ ✓ Starting cluster services on IBMISOURCE              │
│ ✓ Establishing heartbeat connection                    │
│ ⏳ Starting cluster services on IBMICIBLE              │
│                                                         │
│ [View Details]                                         │
└─────────────────────────────────────────────────────────┘
```

#### Étape 4.2: Démarrer le CRG

1. **Sélectionner** MIGRATIONCRG
2. **Clic droit** > "Start CRG"
3. **Confirmer**

**Options de démarrage:**
```
┌─────────────────────────────────────────────────────────┐
│ Start Cluster Resource Group                           │
├─────────────────────────────────────────────────────────┤
│ CRG: MIGRATIONCRG                                       │
│                                                         │
│ Start Options:                                          │
│   ⦿ Normal start                                       │
│   ○ Force start (skip validation)                      │
│                                                         │
│ Initial Synchronization:                                │
│   ⦿ Full synchronization                               │
│   ○ Incremental synchronization                        │
│   ○ Skip synchronization                               │
│                                                         │
│ ⚠ Full synchronization may take several hours          │
│   depending on data size.                               │
│                                                         │
│ [Start]  [Cancel]                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Monitoring et Validation

### 1. Tableau de Bord PowerHA

#### Étape 1.1: Vue d'Ensemble du Cluster

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Onglet:** "Dashboard"

**Tableau de bord:**
```
┌──────────────────────────────────────────────────────────────────┐
│ Cluster Dashboard - MIGRCLUSTER                    [Refresh: 30s]│
├──────────────────────────────────────────────────────────────────┤
│ Cluster Status: ● Active                                         │
│ Replication Status: ● Synchronizing (45% complete)               │
│ Last Update: 2025-12-17 16:30:15                                │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Nodes                                                      │  │
│ ├────────────────────────────────────────────────────────────┤  │
│ │ Node         │ Role    │ Status  │ Heartbeat │ Last Seen │  │
│ ├──────────────┼─────────┼─────────┼───────────┼───────────┤  │
│ │ IBMISOURCE   │ Primary │ ● Active│ ● OK      │ 1s ago    │  │
│ │ IBMICIBLE    │ Backup  │ ● Active│ ● OK      │ 1s ago    │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Replication Status                                         │  │
│ ├────────────────────────────────────────────────────────────┤  │
│ │ ASP │ Size (GB) │ Synced (GB) │ Progress │ Lag (sec)    │  │
│ ├─────┼───────────┼─────────────┼──────────┼──────────────┤  │
│ │ 1   │ 250       │ 112         │ 45% ████ │ 2.3          │  │
│ │ 2   │ 300       │ 135         │ 45% ████ │ 2.1          │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Performance Metrics                                        │  │
│ ├────────────────────────────────────────────────────────────┤  │
│ │ Replication Rate: 125 MB/s                                │  │
│ │ Network Latency: 0.8 ms                                   │  │
│ │ Queue Depth: 234 operations                               │  │
│ └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 2. Monitoring de la Synchronisation

#### Étape 2.1: Détails de la Synchronisation

1. **Cliquer sur** un ASP dans le tableau de bord
2. **Voir les détails:**

```
┌──────────────────────────────────────────────────────────────────┐
│ ASP 1 Replication Details                                        │
├──────────────────────────────────────────────────────────────────┤
│ Status: Synchronizing                                            │
│ Progress: ████████████████████░░░░░░░░░░░░░░░░░░░░ 45%          │
│                                                                  │
│ Statistics:                                                      │
│   Total Size:        250.00 GB                                  │
│   Synchronized:      112.50 GB                                  │
│   Remaining:         137.50 GB                                  │
│   Estimated Time:    2h 15m                                     │
│                                                                  │
│ Performance:                                                     │
│   Current Rate:      125 MB/s                                   │
│   Average Rate:      118 MB/s                                   │
│   Peak Rate:         145 MB/s                                   │
│                                                                  │
│ Replication Lag:                                                 │
│   Current:           2.3 seconds                                │
│   Average:           2.1 seconds                                │
│   Maximum:           5.8 seconds                                │
│                                                                  │
│ [View History]  [Pause]  [Resume]                               │
└──────────────────────────────────────────────────────────────────┘
```

### 3. Alertes et Notifications

#### Étape 3.1: Configurer les Alertes

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Onglet:** "Alerts"
3. **Cliquer sur:** "Configure Alerts"

```
┌─────────────────────────────────────────────────────────┐
│ Configure Cluster Alerts                                │
├─────────────────────────────────────────────────────────┤
│ Alert Conditions:                                       │
│   ☑ Node failure                                       │
│   ☑ Heartbeat timeout                                  │
│   ☑ Replication lag > [10  ] seconds                   │
│   ☑ Synchronization failure                            │
│   ☑ Network connectivity issues                        │
│                                                         │
│ Notification Methods:                                   │
│   ☑ Email                                              │
│     Recipients: [admin@example.com              ]      │
│                                                         │
│   ☑ System message                                     │
│     Message Queue: [QSYSOPR ▼]                         │
│                                                         │
│   ☐ SNMP trap                                          │
│   ☐ Webhook                                            │
│                                                         │
│ [Save]  [Cancel]                                       │
└─────────────────────────────────────────────────────────┘
```

### 4. Rapports

#### Étape 4.1: Générer un Rapport

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Onglet:** "Reports"
3. **Cliquer sur:** "Generate Report"

```
┌─────────────────────────────────────────────────────────┐
│ Generate Cluster Report                                 │
├─────────────────────────────────────────────────────────┤
│ Report Type:                                            │
│   ⦿ Status Report                                      │
│   ○ Performance Report                                 │
│   ○ Historical Report                                  │
│   ○ Configuration Report                               │
│                                                         │
│ Time Period:                                            │
│   From: [2025-12-17 00:00] [📅]                        │
│   To:   [2025-12-17 23:59] [📅]                        │
│                                                         │
│ Format:                                                 │
│   ⦿ HTML                                               │
│   ○ PDF                                                │
│   ○ CSV                                                │
│                                                         │
│ Include:                                                │
│   ☑ Cluster configuration                              │
│   ☑ Node status                                        │
│   ☑ Replication statistics                             │
│   ☑ Performance metrics                                │
│   ☑ Alert history                                      │
│                                                         │
│ [Generate]  [Cancel]                                   │
└─────────────────────────────────────────────────────────┘
```

---

## Procédure de Migration

### 1. Préparation Finale

#### Étape 1.1: Vérification Pré-Migration

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Onglet:** "Pre-Migration Checks"
3. **Cliquer sur:** "Run Checks"

```
┌──────────────────────────────────────────────────────────────────┐
│ Pre-Migration Checks                                             │
├──────────────────────────────────────────────────────────────────┤
│ Check                              │ Status    │ Details         │
├────────────────────────────────────┼───────────┼─────────────────┤
│ Cluster Status                     │ ✓ Pass    │ Active          │
│ Replication Synchronization        │ ✓ Pass    │ 100% synced     │
│ Network Connectivity               │ ✓ Pass    │ All links OK    │
│ Disk Space                         │ ✓ Pass    │ Sufficient      │
│ Active Jobs                        │ ⚠ Warning │ 45 active jobs  │
│ Backup Status                      │ ✓ Pass    │ < 24h old       │
│ PTF Levels                         │ ✓ Pass    │ Up to date      │
│                                                                  │
│ Overall Status: ✓ Ready for Migration                           │
│                                                                  │
│ ⚠ Warning: 45 active jobs detected. Consider stopping           │
│   non-critical jobs before migration.                            │
│                                                                  │
│ [View Details]  [Export Report]                                 │
└──────────────────────────────────────────────────────────────────┘
```

#### Étape 1.2: Notification aux Utilisateurs

1. **Navigation:** IBM i Management > Messages
2. **Cliquer sur:** "Send Break Message"

```
┌─────────────────────────────────────────────────────────┐
│ Send Break Message                                      │
├─────────────────────────────────────────────────────────┤
│ Message:                                                │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ATTENTION: Migration système prévue dans 30 minutes││
│ │                                                     ││
│ │ Le système sera indisponible pendant environ       ││
│ │ 5 minutes à partir de 20h00.                       ││
│ │                                                     ││
│ │ Merci de sauvegarder votre travail et de vous     ││
│ │ déconnecter avant 19h55.                           ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ Send To:                                                │
│   ⦿ All workstations (*ALLWS)                          │
│   ○ Specific users                                     │
│                                                         │
│ [Send]  [Cancel]                                       │
└─────────────────────────────────────────────────────────┘
```

### 2. Arrêt Contrôlé

#### Étape 2.1: Arrêter les Subsystèmes

1. **Navigation:** IBM i Management > Work Management > Subsystems
2. **Sélectionner les subsystèmes applicatifs**
3. **Clic droit** > "End Subsystem"

```
┌─────────────────────────────────────────────────────────┐
│ End Subsystem                                           │
├─────────────────────────────────────────────────────────┤
│ Subsystem: QBATCH                                       │
│                                                         │
│ End Option:                                             │
│   ⦿ Controlled (*CNTRLD) - Wait for jobs to complete   │
│   ○ Immediate (*IMMED) - End jobs immediately          │
│                                                         │
│ Delay Time:                                             │
│   [300  ] seconds                                      │
│                                                         │
│ Active Jobs: 12                                         │
│                                                         │
│ [End]  [Cancel]                                        │
└─────────────────────────────────────────────────────────┘
```

#### Étape 2.2: Synchronisation Finale

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Sélectionner** MIGRATIONCRG
3. **Clic droit** > "Force Synchronization"

```
┌─────────────────────────────────────────────────────────┐
│ Force Synchronization                                   │
├─────────────────────────────────────────────────────────┤
│ This will force a final synchronization of all data    │
│ before migration.                                       │
│                                                         │
│ Current Replication Lag: 2.1 seconds                   │
│ Estimated Sync Time: 30 seconds                        │
│                                                         │
│ ⚠ Warning: This will temporarily pause replication     │
│   to ensure data consistency.                           │
│                                                         │
│ [Start Sync]  [Cancel]                                 │
└─────────────────────────────────────────────────────────┘
```

**Progression:**
```
┌─────────────────────────────────────────────────────────┐
│ Synchronization Progress                                │
├─────────────────────────────────────────────────────────┤
│ ████████████████████████████████████████████ 100%      │
│                                                         │
│ Status: Synchronization Complete                       │
│ Time Elapsed: 28 seconds                               │
│ Data Synchronized: 2.3 GB                              │
│                                                         │
│ ✓ All ASPs are now synchronized                        │
│ ✓ Replication lag: 0 seconds                           │
│                                                         │
│ [Close]                                                │
└─────────────────────────────────────────────────────────┘
```

### 3. Basculement (Switchover)

#### Étape 3.1: Initier le Basculement

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Clic droit** sur le cluster
3. **Sélectionner:** "Switchover"

```
┌─────────────────────────────────────────────────────────┐
│ Cluster Switchover                                      │
├─────────────────────────────────────────────────────────┤
│ Current Primary Node: IBMISOURCE                        │
│ New Primary Node:     IBMICIBLE                         │
│                                                         │
│ Switchover Type:                                        │
│   ⦿ Planned Switchover (Recommended)                   │
│   ○ Forced Switchover                                  │
│                                                         │
│ Pre-Switchover Checks:                                  │
│   ✓ Synchronization complete                           │
│   ✓ Target node ready                                  │
│   ✓ Network connectivity OK                            │
│   ✓ Sufficient resources                               │
│                                                         │
│ Estimated Downtime: 2-5 minutes                        │
│                                                         │
│ ⚠ Warning: This will make IBMICIBLE the primary node   │
│   and IBMISOURCE will become the backup node.           │
│                                                         │
│ [Start Switchover]  [Cancel]                           │
└─────────────────────────────────────────────────────────┘
```

#### Étape 3.2: Suivre la Progression

```
┌──────────────────────────────────────────────────────────────────┐
│ Switchover Progress                                              │
├──────────────────────────────────────────────────────────────────┤
│ Step 1/6: Preparing for switchover                    ✓ Complete │
│ Step 2/6: Stopping applications on source             ✓ Complete │
│ Step 3/6: Final synchronization                       ✓ Complete │
│ Step 4/6: Switching roles                             ⏳ In Progress│
│ Step 5/6: Starting applications on target             ⏸ Pending  │
│ Step 6/6: Verifying switchover                        ⏸ Pending  │
│                                                                  │
│ Current Step Details:                                            │
│ Switching cluster roles...                                       │
│ - Deactivating primary role on IBMISOURCE                       │
│ - Activating primary role on IBMICIBLE                          │
│                                                                  │
│ Elapsed Time: 2m 15s                                            │
│ Estimated Remaining: 1m 30s                                     │
│                                                                  │
│ [View Detailed Log]                                             │
└──────────────────────────────────────────────────────────────────┘
```

### 4. Validation Post-Migration

#### Étape 4.1: Vérification Automatique

```
┌──────────────────────────────────────────────────────────────────┐
│ Post-Switchover Validation                                       │
├──────────────────────────────────────────────────────────────────┤
│ Switchover Status: ✓ Complete                                   │
│ Total Time: 3m 42s                                              │
│                                                                  │
│ Validation Results:                                              │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Check                          │ Status    │ Details       │  │
│ ├────────────────────────────────┼───────────┼───────────────┤  │
│ │ New Primary Node Active        │ ✓ Pass    │ IBMICIBLE     │  │
│ │ Network Connectivity           │ ✓ Pass    │ All OK        │  │
│ │ Disk Access                    │ ✓ Pass    │ All ASPs OK   │  │
│ │ TCP/IP Services                │ ✓ Pass    │ Started       │  │
│ │ Subsystems                     │ ✓ Pass    │ Started       │  │
│ │ Replication Status             │ ✓ Pass    │ Active        │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│ New Cluster Configuration:                                       │
│   Primary Node:  IBMICIBLE (10.0.1.11)                          │
│   Backup Node:   IBMISOURCE (10.0.1.10)                         │
│   Status:        Active                                          │
│                                                                  │
│ [Generate Report]  [Close]                                      │
└──────────────────────────────────────────────────────────────────┘
```

#### Étape 4.2: Tests Manuels

1. **Test de Connectivité**
   - Navigation: Network > Utilities > Ping
   - Tester: Gateway, DNS, clients

2. **Test d'Accès Utilisateur**
   - Demander à des utilisateurs de test de se connecter
   - Vérifier l'accès aux applications

3. **Test de Performance**
   - Navigation: Performance > System Status
   - Vérifier CPU, mémoire, I/O

---

## Dépannage

### 1. Problèmes de Synchronisation

#### Symptôme: Synchronisation Lente

**Diagnostic via Navigator:**
1. Navigation: High Availability > Clusters > MIGRCLUSTER
2. Onglet: "Performance"
3. Vérifier:
   - Taux de réplication
   - Latence réseau
   - Profondeur de la file d'attente

**Solutions:**
```
┌─────────────────────────────────────────────────────────┐
│ Replication Performance Tuning                          │
├─────────────────────────────────────────────────────────┤
│ Current Performance:                                    │
│   Rate: 45 MB/s (Expected: 100+ MB/s)                  │
│   Latency: 15 ms (Expected: < 5 ms)                    │
│                                                         │
│ Recommendations:                                        │
│   ⚠ Network latency is high                            │
│     → Check network configuration                       │
│     → Verify no bandwidth contention                    │
│                                                         │
│   ⚠ Replication rate is low                            │
│     → Increase compression level                        │
│     → Check disk I/O performance                        │
│                                                         │
│ Actions:                                                │
│   [Adjust Compression]                                 │
│   [Network Diagnostics]                                │
│   [View Detailed Metrics]                              │
└─────────────────────────────────────────────────────────┘
```

### 2. Problèmes de Basculement

#### Symptôme: Échec du Switchover

**Diagnostic:**
1. Navigation: High Availability > Clusters > MIGRCLUSTER
2. Onglet: "Events"
3. Filtrer: "Errors"

```
┌──────────────────────────────────────────────────────────────────┐
│ Cluster Events - Errors                                          │
├──────────────────────────────────────────────────────────────────┤
│ Time       │ Severity │ Event                    │ Details       │
├────────────┼──────────┼──────────────────────────┼───────────────┤
│ 20:05:23   │ ERROR    │ Switchover failed        │ View details  │
│ 20:05:22   │ WARNING  │ Target node not ready    │ View details  │
│ 20:05:15   │ INFO     │ Switchover initiated     │ View details  │
└──────────────────────────────────────────────────────────────────┘
```

**Cliquer sur "View details":**
```
┌─────────────────────────────────────────────────────────┐
│ Event Details                                           │
├─────────────────────────────────────────────────────────┤
│ Event: Switchover failed                                │
│ Time: 2025-12-17 20:05:23                              │
│ Severity: ERROR                                         │
│                                                         │
│ Error Message:                                          │
│ Target node IBMICIBLE is not ready to become primary.  │
│ Reason: Insufficient memory available.                 │
│                                                         │
│ Recommended Actions:                                    │
│ 1. Check memory usage on target node                   │
│ 2. End unnecessary jobs                                │
│ 3. Increase memory allocation if possible              │
│ 4. Retry switchover                                    │
│                                                         │
│ [View Target Node Status]  [Retry Switchover]         │
└─────────────────────────────────────────────────────────┘
```

### 3. Rollback

#### Étape 3.1: Annuler le Basculement

Si le basculement échoue ou si vous devez revenir en arrière:

1. **Navigation:** High Availability > Clusters > MIGRCLUSTER
2. **Clic droit** > "Switchback"

```
┌─────────────────────────────────────────────────────────┐
│ Cluster Switchback                                      │
├─────────────────────────────────────────────────────────┤
│ Current Primary Node: IBMICIBLE                         │
│ Original Primary Node: IBMISOURCE                       │
│                                                         │
│ This will switch back to the original configuration.   │
│                                                         │
│ Switchback Type:                                        │
│   ⦿ Planned Switchback                                 │
│   ○ Emergency Switchback                               │
│                                                         │
│ Pre-Switchback Checks:                                  │
│   ✓ Original node available                            │
│   ✓ Data synchronized                                  │
│   ✓ Network connectivity OK                            │
│                                                         │
│ [Start Switchback]  [Cancel]                           │
└─────────────────────────────────────────────────────────┘
```

---

## Annexes

### Annexe A: Raccourcis Navigator for i

**Raccourcis Clavier:**
- `Ctrl + F`: Recherche
- `F5`: Rafraîchir
- `Ctrl + H`: Aide
- `Ctrl + P`: Imprimer
- `Esc`: Fermer dialogue

**Favoris:**
- Ajouter aux favoris: Clic droit > "Add to Favorites"
- Gérer les favoris: Menu > "Favorites"

### Annexe B: URLs Utiles

```
Navigator for i:
https://[ip]:2001/navigator

IBM i Access Client Solutions:
https://[ip]:2001/acs

Performance Tools:
https://[ip]:2001/navigator/performance

System Logs:
https://[ip]:2001/navigator/logs
```

### Annexe C: Ports Réseau

```
Port 2001: Navigator for i (HTTPS)
Port 2005: PowerHA Communication
Port 3000-3010: Réplication de données
Port 449: AS/400 Remote Command
Port 8470-8476: IBM i Access
```

---

## Conclusion

Ce guide vous a montré comment configurer et gérer IBM i Migrate While Active entièrement via Navigator for i. L'interface graphique simplifie grandement la configuration et le monitoring par rapport aux commandes CL traditionnelles.

**Points Clés:**
- ✅ Interface intuitive et moderne
- ✅ Monitoring en temps réel
- ✅ Assistants de configuration
- ✅ Validation automatique
- ✅ Rapports détaillés

**Prochaines Étapes:**
1. Pratiquer dans un environnement de test
2. Documenter votre configuration spécifique
3. Former les équipes d'exploitation
4. Planifier la migration en production

Pour plus d'informations, consultez:
- IBM i Information Center
- IBM Navigator for i Documentation
- PowerHA SystemMirror Documentation

---

**Document créé le**: 2025-12-17  
**Version**: 1.0  
**Auteur**: IBM i Technical Team