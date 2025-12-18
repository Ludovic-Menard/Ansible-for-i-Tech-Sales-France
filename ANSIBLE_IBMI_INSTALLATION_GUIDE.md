# Guide d'Installation Ansible sur IBM i 7.6 (Serveur de Contrôle)

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Architecture](#architecture)
4. [Installation des Produits Sous Licence](#installation-des-produits-sous-licence)
5. [Configuration de PASE](#configuration-de-pase)
6. [Installation de Python et Ansible](#installation-de-python-et-ansible)
7. [Configuration SSH](#configuration-ssh)
8. [Installation des Collections Ansible pour IBM i](#installation-des-collections-ansible-pour-ibm-i)
9. [Configuration et Tests](#configuration-et-tests)
10. [Dépannage](#dépannage)
11. [Ressources](#ressources)

---

## Vue d'ensemble

Ce guide décrit la procédure complète pour installer et configurer Ansible **directement sur IBM i 7.6** qui servira de serveur de contrôle pour gérer d'autres systèmes IBM i. Cette configuration utilise PASE (Portable Application Solutions Environment) pour exécuter Ansible.

### Architecture

```
┌─────────────────────────────────────────┐
│   IBM i 7.6 (Serveur de Contrôle)       │
│   ┌─────────────────────────────────┐   │
│   │  PASE Environment               │   │
│   │  - Python 3.9+                  │   │
│   │  - Ansible Core                 │   │
│   │  - Collections IBM i            │   │
│   │  - SSH Client                   │   │
│   └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ SSH
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐    ┌────▼───────┐
│ IBM i 7.6  │    │ IBM i 7.6  │
│ (Nœud 1)   │    │ (Nœud 2)   │
│ - SSH      │    │ - SSH      │
│ - Python3  │    │ - Python3  │
└────────────┘    └────────────┘
```

---

## Prérequis

### 1. IBM i 7.6 - Serveur de Contrôle

**Version et PTFs:**
- IBM i 7.6 (V7R6M0)
- PTF Group: SF99722 Level 11 ou supérieur (recommandé)
- PTF Group: SF99704 (HTTP Server Group)
- PTF Group: SF99716 (OpenSSH Group)

**Produits sous licence REQUIS:**
- **5770SS1 Option 33** - PASE (Portable Application Solutions Environment)
- **5770SS1 Option 34** - Digital Certificate Manager
- **5733OPS** - IBM i Open Source Solutions (GRATUIT)
- **5733SC1** - Portable Utilities for i (recommandé)

**Configuration système:**
- Profil utilisateur avec autorités *ALLOBJ et *IOSYSCFG
- Minimum 2 GB de mémoire disponible
- Minimum 5 GB d'espace libre dans /QOpenSys
- Minimum 1 GB d'espace libre dans /tmp

**Accès:**
- Accès 5250 ou SSH
- Autorité *ALLOBJ pour l'installation
- Accès réseau vers les nœuds IBM i à gérer

### 2. IBM i 7.6 - Nœuds Gérés

**Configuration minimale:**
- IBM i 7.5 ou supérieur
- SSH Server activé
- Python 3.9+ installé
- Profil utilisateur avec autorités appropriées
- Port 22 ouvert

---

## Installation des Produits Sous Licence

### Étape 1: Vérification des Produits Installés

```
Commandes 5250:

1. Vérifier les produits installés:
   DSPSFWRSC

2. Rechercher spécifiquement:
   - 5770SS1 *BASE
   - 5770SS1 Option 33 (PASE)
   - 5770SS1 Option 34 (Digital Certificate Manager)
   - 5733OPS (Open Source Solutions)
```

### Étape 2: Installation de 5733OPS (Si non installé)

**Méthode 1: Via Access Client Solutions (ACS)**

```
1. Ouvrir ACS
2. Aller dans "Management Central" > "Packages"
3. Clic droit sur le système > "Install Fixes"
4. Sélectionner "5733OPS"
5. Suivre l'assistant d'installation
```

**Méthode 2: Via Commandes 5250**

```
1. Télécharger 5733OPS depuis IBM:
   https://www.ibm.com/support/pages/node/706903

2. Transférer le fichier SAVF vers IBM i (dans QGPL par exemple)

3. Restaurer et installer:
   RSTLICPGM LICPGM(5733OPS) DEV(*SAVF) SAVF(QGPL/5733OPS) RSTOBJ(*ALL)

4. Vérifier l'installation:
   GO LICPGM
   Option 10 (Display installed licensed programs)
   Rechercher 5733OPS
```

### Étape 3: Vérification de PASE

```
1. Vérifier que PASE est installé:
   DSPSFWRSC

2. Tester l'accès à PASE:
   CALL QP2TERM

3. Dans le terminal PASE, taper:
   uname -a
   
   Résultat attendu: AIX <hostname> 1 7 <serial>
```

---

## Configuration de PASE

### Étape 1: Configuration de l'Environnement PASE

```bash
# Se connecter en SSH ou utiliser QP2TERM
# Toutes les commandes suivantes sont dans PASE

# 1. Vérifier le shell par défaut
echo $SHELL

# 2. Créer le répertoire de travail
mkdir -p /home/ANSIBLE
cd /home/ANSIBLE

# 3. Configurer le PATH
cat >> ~/.profile << 'EOF'
# Ansible Environment
export PATH=/QOpenSys/pkgs/bin:$PATH
export PYTHONPATH=/QOpenSys/pkgs/lib/python3.9/site-packages
export ANSIBLE_HOME=/home/ANSIBLE
export LANG=en_US.UTF-8
EOF

# 4. Recharger le profil
. ~/.profile

# 5. Vérifier
echo $PATH
```

### Étape 2: Configuration du Gestionnaire de Paquets yum

```bash
# 1. Vérifier que yum est disponible
which yum

# Si yum n'est pas trouvé, installer bootstrap:
# Télécharger depuis: https://public.dhe.ibm.com/software/ibmi/products/pase/rpms/bootstrap.sh

# 2. Exécuter le bootstrap (si nécessaire)
cd /tmp
# Transférer bootstrap.sh vers /tmp
chmod +x bootstrap.sh
./bootstrap.sh

# 3. Mettre à jour yum
yum update

# 4. Vérifier les dépôts
yum repolist
```

---

## Installation de Python et Ansible

### Étape 1: Installation de Python 3.9

```bash
# 1. Vérifier si Python3 est déjà installé
python3 --version

# 2. Si non installé ou version < 3.9, installer:
yum install python39

# 3. Vérifier l'installation
python3 --version
# Résultat attendu: Python 3.9.x ou supérieur

# 4. Installer pip
yum install python39-pip

# 5. Mettre à jour pip
python3 -m pip install --upgrade pip

# 6. Vérifier pip
pip3 --version
```

### Étape 2: Installation des Dépendances

```bash
# 1. Installer les outils de développement
yum install gcc gcc-c++ make git wget curl

# 2. Installer les bibliothèques Python nécessaires
pip3 install --upgrade setuptools wheel

# 3. Installer les dépendances pour Ansible
yum install libffi-devel openssl-devel

# 4. Installer paramiko (pour SSH)
pip3 install paramiko cryptography
```

### Étape 3: Installation d'Ansible

```bash
# 1. Installation d'Ansible Core
pip3 install ansible-core

# 2. Vérifier l'installation
ansible --version

# Résultat attendu:
# ansible [core 2.15.x]
#   config file = None
#   configured module search path = [...]
#   ansible python module location = /QOpenSys/pkgs/lib/python3.9/site-packages/ansible
#   ansible collection location = /home/ANSIBLE/.ansible/collections
#   executable location = /QOpenSys/pkgs/bin/ansible
#   python version = 3.9.x

# 3. Vérifier les commandes Ansible
which ansible
which ansible-playbook
which ansible-galaxy
```

### Étape 4: Configuration de l'Environnement Ansible

```bash
# 1. Créer la structure de répertoires
mkdir -p /home/ANSIBLE/ansible-ibmi/{playbooks,inventory,roles,group_vars,host_vars,collections}
cd /home/ANSIBLE/ansible-ibmi

# 2. Créer le fichier de configuration Ansible
cat > ansible.cfg << 'EOF'
[defaults]
inventory = ./inventory/hosts
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
stdout_callback = yaml
callbacks_enabled = profile_tasks, timer
collections_paths = ./collections:/home/ANSIBLE/.ansible/collections
interpreter_python = /QOpenSys/pkgs/bin/python3
remote_tmp = /tmp/.ansible-${USER}/tmp

[privilege_escalation]
become = False

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o StrictHostKeyChecking=no
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
EOF

# 3. Créer le répertoire inventory
mkdir -p inventory

# 4. Créer un fichier hosts d'exemple
cat > inventory/hosts << 'EOF'
[ibmi_servers]
ibmi01.example.com ansible_user=ANSIBLE
ibmi02.example.com ansible_user=ANSIBLE

[ibmi_servers:vars]
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF
```

---

## Configuration SSH

### Étape 1: Configuration du Serveur SSH sur le Contrôleur

```
Commandes 5250:

1. Démarrer le serveur SSH:
   STRTCPSVR SERVER(*SSHD)

2. Vérifier le statut:
   NETSTAT *CNN

3. Configuration pour démarrage automatique:
   CHGTCPSVR SVRSPC(*SSHD) AUTOSTART(*YES)

4. Vérifier la configuration:
   WRKTCPSTS *CNN
   Option 3 pour voir les détails
```

### Étape 2: Configuration du Client SSH

```bash
# Dans PASE

# 1. Créer le répertoire .ssh
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 2. Générer une paire de clés SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# 3. Vérifier les clés
ls -la ~/.ssh/
# Résultat attendu: id_rsa (privée) et id_rsa.pub (publique)

# 4. Créer le fichier de configuration SSH
cat > ~/.ssh/config << 'EOF'
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

chmod 600 ~/.ssh/config
```

### Étape 3: Distribution des Clés SSH vers les Nœuds

```bash
# Pour chaque nœud IBM i à gérer:

# Méthode 1: Copie manuelle
# 1. Afficher la clé publique
cat ~/.ssh/id_rsa.pub

# 2. Se connecter au nœud distant
ssh user@ibmi-node.example.com

# 3. Sur le nœud distant, ajouter la clé
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "COLLER_LA_CLE_PUBLIQUE_ICI" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Méthode 2: Utiliser ssh-copy-id (si disponible)
ssh-copy-id -i ~/.ssh/id_rsa.pub user@ibmi-node.example.com

# 4. Tester la connexion sans mot de passe
ssh user@ibmi-node.example.com
# Devrait se connecter sans demander de mot de passe
```

---

## Installation des Collections Ansible pour IBM i

### Étape 1: Installation de la Collection ibm.power_ibmi

```bash
# 1. Installer la collection depuis Ansible Galaxy
ansible-galaxy collection install ibm.power_ibmi

# 2. Vérifier l'installation
ansible-galaxy collection list

# Résultat attendu:
# Collection        Version
# ----------------- -------
# ibm.power_ibmi    2.0.x

# 3. Voir le contenu de la collection
ansible-doc -l ibm.power_ibmi

# 4. Installer dans le répertoire local (optionnel)
cd /home/ANSIBLE/ansible-ibmi
ansible-galaxy collection install ibm.power_ibmi -p ./collections
```

### Étape 2: Installation des Dépendances Python pour IBM i

```bash
# Installer les modules Python requis par la collection
pip3 install itoolkit
pip3 install ibm_db
pip3 install pyodbc
```

### Étape 3: Vérification de la Collection

```bash
# Lister les modules disponibles
ansible-doc -l ibm.power_ibmi | head -20

# Voir la documentation d'un module spécifique
ansible-doc ibm.power_ibmi.ibmi_cl_command
ansible-doc ibm.power_ibmi.ibmi_sql_query
ansible-doc ibm.power_ibmi.ibmi_object_save
```

---

## Configuration et Tests

### Étape 1: Création d'un Playbook de Test

```bash
cd /home/ANSIBLE/ansible-ibmi/playbooks

# Créer un playbook de test simple
cat > test_connection.yml << 'EOF'
---
- name: Test de connexion aux serveurs IBM i
  hosts: ibmi_servers
  gather_facts: no
  
  tasks:
    - name: Ping les serveurs
      ansible.builtin.ping:
      
    - name: Collecter les facts IBM i
      ibm.power_ibmi.ibmi_facts:
      register: ibmi_facts
      
    - name: Afficher la version d'IBM i
      ansible.builtin.debug:
        msg: "Système: {{ ibmi_facts.ansible_facts.ibmi_version }}"
EOF
```

### Étape 2: Test de Connectivité

```bash
# 1. Test ping Ansible
ansible ibmi_servers -m ping

# Résultat attendu:
# ibmi01.example.com | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }

# 2. Test de commande simple
ansible ibmi_servers -m shell -a "uname -a"

# 3. Exécuter le playbook de test
ansible-playbook playbooks/test_connection.yml
```

### Étape 3: Playbook de Test Avancé

```bash
cat > playbooks/test_ibmi_commands.yml << 'EOF'
---
- name: Test des commandes IBM i
  hosts: ibmi_servers
  gather_facts: yes
  
  tasks:
    - name: Exécuter une commande CL
      ibm.power_ibmi.ibmi_cl_command:
        cmd: DSPLIBL
      register: cl_result
      
    - name: Afficher le résultat
      ansible.builtin.debug:
        var: cl_result
        
    - name: Exécuter une requête SQL
      ibm.power_ibmi.ibmi_sql_query:
        sql: "SELECT * FROM QSYS2.SYSTEM_STATUS_INFO"
      register: sql_result
      
    - name: Afficher les informations système
      ansible.builtin.debug:
        var: sql_result.row
        
    - name: Lister les bibliothèques
      ibm.power_ibmi.ibmi_object_find:
        object_type: '*LIB'
        object_name: 'Q*'
      register: libs
      
    - name: Afficher les bibliothèques trouvées
      ansible.builtin.debug:
        msg: "Trouvé {{ libs.object_list | length }} bibliothèques"
EOF

# Exécuter le playbook
ansible-playbook playbooks/test_ibmi_commands.yml
```

### Étape 4: Création d'un Inventaire Complet

```bash
cat > inventory/production.ini << 'EOF'
# Inventaire de production IBM i

[ibmi_prod]
ibmi-prod-01.example.com ansible_user=ANSIBLE
ibmi-prod-02.example.com ansible_user=ANSIBLE

[ibmi_dev]
ibmi-dev-01.example.com ansible_user=ANSIBLE

[ibmi_test]
ibmi-test-01.example.com ansible_user=ANSIBLE

[ibmi_all:children]
ibmi_prod
ibmi_dev
ibmi_test

[ibmi_all:vars]
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
ansible_connection=ssh
ansible_port=22
EOF
```

---

## Dépannage

### Problème 1: Erreur "python3: command not found"

**Solution:**
```bash
# Vérifier l'installation de Python
yum list installed | grep python

# Réinstaller si nécessaire
yum install python39

# Vérifier le PATH
echo $PATH
export PATH=/QOpenSys/pkgs/bin:$PATH
```

### Problème 2: Erreur "Permission denied" lors de l'exécution d'Ansible

**Solution:**
```bash
# Vérifier les permissions du répertoire
ls -la /home/ANSIBLE

# Corriger les permissions
chmod 755 /home/ANSIBLE
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Problème 3: Erreur "Failed to connect to the host via ssh"

**Solution:**
```bash
# Tester la connexion SSH manuellement
ssh -vvv user@target-host

# Vérifier les clés SSH
cat ~/.ssh/authorized_keys

# Vérifier le serveur SSH sur le nœud distant
# Sur le nœud distant (5250):
NETSTAT *CNN
# Chercher le port 22
```

### Problème 4: Module ibm.power_ibmi non trouvé

**Solution:**
```bash
# Réinstaller la collection
ansible-galaxy collection install ibm.power_ibmi --force

# Vérifier le chemin des collections
ansible-config dump | grep COLLECTIONS_PATHS

# Définir explicitement le chemin
export ANSIBLE_COLLECTIONS_PATHS=/home/ANSIBLE/.ansible/collections
```

### Problème 5: Erreur "itoolkit module not found"

**Solution:**
```bash
# Installer itoolkit
pip3 install itoolkit

# Vérifier l'installation
python3 -c "import itoolkit; print(itoolkit.__version__)"
```

### Problème 6: Timeout lors de l'exécution de playbooks

**Solution:**
```bash
# Augmenter le timeout dans ansible.cfg
cat >> ansible.cfg << 'EOF'
[defaults]
timeout = 60
command_timeout = 60
EOF

# Ou dans le playbook
# tasks:
#   - name: Commande longue
#     ibm.power_ibmi.ibmi_cl_command:
#       cmd: LONGCMD
#     async: 300
#     poll: 10
```

### Logs et Débogage

```bash
# Activer le mode verbose
ansible-playbook playbook.yml -vvv

# Activer les logs Ansible
export ANSIBLE_LOG_PATH=/home/ANSIBLE/ansible.log

# Vérifier les logs
tail -f /home/ANSIBLE/ansible.log

# Déboguer un module spécifique
ANSIBLE_DEBUG=1 ansible-playbook playbook.yml
```

---

## Ressources

### Documentation Officielle

- **Ansible Documentation**: https://docs.ansible.com/
- **IBM i Ansible Collection**: https://galaxy.ansible.com/ibm/power_ibmi
- **IBM i Open Source**: https://ibmi-oss-docs.readthedocs.io/
- **IBM i PTF Groups**: https://www.ibm.com/support/pages/node/1119111

### Liens Utiles

- **5733OPS Download**: https://www.ibm.com/support/pages/node/706903
- **Bootstrap yum**: https://public.dhe.ibm.com/software/ibmi/products/pase/rpms/
- **IBM i Community**: https://www.ibm.com/community/ibmi/
- **GitHub IBM Power Systems**: https://github.com/IBM/ansible-power-ibmi

### Commandes de Référence Rapide

```bash
# Vérifier la version d'Ansible
ansible --version

# Lister les hosts
ansible-inventory --list

# Tester la connectivité
ansible all -m ping

# Exécuter une commande ad-hoc
ansible ibmi_servers -m shell -a "uname -a"

# Exécuter un playbook
ansible-playbook playbook.yml

# Exécuter en mode check (dry-run)
ansible-playbook playbook.yml --check

# Lister les tags disponibles
ansible-playbook playbook.yml --list-tags

# Exécuter seulement certains tags
ansible-playbook playbook.yml --tags "config,deploy"

# Lister les tâches
ansible-playbook playbook.yml --list-tasks

# Mode verbeux
ansible-playbook playbook.yml -v   # verbose
ansible-playbook playbook.yml -vv  # plus verbose
ansible-playbook playbook.yml -vvv # debug
```

### Exemples de Playbooks Utiles

```yaml
# Collecter des informations système
---
- name: Collecter informations IBM i
  hosts: ibmi_servers
  tasks:
    - name: System status
      ibm.power_ibmi.ibmi_sql_query:
        sql: "SELECT * FROM QSYS2.SYSTEM_STATUS_INFO"
      register: sys_status
      
    - name: Disk status
      ibm.power_ibmi.ibmi_sql_query:
        sql: "SELECT * FROM QSYS2.SYSDISKSTAT"
      register: disk_status

# Gérer les PTFs
---
- name: Vérifier les PTFs
  hosts: ibmi_servers
  tasks:
    - name: Lister les PTFs
      ibm.power_ibmi.ibmi_fix_group_check:
        groups:
          - "SF99722"
          - "SF99704"
      register: ptf_status

# Sauvegarder des objets
---
- name: Sauvegarder bibliothèque
  hosts: ibmi_servers
  tasks:
    - name: Save library
      ibm.power_ibmi.ibmi_object_save:
        object_names: 'MYLIB'
        object_lib: '*LIBL'
        object_types: '*LIB'
        savefile_name: 'MYLIB'
        savefile_lib: 'QGPL'
```

---

## Conclusion

Vous disposez maintenant d'un serveur de contrôle Ansible fonctionnel sur IBM i 7.6. Cette configuration vous permet de:

- Gérer plusieurs systèmes IBM i de manière centralisée
- Automatiser les tâches d'administration
- Standardiser les configurations
- Déployer des applications
- Gérer les PTFs et mises à jour
- Effectuer des sauvegardes automatisées

### Prochaines Étapes

1. Créer des playbooks pour vos cas d'usage spécifiques
2. Organiser vos playbooks en rôles réutilisables
3. Mettre en place un système de gestion de version (Git)
4. Documenter vos procédures
5. Former les équipes à l'utilisation d'Ansible

### Support

Pour toute question ou problème:
- Consulter la documentation officielle
- Rejoindre la communauté IBM i
- Ouvrir des issues sur GitHub
- Contacter le support IBM

---

**Version du document**: 1.0  
**Date**: Décembre 2024  
**Auteur**: Documentation Technique IBM i