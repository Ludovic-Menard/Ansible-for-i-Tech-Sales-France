# Guide Rapide - IBM i Migrate While Active via Navigator for i

## 🚀 Démarrage Rapide en 10 Étapes

Ce guide vous permet de configurer rapidement la migration en suivant les étapes essentielles.

---

## Étape 1: Accès à Navigator for i (5 min)

### 1.1 Démarrer le serveur HTTP (si nécessaire)

**Via 5250:**
```
STRTCPSVR SERVER(*HTTP) HTTPSVR(*ADMIN)
```

### 1.2 Se connecter

**URL:** `https://192.168.1.10:2001/navigator`

**Credentials:**
- Utilisateur: `QSECOFR`
- Mot de passe: `[votre mot de passe]`

**Interface d'accueil:**
```
┌────────────────────────────────────────────────────────────────┐
│ IBM Navigator for i                          [User] [Settings] │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   System     │  │   Network    │  │ High Avail.  │        │
│  │   Status     │  │   Config     │  │   Clusters   │        │
│  │              │  │              │  │              │        │
│  │   ● Active   │  │   ✓ OK       │  │   ⚠ Setup   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│  Quick Links:                                                  │
│  • Work Management                                             │
│  • Disk Management                                             │
│  • TCP/IP Configuration                                        │
│  • PowerHA SystemMirror                                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Étape 2: Vérifier les Prérequis (10 min)

### 2.1 Vérifier la version IBM i

**Navigation:** `Dashboard > System Information`

**À vérifier:**
- ✅ Version: 7.2 ou supérieur
- ✅ PTF Groups à jour
- ✅ Espace disque > 200 GB libre

### 2.2 Checklist rapide

```
☐ IBM i 7.2+ sur les deux partitions
☐ PowerHA (5770-XE1) installé
☐ Espace disque suffisant (>200 GB libre)
☐ Réseau 10 Gbps configuré
☐ Sauvegarde récente (<24h)
```

---

## Étape 3: Configuration Réseau de Réplication (15 min)

### 3.1 Créer la ligne Ethernet

**Navigation:** `Network > TCP/IP Configuration > Lines > Add`

**Paramètres:**
```
Name:         REPLLINE
Resource:     CMN05
Speed:        10G
Duplex:       *FULL
MTU:          9000 (Jumbo Frames)
```

### 3.2 Ajouter l'interface IP

**Navigation:** `Network > TCP/IP Configuration > IPv4 > Interfaces > Add`

**Partition SOURCE:**
```
IP Address:   10.0.1.10
Line:         REPLLINE
Subnet Mask:  255.255.255.0
MTU:          9000
```

**Partition CIBLE:**
```
IP Address:   10.0.1.11
Line:         REPLLINE
Subnet Mask:  255.255.255.0
MTU:          9000
```

### 3.3 Tester la connectivité

**Navigation:** `Network > Utilities > Ping`

```
Source → Cible:  ping 10.0.1.11 (100 packets)
Cible → Source:  ping 10.0.1.10 (100 packets)

✓ Résultat attendu: 0% packet loss, latence < 5ms
```

---

## Étape 4: Configuration PowerHA - Cluster (20 min)

### 4.1 Créer le cluster

**Navigation:** `High Availability > Clusters > New Cluster`

**Assistant - Page 1/5:**
```
Cluster Name:     MIGRCLUSTER
Type:             Geographic Mirroring
Description:      Cluster pour migration
```

**Assistant - Page 2/5:**
```
Primary Node:     IBMISOURCE (10.0.1.10)
Backup Node:      IBMICIBLE (10.0.1.11)
```

**Assistant - Page 3/5:**
```
Heartbeat Interface:
  Primary:        10.0.1.10
  Backup:         10.0.1.11
  Interval:       1000 ms
  Timeout:        5000 ms

Data Replication:
  Primary:        10.0.1.10
  Backup:         10.0.1.11
  Port:           3000
