# Guide de Démarrage Rapide - Bob Shell sur IBM i

## 🚀 Installation en 5 minutes

### Prérequis rapides
```bash
# Vérifier que vous avez accès à PASE
ssh votre_user@votre_ibmi

# Vérifier yum et Node.js
which yum && node --version
```

### Installation express

```bash
# 1. Installer Node.js (si nécessaire)
yum install -y nodejs18

# 2. Installer Bob Shell
npm install -g @ibm/bob

# 3. Vérifier
bob --version
```

---

## 📝 Premier projet en 3 étapes

### 1. Créer un projet
```bash
mkdir mon_projet
cd mon_projet
bob init
```

### 2. Ajouter un programme RPG
```bash
mkdir -p src/QRPGLESRC
cat > src/QRPGLESRC/HELLO.RPGLE << 'EOF'
**FREE
Dcl-S message Char(50);
message = 'Hello from Bob Shell!';
Dsply message;
*InLR = *On;
EOF
```

### 3. Configurer et compiler
```bash
# Éditer .bob/Rules.mk
cat > .bob/Rules.mk << 'EOF'
TGTLIB = MYLIB
RPGLESRC = src/QRPGLESRC

%.PGM: $(RPGLESRC)/%.RPGLE
	system "CRTBNDRPG PGM($(TGTLIB)/$*) SRCSTMF('$<') DBGVIEW(*SOURCE)"

all: HELLO.PGM
EOF

# Créer la bibliothèque
system "CRTLIB LIB(MYLIB)"

# Compiler
bob --build

# Exécuter
system "CALL MYLIB/HELLO"
```

---

## 🎯 Cas d'usage : Compiler CPUSTRESS_V2

```bash
# 1. Créer la structure
mkdir -p cpustress_project/src/QRPGLESRC
cd cpustress_project

# 2. Copier le source
cp /path/to/CPUSTRESS_V2.RPGLE src/QRPGLESRC/CPUSTRV2.RPGLE

# 3. Configurer Bob
cat > .bob/Rules.mk << 'EOF'
TGTLIB = STRESSLIB
RPGLESRC = src/QRPGLESRC

%.PGM: $(RPGLESRC)/%.RPGLE
	system "CRTBNDRPG PGM($(TGTLIB)/$*) SRCSTMF('$<') DBGVIEW(*SOURCE) DFTACTGRP(*NO) ACTGRP(*NEW)"

all: CPUSTRV2.PGM
EOF

# 4. Compiler
bob --build

# 5. Tester
system "CALL STRESSLIB/CPUSTRV2 PARM(60 'LIGHT' ' ')"
```

---

## 🔧 Commandes essentielles

| Commande | Description |
|----------|-------------|
| `bob init` | Initialiser un projet |
| `bob --build` | Compiler le projet |
| `bob --build -v` | Compiler avec détails |
| `bob clean` | Nettoyer les objets |
| `bob --help` | Afficher l'aide |
| `bob --version` | Afficher la version |

---

## 📚 Ressources

- **Guide complet** : [`BOB_SHELL_INSTALLATION_GUIDE.md`](BOB_SHELL_INSTALLATION_GUIDE.md)
- **Playbook Ansible** : [`ANSIBLE_BOB_SHELL_PLAYBOOK.md`](ANSIBLE_BOB_SHELL_PLAYBOOK.md)
- **Documentation officielle** : https://github.com/IBM/ibmi-bob

---

## ❓ Problèmes courants

### Bob command not found
```bash
export PATH=/QOpenSys/pkgs/bin:$PATH
echo 'export PATH=/QOpenSys/pkgs/bin:$PATH' >> ~/.bashrc
```

### Erreur de compilation
```bash
# Vérifier que la bibliothèque existe
system "CRTLIB LIB(MYLIB)"

# Compiler avec détails
bob --build -v
```

### Node.js trop ancien
```bash
# Installer Node.js 18
yum install -y nodejs18
```

---

**Besoin d'aide ?** Consultez le guide complet ou la communauté IBM i OSS.