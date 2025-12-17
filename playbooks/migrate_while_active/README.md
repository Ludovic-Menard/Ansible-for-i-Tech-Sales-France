# IBM i Migrate While Active - Playbooks Ansible

Ce répertoire contient des playbooks Ansible pour automatiser la configuration et la migration IBM i While Active.

## Structure

```
migrate_while_active/
├── README.md                           # Ce fichier
├── IBM_i_MIGRATE_WHILE_ACTIVE_GUIDE.md # Guide complet de migration
├── inventory.ini                       # Inventaire des partitions
├── vars.yml                           # Variables de configuration
├── 01_check_prerequisites.yml         # Vérification des prérequis
├── 02_prepare_source.yml              # Préparation de la partition source
├── 03_prepare_target.yml              # Préparation de la partition cible
├── 04_configure_replication.yml       # Configuration de la réplication
├── 05_initial_sync.yml                # Synchronisation initiale
├── 06_validate_sync.yml               # Validation de la synchronisation
├── 07_pre_migration_checks.yml        # Vérifications pré-migration
├── 08_post_migration_validation.yml   # Validation post-migration
└── main_migration.yml                 # Playbook principal orchestrant tout
```

## Prérequis

### Sur la machine de contrôle Ansible

```bash
# Installer Ansible
pip install ansible

# Installer la collection IBM i
ansible-galaxy collection install ibm.power_ibmi

# Installer les dépendances Python
pip install itoolkit ibm_db
```

### Sur les partitions IBM i

```bash
# Installer Python 3 et les dépendances
# Via ACS (Access Client Solutions) ou yum

# Installer OpenSSH
yum install openssh openssh-server

# Démarrer SSH
STRTCPSVR SERVER(*SSHD)

# Créer l'utilisateur Ansible
CRTUSRPRF USRPRF(ANSIBLE) PASSWORD(VotreMotDePasse) 
          USRCLS(*SECOFR) SPCAUT(*ALLOBJ *IOSYSCFG)
```

## Configuration

### 1. Éditer l'inventaire

Copier et éditer `inventory.ini`:

```ini
[ibmi_source]
source ansible_host=192.168.1.10

[ibmi_target]
target ansible_host=192.168.1.11

[ibmi_all:children]
ibmi_source
ibmi_target

[ibmi_all:vars]
ansible_user=ANSIBLE
ansible_ssh_pass=VotreMotDePasse
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
```

### 2. Éditer les variables

Copier et éditer `vars.yml` avec vos paramètres spécifiques.

## Utilisation

### Vérification des prérequis

```bash
ansible-playbook -i inventory.ini 01_check_prerequisites.yml
```

### Préparation complète

```bash
# Préparer la partition source
ansible-playbook -i inventory.ini 02_prepare_source.yml

# Préparer la partition cible
ansible-playbook -i inventory.ini 03_prepare_target.yml
```

### Configuration de la réplication

```bash
ansible-playbook -i inventory.ini 04_configure_replication.yml
```

### Synchronisation initiale

```bash
ansible-playbook -i inventory.ini 05_initial_sync.yml
```

### Validation

```bash
# Valider la synchronisation
ansible-playbook -i inventory.ini 06_validate_sync.yml

# Vérifications pré-migration
ansible-playbook -i inventory.ini 07_pre_migration_checks.yml
```

### Migration complète (orchestration)

```bash
ansible-playbook -i inventory.ini main_migration.yml
```

### Validation post-migration

```bash
ansible-playbook -i inventory.ini 08_post_migration_validation.yml
```

## Playbooks Détaillés

### 01_check_prerequisites.yml
Vérifie tous les prérequis:
- Versions IBM i
- PTFs installés
- Espace disque
- Configuration réseau
- Connectivité

### 02_prepare_source.yml
Prépare la partition source:
- Collecte des informations système
- Création des utilisateurs de réplication
- Configuration du réseau de réplication
- Sauvegarde complète

### 03_prepare_target.yml
Prépare la partition cible:
- Configuration de base
- Création des utilisateurs
- Configuration réseau
- Préparation du stockage

### 04_configure_replication.yml
Configure la réplication:
- Installation PowerHA (si nécessaire)
- Configuration du cluster
- Configuration des groupes de réplication
- Démarrage de la réplication

### 05_initial_sync.yml
Effectue la synchronisation initiale:
- Sauvegarde de la source
- Transfert vers la cible
- Restauration sur la cible
- Vérification de l'intégrité

### 06_validate_sync.yml
Valide la synchronisation:
- Vérification de l'état de réplication
- Comparaison des données
- Tests de connectivité
- Génération de rapports

### 07_pre_migration_checks.yml
Vérifications avant migration:
- État de la réplication
- Jobs actifs
- Espace disque
- Connectivité réseau
- Génération de checklist

### 08_post_migration_validation.yml
Validation après migration:
- Tests fonctionnels
- Tests de performance
- Validation des données
- Génération de rapport

### main_migration.yml
Orchestration complète:
- Exécute tous les playbooks dans l'ordre
- Gère les erreurs
- Génère des rapports
- Envoie des notifications

## Rapports

Les rapports sont générés dans le répertoire `reports/`:
- `prerequisites_report.html` - Rapport des prérequis
- `sync_status_report.html` - État de la synchronisation
- `pre_migration_report.html` - Rapport pré-migration
- `post_migration_report.html` - Rapport post-migration

## Notifications

Les playbooks peuvent envoyer des notifications par:
- Email (SMTP)
- Slack
- Microsoft Teams
- Webhook personnalisé

Configurer dans `vars.yml`:

```yaml
notifications:
  enabled: true
  email:
    smtp_server: smtp.example.com
    smtp_port: 587
    from: ansible@example.com
    to: admin@example.com
  slack:
    webhook_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Dépannage

### Erreur de connexion SSH

```bash
# Vérifier que SSH est démarré sur IBM i
ssh ansible@192.168.1.10 "system 'NETSTAT *CNN'"

# Tester la connexion
ansible ibmi_all -i inventory.ini -m ping
```

### Erreur de permissions

```bash
# Vérifier les autorisations de l'utilisateur
ssh ansible@192.168.1.10 "system 'DSPUSRPRF USRPRF(ANSIBLE)'"
```

### Erreur Python

```bash
# Vérifier l'installation Python
ssh ansible@192.168.1.10 "/QOpenSys/pkgs/bin/python3 --version"

# Installer les packages manquants
ssh ansible@192.168.1.10 "yum install python3-itoolkit python3-ibm_db"
```

## Support

Pour toute question ou problème:
1. Consulter le guide complet: `IBM_i_MIGRATE_WHILE_ACTIVE_GUIDE.md`
2. Vérifier les logs Ansible: `ansible.log`
3. Contacter le support IBM

## Licence

Ce projet est fourni sous licence MIT.