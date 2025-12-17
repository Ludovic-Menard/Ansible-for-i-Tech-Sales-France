# Configuration SR-IOV pour IBM i avec Ansible

## 📋 Description

Ce projet Ansible automatise la configuration SR-IOV (Single Root I/O Virtualization) pour les partitions IBM i. SR-IOV permet d'améliorer significativement les performances réseau en donnant un accès direct aux ressources matérielles, en contournant la couche de virtualisation VIOS.

## 🎯 Objectifs

- Automatiser la configuration SR-IOV sur IBM i
- Réduire la latence réseau
- Améliorer le débit réseau
- Diminuer la charge CPU sur VIOS
- Fournir une documentation complète en français

## 📊 Avantages SR-IOV

| Critère | Adaptateur Virtuel | SR-IOV |
|---------|-------------------|---------|
| **Latence** | ~100-200 µs | ~10-20 µs |
| **Débit** | 8-9 Gbps | 9.5+ Gbps |
| **CPU VIOS** | 15-25% | 2-5% |
| **Flexibilité** | ✅ Haute | ⚠️ Moyenne |
| **Live Migration** | ✅ Oui | ❌ Non |

## 🔧 Prérequis

### Matériel
- ✅ Serveur IBM Power Systems (Power8 ou supérieur)
- ✅ Adaptateurs réseau compatibles SR-IOV:
  - IBM 10GbE SR-IOV Ethernet Adapter
  - IBM 25GbE SR-IOV Ethernet Adapter
  - IBM 40GbE SR-IOV Ethernet Adapter
- ✅ Firmware HMC à jour (V9R1M940 ou supérieur recommandé)

### Logiciel
- ✅ IBM i 7.3 TR11 ou supérieur (7.4 ou 7.5 recommandé)
- ✅ HMC (Hardware Management Console) configurée
- ✅ Ansible 2.9 ou supérieur
- ✅ Collection Ansible: `ibm.power_ibmi` (version 1.5.0+)
- ✅ Python 3.6+ sur le serveur de contrôle Ansible

### Permissions
- ✅ Accès administrateur sur HMC (hscroot ou équivalent)
- ✅ Profil utilisateur IBM i avec:
  - `*ALLOBJ` (tous les objets)
  - `*IOSYSCFG` (configuration I/O système)
  - `*SECADM` (administration sécurité)
- ✅ Accès SSH configuré sur IBM i

## 📁 Structure du Projet

```
playbooks/sriov_config/
├── configure_sriov.yml              # 🎯 Playbook principal
├── inventory.ini                    # 📝 Inventaire des systèmes
├── vars.yml                         # ⚙️ Variables de configuration
├── README.md                        # 📖 Cette documentation
├── PLAN_SRIOV.md                   # 📋 Plan détaillé
│
├── roles/                           # 🎭 Rôles Ansible
│   ├── sriov_check/                # ✓ Vérification prérequis
│   │   ├── tasks/main.yml
│   │   ├── defaults/main.yml
│   │   └── templates/
│   │       └── check_report.j2
│   │
│   ├── sriov_configure/            # ⚙️ Configuration SR-IOV
│   │   ├── tasks/main.yml
│   │   ├── defaults/main.yml
│   │   └── templates/
│   │       ├── create_line.cl      # Script CL création ligne
│   │       └── configure_tcp.cl    # Script CL config TCP/IP
│   │
│   └── sriov_validate/             # ✅ Validation
│       ├── tasks/main.yml
│       ├── defaults/main.yml
│       └── templates/
│           └── validation_report.j2
│
└── files/
    └── sriov_commands.txt          # 📝 Commandes de référence
```

## 🚀 Installation

### 1. Cloner le dépôt
```bash
cd playbooks/sriov_config
```

### 2. Installer les collections Ansible requises
```bash
ansible-galaxy collection install ibm.power_ibmi
```

### 3. Configurer l'inventaire
Éditer [`inventory.ini`](inventory.ini) avec vos informations:
```ini
[ibmi_servers]
ibmi_prod ansible_host=192.168.1.100 ansible_user=QSECOFR

[hmc_servers]
hmc01 ansible_host=192.168.1.10 ansible_user=hscroot

[ibmi_servers:vars]
ansible_python_interpreter=/QOpenSys/pkgs/bin/python3
```

