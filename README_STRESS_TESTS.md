# 🚀 Outils de Stress Test IBM i pour Démonstrations Commerciales

## 📋 Vue d'ensemble

Suite d'outils Python pour effectuer des tests de stress CPU et I/O sur les systèmes IBM i (Power Systems). Conçus spécifiquement pour les démonstrations commerciales afin de montrer les capacités et performances des serveurs IBM Power aux clients.

## 🎯 Objectifs

- **Démontrer les performances** : Montrer la puissance de traitement des systèmes IBM Power
- **Tester la charge** : Simuler des charges de travail intensives
- **Monitoring en temps réel** : Visualiser les métriques de performance pendant les tests
- **Facilité d'utilisation** : Scripts simples à lancer pour les commerciaux

## 📦 Composants

### 1. `ibmi_stress_cpu.py` - Test de Stress CPU

Génère une charge intensive sur les processeurs pour démontrer les capacités CPU.

**Caractéristiques :**
- Support multi-cœurs
- 4 niveaux d'intensité (low, medium, high, extreme)
- Calculs mathématiques intensifs
- Statistiques détaillées

**Utilisation :**
```bash
# Test simple sur 1 cœur pendant 60 secondes
python ibmi_stress_cpu.py --duration 60

# Test sur 4 cœurs pendant 5 minutes
python ibmi_stress_cpu.py --duration 300 --cores 4

# Test intensif sur 8 cœurs
python ibmi_stress_cpu.py --duration 600 --cores 8 --intensity extreme
```

### 2. `ibmi_stress_io.py` - Test de Stress I/O

Génère une charge intensive sur les disques pour démontrer les performances I/O.

**Caractéristiques :**
- Opérations de lecture, écriture ou mixtes
- Support multi-processus
- Fichiers de taille configurable
- Nettoyage automatique optionnel

**Utilisation :**
```bash
# Test d'écriture pendant 60 secondes
python ibmi_stress_io.py --duration 60 --operation write

# Test mixte sur 4 processus
python ibmi_stress_io.py --duration 300 --operation mixed --processes 4

# Test avec nettoyage automatique
python ibmi_stress_io.py --duration 600 --processes 8 --cleanup
```

### 3. `ibmi_monitor.py` - Monitoring des Performances

Surveille et affiche les métriques de performance en temps réel.

**Caractéristiques :**
- Monitoring CPU, mémoire, disque, réseau
- Affichage en temps réel avec barres de progression
- Top 5 des processus consommateurs
- Export des métriques en JSON

**Utilisation :**
```bash
# Monitoring continu
python ibmi_monitor.py

# Monitoring pendant 5 minutes avec intervalle de 2 secondes
python ibmi_monitor.py --duration 300 --interval 2

# Monitoring avec sauvegarde des métriques
python ibmi_monitor.py --output metrics.jsonl --duration 600
```

### 4. `ibmi_stress_orchestrator.py` - Orchestrateur de Tests

Lance et coordonne plusieurs tests simultanément avec des scénarios prédéfinis.

**Caractéristiques :**
- 6 scénarios prédéfinis
- Lancement automatique de tests CPU + I/O + monitoring
- Gestion des processus
- Résumé des résultats

**Utilisation :**
```bash
# Lister les scénarios disponibles
python ibmi_stress_orchestrator.py --list-scenarios

# Lancer un scénario prédéfini
python ibmi_stress_orchestrator.py --scenario demo_standard

# Lancer un scénario personnalisé
python ibmi_stress_orchestrator.py --file mon_scenario.json
```

## 🎬 Scénarios Prédéfinis

### 1. **demo_light** - Démonstration Légère (2 min)
- 2 cœurs CPU (intensité moyenne)
- 1 processus I/O (fichiers 50 MB)
- Idéal pour une démo rapide

### 2. **demo_standard** - Démonstration Standard (5 min)
- 4 cœurs CPU (intensité haute)
- 2 processus I/O (fichiers 100 MB)
- Scénario recommandé pour la plupart des démos

### 3. **demo_intensive** - Démonstration Intensive (10 min)
- 8 cœurs CPU (intensité extrême)
- 4 processus I/O (fichiers 200 MB)
- Pour montrer les capacités maximales

### 4. **cpu_only** - Stress CPU Uniquement (5 min)
- 8 cœurs CPU répartis sur 2 tests
- Aucun test I/O
- Focus sur les performances CPU

### 5. **io_only** - Stress I/O Uniquement (5 min)
- 8 processus I/O (lecture + écriture)
- Aucun test CPU
- Focus sur les performances disque

### 6. **full_stress** - Stress Complet (15 min)
- 8 cœurs CPU (intensité extrême)
- 8 processus I/O
- Test complet de toutes les capacités

## 📊 Exemple de Démonstration Client

### Scénario : Démonstration Standard (5 minutes)

**Préparation (2 minutes) :**
1. Ouvrir 2 terminaux SSH sur le système IBM i
2. Terminal 1 : Lancer le monitoring
3. Terminal 2 : Préparer la commande de stress

**Démonstration (5 minutes) :**

**Terminal 1 - Monitoring :**
```bash
python ibmi_monitor.py --interval 5
```

**Terminal 2 - Stress Test :**
```bash
python ibmi_stress_orchestrator.py --scenario demo_standard
```

**Points à montrer au client :**
- ✅ Utilisation CPU montant progressivement
- ✅ Répartition de la charge sur tous les cœurs
- ✅ Débit I/O en lecture/écriture
- ✅ Stabilité du système sous charge
- ✅ Métriques en temps réel

