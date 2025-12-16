# 🎯 Scénarios de Démonstration Client

Ce répertoire contient des scénarios prédéfinis adaptés à différents secteurs d'activité et cas d'usage.

## 📁 Scénarios Disponibles

### 1. `scenario_client_banque.json` - Secteur Bancaire
**Cas d'usage :** Traitement batch bancaire de fin de journée
- **Durée :** 10 minutes
- **CPU :** 6 cœurs (intensité haute)
- **I/O :** 4 processus, fichiers 200 MB, opérations mixtes
- **Idéal pour :** Démontrer la capacité à gérer des traitements batch intensifs

**Lancement :**
```bash
python ibmi_stress_orchestrator.py --file demo_scenarios/scenario_client_banque.json
```

### 2. `scenario_client_retail.json` - Secteur Retail
**Cas d'usage :** Pic d'activité (soldes, Black Friday)
- **Durée :** 8 minutes
- **CPU :** 8 cœurs (intensité extrême)
- **I/O :** 6 processus, fichiers 150 MB, opérations mixtes
- **Idéal pour :** Montrer la gestion de pics de charge transactionnelle

**Lancement :**
```bash
python ibmi_stress_orchestrator.py --file demo_scenarios/scenario_client_retail.json
```

### 3. `scenario_client_manufacturing.json` - Secteur Manufacturing
**Cas d'usage :** Calculs ERP et MRP intensifs
- **Durée :** 12 minutes
- **CPU :** 8 cœurs répartis (haute et moyenne intensité)
- **I/O :** 6 processus (lecture et écriture séparées)
- **Idéal pour :** Démontrer la capacité à gérer des charges ERP complexes

**Lancement :**
```bash
python ibmi_stress_orchestrator.py --file demo_scenarios/scenario_client_manufacturing.json
```

## 🎨 Personnalisation des Scénarios

### Structure d'un Scénario

```json
{
  "name": "Nom du Scénario",
  "description": "Description détaillée",
  "duration": 300,
  "monitor": true,
  "monitor_interval": 5,
  "cpu_tests": [
    {
      "cores": 4,
      "intensity": "high"
    }
  ],
  "io_tests": [
    {
      "processes": 2,
      "file_size": 100,
      "operation": "mixed",
      "directory": "/tmp/custom_test"
    }
  ]
}
```

### Paramètres Disponibles

#### Paramètres Généraux
- `name` : Nom du scénario (string)
- `description` : Description détaillée (string)
- `duration` : Durée en secondes (integer)
- `monitor` : Activer le monitoring (boolean)
- `monitor_interval` : Intervalle de monitoring en secondes (integer)

#### Paramètres CPU Tests
- `cores` : Nombre de cœurs à utiliser (integer)
- `intensity` : Intensité du test
  - `"low"` : Charge légère (~25% par cœur)
  - `"medium"` : Charge moyenne (~50% par cœur)
  - `"high"` : Charge élevée (~80% par cœur)
  - `"extreme"` : Charge maximale (~100% par cœur)

#### Paramètres I/O Tests
- `processes` : Nombre de processus parallèles (integer)
- `file_size` : Taille des fichiers en MB (integer)
- `operation` : Type d'opération
  - `"read"` : Lecture uniquement
  - `"write"` : Écriture uniquement
  - `"mixed"` : Lecture et écriture (50/50)
- `directory` : Répertoire pour les fichiers de test (string)

## 💡 Guide de Sélection par Secteur

### 🏦 Banque / Finance
**Caractéristiques :**
- Traitements batch nocturnes
- Calculs financiers complexes
- Forte charge I/O pour les rapports

**Scénario recommandé :** `scenario_client_banque.json`

**Points à mettre en avant :**
- Stabilité sous charge
- Temps de traitement batch
- Capacité de calcul

### 🛒 Retail / Distribution
**Caractéristiques :**
- Pics de charge imprévisibles
- Nombreuses transactions simultanées
- Besoin de réactivité

**Scénario recommandé :** `scenario_client_retail.json`

**Points à mettre en avant :**
- Gestion des pics de charge
- Scalabilité
- Temps de réponse

### 🏭 Manufacturing / Industrie
**Caractéristiques :**
- Calculs MRP/ERP complexes
- Gestion de production
- Charge mixte CPU/I/O