### 4. Configurer les variables
Éditer [`vars.yml`](vars.yml) selon votre environnement:
```yaml
# Informations HMC
hmc_host: "192.168.1.10"
hmc_user: "hscroot"

# Informations partition
partition_name: "IBMI_PROD"
managed_system: "Server-8284-22A"

# Configuration SR-IOV
sriov_adapter_id: "U78CB.001.WZS0CW5-P1-C2"
sriov_vf_number: 1
sriov_capacity: 10

# Configuration réseau IBM i
line_description: "ETHLINE01"
interface_name: "SRIOV01"
ip_address: "192.168.100.50"
subnet_mask: "255.255.255.0"
gateway: "192.168.100.1"
```

## 📖 Utilisation

### Mode Standard - Configuration Complète

```bash
# Exécuter la configuration complète
ansible-playbook -i inventory.ini configure_sriov.yml

# Avec vérification préalable (dry-run)
ansible-playbook -i inventory.ini configure_sriov.yml --check

# Avec verbosité pour le débogage
ansible-playbook -i inventory.ini configure_sriov.yml -vvv
```

### Mode Étape par Étape

```bash
# 1. Vérification uniquement
ansible-playbook -i inventory.ini configure_sriov.yml --tags check

# 2. Configuration uniquement
ansible-playbook -i inventory.ini configure_sriov.yml --tags configure

# 3. Validation uniquement
ansible-playbook -i inventory.ini configure_sriov.yml --tags validate
```

### Exemples de Scénarios

#### Scénario 1: Première installation
```bash
# Vérifier l'environnement
ansible-playbook -i inventory.ini configure_sriov.yml --tags check

# Si OK, configurer
ansible-playbook -i inventory.ini configure_sriov.yml --tags configure,validate
```

#### Scénario 2: Ajouter une deuxième interface SR-IOV
```bash
# Modifier vars.yml pour la deuxième interface
# sriov_vf_number: 2
# line_description: "ETHLINE02"
# ip_address: "192.168.100.51"

ansible-playbook -i inventory.ini configure_sriov.yml
```

#### Scénario 3: Validation après maintenance
```bash
ansible-playbook -i inventory.ini configure_sriov.yml --tags validate
```

## 🔍 Vérification Manuelle

### Sur IBM i

```bash
# Se connecter en SSH
ssh QSECOFR@192.168.1.100

# Vérifier le matériel
WRKHDWRSC TYPE(*CMN) RSRCNAME(LIN*)

# Vérifier les lignes de communication
WRKCFGSTS *LIN

# Vérifier les interfaces TCP/IP
NETSTAT *IFC

# Tester la connectivité
PING RMTSYS('192.168.100.1')

# Vérifier les statistiques réseau
WRKTCPSTS *IFC
```

### Sur HMC

```bash
# Se connecter en SSH
ssh hscroot@192.168.1.10

# Lister les adaptateurs SR-IOV
lshwres -r sriov --rsubtype adapter -m Server-8284-22A

# Vérifier les Virtual Functions
lshwres -r sriov --rsubtype logport -m Server-8284-22A \
  --filter "adapter_id=U78CB.001.WZS0CW5-P1-C2"

# Vérifier l'assignation à la partition
lshwres -r sriov -m Server-8284-22A -p IBMI_PROD
```

## 📊 Tests de Performance

### Test de latence
```bash
# Sur IBM i
ping -s 64 -c 1000 192.168.100.1 | grep avg
ping -s 1500 -c 1000 192.168.100.1 | grep avg
```

### Test de débit
```bash
# Installer iperf3 sur IBM i (via yum)
yum install iperf3

# Sur le serveur distant (Linux/Windows)
iperf3 -s

# Sur IBM i
iperf3 -c 192.168.100.10 -t 60 -P 4
```

### Comparaison Avant/Après
```bash
# Sauvegarder les métriques avant SR-IOV
WRKTCPSTS *IFC > /tmp/before_sriov.txt

# Après configuration SR-IOV
WRKTCPSTS *IFC > /tmp/after_sriov.txt

# Comparer les résultats
```

## 🛠️ Dépannage

### Problème: VF non visible dans IBM i

**Symptômes**: La Virtual Function n'apparaît pas dans `WRKHDWRSC`

**Solutions**:
1. Vérifier l'assignation dans HMC:
   ```bash
   lshwres -r sriov -m <system> -p <partition>
   ```
2. Redémarrer la partition IBM i
3. Vérifier les logs système:
   ```
   DSPLOG QHST
   ```

### Problème: Ligne ne démarre pas

**Symptômes**: `WRKCFGSTS *LIN` montre la ligne en statut VARIED OFF

**Solutions**:
1. Vérifier le RSRCNAME correspond au matériel:
   ```
   WRKHDWRSC TYPE(*CMN)
   ```
