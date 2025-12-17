# Plan de Configuration SR-IOV pour IBM i

## Vue d'ensemble
Configuration SR-IOV (Single Root I/O Virtualization) pour améliorer les performances réseau d'une partition IBM i en permettant un accès direct aux ressources matérielles réseau.

## Prérequis

### Matériel
- Serveur IBM Power Systems avec support SR-IOV
- Adaptateurs réseau compatibles SR-IOV (ex: IBM 10GbE SR-IOV)
- Firmware HMC à jour

### Logiciel
- IBM i 7.3 ou supérieur
- HMC (Hardware Management Console) configurée
- Ansible 2.9+ avec collection `ibm.power_ibmi`
- Accès SSH à la partition IBM i

### Permissions
- Accès administrateur sur HMC
- Profil utilisateur avec *ALLOBJ et *IOSYSCFG sur IBM i
- Droits pour modifier la configuration LPAR

## Architecture SR-IOV

```
┌─────────────────────────────────────────┐
│         Serveur Power Systems           │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Adaptateur Physique SR-IOV      │ │
│  │   (Physical Function - PF)        │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│      ┌───────┴───────┬─────────┐       │
│      │               │         │       │
│  ┌───▼───┐      ┌───▼───┐ ┌───▼───┐  │
│  │  VF1  │      │  VF2  │ │  VF3  │  │
│  │(IBM i)│      │(VIOS) │ │(Linux)│  │
│  └───────┘      └───────┘ └───────┘  │
└─────────────────────────────────────────┘
```

## Étapes de Configuration

### 1. Vérification de l'environnement
- Vérifier le support SR-IOV sur le serveur
- Identifier les adaptateurs compatibles
- Vérifier la version du firmware
- Vérifier les slots disponibles

### 2. Configuration HMC
- Activer SR-IOV sur l'adaptateur physique
- Créer des Virtual Functions (VF)
- Définir les paramètres de bande passante
- Configurer les VLANs si nécessaire

### 3. Configuration de la partition IBM i
- Arrêter la partition (si nécessaire)
- Assigner une Virtual Function à la partition
- Configurer les paramètres réseau
- Démarrer la partition

### 4. Configuration réseau IBM i
- Créer la ligne de communication
- Configurer l'interface TCP/IP
- Définir l'adresse IP et le masque
- Configurer le routage

### 5. Validation
- Tester la connectivité réseau
- Mesurer les performances
- Vérifier la configuration SR-IOV
- Valider la haute disponibilité

## Structure des Fichiers Ansible

```
playbooks/sriov_config/
├── configure_sriov.yml          # Playbook principal
├── inventory.ini                # Inventaire des systèmes
├── vars.yml                     # Variables de configuration
├── README.md                    # Documentation
├── PLAN_SRIOV.md               # Ce fichier
├── roles/
│   ├── sriov_check/            # Vérification prérequis
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   └── templates/
│   │       └── check_report.j2
│   ├── sriov_configure/        # Configuration SR-IOV
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   └── templates/
│   │       ├── create_line.cl
│   │       └── configure_tcp.cl
│   └── sriov_validate/         # Validation
│       ├── tasks/
│       │   └── main.yml
│       ├── defaults/
│       │   └── main.yml
│       └── templates/
│           └── validation_report.j2
└── files/
    └── sriov_commands.txt      # Commandes de référence
```

## Variables de Configuration

### Variables principales (vars.yml)
```yaml
# Informations HMC
hmc_host: "hmc.example.com"
hmc_user: "hscroot"

# Informations partition
partition_name: "IBMI_PROD"
managed_system: "Server-8284-22A"

# Configuration SR-IOV
sriov_adapter_id: "U78CB.001.WZS0CW5-P1-C2"
sriov_vf_number: 1
sriov_capacity: 10  # Pourcentage de bande passante

# Configuration réseau IBM i
line_description: "ETHLINE01"
interface_name: "SRIOV01"
ip_address: "192.168.100.50"
subnet_mask: "255.255.255.0"
gateway: "192.168.100.1"
vlan_id: 100  # Optionnel
```

## Commandes IBM i Clés

### Vérification du matériel
```
WRKHDWRSC TYPE(*CMN) RSRCNAME(LIN*)
DSPHWRSC TYPE(*LIN) RSRCNAME(CMNxx)
```

### Configuration de la ligne
```
CRTLINETH LIND(ETHLINE01) RSRCNAME(CMNxx) +
          LINESPEED(10G) DUPLEX(*FULL) +
          AUTOSTART(*YES)
```

