# Playbook Ansible pour l'Installation de Bob Shell

## Vue d'ensemble

Ce document décrit le playbook Ansible pour automatiser l'installation de Bob Shell sur IBM i. Le playbook peut être créé en mode Code.

---

## Fichier : playbooks/install_bob_shell.yml

```yaml
---
# ==============================================================================
# Playbook: Installation automatisée de Bob Shell sur IBM i
# Description: Installe et configure Bob Shell (Better Object Builder)
# Usage: ansible-playbook -i hosts playbooks/install_bob_shell.yml
# ==============================================================================

- name: Installer Bob Shell sur IBM i
  hosts: ibmi_servers
  gather_facts: yes
  
  vars:
    nodejs_version: "nodejs18"
    bob_version: "latest"
    install_path: "/QOpenSys/pkgs/bin"
    
  tasks:
    - name: Afficher informations d'installation
      debug:
        msg:
          - "Installation de Bob Shell"
          - "Serveur: {{ inventory_hostname }}"
          - "Version Node.js: {{ nodejs_version }}"
          - "Chemin d'installation: {{ install_path }}"
    
    # ========================================
    # Vérification des prérequis
    # ========================================
    
    - name: Vérifier si yum est disponible
      ansible.builtin.shell: |
        which yum
      register: yum_check
      ignore_errors: yes
      changed_when: false
      
    - name: Afficher statut yum
      debug:
        msg: "yum est {{ 'disponible' if yum_check.rc == 0 else 'NON disponible' }}"
    
    - name: Échouer si yum n'est pas disponible
      fail:
        msg: "yum n'est pas installé. Veuillez installer yum d'abord."
      when: yum_check.rc != 0
    
    # ========================================
    # Installation de Node.js
    # ========================================
    
    - name: Vérifier si Node.js est déjà installé
      ansible.builtin.shell: |
        node --version
      register: node_check
      ignore_errors: yes
      changed_when: false
      
    - name: Afficher version Node.js existante
      debug:
        msg: "Node.js version: {{ node_check.stdout }}"
      when: node_check.rc == 0
    
    - name: Installer Node.js via yum
      ansible.builtin.shell: |
        yum install -y {{ nodejs_version }}
      when: node_check.rc != 0
      register: nodejs_install
      
    - name: Afficher résultat installation Node.js
      debug:
        msg: "Node.js installé avec succès"
      when: nodejs_install.changed
    
    - name: Vérifier l'installation de Node.js
      ansible.builtin.shell: |
        node --version
        npm --version
      register: node_verify
      changed_when: false
      
    - name: Afficher versions installées
      debug:
        msg:
          - "Node.js: {{ node_verify.stdout_lines[0] }}"
          - "npm: {{ node_verify.stdout_lines[1] }}"
    
    # ========================================
    # Installation de Bob Shell
    # ========================================
    
    - name: Vérifier si Bob Shell est déjà installé
      ansible.builtin.shell: |
        bob --version
      register: bob_check
      ignore_errors: yes
      changed_when: false
      
    - name: Afficher version Bob Shell existante
      debug:
        msg: "Bob Shell version: {{ bob_check.stdout }}"
      when: bob_check.rc == 0
    
    - name: Installer Bob Shell via npm
      ansible.builtin.shell: |
        npm install -g @ibm/bob
      when: bob_check.rc != 0
      register: bob_install
      environment:
        PATH: "{{ install_path }}:{{ ansible_env.PATH }}"
      
    - name: Afficher résultat installation Bob Shell
      debug:
        msg: "Bob Shell installé avec succès"
      when: bob_install.changed
    
    - name: Vérifier l'installation de Bob Shell
      ansible.builtin.shell: |
        bob --version
      register: bob_verify
      changed_when: false
      environment:
        PATH: "{{ install_path }}:{{ ansible_env.PATH }}"
      
    - name: Afficher version Bob Shell installée
      debug:
        msg: "Bob Shell version: {{ bob_verify.stdout }}"
    
    # ========================================
    # Configuration de l'environnement
    # ========================================
    
    - name: Vérifier si .bashrc existe
      ansible.builtin.stat:
        path: "~/.bashrc"
      register: bashrc_stat
      
    - name: Créer .bashrc si nécessaire
      ansible.builtin.file:
        path: "~/.bashrc"
        state: touch
        mode: '0644'
      when: not bashrc_stat.stat.exists
    
    - name: Ajouter Bob Shell au PATH dans .bashrc
      ansible.builtin.lineinfile:
        path: "~/.bashrc"
        line: 'export PATH={{ install_path }}:$PATH'
        state: present
        create: yes
      register: bashrc_update
      
    - name: Afficher mise à jour .bashrc
      debug:
        msg: "PATH mis à jour dans .bashrc"
      when: bashrc_update.changed
    
    # ========================================
    # Tests de validation
    # ========================================
    
    - name: Tester Bob Shell - Afficher l'aide
      ansible.builtin.shell: |
        bob --help
      register: bob_help
      changed_when: false
      environment:
        PATH: "{{ install_path }}:{{ ansible_env.PATH }}"
      
    - name: Afficher aide Bob Shell
      debug:
        msg: "{{ bob_help.stdout_lines[:10] }}"
    
    - name: Créer un répertoire de test
      ansible.builtin.file:
        path: "/tmp/bob_test"
        state: directory
        mode: '0755'
      
    - name: Initialiser un projet Bob de test
      ansible.builtin.shell: |
        cd /tmp/bob_test
        bob init
      register: bob_init
      ignore_errors: yes
      environment:
        PATH: "{{ install_path }}:{{ ansible_env.PATH }}"
      
    - name: Vérifier l'initialisation du projet
      ansible.builtin.stat:
        path: "/tmp/bob_test/.bob/Rules.mk"
      register: rules_mk_stat
      
    - name: Afficher résultat du test
      debug:
        msg: "Test d'initialisation Bob: {{ 'RÉUSSI' if rules_mk_stat.stat.exists else 'ÉCHOUÉ' }}"
    
    - name: Nettoyer le répertoire de test
      ansible.builtin.file:
        path: "/tmp/bob_test"
        state: absent
    
    # ========================================
    # Résumé de l'installation
    # ========================================
    
    - name: Résumé de l'installation
      debug:
        msg:
          - "=========================================="
          - "Installation de Bob Shell terminée"
          - "=========================================="
          - "Serveur: {{ inventory_hostname }}"
          - "Node.js: {{ node_verify.stdout_lines[0] }}"
          - "npm: {{ node_verify.stdout_lines[1] }}"
          - "Bob Shell: {{ bob_verify.stdout }}"
          - "Chemin: {{ install_path }}"
          - "=========================================="
          - "Prochaines étapes:"
          - "1. Se reconnecter pour charger le nouveau PATH"
          - "2. Créer un projet: bob init"
          - "3. Compiler: bob --build"
          - "=========================================="
```