2. Vérifier les paramètres de vitesse:
   ```
   DSPLINETH LIND(ETHLINE01)
   ```
3. Essayer de démarrer manuellement:
   ```
   VRYCFG CFGOBJ(ETHLINE01) CFGTYPE(*LIN) STATUS(*ON)
   ```

### Problème: Pas de connectivité réseau

**Symptômes**: PING échoue, pas de trafic réseau

**Solutions**:
1. Vérifier la configuration IP:
   ```
   NETSTAT *IFC
   ```
2. Vérifier le VLAN (si utilisé):
   ```
   DSPLINETH LIND(ETHLINE01)
   ```
3. Vérifier la route par défaut:
   ```
   NETSTAT *RTE
   ```
4. Tester avec traceroute:
   ```
   TRACEROUTE RMTSYS('192.168.100.1')
   ```

### Problème: Performances décevantes

**Symptômes**: Débit inférieur aux attentes

**Solutions**:
1. Vérifier l'allocation de bande passante sur HMC
2. Activer les jumbo frames (MTU 9000):
   ```
   CHGLINETH LIND(ETHLINE01) MAXFRAME(8996)
   ```
3. Vérifier les statistiques d'erreurs:
   ```
   WRKTCPSTS *IFC
   ```
4. Analyser avec Performance Tools (si disponible)

## 🔄 Rollback

### Procédure de retour arrière complète

```bash
# 1. Sauvegarder la configuration actuelle
ansible-playbook -i inventory.ini configure_sriov.yml --tags validate

# 2. Exécuter le rollback sur IBM i
ssh QSECOFR@192.168.1.100

# Arrêter l'interface
ENDTCPIFC INTNETADR('192.168.100.50')

# Supprimer la ligne
VRYCFG CFGOBJ(ETHLINE01) CFGTYPE(*LIN) STATUS(*OFF)
DLTLINETH LIND(ETHLINE01)

# 3. Retirer la VF de la partition (sur HMC)
ssh hscroot@192.168.1.10
chhwres -r sriov -m Server-8284-22A -o r \
  -p IBMI_PROD --id U78CB.001.WZS0CW5-P1-C2 \
  --logport 1

# 4. Reconfigurer l'adaptateur virtuel standard
# (suivre la procédure standard de votre organisation)
```

## 📚 Documentation Complémentaire

- [Plan détaillé SR-IOV](PLAN_SRIOV.md) - Architecture et détails techniques
- [IBM i Network Configuration Guide](https://www.ibm.com/docs/en/i/7.5?topic=concepts-tcpip-configuration)
- [PowerVM SR-IOV Configuration](https://www.ibm.com/docs/en/power-systems)
- [Ansible for IBM i](https://galaxy.ansible.com/ibm/power_ibmi)

## ⚠️ Notes Importantes

### Limitations SR-IOV
- ❌ **Pas de Live Partition Mobility**: La partition ne peut pas être migrée à chaud
- ❌ **Dépendance matérielle**: Lié à un adaptateur physique spécifique
- ⚠️ **Moins de flexibilité**: Moins d'options de configuration que SEA/VIOS
- ⚠️ **Complexité**: Configuration plus technique

### Recommandations
- ✅ Tester d'abord dans un environnement de développement
- ✅ Planifier une fenêtre de maintenance (arrêt partition requis)
- ✅ Sauvegarder la configuration réseau avant modification
- ✅ Documenter tous les changements
- ✅ Avoir un plan de rollback prêt
- ✅ Former l'équipe sur la nouvelle configuration

### Cas d'Usage Idéaux
- 🎯 Applications nécessitant une latence minimale
- 🎯 Bases de données avec beaucoup de trafic réseau
- 🎯 Serveurs d'applications critiques
- 🎯 Environnements de production stables (pas de migration fréquente)

## 🤝 Support

Pour toute question ou problème:
1. Consulter la [documentation détaillée](PLAN_SRIOV.md)
2. Vérifier les logs Ansible: `/var/log/ansible.log`
3. Vérifier les logs IBM i: `DSPLOG QHST`
4. Contacter le support IBM si nécessaire

## 📝 Licence

Ce projet est fourni tel quel, sans garantie. Utilisez-le à vos propres risques.

## 🔄 Historique des Versions

- **v1.0.0** (2025-12-17): Version initiale
  - Configuration SR-IOV de base
  - Vérification des prérequis
  - Validation automatique
  - Documentation complète en français

---

**Auteur**: Configuration automatisée pour IBM i  
**Date**: Décembre 2025  
**Version**: 1.0.0