# Guide de Démarrage Rapide - Ansible sur IBM i 7.6

## Installation en 10 Minutes

Ce guide vous permet d'installer rapidement Ansible sur IBM i 7.6.

---

## Étape 1: Vérification des Prérequis (2 min)

### Via 5250

```
DSPSFWRSC
```

Vérifiez que vous avez:
- ✅ 5770SS1 Option 33 (PASE)
- ✅ 5733OPS (Open Source Solutions)

Si 5733OPS n'est pas installé:
```
Télécharger depuis: https://www.ibm.com/support/pages/node/706903
RSTLICPGM LICPGM(5733OPS) DEV(*SAVF) SAVF(QGPL/5733OPS)
```

### Démarrer SSH

```
STRTCPSVR SERVER(*SSHD)
CHGTCPSVR SVRSPC(*SSHD) AUTOSTART(*YES)
```

---

## Étape 2: Installation de Python et Ansible (5 min)

### Se connecter en SSH

```bash
ssh votre_user@votre_ibmi
```

### Installer Python et Ansible

```bash
# Mettre à jour yum
yum update

# Installer Python 3.9
yum install -y python39 python39-pip

# Installer les dépendances
yum install -y gcc git wget curl

# Installer Ansible
pip3 install ansible-core

# Vérifier
ansible --version
```

---

## Étape 3: Configuration de Base (2 min)

```bash
# Créer la structure
mkdir -p ~/ansible-ibmi/{playbooks,inventory}
cd ~/ansible-ibmi

# Créer ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
inventory = ./inventory/hosts
host_key_checking = False
interpreter_python = /QOpenSys/pkgs/bin/python3
EOF

# Créer l'inventaire
cat > inventory/hosts << 'EOF'
[ibmi_servers]
localhost ansible_connection=local

[ibmi_servers:vars]
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
EOF
```

---

## Étape 4: Installer la Collection IBM i (1 min)

```bash
# Installer la collection
ansible-galaxy collection install ibm.power_ibmi

# Installer les dépendances Python
pip3 install itoolkit
```

---

## Étape 5: Premier Test (< 1 min)

```bash
# Test de connexion
ansible localhost -m ping

# Créer un playbook de test
cat > playbooks/test.yml << 'EOF'
---
- name: Test IBM i
  hosts: localhost
  gather_facts: no
  
  tasks:
    - name: Exécuter commande CL
      ibm.power_ibmi.ibmi_cl_command:
        cmd: DSPLIBL
      register: result
      
    - name: Afficher résultat
      debug:
        var: result
EOF

# Exécuter le playbook
ansible-playbook playbooks/test.yml
```

---

## Commandes Essentielles

```bash
# Tester la connectivité
ansible all -m ping

# Exécuter une commande
ansible all -m shell -a "uname -a"

# Lancer un playbook
ansible-playbook playbook.yml

# Mode dry-run
ansible-playbook playbook.yml --check

# Mode verbose
ansible-playbook playbook.yml -vvv
```

---

## Exemples de Playbooks Utiles

### 1. Collecter des Informations Système

```yaml
---
- name: Informations Système
  hosts: localhost
  tasks:
    - name: Status système
      ibm.power_ibmi.ibmi_sql_query:
        sql: "SELECT * FROM QSYS2.SYSTEM_STATUS_INFO"
      register: sys_info
      
    - name: Afficher
      debug:
        var: sys_info.row
```

### 2. Lister les Bibliothèques

```yaml
---
- name: Lister Bibliothèques
  hosts: localhost
  tasks:
    - name: Trouver bibliothèques Q*
      ibm.power_ibmi.ibmi_object_find:
        object_type: '*LIB'
        object_name: 'Q*'
      register: libs
      
    - name: Afficher
      debug:
        msg: "{{ libs.object_list | length }} bibliothèques trouvées"
```

### 3. Vérifier les PTFs

```yaml
---
- name: Vérifier PTFs
  hosts: localhost
  tasks:
    - name: Check PTF Groups
      ibm.power_ibmi.ibmi_fix_group_check:
        groups:
          - "SF99722"
          - "SF99704"
      register: ptf_status
      
    - name: Afficher status
      debug:
        var: ptf_status
```

---

## Configuration pour Gérer d'Autres IBM i

### 1. Configurer SSH sans Mot de Passe

```bash
# Générer clé SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Copier vers le serveur distant
ssh-copy-id user@serveur-distant

# Tester
ssh user@serveur-distant
```

### 2. Ajouter à l'Inventaire

```ini
[ibmi_servers]
localhost ansible_connection=local
ibmi-prod-01 ansible_user=ANSIBLE
ibmi-prod-02 ansible_user=ANSIBLE

[ibmi_servers:vars]
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
```

### 3. Tester

```bash
ansible ibmi_servers -m ping
```

---

## Dépannage Rapide

### Python non trouvé
```bash
export PATH=/QOpenSys/pkgs/bin:$PATH
echo 'export PATH=/QOpenSys/pkgs/bin:$PATH' >> ~/.profile
```

### Module ibm.power_ibmi non trouvé
```bash
ansible-galaxy collection install ibm.power_ibmi --force
pip3 install itoolkit
```

### Erreur SSH
```bash
# Vérifier SSH
ssh -vvv user@host

# Vérifier les clés
ls -la ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
```

### Timeout
```bash
# Dans ansible.cfg
[defaults]
timeout = 60
```

---

## Ressources

- **Documentation complète**: `ANSIBLE_IBMI_INSTALLATION_GUIDE.md`
- **Collection IBM i**: https://galaxy.ansible.com/ibm/power_ibmi
- **Documentation Ansible**: https://docs.ansible.com/
- **IBM i Open Source**: https://ibmi-oss-docs.readthedocs.io/

---

## Prochaines Étapes

1. ✅ Ansible installé et fonctionnel
2. 📚 Lire la documentation complète
3. 🎯 Créer vos premiers playbooks
4. 🔧 Automatiser vos tâches récurrentes
5. 📊 Mettre en place des rapports automatisés

**Félicitations ! Vous êtes prêt à utiliser Ansible sur IBM i !** 🎉