---

## Fichier : playbooks/bob_shell/README.md

```markdown
# Playbook d'Installation Bob Shell

## Description

Ce playbook automatise l'installation complète de Bob Shell sur les serveurs IBM i.

## Prérequis

- Ansible installé sur le serveur de contrôle
- Collection `ibm.power_ibmi` installée
- Accès SSH aux serveurs IBM i cibles
- yum configuré sur les serveurs IBM i

## Utilisation

### Installation simple

```bash
ansible-playbook -i hosts playbooks/install_bob_shell.yml
```

### Installation sur un serveur spécifique

```bash
ansible-playbook -i hosts playbooks/install_bob_shell.yml --limit ibmi-prod.example.com
```

### Installation avec verbosité

```bash
ansible-playbook -i hosts playbooks/install_bob_shell.yml -vvv
```

### Mode dry-run (vérification)

```bash
ansible-playbook -i hosts playbooks/install_bob_shell.yml --check
```

## Variables personnalisables

Vous pouvez personnaliser l'installation en définissant ces variables :

```yaml
vars:
  nodejs_version: "nodejs18"    # Version de Node.js à installer
  bob_version: "latest"         # Version de Bob Shell
  install_path: "/QOpenSys/pkgs/bin"  # Chemin d'installation
```

### Exemple avec variables personnalisées

```bash
ansible-playbook -i hosts playbooks/install_bob_shell.yml \
  -e "nodejs_version=nodejs20" \
  -e "bob_version=2.0.0"
```

## Fichier d'inventaire

Exemple de fichier `hosts` :

```ini
[ibmi_servers]
ibmi-dev.example.com
ibmi-test.example.com
ibmi-prod.example.com

[ibmi_servers:vars]
ansible_user=QSECOFR
ansible_ssh_pass=your_password
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
```

## Vérification post-installation

Après l'exécution du playbook, vérifiez l'installation :

```bash
# Se connecter au serveur
ssh user@ibmi-server

# Vérifier Bob Shell
bob --version

# Tester Bob Shell
mkdir test_project
cd test_project
bob init
bob --help
```

## Dépannage

### Erreur : yum not found

Si yum n'est pas installé, installez-le d'abord :

```bash
# Voir le guide d'installation dans BOB_SHELL_INSTALLATION_GUIDE.md
```

### Erreur : npm install failed

Vérifiez la connectivité Internet :

```bash
ping registry.npmjs.org
```

### Erreur : Permission denied

Vérifiez les permissions de l'utilisateur :

```bash
ansible-playbook -i hosts playbooks/install_bob_shell.yml --become
```

## Structure du projet

```
playbooks/
├── install_bob_shell.yml          # Playbook principal
└── bob_shell/
    ├── README.md                  # Ce fichier
    └── vars/
        └── main.yml               # Variables par défaut