```

**Assistant - Page 4/5:**
```
Replication Mode: Asynchronous
ASPs to Replicate:
  ☑ ASP 1 (System)
  ☑ ASP 2 (User Data)
Compression:      Level 6
```

**Assistant - Page 5/5:**
```
Review and Create
[Create Cluster]
```

---

## Étape 5: Configuration PowerHA - CRG (15 min)

### 5.1 Créer le Cluster Resource Group

**Navigation:** `High Availability > Clusters > MIGRCLUSTER > New CRG`

**Paramètres:**
```
CRG Name:         MIGRATIONCRG
Type:             Device CRG
Primary Node:     IBMISOURCE
Backup Nodes:     IBMICIBLE
Recovery Domain:  All nodes
```

### 5.2 Ajouter les ressources

**Sélectionner:** `MIGRATIONCRG > Resources > Add Resources`

```
Resource Type:    Disk Units (ASP)
ASPs:
  ☑ ASP 1 (System)
  ☑ ASP 2 (User Data)
Sync Mode:        Asynchronous
Priority:         Normal
```

---

## Étape 6: Démarrer la Réplication (5 min)

### 6.1 Démarrer le cluster

**Navigation:** `High Availability > Clusters > MIGRCLUSTER`

**Actions:**
1. Clic droit sur `MIGRCLUSTER`
2. Sélectionner `Start Cluster`
3. Confirmer

### 6.2 Démarrer le CRG

**Actions:**
1. Sélectionner `MIGRATIONCRG`
2. Clic droit > `Start CRG`
3. Options:
   - Start Type: `Normal start`
   - Initial Sync: `Full synchronization`
4. Cliquer `Start`

**Progression attendue:**
```
┌────────────────────────────────────────────────┐
│ Starting CRG...                                │
│ ████████████████████░░░░░░░░░░░░ 60%          │
│                                                │
│ Current: Starting replication services...      │
│ Estimated time: 2 minutes remaining            │
└────────────────────────────────────────────────┘
```

---

## Étape 7: Monitoring de la Synchronisation (Variable)

### 7.1 Tableau de bord

**Navigation:** `High Availability > Clusters > MIGRCLUSTER > Dashboard`

**Métriques à surveiller:**
```
┌─────────────────────────────────────────────────┐
│ Replication Status                              │
├─────────────────────────────────────────────────┤
│ ASP 1: ████████████████░░░░░░░░░░ 65%          │
│        Synced: 162 GB / 250 GB                  │
│        Rate: 125 MB/s                           │
│        ETA: 1h 15m                              │
│                                                 │
│ ASP 2: ████████████████░░░░░░░░░░ 65%          │
│        Synced: 195 GB / 300 GB                  │
│        Rate: 118 MB/s                           │
│        ETA: 1h 20m                              │
│                                                 │
│ Replication Lag: 2.3 seconds                   │
│ Network Latency: 0.8 ms                        │
└─────────────────────────────────────────────────┘
```

### 7.2 Attendre la synchronisation complète

**Critères de validation:**
- ✅ Progress: 100% pour tous les ASPs
- ✅ Replication Lag: < 5 secondes
- ✅ Status: "Synchronized"

---

## Étape 8: Vérifications Pré-Migration (10 min)

### 8.1 Exécuter les vérifications

**Navigation:** `High Availability > Clusters > MIGRCLUSTER > Pre-Migration Checks`

**Cliquer:** `Run Checks`

**Résultats attendus:**
```
┌─────────────────────────────────────────────────┐
│ Pre-Migration Checks                            │
├─────────────────────────────────────────────────┤
│ ✓ Cluster Status: Active                       │
│ ✓ Replication: 100% synchronized               │
│ ✓ Network: All links OK                        │
│ ✓ Disk Space: Sufficient                       │
│ ✓ Backup: < 24h old                            │
│ ✓ PTF Levels: Up to date                       │
│                                                 │
│ Overall: ✓ READY FOR MIGRATION                 │
└─────────────────────────────────────────────────┘
```

### 8.2 Notifier les utilisateurs

**Navigation:** `IBM i Management > Messages > Send Break Message`

**Message:**
```
ATTENTION: Migration système dans 30 minutes
Le système sera indisponible pendant 5 minutes
à partir de 20h00.
Merci de sauvegarder et de vous déconnecter.
```

---

## Étape 9: Migration (Switchover) (5-10 min)

### 9.1 Arrêter les subsystèmes

**Navigation:** `IBM i Management > Work Management > Subsystems`

**Arrêter:**
- QBATCH (Controlled, 300 sec)
- QCMN (Controlled, 300 sec)
- QINTER (Controlled, 300 sec)

### 9.2 Synchronisation finale

**Navigation:** `High Availability > Clusters > MIGRCLUSTER > MIGRATIONCRG`

**Actions:**
1. Clic droit > `Force Synchronization`
2. Attendre la fin (30-60 secondes)
3. Vérifier: Lag = 0 seconds

### 9.3 Exécuter le switchover

**Navigation:** `High Availability > Clusters > MIGRCLUSTER`

**Actions:**
1. Clic droit sur cluster
2. Sélectionner `Switchover`
3. Paramètres:
   ```
   Current Primary: IBMISOURCE
   New Primary:     IBMICIBLE
   Type:            Planned Switchover
   ```
4. Cliquer `Start Switchover`

**Progression:**
```
┌────────────────────────────────────────────────┐
│ Switchover Progress                            │
├────────────────────────────────────────────────┤
│ Step 1/6: Preparing ✓                          │
│ Step 2/6: Stopping apps ✓                      │
│ Step 3/6: Final sync ✓                         │
│ Step 4/6: Switching roles ⏳                   │
│ Step 5/6: Starting apps ⏸                      │
│ Step 6/6: Verifying ⏸                          │
│                                                │
│ Elapsed: 2m 15s                                │
│ Remaining: 1m 30s                              │
└────────────────────────────────────────────────┘
```

---

## Étape 10: Validation Post-Migration (15 min)

### 10.1 Vérification automatique

**Résultats attendus:**
```
┌─────────────────────────────────────────────────┐
│ Post-Switchover Validation                      │
├─────────────────────────────────────────────────┤
│ ✓ New Primary Active: IBMICIBLE                │
│ ✓ Network Connectivity: OK                     │
│ ✓ Disk Access: All ASPs OK                     │
│ ✓ TCP/IP Services: Started                     │
│ ✓ Subsystems: Started                          │
│ ✓ Replication: Active (reversed)               │
│                                                 │
│ Total Downtime: 3m 42s                         │
│ Status: ✓ MIGRATION SUCCESSFUL                 │
└─────────────────────────────────────────────────┘
```

### 10.2 Tests manuels

**Tests à effectuer:**

1. **Connectivité réseau**
   ```
   Navigation: Network > Utilities > Ping
   Test: Gateway, DNS, Clients
   ✓ Résultat: Tous OK
   ```

2. **Accès utilisateurs**
   ```
   Demander à 3-5 utilisateurs de test de se connecter
   ✓ Résultat: Connexion réussie
   ```

3. **Applications**
   ```
   Lancer les applications critiques
   ✓ Résultat: Fonctionnelles
   ```

4. **Performance**
   ```
   Navigation: Performance > System Status
   Vérifier: CPU < 80%, Memory < 85%
   ✓ Résultat: Dans les normes
   ```

### 10.3 Notification de fin

**Navigation:** `IBM i Management > Messages > Send Break Message`

**Message:**
```
Migration terminée avec succès.
Le système est de nouveau opérationnel.
Nouvelle partition active: IBMICIBLE
```

---

## 📊 Résumé des Temps

| Étape | Description | Durée |
|-------|-------------|-------|
| 1 | Accès Navigator | 5 min |
| 2 | Vérification prérequis | 10 min |
| 3 | Configuration réseau | 15 min |
| 4 | Configuration cluster | 20 min |
| 5 | Configuration CRG | 15 min |
| 6 | Démarrage réplication | 5 min |
| 7 | Synchronisation initiale | 2-8 heures |
| 8 | Vérifications pré-migration | 10 min |
| 9 | Migration (switchover) | 5-10 min |
| 10 | Validation post-migration | 15 min |
| **TOTAL (hors sync)** | | **~2 heures** |
| **Downtime** | | **3-5 minutes** |

---

## 🎯 Checklist Complète

### Avant la Migration (J-7)
```
☐ Vérifier versions IBM i (7.2+)
☐ Installer PowerHA (5770-XE1)
☐ Vérifier PTF Groups
☐ Vérifier espace disque (>200 GB)
☐ Configurer réseau de réplication
☐ Tester connectivité (ping, bande passante)
☐ Créer utilisateurs de réplication
☐ Effectuer sauvegarde complète
```

### Configuration (J-3)
```
☐ Créer cluster PowerHA
☐ Configurer CRG
☐ Ajouter ressources (ASPs)
☐ Démarrer réplication
☐ Vérifier synchronisation initiale
☐ Configurer alertes et monitoring
☐ Tester procédure de rollback
```

### Jour de Migration (J-Day)
```
☐ Vérifier synchronisation (100%)
☐ Exécuter pre-migration checks
☐ Notifier utilisateurs (T-30 min)
☐ Arrêter subsystèmes (T-5 min)
☐ Synchronisation finale (T-0)
☐ Exécuter switchover
☐ Vérifier validation automatique
☐ Tests manuels
☐ Redémarrer applications
☐ Notifier fin de migration
```

### Post-Migration (J+1)
```
☐ Monitoring intensif 24h
☐ Tests de performance
☐ Validation données
☐ Feedback utilisateurs
☐ Documenter incidents
☐ Générer rapport final
```

---

## 🆘 Dépannage Rapide

### Problème: Synchronisation lente

**Diagnostic:**
```
Navigation: High Availability > Clusters > Performance
Vérifier: Rate < 50 MB/s
```

**Solutions:**
1. Vérifier latence réseau (doit être < 5ms)
2. Augmenter compression (niveau 7-8)
3. Vérifier I/O disque
4. Éliminer contention réseau

### Problème: Switchover échoue

**Diagnostic:**
```
Navigation: High Availability > Clusters > Events
Filtrer: Errors
```

**Solutions:**
1. Vérifier que cible a assez de mémoire
2. Vérifier que tous les ASPs sont synchronisés
3. Vérifier connectivité réseau
4. Consulter les logs détaillés

### Problème: Rollback nécessaire

**Procédure:**
```
1. Navigation: High Availability > Clusters > MIGRCLUSTER
2. Clic droit > Switchback
3. Type: Planned Switchback
4. Confirmer
5. Attendre validation
```

---

## 📞 Support

### Contacts
- **Support IBM:** 0800 426 426 (France)
- **Documentation:** https://www.ibm.com/docs/en/i
- **Navigator for i:** https://[ip]:2001/navigator

### Logs à Collecter
```
Navigation: IBM i Management > Logs
- System Log (QHST)
- Job Logs
- Cluster Events
- Network Logs
```

---

## 🎓 Bonnes Pratiques

1. **Toujours tester en environnement non-production d'abord**
2. **Effectuer une sauvegarde complète avant migration**
3. **Planifier pendant une fenêtre de maintenance**
4. **Avoir un plan de rollback documenté**
5. **Communiquer clairement avec les utilisateurs**
6. **Monitorer intensivement pendant 24-48h après migration**
7. **Documenter tous les incidents et résolutions**

---

**Version:** 1.0  
**Date:** 2025-12-17  
**Auteur:** IBM i Technical Team