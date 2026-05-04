# Configuration PowerSC MFA (TOTP) sur IBM i

## 📋 Vue d'ensemble

Ce projet Ansible automatise la configuration de PowerSC Multi-Factor Authentication (MFA) avec authentification TOTP (Time-based One-Time Password) sur IBM i. Il permet de sécuriser l'accès aux systèmes IBM i en ajoutant une couche d'authentification supplémentaire compatible avec des applications comme Google Authenticator, Microsoft Authenticator ou IBM Verify.

## 🎯 Objectifs

- ✅ Automatiser la configuration complète de PowerSC MFA
- ✅ Simplifier l'enregistrement des utilisateurs
- ✅ Générer automatiquement les QR codes pour l'enregistrement
- ✅ Valider la configuration avec des tests automatisés
- ✅ Fournir une documentation complète en français

## 📁 Structure du projet

```
playbooks/powersc_mfa/
├── README.md                          # Ce fichier
├── POWERSC_MFA_GUIDE.md              # Guide détaillé de configuration
├── inventory.ini                      # Inventaire des serveurs IBM i
├── vars.yml                          # Variables de configuration
├── main_configure_mfa.yml            # Orchestrateur principal
├── 01_check_prerequisites.yml        # Vérification des prérequis
├── 02_configure_mfa_server.yml       # Configuration du serveur MFA
├── 03_enroll_users.yml               # Enregistrement des utilisateurs
├── 04_test_validation.yml            # Tests et validation
├── .gitignore                        # Fichiers à ignorer
├── templates/                        # Templates Jinja2
│   ├── mfa_policy.j2                # Politique MFA
│   ├── user_enrollment.j2           # Template d'enregistrement
│   └── validation_report.html.j2    # Rapport de validation
├── files/                            # Fichiers de support
│   └── qr_code_generator.py         # Générateur de QR codes
└── reports/                          # Rapports générés (créé automatiquement)
```

## 🚀 Démarrage rapide

### Prérequis

1. **Système IBM i**
   - IBM i 7.3 ou supérieur
   - PowerSC installé et licencié
   - PTFs requis installés (voir POWERSC_MFA_GUIDE.md)

2. **Station de contrôle Ansible**
   - Ansible 2.9 ou supérieur
   - Collection IBM i pour Ansible (`ibm.power_ibmi`)
   - Python 3.6 ou supérieur
   - Modules Python : `qrcode`, `pillow`, `pyotp`

3. **Accès et privilèges**
   - Utilisateur avec *SECADM et *ALLOBJ
   - Accès SSH au système IBM i
   - Connectivité réseau

### Installation rapide

```bash
# 1. Cloner ou naviguer vers le répertoire
cd playbooks/powersc_mfa

# 2. Installer les dépendances Python
pip install -r files/requirements.txt

# 3. Installer la collection Ansible IBM i
ansible-galaxy collection install ibm.power_ibmi

# 4. Configurer l'inventaire
cp inventory.ini.example inventory.ini
# Éditer inventory.ini avec vos informations

# 5. Configurer les variables
cp vars.yml.example vars.yml
# Éditer vars.yml selon vos besoins

# 6. Exécuter le playbook principal
ansible-playbook -i inventory.ini main_configure_mfa.yml
```

## 📖 Utilisation

### Exécution complète

Pour configurer PowerSC MFA de A à Z :

```bash
ansible-playbook -i inventory.ini main_configure_mfa.yml
```

### Exécution par étapes

Vous pouvez exécuter chaque étape individuellement :

```bash
# 1. Vérifier les prérequis
ansible-playbook -i inventory.ini 01_check_prerequisites.yml

# 2. Configurer le serveur MFA
ansible-playbook -i inventory.ini 02_configure_mfa_server.yml

# 3. Enregistrer les utilisateurs
ansible-playbook -i inventory.ini 03_enroll_users.yml

# 4. Tester et valider
ansible-playbook -i inventory.ini 04_test_validation.yml
```

### Mode vérification (dry-run)

Pour simuler l'exécution sans faire de modifications :

```bash
ansible-playbook -i inventory.ini main_configure_mfa.yml --check
```

### Mode verbeux

Pour obtenir plus de détails pendant l'exécution :

```bash
ansible-playbook -i inventory.ini main_configure_mfa.yml -v   # Verbeux
ansible-playbook -i inventory.ini main_configure_mfa.yml -vv  # Très verbeux
ansible-playbook -i inventory.ini main_configure_mfa.yml -vvv # Debug
```

## 🔧 Configuration

### Variables principales (vars.yml)

