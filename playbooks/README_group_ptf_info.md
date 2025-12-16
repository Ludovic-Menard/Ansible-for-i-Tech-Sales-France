# Playbook GROUP_PTF_INFO - Documentation

## Description

Ces playbooks permettent d'interroger la vue système `QSYS2.GROUP_PTF_INFO` sur un système IBM i pour obtenir des informations sur les groupes de PTF (Program Temporary Fix).

## Fichiers créés

### 1. mop_group_ptf_info.yml (Version simple)
Playbook basique qui exécute la requête SQL et affiche les résultats dans la console.

### 2. mop_group_ptf_info_V2.yml (Version avec export CSV)
Playbook avancé qui exécute la requête SQL, affiche les résultats ET génère un fichier CSV.

### 3. group_ptf_info_csv.j2
Template Jinja2 pour générer le fichier CSV avec les colonnes suivantes :
- PTF_GROUP_NUMBER
- PTF_GROUP_TITLE
- PTF_GROUP_DESCRIPTION
- PTF_GROUP_LEVEL
- PTF_GROUP_STATUS
- PTF_GROUP_RELEASE
- PTF_GROUP_CURRENCY
- PTF_GROUP_TYPE

## Prérequis

- Collection Ansible : `ibm.power_ibmi`
- Accès SSH au système IBM i
- Fichier d'inventaire configuré (hosts ou hosts_IBMi.ini)

## Utilisation

### Version simple (affichage console uniquement)

```bash
ansible-playbook -i hosts playbooks/mop_group_ptf_info.yml
```

### Version avec export CSV

```bash
ansible-playbook -i hosts playbooks/mop_group_ptf_info_V2.yml
```

Le fichier CSV sera généré dans : `/home/ludo/group_ptf_info.csv`

### Exécution avec tags

Pour exécuter uniquement la requête SQL :
```bash
ansible-playbook -i hosts playbooks/mop_group_ptf_info_V2.yml --tags group_ptf_info
```

Pour exécuter uniquement l'export CSV :
```bash
ansible-playbook -i hosts playbooks/mop_group_ptf_info_V2.yml --tags export_csv
```

## Variables personnalisables

Dans le playbook, vous pouvez modifier :

```yaml
vars:
  user_profile: ludo              # Profil utilisateur pour l'export CSV
  become_user_name: null          # Utilisateur pour élévation de privilèges
  become_user_password: null      # Mot de passe pour élévation de privilèges
```

## Informations retournées

La requête `SELECT * FROM QSYS2.GROUP_PTF_INFO` retourne des informations sur :
- Les groupes de PTF disponibles
- Leur statut d'installation
- Les niveaux de version
- Les dates de mise à jour
- Les descriptions et types de groupes

## Exemples de résultats

### Affichage console
```json
{
  "row": [
    {
      "PTF_GROUP_NUMBER": "SF99740",
      "PTF_GROUP_TITLE": "740 IBM i Group",
      "PTF_GROUP_STATUS": "INSTALLED",
      "PTF_GROUP_LEVEL": "23456",
      ...
    }
  ]
}
```

### Fichier CSV
```csv
PTF_GROUP_NUMBER,PTF_GROUP_TITLE,PTF_GROUP_DESCRIPTION,PTF_GROUP_LEVEL,PTF_GROUP_STATUS,...
SF99740,740 IBM i Group,IBM i 7.4 Group PTF,23456,INSTALLED,...
```

## Dépannage

### Erreur de connexion
Vérifiez que :
- Le système IBM i est accessible
- Les credentials SSH sont corrects
- Le fichier d'inventaire est bien configuré

### Erreur SQL
Si la requête échoue, vérifiez que :
- L'utilisateur a les droits d'accès à QSYS2
- La vue GROUP_PTF_INFO existe (disponible sur IBM i 7.2+)

### Erreur d'export CSV
Vérifiez que :
- Le répertoire `/home/ludo/` existe
- L'utilisateur a les droits d'écriture
- Le template `group_ptf_info_csv.j2` est présent

## Auteur

Créé pour le projet Ansible-for-i-Tech-Sales-France
Basé sur la structure des playbooks existants (mop_ptfs_list.yml)