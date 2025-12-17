# Prérequis Logiciels et Matériels pour Cartes Spyre sur IBM i

## Vue d'ensemble

Ce document détaille tous les composants nécessaires pour utiliser les cartes accélératrices Spyre sur IBM i dans le cadre des use cases d'IA et de machine learning.

---

## 1. MATÉRIEL REQUIS

### 1.1 Serveur IBM Power11
**Modèles compatibles** :
- IBM Power S1014 (1-socket)
- IBM Power S1022s (2-socket)
- IBM Power S1024 (2-socket)
- IBM Power E1050 (4-socket)

**Spécifications minimales** :
- Processeurs : Power11 (minimum 8 cores)
- RAM : 64 GB minimum (128 GB recommandé)
- Slots PCIe : Minimum 1 slot PCIe Gen5 x16 disponible
- Stockage : 500 GB minimum pour OS + données ML

### 1.2 Carte Spyre
**Modèle** : IBM Spyre Accelerator Card
- Interface : PCIe Gen5 x16
- Mémoire embarquée : 32 GB HBM2e
- TDP : 300W
- Refroidissement : Actif requis

**Quantité recommandée par use case** :
- Use case simple (1-2 modèles) : 1 carte
- Use cases multiples (3-5 modèles) : 2 cartes
- Production intensive : 2-4 cartes

### 1.3 Infrastructure Réseau
- Adaptateur réseau : 10 GbE minimum (25 GbE recommandé)
- Switch : Compatible avec débit requis
- Câblage : Cat6a minimum pour 10GbE

### 1.4 Alimentation
- UPS : Capacité suffisante pour charge additionnelle (+300W par carte)
- PDU : Redondance recommandée

---

## 2. SYSTÈME D'EXPLOITATION

### 2.1 IBM i
**Version requise** :
- IBM i 7.5 TR2 minimum
- IBM i 7.5 TR5 recommandé (support optimisé Spyre)

**PTFs critiques** :
```
SI84920 - Spyre Device Driver Support
SI84921 - PCIe Gen5 Optimization
SI84922 - ML Services Integration
SI84923 - PASE Python ML Libraries
```

**Installation des PTFs** :
```bash
# Vérifier les PTFs installés
DSPPTF

# Installer les PTFs requis
LODPTF DEV(*SERVICE) SELECT(SI84920 SI84921 SI84922 SI84923)
APYPTF LICPGM(5770SS1) SELECT(SI84920 SI84921 SI84922 SI84923)
```

### 2.2 Groupes PTF recommandés
- SF99722 - Technology Refresh
- SF99368 - Security Fixes
- SF99704 - Database Group

---

## 3. LOGICIELS IBM i

### 3.1 Produits sous licence IBM i
**Requis** :
- 5770SS1 Option 3 - Extended Base Support
- 5770SS1 Option 12 - Host Servers
- 5770SS1 Option 30 - QShell
- 5770SS1 Option 33 - PASE (Portable Application Solutions Environment)
- 5770SS1 Option 34 - Digital Certificate Manager
- 5770SS1 Option 39 - International Components for Unicode

**Recommandés** :
- 5770DG1 - HTTP Server (pour API REST)
- 5770JV1 - Java Developer Kit
- 5770WDS - WebSphere Development Studio (pour développement)

**Vérification** :
```sql
-- Vérifier les options installées
SELECT * FROM QSYS2.PRODUCT_INFO 
WHERE PRODUCT_ID = '5770SS1';
```

### 3.2 IBM i Access Client Solutions (ACS)
**Version** : 1.1.9.5 ou supérieur
**Composants requis** :
- 5250 Emulator
- SQL Performance Monitor
- System Debugger
- Navigator for i

**Téléchargement** :
```
https://www.ibm.com/support/pages/ibm-i-access-client-solutions
```

---

## 4. ENVIRONNEMENT PASE

### 4.1 Python pour IBM i
**Version requise** : Python 3.9 ou 3.11

**Installation via yum** :
```bash
# Se connecter en SSH à IBM i
ssh user@ibmi_hostname

# Installer Python 3.11
yum install python311

# Vérifier l'installation
python3.11 --version
```

**Packages Python essentiels** :
```bash
# Installer pip
python3.11 -m ensurepip

# Mettre à jour pip
python3.11 -m pip install --upgrade pip

# Installer packages de base
pip3.11 install numpy scipy pandas
```