**Scénario recommandé :** `scenario_client_manufacturing.json`

**Points à mettre en avant :**
- Capacité de calcul
- Gestion multi-tâches
- Performance I/O

### 🏥 Santé / Healthcare
**Caractéristiques :**
- Disponibilité 24/7
- Traitement de données sensibles
- Charge constante

**Scénario recommandé :** Créer un scénario personnalisé avec :
- CPU : 4-6 cœurs, intensité medium-high
- I/O : 2-3 processus, opérations mixtes
- Durée : 10-15 minutes

### 📦 Logistique / Transport
**Caractéristiques :**
- Optimisation de routes
- Gestion de stocks
- Forte charge I/O

**Scénario recommandé :** Créer un scénario personnalisé avec :
- CPU : 4 cœurs, intensité high
- I/O : 4-6 processus, opérations mixtes
- Durée : 8-10 minutes

## 📊 Création de Scénarios Personnalisés

### Étape 1 : Analyser les Besoins du Client
- Quel est le secteur d'activité ?
- Quels sont les pics de charge ?
- Quelles sont les applications critiques ?

### Étape 2 : Définir les Paramètres
- Durée du test (recommandé : 5-15 minutes)
- Nombre de cœurs CPU à tester
- Intensité de la charge
- Type d'opérations I/O

### Étape 3 : Créer le Fichier JSON
Copiez un scénario existant et adaptez-le :
```bash
cp scenario_client_banque.json scenario_mon_client.json
# Éditez le fichier avec vos paramètres
```

### Étape 4 : Tester le Scénario
```bash
python ibmi_stress_orchestrator.py --file demo_scenarios/scenario_mon_client.json
```

## 🎬 Déroulement d'une Démonstration

### Préparation (5 minutes)
1. Choisir le scénario adapté au client
2. Ouvrir 2 terminaux SSH
3. Vérifier l'espace disque disponible
4. Préparer les commandes

### Démonstration (10-15 minutes)
1. **Introduction (2 min)**
   - Présenter les outils
   - Expliquer le scénario choisi

2. **Lancement (1 min)**
   - Terminal 1 : Monitoring
   - Terminal 2 : Scénario de stress

3. **Observation (5-10 min)**
   - Commenter les métriques en temps réel
   - Répondre aux questions
   - Montrer la stabilité du système

4. **Résultats (2 min)**
   - Afficher le résumé
   - Discuter des performances
   - Comparer avec les besoins du client

### Conclusion (5 minutes)
1. Sauvegarder les métriques
2. Créer un rapport rapide
3. Discuter du dimensionnement
4. Planifier les prochaines étapes

## 📝 Template de Rapport Client

Après chaque démonstration, créez un rapport avec :

```
RAPPORT DE DÉMONSTRATION IBM POWER
===================================

Client : [Nom du client]
Date : [Date]
Scénario : [Nom du scénario]

CONFIGURATION TESTÉE
--------------------
- Système : IBM Power [modèle]
- Cœurs CPU : [nombre]
- Mémoire : [quantité] GB
- Stockage : [type et capacité]

RÉSULTATS
---------
- Durée du test : [durée] minutes
- CPU moyen : [%]
- CPU maximum : [%]
- Débit I/O : [MB/s]
- Stabilité : [Excellente/Bonne/Acceptable]

OBSERVATIONS
------------
[Vos observations]

RECOMMANDATIONS
---------------
[Vos recommandations de configuration]

PROCHAINES ÉTAPES
-----------------
[Actions à suivre]
```

## 🔧 Dépannage

### Scénario trop intensif
**Symptôme :** Système non responsive
**Solution :** Réduire le nombre de cœurs ou l'intensité

### Manque d'espace disque
**Symptôme :** Erreur lors des tests I/O
**Solution :** Réduire la taille des fichiers ou le nombre de processus

### Tests trop courts
**Symptôme :** Pas assez de temps pour observer
**Solution :** Augmenter la durée du scénario

## 📞 Support

Pour toute question sur les scénarios :
1. Consultez la documentation principale (README_STRESS_TESTS.md)
2. Testez d'abord dans un environnement de développement
3. Contactez l'équipe technique IBM

---

**Dernière mise à jour :** Décembre 2024  
**Maintenu par :** IBM Tech Sales France