# Guide d'Installation de Bob Shell sur IBM i

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Qu'est-ce que Bob Shell ?](#quest-ce-que-bob-shell)
3. [Prérequis](#prérequis)
4. [Vérification de l'environnement](#vérification-de-lenvironnement)
5. [Installation de Bob Shell](#installation-de-bob-shell)
6. [Configuration de Bob Shell](#configuration-de-bob-shell)
7. [Utilisation de Bob Shell](#utilisation-de-bob-shell)
8. [Intégration avec les projets existants](#intégration-avec-les-projets-existants)
9. [Dépannage](#dépannage)
10. [Ressources](#ressources)

---

## Vue d'ensemble

Ce guide fournit une procédure complète pour installer et configurer **Bob Shell** (Better Object Builder) sur IBM i, couvrant toutes les versions d'IBM i (7.3, 7.4, 7.5, 7.6) et tous les scénarios d'utilisation.

---

## Qu'est-ce que Bob Shell ?

**Bob Shell** (Better Object Builder) est un outil de build moderne pour IBM i qui permet de :

- ✅ Compiler des programmes RPG, COBOL, CL, etc. depuis la ligne de commande
- ✅ Gérer des projets de développement avec des fichiers de configuration
- ✅ Intégrer le développement IBM i avec Git et les outils CI/CD
- ✅ Automatiser les builds et les déploiements
- ✅ Utiliser des conventions modernes de développement (fichiers sources dans IFS)

### Avantages de Bob Shell

| Fonctionnalité | Description |
|----------------|-------------|
| **Build automatisé** | Compile automatiquement tous les objets d'un projet |
| **Gestion de dépendances** | Détecte et compile dans le bon ordre |
| **Configuration flexible** | Fichiers `.bob` pour définir les règles de build |
| **Intégration Git** | Travaillez avec des sources dans l'IFS |
| **CI/CD Ready** | S'intègre facilement dans des pipelines |

---

## Prérequis

### Versions IBM i supportées
- IBM i 7.3 TR11 ou supérieur
- IBM i 7.4 TR5 ou supérieur
- IBM i 7.5 (toutes versions)
- IBM i 7.6 (toutes versions)

### Produits sous licence requis
```
5770SS1 Option 30 - Qshell
5770SS1 Option 33 - PASE
5770SS1 Option 34 - Digital Certificate Manager
5770DG1 - IBM HTTP Server for i
```

### Vérifier les produits installés
```
DSPSFWRSC
```

Recherchez les options 30, 33, 34 de 5770SS1.

### Compilateurs requis (selon vos besoins)
- **5770WDS** - IBM Rational Development Studio for i (pour RPG, COBOL, CL)
- **5770BR1** - Backup Recovery and Media Services for i

---

## Vérification de l'environnement

### Étape 1 : Vérifier l'accès PASE

```bash
# Se connecter en SSH ou utiliser QP2TERM
ssh votre_user@votre_ibmi

# Vérifier que vous êtes dans PASE
echo $SHELL
# Résultat attendu : /QOpenSys/pkgs/bin/bash ou /usr/bin/sh
```

Si vous n'êtes pas dans PASE :
```bash
# Démarrer PASE depuis 5250
CALL QP2TERM
```

### Étape 2 : Vérifier yum

```bash
# Vérifier si yum est disponible
which yum
# Résultat attendu : /QOpenSys/pkgs/bin/yum

# Si yum n'est pas trouvé, l'installer
```

#### Installation de yum (si nécessaire)

**Pour IBM i 7.3 et 7.4 :**
```bash
# Télécharger le bootstrap depuis IBM
# Via navigateur web : https://public.dhe.ibm.com/software/ibmi/products/pase/rpms/

# Ou via FTP
ftp public.dhe.ibm.com
# User: anonymous
# Password: votre_email@example.com
cd /software/ibmi/products/pase/rpms
get bootstrap.tar.Z
quit

# Extraire et installer
uncompress bootstrap.tar.Z
tar -xvf bootstrap.tar
/QOpenSys/QIBM/ProdData/OPS/tools/lib/bootstrap.sh
```

**Pour IBM i 7.5 et 7.6 :**
```bash
# yum est généralement pré-installé
# Mettre à jour yum
yum update yum
```

### Étape 3 : Vérifier Python3

```bash
# Vérifier Python3
python3 --version
# Résultat attendu : Python 3.9.x ou supérieur

# Si Python3 n'est pas installé
yum install python39
yum install python39-pip
```

### Étape 4 : Vérifier Node.js (requis pour Bob Shell)

```bash
# Vérifier Node.js
node --version
# Résultat attendu : v18.x.x ou supérieur

# Vérifier npm
npm --version
# Résultat attendu : 9.x.x ou supérieur
```

---

## Installation de Bob Shell

### Méthode 1 : Installation via npm (Recommandée)

```bash
# 1. Installer Node.js si nécessaire
yum install nodejs18

# 2. Vérifier l'installation
node --version
npm --version

# 3. Installer Bob Shell globalement
npm install -g @ibm/bob

# 4. Vérifier l'installation
bob --version
# Résultat attendu : @ibm/bob version x.x.x

# 5. Afficher l'aide
bob --help
```

### Méthode 2 : Installation depuis les sources (Alternative)

```bash
# 1. Installer Git si nécessaire
yum install git

# 2. Cloner le dépôt Bob Shell
cd /home/votre_user
git clone https://github.com/IBM/ibmi-bob.git
cd ibmi-bob

# 3. Installer les dépendances
npm install

# 4. Créer un lien symbolique global
npm link

# 5. Vérifier l'installation
bob --version
```

### Vérification de l'installation

```bash
# Tester Bob Shell
bob --help

# Résultat attendu :
# Usage: bob [options] [command]
# 
# Better Object Builder for IBM i
# 
# Options:
#   -V, --version        output the version number
#   -h, --help           display help for command
# 
# Commands:
#   build [options]      Build the project
#   clean                Clean build artifacts
#   init                 Initialize a new Bob project
#   help [command]       display help for command
```

---

## Configuration de Bob Shell

### Étape 1 : Créer un projet Bob

```bash
# Naviguer vers votre répertoire de projet
cd /home/votre_user/mon_projet

# Initialiser un projet Bob
bob init

# Cela crée un fichier .bob/Rules.mk
```

### Étape 2 : Structure d'un projet Bob

```
mon_projet/
├── .bob/
│   └── Rules.mk          # Règles de build
├── src/
│   ├── QRPGLESRC/       # Sources RPG
│   │   └── MYPGM.RPGLE
│   ├── QCLSRC/          # Sources CL
│   │   └── MYCMD.CLP
│   └── QDDSSRC/         # Sources DDS
│       └── MYFILE.PF
├── .gitignore
└── README.md
```

### Étape 3 : Configurer Rules.mk

Créer ou éditer `.bob/Rules.mk` :

```makefile
# Configuration Bob Shell pour mon projet

# Bibliothèque cible
TGTLIB = MYLIB

# Répertoires sources
RPGLESRC = src/QRPGLESRC
CLSRC = src/QCLSRC
DDSSRC = src/QDDSSRC

# Options de compilation RPG
RPGFLAGS = DBGVIEW(*SOURCE) OPTION(*EVENTF) TGTRLS(*CURRENT)

# Options de compilation CL
CLFLAGS = DBGVIEW(*SOURCE)

# Règles de build
%.PGM: $(RPGLESRC)/%.RPGLE
	@echo "Compiling RPG program $@..."
	system "CRTBNDRPG PGM($(TGTLIB)/$*) SRCSTMF('$<') $(RPGFLAGS)"

%.PGM: $(CLSRC)/%.CLP
	@echo "Compiling CL program $@..."
	system "CRTBNDCL PGM($(TGTLIB)/$*) SRCSTMF('$<') $(CLFLAGS)"

%.FILE: $(DDSSRC)/%.PF
	@echo "Creating physical file $@..."
	system "CRTPF FILE($(TGTLIB)/$*) SRCSTMF('$<')"

# Cible par défaut
all: build

# Nettoyer
clean:
	system "CLRLIB LIB($(TGTLIB))"

.PHONY: all clean
```

### Étape 4 : Fichier de configuration iproj.json (Optionnel)

Créer `iproj.json` pour une configuration plus avancée :

```json
{
  "version": "1.0.0",
  "name": "MonProjet",
  "description": "Mon projet IBM i avec Bob Shell",
  "objlib": "MYLIB",
  "curlib": "MYLIB",
  "includePath": [
    "src/QRPGLESRC",
    "src/QRPGLEREF"
  ],
  "preUsrlibl": [],
  "postUsrlibl": [],
  "setIBMiEnvCmd": [],
  "extensions": {
    "rpgle": "**/*.{rpgle,sqlrpgle}",
    "cl": "**/*.{clle,clp}",
    "dds": "**/*.{pf,lf,dspf,prtf}"
  },
  "buildOptions": {
    "rpgle": {
      "DBGVIEW": "*SOURCE",
      "OPTION": "*EVENTF",
      "TGTRLS": "*CURRENT"
    },
    "cl": {
      "DBGVIEW": "*SOURCE"
    }
  }
}
```

---

## Utilisation de Bob Shell

### Commandes de base

#### 1. Initialiser un projet
```bash
cd /home/votre_user/nouveau_projet
bob init
```

#### 2. Compiler le projet
```bash
# Compiler tous les objets
bob --build

# Compiler avec verbosité
bob --build -v

# Compiler un objet spécifique
bob --build src/QRPGLESRC/MYPGM.RPGLE
```

#### 3. Nettoyer le projet
```bash
# Supprimer les objets compilés
bob clean
```

#### 4. Afficher les informations
```bash
# Afficher la configuration
bob --info

# Afficher la version
bob --version
```

### Workflow de développement typique

```bash
# 1. Créer/modifier un source
vi src/QRPGLESRC/MYPGM.RPGLE

# 2. Compiler
bob --build

# 3. Tester
system "CALL MYLIB/MYPGM"

# 4. Commiter dans Git
git add src/QRPGLESRC/MYPGM.RPGLE
git commit -m "Update MYPGM"
git push
```

---

## Intégration avec les projets existants

### Exemple 1 : Compiler CPUSTRESS_V2 avec Bob

Basé sur votre projet existant :

```bash
# 1. Naviguer vers le répertoire du projet
cd /home/votre_user/stress_tests

# 2. Créer la structure Bob
mkdir -p .bob
mkdir -p src/QRPGLESRC

# 3. Copier le source
cp /path/to/CPUSTRESS_V2.RPGLE src/QRPGLESRC/CPUSTRV2.RPGLE

# 4. Créer Rules.mk
cat > .bob/Rules.mk << 'EOF'
TGTLIB = STRESSLIB
RPGLESRC = src/QRPGLESRC

%.PGM: $(RPGLESRC)/%.RPGLE
	system "CRTBNDRPG PGM($(TGTLIB)/$*) SRCSTMF('$<') DBGVIEW(*SOURCE) DFTACTGRP(*NO) ACTGRP(*NEW)"

all: CPUSTRV2.PGM

.PHONY: all
EOF

# 5. Compiler avec Bob
bob --build

# 6. Vérifier
system "CALL STRESSLIB/CPUSTRV2 PARM(60 'LIGHT' ' ')"
```

### Exemple 2 : Projet multi-sources

```bash
# Structure du projet
mon_projet/
├── .bob/
│   └── Rules.mk
├── src/
│   ├── QRPGLESRC/
│   │   ├── PGM001.RPGLE
│   │   ├── PGM002.RPGLE
│   │   └── PGM003.RPGLE
│   ├── QCLSRC/
│   │   └── SETUP.CLP
│   └── QDDSSRC/
│       └── MYFILE.PF

# Rules.mk pour compiler tout
cat > .bob/Rules.mk << 'EOF'
TGTLIB = MYLIB
RPGLESRC = src/QRPGLESRC
CLSRC = src/QCLSRC
DDSSRC = src/QDDSSRC

# Lister tous les programmes
RPGPGMS = PGM001 PGM002 PGM003
CLPGMS = SETUP
FILES = MYFILE

# Règles
%.PGM: $(RPGLESRC)/%.RPGLE
	system "CRTBNDRPG PGM($(TGTLIB)/$*) SRCSTMF('$<') DBGVIEW(*SOURCE)"

%.PGM: $(CLSRC)/%.CLP
	system "CRTBNDCL PGM($(TGTLIB)/$*) SRCSTMF('$<') DBGVIEW(*SOURCE)"

%.FILE: $(DDSSRC)/%.PF
	system "CRTPF FILE($(TGTLIB)/$*) SRCSTMF('$<')"

# Cibles
all: $(addsuffix .PGM,$(RPGPGMS)) $(addsuffix .PGM,$(CLPGMS)) $(addsuffix .FILE,$(FILES))

clean:
	system "CLRLIB LIB($(TGTLIB))"

.PHONY: all clean
EOF

# Compiler tout le projet
bob --build
```

### Exemple 3 : Intégration avec Git et CI/CD

```bash
# 1. Initialiser Git
cd /home/votre_user/mon_projet
git init

# 2. Créer .gitignore
cat > .gitignore << 'EOF'
# Ignorer les fichiers temporaires
*.tmp
*.log

# Ignorer les builds locaux
build/
*.o

# Garder les sources
!src/**
!.bob/**
EOF

# 3. Créer un script de build CI/CD
cat > build.sh << 'EOF'
#!/QOpenSys/pkgs/bin/bash

# Script de build pour CI/CD
set -e

echo "Starting build..."

# Créer la bibliothèque si nécessaire
system "CRTLIB LIB(MYLIB) TEXT('My Library')" || true

# Compiler avec Bob
bob --build

echo "Build completed successfully!"
EOF

chmod +x build.sh

# 4. Commiter
git add .
git commit -m "Initial commit with Bob Shell"
```

---

## Dépannage

### Problème 1 : Bob command not found

**Symptôme :**
```bash
bob --version
# bash: bob: command not found
```

**Solution :**
```bash
# Vérifier l'installation npm
npm list -g @ibm/bob

# Réinstaller si nécessaire
npm install -g @ibm/bob

# Vérifier le PATH
echo $PATH
# Doit contenir /QOpenSys/pkgs/bin

# Ajouter au PATH si nécessaire
export PATH=/QOpenSys/pkgs/bin:$PATH
echo 'export PATH=/QOpenSys/pkgs/bin:$PATH' >> ~/.bashrc
```

### Problème 2 : Erreur de compilation

**Symptôme :**
```bash
bob --build
# Error: Failed to compile MYPGM.RPGLE
```

**Solution :**
```bash
# 1. Vérifier les logs détaillés
bob --build -v

# 2. Vérifier que la bibliothèque existe
system "DSPLIB LIB(MYLIB)"

# 3. Créer la bibliothèque si nécessaire
system "CRTLIB LIB(MYLIB) TEXT('My Library')"

# 4. Vérifier les permissions
system "DSPOBJAUT OBJ(MYLIB) OBJTYPE(*LIB)"

# 5. Compiler manuellement pour voir l'erreur
system "CRTBNDRPG PGM(MYLIB/MYPGM) SRCSTMF('/home/user/src/QRPGLESRC/MYPGM.RPGLE')"
```

### Problème 3 : Node.js version incompatible

**Symptôme :**
```bash
npm install -g @ibm/bob
# Error: Requires Node.js >= 18.0.0
```

**Solution :**
```bash
# Vérifier la version actuelle
node --version

# Installer Node.js 18
yum install nodejs18

# Vérifier à nouveau
node --version
# Résultat attendu : v18.x.x

# Réinstaller Bob
npm install -g @ibm/bob
```

### Problème 4 : Permissions insuffisantes

**Symptôme :**
```bash
bob --build
# Error: Authority violation
```

**Solution :**
```bash
# Vérifier les autorisations utilisateur
system "DSPUSRPRF USRPRF(VOTRE_USER)"

# L'utilisateur doit avoir :
# - *ALLOBJ ou accès à la bibliothèque cible
# - Autorisation de créer des objets

# Accorder les autorisations nécessaires
system "GRTOBJAUT OBJ(MYLIB) OBJTYPE(*LIB) USER(VOTRE_USER) AUT(*ALL)"
```

### Problème 5 : Fichier Rules.mk non trouvé

**Symptôme :**
```bash
bob --build
# Error: No Rules.mk found
```

**Solution :**
```bash
# Vérifier la structure du projet
ls -la .bob/

# Créer le répertoire .bob si nécessaire
mkdir -p .bob

# Initialiser le projet
bob init

# Ou créer Rules.mk manuellement
cat > .bob/Rules.mk << 'EOF'
TGTLIB = MYLIB
all:
	@echo "Build rules here"
EOF
```

---

## Bonnes pratiques

### 1. Organisation des sources

```
projet/
├── .bob/
│   └── Rules.mk
├── src/
│   ├── QRPGLESRC/      # Sources RPG
│   ├── QRPGLEREF/      # Copy books RPG
│   ├── QCLSRC/         # Sources CL
│   ├── QDDSSRC/        # Sources DDS
│   └── QSQLSRC/        # Sources SQL
├── tests/              # Tests unitaires
├── docs/               # Documentation
├── .gitignore
└── README.md
```

### 2. Nommage des fichiers

```bash
# Utiliser des extensions claires
MYPGM.RPGLE      # Programme RPG ILE
MYPROC.SQLRPGLE  # Programme RPG avec SQL
MYCMD.CLP        # Programme CL
MYFILE.PF        # Physical File
MYDISP.DSPF      # Display File
```

### 3. Gestion des versions

```bash
# Utiliser Git pour le versioning
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0

# Inclure la version dans Rules.mk
VERSION = 1.0.0
```

### 4. Documentation

```bash
# Créer un README.md pour chaque projet
cat > README.md << 'EOF'
# Mon Projet IBM i

## Description
Description du projet

## Prérequis
- IBM i 7.4+
- Bob Shell
- Bibliothèque MYLIB

## Installation
```bash
bob --build
```

## Utilisation
```bash
CALL MYLIB/MYPGM
```
EOF
```

### 5. Tests automatisés

```bash
# Créer un script de test
cat > tests/run_tests.sh << 'EOF'
#!/QOpenSys/pkgs/bin/bash

echo "Running tests..."

# Test 1
system "CALL MYLIB/TESTPGM1" || exit 1

# Test 2
system "CALL MYLIB/TESTPGM2" || exit 1

echo "All tests passed!"
EOF

chmod +x tests/run_tests.sh
```

---

## Ressources

### Documentation officielle
- **Bob Shell GitHub** : https://github.com/IBM/ibmi-bob
- **IBM i Open Source** : https://ibmi-oss-docs.readthedocs.io/
- **Node.js sur IBM i** : https://nodejs.org/

### Communauté
- **IBM i OSS Community** : https://github.com/IBM/ibmi-oss-examples
- **Ryver IBM i OSS** : https://ibmioss.ryver.com/

### Outils complémentaires
- **Code for IBM i** (VS Code extension) : Intégration avec Bob Shell
- **Git for IBM i** : Gestion de version
- **Jenkins** : CI/CD avec Bob Shell

### Tutoriels
- **Getting Started with Bob** : https://github.com/IBM/ibmi-bob/wiki
- **Modern IBM i Development** : https://ibmi-oss-docs.readthedocs.io/en/latest/

---

## Annexe : Commandes utiles

### Commandes Bob Shell

```bash
# Afficher l'aide
bob --help

# Afficher la version
bob --version

# Initialiser un projet
bob init

# Compiler le projet
bob --build

# Compiler avec verbosité
bob --build -v

# Nettoyer
bob clean

# Afficher les informations
bob --info
```

### Commandes système IBM i utiles

```bash
# Créer une bibliothèque
system "CRTLIB LIB(MYLIB) TEXT('My Library')"

# Lister les objets
system "DSPLIB LIB(MYLIB)"

# Supprimer une bibliothèque
system "DLTLIB LIB(MYLIB)"

# Afficher un objet
system "DSPPGM PGM(MYLIB/MYPGM)"

# Exécuter un programme
system "CALL MYLIB/MYPGM"

# Afficher le journal
system "DSPJOBLOG"
```

### Commandes Git

```bash
# Initialiser un dépôt
git init

# Ajouter des fichiers
git add .

# Commiter
git commit -m "Message"

# Pousser vers remote
git push origin main

# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Fusionner
git merge feature/nouvelle-fonctionnalite
```

---

## Conclusion

Bob Shell est un outil puissant qui modernise le développement sur IBM i en permettant :
- ✅ Des builds automatisés et reproductibles
- ✅ L'intégration avec Git et les outils modernes
- ✅ Une meilleure organisation des projets
- ✅ La mise en place de CI/CD

Pour toute question ou problème, consultez la documentation officielle ou la communauté IBM i Open Source.

---

**Document créé le :** 2026-05-06  
**Version :** 1.0  
**Auteur :** Guide d'installation Bob Shell pour IBM i