### 4.2 Bibliothèques ML/AI
**Framework ML** :
```bash
# TensorFlow pour Spyre
pip3.11 install tensorflow==2.15.0

# PyTorch pour Spyre
pip3.11 install torch==2.1.0 torchvision torchaudio

# Scikit-learn
pip3.11 install scikit-learn==1.3.2

# XGBoost
pip3.11 install xgboost==2.0.2
```

**Bibliothèques NLP** :
```bash
# Transformers (Hugging Face)
pip3.11 install transformers==4.35.0

# NLTK
pip3.11 install nltk==3.8.1

# spaCy
pip3.11 install spacy==3.7.2
python3.11 -m spacy download en_core_web_sm
python3.11 -m spacy download fr_core_news_sm
```

**Vision par ordinateur** :
```bash
# OpenCV
pip3.11 install opencv-python==4.8.1

# Pillow
pip3.11 install Pillow==10.1.0
```

### 4.3 SDK Spyre
**Installation** :
```bash
# SDK officiel IBM Spyre
pip3.11 install ibm-spyre-sdk==1.2.0

# Outils de monitoring
pip3.11 install spyre-monitor==1.0.5

# Utilitaires
pip3.11 install spyre-utils==1.1.0
```

### 4.4 Frameworks API
```bash
# Flask (API REST légère)
pip3.11 install Flask==3.0.0 Flask-CORS==4.0.0

# FastAPI (API haute performance)
pip3.11 install fastapi==0.104.1 uvicorn==0.24.0

# Connexion DB2
pip3.11 install ibm_db==3.2.0 ibm_db_sa==0.4.0
```

---

## 5. OUTILS DE DÉVELOPPEMENT

### 5.1 Rational Developer for i (RDi)
**Version** : 9.8.0.3 ou supérieur
**Composants** :
- RPG/COBOL Editor
- SQL Development
- Debug Tools
- Source Management

### 5.2 Visual Studio Code
**Extensions recommandées** :
```
- IBM i Development Pack
- Python
- Jupyter
- REST Client
- YAML
- Ansible
```

**Installation extensions** :
```bash
code --install-extension IBM.vscode-ibmi
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
```

### 5.3 Git pour IBM i
```bash
# Installer Git via yum
yum install git

# Configurer Git
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@entreprise.com"
```

---

## 6. MIDDLEWARE ET INTÉGRATION

### 6.1 Node.js (optionnel)
**Pour API Gateway ou microservices** :
```bash
# Installer Node.js 18 LTS
yum install nodejs18

# Vérifier
node --version
npm --version

# Packages utiles
npm install -g express
npm install -g pm2
```

### 6.2 Message Broker (optionnel)
**RabbitMQ** :
```bash
yum install rabbitmq-server

# Démarrer le service
systemctl start rabbitmq-server
systemctl enable rabbitmq-server
```

**Apache Kafka** (via conteneur ou externe) :
- Kafka Connect pour IBM i
- Confluent Platform

### 6.3 Redis (Cache)
```bash
# Installer Redis
yum install redis

# Démarrer Redis
systemctl start redis
systemctl enable redis
```

---

## 7. OUTILS DE MONITORING

### 7.1 IBM Navigator for i
**Composants à activer** :
- Performance Data
- Job Watcher
- SQL Performance Center
- System Values

### 7.2 Prometheus + Grafana (optionnel)
**Pour monitoring avancé** :
```bash
# Exporter métriques Spyre
pip3.11 install prometheus-client==0.19.0

# Node exporter pour IBM i
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-ppc64le.tar.gz
```

### 7.3 Scripts de monitoring personnalisés
```python
# Exemple: monitor_spyre.py
from spyre_monitor import SpyreMonitor
import time

monitor = SpyreMonitor()
while True:
    stats = monitor.get_stats()
    print(f"GPU Utilization: {stats['gpu_util']}%")
    print(f"Memory Used: {stats['mem_used']} GB")
    print(f"Temperature: {stats['temp']}°C")
    time.sleep(5)
```

---

## 8. SÉCURITÉ

### 8.1 Certificats SSL/TLS
```bash
# Générer certificat auto-signé pour dev
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Pour production: utiliser Digital Certificate Manager (DCM)
```