### Configuration TCP/IP
```
CFGTCP
Option 1 - Work with TCP/IP interfaces
Option 10 - Add interface
```

### Vérification
```
NETSTAT *IFC
PING RMTSYS('192.168.100.1')
WRKTCPSTS
```

## Commandes HMC

### Lister les adaptateurs SR-IOV
```bash
lshwres -r sriov --rsubtype adapter -m <managed_system>
```

### Créer une Virtual Function
```bash
chhwres -r sriov -m <managed_system> -o a \
  --id <adapter_id> --logport <vf_number> \
  -a "adapter_id=<adapter_id>,logical_port_type=eth"
```

### Assigner VF à une partition
```bash
chhwres -r sriov -m <managed_system> -o a \
  -p <partition_name> \
  --id <adapter_id> --logport <vf_number>
```

## Tests de Performance

### Mesures à effectuer
1. **Latence réseau**: Ping avec différentes tailles de paquets
2. **Débit**: Test iperf3 ou FTP de gros fichiers
3. **CPU**: Utilisation CPU pendant transferts réseau
4. **Comparaison**: Avant/après SR-IOV

### Commandes de test
```bash
# Sur IBM i
ping -s 1500 -c 100 192.168.100.1

# Test de débit (nécessite iperf3)
iperf3 -c 192.168.100.10 -t 60
```

## Dépannage

### Problèmes courants

#### 1. VF non visible dans IBM i
- Vérifier l'assignation dans HMC
- Redémarrer la partition
- Vérifier les logs: `DSPLOG QHST`

#### 2. Ligne ne démarre pas
- Vérifier RSRCNAME correspond au matériel
- Vérifier les paramètres de vitesse
- Commande: `WRKCFGSTS *LIN`

#### 3. Pas de connectivité réseau
- Vérifier configuration IP
- Vérifier VLAN si utilisé
- Tester avec `PING` et `TRACEROUTE`

#### 4. Performances décevantes
- Vérifier allocation de bande passante
- Vérifier MTU (jumbo frames)
- Analyser avec `WRKTCPSTS`

## Rollback

### Procédure de retour arrière
1. Sauvegarder la configuration actuelle
2. Supprimer l'interface SR-IOV dans IBM i
3. Supprimer la ligne de communication
4. Retirer la VF de la partition (HMC)
5. Reconfigurer l'adaptateur virtuel standard

### Commandes de rollback
```
ENDTCPIFC INTNETADR('192.168.100.50')
DLTLINETCP LIND(ETHLINE01)
VRYCFG CFGOBJ(ETHLINE01) CFGTYPE(*LIN) STATUS(*OFF)
DLTLINETH LIND(ETHLINE01)
```

## Sécurité

### Considérations
- SR-IOV bypass le VIOS = moins de contrôle
- Configurer firewall au niveau IBM i
- Utiliser VLANs pour isolation
- Activer IPsec si nécessaire
- Surveiller le trafic réseau

### Commandes de sécurité
```
CFGTCP -> Option 20 (Configure IP security)
WRKTCPSTS *CNN  # Surveiller connexions
```

## Maintenance

### Tâches régulières
- Surveiller les performances réseau
- Vérifier les logs d'erreurs
- Mettre à jour le firmware
- Tester le failover
- Documenter les changements

### Monitoring
```
WRKTCPSTS *IFC  # État des interfaces
WRKHDWRSC TYPE(*CMN)  # État du matériel
DSPLOG QHST  # Logs système
```

## Références

### Documentation IBM
- IBM i Network Configuration Guide
- PowerVM SR-IOV Configuration
- HMC Command Reference

### Liens utiles
- IBM Power Systems SR-IOV: https://www.ibm.com/docs/en/power-systems
- IBM i Network Configuration: https://www.ibm.com/docs/en/i/7.5
- Ansible for IBM i: https://galaxy.ansible.com/ibm/power_ibmi

## Notes importantes

⚠️ **Attention**:
- La configuration SR-IOV nécessite un arrêt de la partition
- Sauvegarder la configuration réseau avant modification
- Tester d'abord dans un environnement de développement
- Prévoir une fenêtre de maintenance
- Avoir un plan de rollback prêt

✅ **Avantages SR-IOV**:
- Latence réduite (bypass VIOS)
- Débit amélioré
- Moins de charge CPU sur VIOS
- Performances quasi-natives

❌ **Limitations SR-IOV**:
- Moins de flexibilité que SEA
- Pas de Live Partition Mobility
- Dépendance au matériel physique
- Configuration plus complexe