```

## Maintenance

### Mise à jour de Bob Shell

Pour mettre à jour Bob Shell sur tous les serveurs :

```bash
ansible ibmi_servers -m shell -a "npm update -g @ibm/bob"
```

### Désinstallation

Pour désinstaller Bob Shell :

```bash
ansible ibmi_servers -m shell -a "npm uninstall -g @ibm/bob"
```

## Support

Pour toute question ou problème :
- Consultez le guide principal : `BOB_SHELL_INSTALLATION_GUIDE.md`
- Documentation officielle : https://github.com/IBM/ibmi-bob
- Communauté IBM i OSS : https://ibmioss.ryver.com/
```

---

## Fichier : playbooks/bob_shell/vars/main.yml

```yaml
---
# Variables par défaut pour l'installation de Bob Shell

# Version de Node.js à installer
nodejs_version: "nodejs18"

# Version de Bob Shell (latest ou version spécifique)
bob_version: "latest"

# Chemin d'installation
install_path: "/QOpenSys/pkgs/bin"

# Packages npm additionnels (optionnel)
additional_npm_packages: []
  # - "@ibm/ibmi-repos"
  # - "typescript"

# Configuration du timeout pour npm install
npm_timeout: 300

# Activer les logs détaillés
verbose_logging: false
```

---

## Utilisation avancée

### Playbook avec rôles

Pour une organisation plus modulaire, créez une structure avec rôles :

```
playbooks/bob_shell/
├── install_bob_shell.yml
├── roles/
│   ├── nodejs_install/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── defaults/
│   │       └── main.yml
│   └── bob_install/
│       ├── tasks/
│       │   └── main.yml
│       ├── defaults/
│       │   └── main.yml
│       └── templates/
│           └── bob_config.j2
└── vars/
    └── main.yml
```

### Intégration CI/CD

Exemple d'intégration dans un pipeline Jenkins :

```groovy
pipeline {
    agent any
    
    stages {
        stage('Install Bob Shell') {
            steps {
                sh '''
                    ansible-playbook -i inventory/production.ini \
                        playbooks/install_bob_shell.yml \
                        --limit ibmi-dev
                '''
            }
        }
        
        stage('Verify Installation') {
            steps {
                sh '''
                    ansible ibmi-dev -m shell \
                        -a "bob --version"
                '''
            }
        }
    }
}
```

### Playbook de mise à jour

Créez un playbook séparé pour les mises à jour :

```yaml
---
# playbooks/update_bob_shell.yml
- name: Mettre à jour Bob Shell
  hosts: ibmi_servers
  tasks:
    - name: Mettre à jour Bob Shell
      ansible.builtin.shell: |
        npm update -g @ibm/bob
      register: update_result
      
    - name: Afficher résultat
      debug:
        var: update_result.stdout_lines
```

---

## Exemples de scénarios

### Scénario 1 : Installation sur environnement de développement

```bash
# Installer sur tous les serveurs de dev
ansible-playbook -i hosts playbooks/install_bob_shell.yml \
  --limit dev_servers
```

### Scénario 2 : Installation avec validation complète

```bash
# Installation avec tests étendus
ansible-playbook -i hosts playbooks/install_bob_shell.yml \
  -e "verbose_logging=true" \
  --tags "install,validate"
```

### Scénario 3 : Installation en production avec approbation

```bash
# Mode check d'abord
ansible-playbook -i hosts playbooks/install_bob_shell.yml \
  --limit prod_servers \
  --check

# Si OK, installation réelle
ansible-playbook -i hosts playbooks/install_bob_shell.yml \
  --limit prod_servers
```

---

## Checklist de déploiement

Avant d'exécuter le playbook en production :

- [ ] Vérifier la connectivité SSH vers tous les serveurs
- [ ] Confirmer que yum est configuré
- [ ] Vérifier l'espace disque disponible (minimum 500 MB)
- [ ] Tester le playbook en environnement de développement
- [ ] Planifier une fenêtre de maintenance si nécessaire
- [ ] Préparer un plan de rollback
- [ ] Documenter la version installée
- [ ] Notifier les utilisateurs concernés

---

## Notes importantes

1. **Permissions** : L'utilisateur Ansible doit avoir les droits suffisants pour installer des packages
2. **Connectivité** : Une connexion Internet est requise pour télécharger les packages npm
3. **Espace disque** : Prévoir au moins 500 MB d'espace libre dans `/QOpenSys`
4. **Compatibilité** : Testé sur IBM i 7.3, 7.4, 7.5, et 7.6

---

**Document créé le :** 2026-05-06  
**Version :** 1.0  
**Auteur :** Playbook Ansible pour Bob Shell