```yaml
# Configuration PowerSC MFA
powersc_mfa:
  enabled: true
  totp_algorithm: "SHA256"      # SHA1, SHA256, SHA512
  totp_period: 30               # Secondes
  totp_digits: 6                # 6 ou 8 digits
  grace_period: 300             # Période de grâce en secondes
  
# Utilisateurs à enregistrer
mfa_users:
  - username: "USER1"
    email: "user1@example.com"
    description: "Administrateur système"
  - username: "USER2"
    email: "user2@example.com"
    description: "Développeur"

# Politiques de sécurité
security_policies:
  require_mfa_for_ssh: true
  require_mfa_for_5250: true
  require_mfa_for_ftp: false
  backup_codes_count: 10
  max_failed_attempts: 3
  lockout_duration: 900         # Secondes
```

### Inventaire (inventory.ini)

```ini
[ibmi_servers]
ibmi_prod ansible_host=192.168.1.100 ansible_user=QSECOFR

[ibmi_servers:vars]
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

## 📊 Rapports

Les rapports sont générés dans le répertoire `reports/` :

- `prerequisites_report_<timestamp>.html` : Rapport de vérification des prérequis
- `configuration_report_<timestamp>.html` : Rapport de configuration
- `enrollment_report_<timestamp>.html` : Rapport d'enregistrement des utilisateurs
- `validation_report_<timestamp>.html` : Rapport de validation finale
- `qr_codes/` : QR codes générés pour chaque utilisateur

## 🔐 Sécurité

### Gestion des secrets

Utilisez Ansible Vault pour protéger les informations sensibles :

```bash
# Créer un fichier vault pour les mots de passe
ansible-vault create vault.yml

# Éditer le fichier vault
ansible-vault edit vault.yml

# Exécuter avec le vault
ansible-playbook -i inventory.ini main_configure_mfa.yml --ask-vault-pass
```

### Bonnes pratiques

1. **Ne jamais commiter** les fichiers contenant des secrets
2. **Utiliser des clés SSH** plutôt que des mots de passe
3. **Limiter les privilèges** de l'utilisateur Ansible au strict nécessaire
4. **Auditer régulièrement** les logs d'authentification MFA
5. **Tester en environnement de développement** avant la production

## 🧪 Tests

### Tests unitaires

```bash
# Tester la connectivité
ansible -i inventory.ini ibmi_servers -m ping

# Tester les privilèges
ansible -i inventory.ini ibmi_servers -m ibmi_sql_query \
  -a "sql='SELECT CURRENT USER FROM SYSIBM.SYSDUMMY1'"
```

### Tests d'intégration

Le playbook `04_test_validation.yml` effectue automatiquement :
- Test d'authentification MFA avec un utilisateur test
- Vérification des logs d'authentification
- Test des codes de secours
- Validation des politiques de sécurité

## 📚 Documentation

- [POWERSC_MFA_GUIDE.md](POWERSC_MFA_GUIDE.md) : Guide détaillé de configuration
- [IBM PowerSC Documentation](https://www.ibm.com/docs/en/powersc)
- [IBM i Security Reference](https://www.ibm.com/docs/en/i/7.5?topic=security)

## 🐛 Dépannage

### Problèmes courants

**Erreur : "PowerSC not found"**
```bash
# Vérifier l'installation de PowerSC
ansible -i inventory.ini ibmi_servers -m ibmi_cl_command \
  -a "cmd='DSPOBJD OBJ(QPWRSC/*ALL) OBJTYPE(*LIB)'"
```

**Erreur : "Insufficient privileges"**
```bash
# Vérifier les privilèges de l'utilisateur
ansible -i inventory.ini ibmi_servers -m ibmi_sql_query \
  -a "sql='SELECT * FROM QSYS2.USER_INFO WHERE AUTHORIZATION_NAME = CURRENT USER'"
```

**Erreur : "QR code generation failed"**
```bash
# Installer les dépendances Python
pip install qrcode[pil] pyotp
```

### Logs

Les logs détaillés sont disponibles dans :
- `/var/log/ansible/powersc_mfa_<timestamp>.log` (station Ansible)
- `QSYS/QAUDJRN` (journal d'audit IBM i)
- PowerSC logs via `DSPPWRSCLOG`

## 🤝 Contribution

Pour contribuer à ce projet :

1. Créer une branche pour votre fonctionnalité
2. Tester vos modifications
3. Documenter les changements
4. Soumettre une pull request

## 📝 Changelog

### Version 1.0.0 (2026-01-29)
- ✨ Configuration initiale de PowerSC MFA avec TOTP
- ✨ Génération automatique de QR codes
- ✨ Playbooks de vérification et validation
- ✨ Documentation complète en français
- ✨ Templates de rapports HTML

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](../../LICENSE) pour plus de détails.

## 👥 Auteurs

- **Ludovic Menard** - Développement initial

## 🙏 Remerciements

- IBM pour PowerSC et la collection Ansible IBM i
- La communauté Ansible
- Les contributeurs du projet

## 📞 Support

Pour toute question ou problème :
- Consulter la documentation dans `POWERSC_MFA_GUIDE.md`
- Vérifier les issues GitHub
- Contacter l'équipe de support IBM i

---

**Note** : Ce projet est fourni "tel quel" sans garantie. Testez toujours en environnement de développement avant de déployer en production.