**Conclusion (1 minute) :**
- Afficher le résumé des tests
- Montrer les métriques collectées
- Discuter des résultats avec le client

## 🔧 Installation

### Prérequis
- Python 3.6 ou supérieur
- Bibliothèque `psutil`

### Installation des dépendances
```bash
pip install psutil
```

Ou avec le fichier requirements.txt :
```bash
pip install -r requirements.txt
```

## 📝 Création de Scénarios Personnalisés

Créez un fichier JSON avec votre configuration :

```json
{
  "name": "Mon Scénario Personnalisé",
  "description": "Test adapté aux besoins du client",
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

Lancez-le avec :
```bash
python ibmi_stress_orchestrator.py --file mon_scenario.json
```

## 💡 Conseils pour les Démonstrations

### Avant la Démo
1. **Tester l'environnement** : Lancez un test rapide pour vérifier que tout fonctionne
2. **Vérifier les ressources** : Assurez-vous d'avoir suffisamment d'espace disque
3. **Préparer les terminaux** : Ouvrez les fenêtres nécessaires à l'avance
4. **Documenter la baseline** : Notez les performances au repos

### Pendant la Démo
1. **Commencer léger** : Utilisez `demo_light` pour introduire les outils
2. **Expliquer les métriques** : Commentez ce que le client voit à l'écran
3. **Montrer la scalabilité** : Augmentez progressivement la charge
4. **Rester interactif** : Répondez aux questions en temps réel

### Après la Démo
1. **Sauvegarder les métriques** : Conservez les fichiers de monitoring
2. **Créer un rapport** : Résumez les résultats pour le client
3. **Nettoyer** : Supprimez les fichiers de test temporaires
4. **Follow-up** : Envoyez les métriques au client

## 🎓 Arguments Détaillés

### ibmi_stress_cpu.py
```
--duration SECONDS    Durée du test (requis)
--cores NUMBER        Nombre de cœurs à utiliser (défaut: 1)
--intensity LEVEL     Intensité: low, medium, high, extreme (défaut: high)
```

### ibmi_stress_io.py
```
--duration SECONDS    Durée du test (requis)
--processes NUMBER    Nombre de processus parallèles (défaut: 1)
--directory PATH      Répertoire pour les fichiers de test
--file-size MB        Taille des fichiers en MB (défaut: 100)
--operation TYPE      Type: read, write, mixed (défaut: mixed)
--cleanup             Nettoyer les fichiers après le test
```

### ibmi_monitor.py
```
--interval SECONDS    Intervalle de collecte (défaut: 5)
--duration SECONDS    Durée du monitoring (défaut: infini)
--output FILE         Fichier de sortie JSON Lines
```

### ibmi_stress_orchestrator.py
```
--scenario NAME       Nom du scénario prédéfini
--file PATH           Fichier JSON de configuration
--list-scenarios      Afficher les scénarios disponibles
```

## 📈 Interprétation des Résultats

### Métriques CPU
- **< 50%** : Charge légère, système sous-utilisé
- **50-80%** : Charge normale, bon équilibre
- **80-95%** : Charge élevée, performances optimales
- **> 95%** : Charge maximale, saturation possible

### Métriques I/O
- **Débit lecture/écriture** : Compare avec les specs du disque
- **IOPS** : Nombre d'opérations par seconde
- **Latence** : Temps de réponse des opérations

### Métriques Mémoire
- **< 70%** : Utilisation normale
- **70-85%** : Utilisation élevée mais acceptable
- **> 85%** : Risque de swap, considérer plus de RAM

## 🛠️ Dépannage

### Problème : "Permission denied"
**Solution :** Vérifiez les droits d'accès au répertoire de test
```bash
chmod 755 /tmp/ibmi_io_stress
```

### Problème : "Module psutil not found"
**Solution :** Installez psutil
```bash
pip install psutil
```

### Problème : Tests trop lents
**Solution :** Réduisez l'intensité ou le nombre de processus
```bash
python ibmi_stress_cpu.py --duration 60 --intensity medium
```

### Problème : Système non responsive
**Solution :** Arrêtez les tests avec Ctrl+C et réduisez la charge

## 📞 Support

Pour toute question ou problème :
1. Vérifiez les logs des tests
2. Consultez la documentation IBM i
3. Contactez l'équipe technique IBM

## 📄 Licence

Ces outils sont fournis à des fins de démonstration commerciale. Utilisez-les de manière responsable et uniquement dans des environnements de test ou de démonstration.

## ⚠️ Avertissements

- **Ne pas utiliser en production** sans autorisation
- **Surveiller les ressources** pendant les tests
- **Prévoir du temps** pour le nettoyage après les tests
- **Documenter les résultats** pour référence future

## 🎯 Cas d'Usage Commerciaux

### 1. Comparaison de Performances
Montrez la différence entre l'ancien système et un nouveau Power System.

### 2. Dimensionnement
Aidez le client à choisir la bonne configuration (nombre de cœurs, RAM, disques).

### 3. Proof of Concept
Démontrez que le système peut gérer la charge prévue.

### 4. Migration Planning
Testez les performances avant une migration vers IBM i.

### 5. Capacity Planning
Montrez comment le système se comporte sous différentes charges.

---

**Version :** 1.0  
**Date :** Décembre 2024  
**Auteur :** IBM Tech Sales France  
**Contact :** Équipe IBM Power Systems