### 8.2 Firewall
**Ports à ouvrir** :
- 22 : SSH
- 8080 : API REST (configurable)
- 5432 : PostgreSQL (si utilisé)
- 6379 : Redis (si utilisé)
- 9090 : Prometheus (si utilisé)

### 8.3 Gestion des accès
```sql
-- Créer profil utilisateur pour services ML
CREATE USER MLSERVICE PASSWORD('SecureP@ssw0rd') 
  TEXT('ML Services User');

-- Accorder permissions
GRANT SELECT, INSERT, UPDATE ON SCHEMA MLDATA TO MLSERVICE;
```

---

## 9. AUTOMATISATION

### 9.1 Ansible
**Installation sur poste de contrôle** :
```bash
# Sur Linux/Mac
pip3 install ansible

# Collection IBM i
ansible-galaxy collection install ibm.power_ibmi
```

**Playbook exemple** :
```yaml
---
- name: Configure Spyre Environment
  hosts: ibmi
  tasks:
    - name: Install Python packages
      ibmi_cl_command:
        cmd: "CALL QP2TERM PARM('pip3.11 install ibm-spyre-sdk')"
    
    - name: Deploy ML models
      ibmi_copy:
        src: models/
        dest: /home/mlservice/models/
```

### 9.2 Scripts CL
```cl
/* SETUP_SPYRE.CL - Configuration initiale */
PGM

  /* Créer bibliothèque pour ML */
  CRTLIB LIB(MLSERVICES) TEXT('ML Services Library')

  /* Créer répertoire IFS */
  MKDIR DIR('/home/mlservice/models')
  MKDIR DIR('/home/mlservice/logs')

  /* Définir variables d'environnement */
  ADDENVVAR ENVVAR(SPYRE_HOME) VALUE('/opt/spyre') LEVEL(*SYS)
  ADDENVVAR ENVVAR(PYTHONPATH) VALUE('/QOpenSys/pkgs/lib/python3.11/site-packages') LEVEL(*SYS)

ENDPGM
```

---

## 10. DOCUMENTATION ET FORMATION

### 10.1 Documentation IBM
**Manuels requis** :
- IBM Power11 Installation Guide
- IBM i 7.5 Information Center
- Spyre Accelerator Programming Guide
- IBM i PASE for AIX Guide

**Liens** :
```
https://www.ibm.com/docs/en/i/7.5
https://www.ibm.com/docs/en/power11
https://www.ibm.com/docs/en/spyre-accelerator
```

### 10.2 Formations recommandées
**IBM Skills Gateway** :
- IBM i Basics (gratuit)
- Python on IBM i
- AI/ML Fundamentals
- Spyre Programming Workshop

**Certifications** :
- IBM Certified System Administrator - IBM i
- IBM AI Engineering Professional Certificate

---

## 11. CHECKLIST D'INSTALLATION

### Phase 1: Préparation matérielle
- [ ] Vérifier compatibilité serveur Power11
- [ ] Vérifier disponibilité slot PCIe Gen5
- [ ] Vérifier alimentation suffisante
- [ ] Commander carte(s) Spyre
- [ ] Planifier fenêtre de maintenance

### Phase 2: Installation matérielle
- [ ] Installer carte Spyre dans slot PCIe
- [ ] Connecter alimentation additionnelle
- [ ] Vérifier refroidissement
- [ ] Démarrer le système
- [ ] Vérifier détection carte (WRKHDWRSC)

### Phase 3: Configuration IBM i
- [ ] Mettre à jour IBM i vers 7.5 TR2+
- [ ] Installer PTFs Spyre (SI84920-SI84923)
- [ ] Vérifier options 5770SS1 (3, 12, 30, 33, 34, 39)
- [ ] Configurer PASE
- [ ] Installer ACS 1.1.9.5+

### Phase 4: Installation logiciels PASE
- [ ] Installer Python 3.11
- [ ] Installer pip et packages de base
- [ ] Installer TensorFlow/PyTorch
- [ ] Installer SDK Spyre
- [ ] Installer frameworks API (Flask/FastAPI)
- [ ] Installer outils monitoring

### Phase 5: Configuration réseau et sécurité
- [ ] Configurer interfaces réseau
- [ ] Ouvrir ports firewall
- [ ] Générer certificats SSL
- [ ] Créer profils utilisateurs
- [ ] Configurer accès SSH

### Phase 6: Tests et validation
- [ ] Test détection carte Spyre
- [ ] Test inférence simple
- [ ] Test API REST
- [ ] Test connexion DB2
- [ ] Benchmark performance
- [ ] Validation monitoring

### Phase 7: Déploiement use case
- [ ] Déployer modèles ML
- [ ] Configurer intégration applicative
- [ ] Tester use case end-to-end
- [ ] Former utilisateurs
- [ ] Documenter procédures

---

## 12. COMMANDES UTILES

### Vérification matériel
```bash
# Lister périphériques PCIe
system "WRKHDWRSC TYPE(*PCI)"

# Vérifier carte Spyre
system "DSPHWRSC TYPE(*PCI) RESOURCE(CMN*)"

# Température et état
spyre-cli status
```

### Gestion Python
```bash
# Lister packages installés
pip3.11 list

# Mettre à jour tous les packages
pip3.11 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3.11 install -U

# Créer environnement virtuel
python3.11 -m venv /home/mlservice/venv
source /home/mlservice/venv/bin/activate
```

### Monitoring
```bash
# Utilisation CPU/Mémoire
system "WRKSYSSTS"

# Jobs actifs
system "WRKACTJOB"

# Logs système
system "DSPLOG"

# Métriques Spyre
spyre-cli metrics --json
```

---

## 13. COÛTS ESTIMÉS

### Licences logicielles (annuel)
- IBM i 7.5 : Inclus avec serveur
- Options 5770SS1 : Incluses
- RDi : ~2 000€/développeur
- ACS : Gratuit

### Logiciels open source
- Python, TensorFlow, PyTorch : Gratuit
- Flask, FastAPI : Gratuit
- Ansible : Gratuit

### Formation
- IBM Skills Gateway : Gratuit
- Workshops Spyre : ~1 500€/personne
- Certification : ~200€/examen

### Support
- IBM Support Standard : Inclus
- Support Premium : ~10% valeur matériel/an

---

## 14. SUPPORT ET ASSISTANCE

### IBM Support
- **Portal** : https://www.ibm.com/mysupport
- **Téléphone** : +33 (0)1 41 89 00 00
- **Email** : support@fr.ibm.com

### Communauté
- **Forum IBM i** : https://community.ibm.com/community/user/power/communities/community-home?CommunityKey=c0d0d5f5-0d7e-4e3f-9a5e-8e5e5e5e5e5e
- **Reddit** : r/IBMi
- **LinkedIn** : IBM i Professionals Group

### Partenaires IBM
- Business Partners certifiés
- Intégrateurs systèmes
- Consultants spécialisés

---

## 15. RESSOURCES ADDITIONNELLES

### Fichiers de configuration exemple
Disponibles dans le repository :
```
/config/spyre_config.json
/config/python_requirements.txt
/scripts/setup_spyre.sh
/scripts/deploy_model.py
/ansible/spyre_playbook.yml
```

### Modèles pré-entraînés
```bash
# Télécharger modèles de démonstration
wget https://ibm.com/spyre/models/fraud_detection_v1.tar.gz
wget https://ibm.com/spyre/models/sentiment_analysis_v1.tar.gz
wget https://ibm.com/spyre/models/predictive_maintenance_v1.tar.gz
```

---

## CONCLUSION

Cette liste complète couvre tous les prérequis logiciels et matériels pour exploiter les cartes Spyre sur IBM i. L'installation complète prend environ 2-3 jours pour un administrateur expérimenté.

**Temps estimés** :
- Installation matérielle : 2-4 heures
- Configuration IBM i : 4-6 heures
- Installation logiciels PASE : 2-3 heures
- Tests et validation : 4-8 heures
- Formation équipe : 1-2 jours

**Prochaines étapes** :
1. Valider la compatibilité de votre infrastructure actuelle
2. Commander le matériel nécessaire
3. Planifier la fenêtre de maintenance
4. Former l'équipe technique
5. Démarrer l'implémentation

---

*Document créé le: 2025-12-17*
*Version: 1.0*
*Auteur: IBM i Technical Sales*
*Dernière mise à jour: 2025-12-17*