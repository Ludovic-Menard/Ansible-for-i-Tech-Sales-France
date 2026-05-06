# Guide Complet d'Audit de Sécurité IBM i

## Vue d'ensemble

Ce guide fournit des requêtes SQL complètes pour auditer la sécurité d'une partition IBM i et identifier les vulnérabilités potentielles. Toutes les requêtes utilisent les vues système QSYS2.

## Table des Matières

1. [Configuration Système de Sécurité](#1-configuration-système-de-sécurité)
2. [Gestion des Utilisateurs](#2-gestion-des-utilisateurs)
3. [Autorisations et Privilèges](#3-autorisations-et-privilèges)
4. [Audit et Journalisation](#4-audit-et-journalisation)
5. [Mots de Passe et Authentification](#5-mots-de-passe-et-authentification)
6. [Objets Sensibles](#6-objets-sensibles)
7. [Connexions et Sessions](#7-connexions-et-sessions)
8. [Conformité et Recommandations](#8-conformité-et-recommandations)

---

## 1. Configuration Système de Sécurité

### 1.1 Niveau de Sécurité Système (QSECURITY)

```sql
-- Vérifier le niveau de sécurité (doit être 40 ou 50)
SELECT 
    SYSTEM_VALUE_NAME,
    CURRENT_NUMERIC_VALUE AS SECURITY_LEVEL,
    CASE 
        WHEN CURRENT_NUMERIC_VALUE >= 50 THEN '✓ EXCELLENT'
        WHEN CURRENT_NUMERIC_VALUE = 40 THEN '✓ BON'
        WHEN CURRENT_NUMERIC_VALUE = 30 THEN '⚠ MOYEN - À améliorer'
        ELSE '✗ FAIBLE - Action requise'
    END AS EVALUATION
FROM QSYS2.SYSTEM_VALUE_INFO
WHERE SYSTEM_VALUE_NAME = 'QSECURITY';
```

### 1.2 Valeurs Système de Sécurité Critiques

```sql
-- Audit complet des valeurs système de sécurité
SELECT 
    SYSTEM_VALUE_NAME,
    CURRENT_CHARACTER_VALUE,
    CURRENT_NUMERIC_VALUE,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QSECURITY' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE >= 40 THEN '✓' ELSE '✗' END
        WHEN 'QPWDEXPITV' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE BETWEEN 30 AND 90 THEN '✓' ELSE '⚠' END
        WHEN 'QPWDMINLEN' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE >= 8 THEN '✓' ELSE '✗' END
        WHEN 'QPWDMAXLEN' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE >= 10 THEN '✓' ELSE '⚠' END
        WHEN 'QMAXSIGN' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE <= 3 THEN '✓' ELSE '⚠' END
        WHEN 'QRETSVRSEC' THEN 
            CASE WHEN CURRENT_CHARACTER_VALUE = '1' THEN '✓' ELSE '✗' END
        WHEN 'QLMTSECOFR' THEN 
            CASE WHEN CURRENT_CHARACTER_VALUE = '1' THEN '✓' ELSE '⚠' END
        ELSE '?'
    END AS STATUS,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QSECURITY' THEN 'Niveau de sécurité (40 ou 50 recommandé)'
        WHEN 'QPWDEXPITV' THEN 'Expiration mot de passe (30-90 jours)'
        WHEN 'QPWDMINLEN' THEN 'Longueur min mot de passe (8+ recommandé)'
        WHEN 'QPWDMAXLEN' THEN 'Longueur max mot de passe (10+ recommandé)'
        WHEN 'QMAXSIGN' THEN 'Tentatives connexion max (3 recommandé)'
        WHEN 'QRETSVRSEC' THEN 'Restaurer sécurité objets (1=Oui)'
        WHEN 'QLMTSECOFR' THEN 'Limiter QSECOFR (1=Oui recommandé)'
        ELSE ''
    END AS DESCRIPTION
FROM QSYS2.SYSTEM_VALUE_INFO
WHERE SYSTEM_VALUE_NAME IN (
    'QSECURITY', 'QPWDEXPITV', 'QPWDMINLEN', 'QPWDMAXLEN',
    'QMAXSIGN', 'QRETSVRSEC', 'QLMTSECOFR', 'QPWDRQDDIF',
    'QPWDLVL', 'QPWDRQDDGT', 'QPWDPOSDIF', 'QINACTITV',
    'QAUDCTL', 'QAUDLVL', 'QCRTOBJAUD', 'QAUDENDACN'
)
ORDER BY SYSTEM_VALUE_NAME;
```

### 1.3 Informations Générales de Sécurité

```sql
-- Vue d'ensemble de la sécurité système
SELECT * FROM QSYS2.SECURITY_INFO;
```

---

## 2. Gestion des Utilisateurs

### 2.1 Utilisateurs avec Privilèges Élevés (*ALLOBJ, *SECADM)

```sql
-- ⚠️ CRITIQUE: Utilisateurs avec autorités spéciales
SELECT 
    AUTHORIZATION_NAME AS USER_PROFILE,
    USER_CLASS_NAME,
    STATUS,
    SPECIAL_AUTHORITIES,
    CASE 
        WHEN SPECIAL_AUTHORITIES LIKE '%*ALLOBJ*' THEN '✗ CRITIQUE'
        WHEN SPECIAL_AUTHORITIES LIKE '%*SECADM*' THEN '⚠ ÉLEVÉ'
        WHEN SPECIAL_AUTHORITIES LIKE '%*JOBCTL*' THEN '⚠ MOYEN'
        ELSE '✓ NORMAL'
    END AS RISK_LEVEL,
    PREVIOUS_SIGNON,
    SIGN_ON_ATTEMPTS_NOT_VALID,
    PASSWORD_CHANGE_DATE,
    PASSWORD_EXPIRATION_DATE,
    DAYS_UNTIL_PASSWORD_EXPIRES,
    NO_PASSWORD_INDICATOR
FROM QSYS2.USER_INFO
WHERE SPECIAL_AUTHORITIES <> '*NONE'
   OR USER_CLASS_NAME = '*SECOFR'
ORDER BY 
    CASE 
        WHEN SPECIAL_AUTHORITIES LIKE '%*ALLOBJ*' THEN 1
        WHEN SPECIAL_AUTHORITIES LIKE '%*SECADM*' THEN 2
        ELSE 3
    END,
    AUTHORIZATION_NAME;
```

### 2.2 Comptes Utilisateurs à Risque

```sql
-- Comptes avec problèmes de sécurité
SELECT 
    AUTHORIZATION_NAME,
    STATUS,
    USER_CLASS_NAME,
    CASE 
        WHEN STATUS = '*DISABLED' THEN '✓ Désactivé'
        WHEN NO_PASSWORD_INDICATOR = 'YES' THEN '✗ CRITIQUE: Pas de mot de passe'
        WHEN PASSWORD_EXPIRATION_DATE < CURRENT_DATE THEN '✗ Mot de passe expiré'
        WHEN DAYS_UNTIL_PASSWORD_EXPIRES <= 7 THEN '⚠ Expire bientôt'
        WHEN SIGN_ON_ATTEMPTS_NOT_VALID > 0 THEN '⚠ Tentatives échouées'
        ELSE '✓ OK'
    END AS SECURITY_STATUS,
    NO_PASSWORD_INDICATOR,
    PASSWORD_CHANGE_DATE,
    PASSWORD_EXPIRATION_DATE,
    DAYS_UNTIL_PASSWORD_EXPIRES,
    SIGN_ON_ATTEMPTS_NOT_VALID,
    PREVIOUS_SIGNON,
    DAYS_USED_COUNT,
    SPECIAL_AUTHORITIES
FROM QSYS2.USER_INFO
WHERE 
    NO_PASSWORD_INDICATOR = 'YES'
    OR PASSWORD_EXPIRATION_DATE < CURRENT_DATE
    OR DAYS_UNTIL_PASSWORD_EXPIRES <= 7
    OR SIGN_ON_ATTEMPTS_NOT_VALID > 0
    OR (STATUS = '*ENABLED' AND DAYS_USED_COUNT = 0)
ORDER BY 
    CASE 
        WHEN NO_PASSWORD_INDICATOR = 'YES' THEN 1
        WHEN PASSWORD_EXPIRATION_DATE < CURRENT_DATE THEN 2
        ELSE 3
    END;
```

### 2.3 Utilisateurs Inactifs

```sql
-- Comptes non utilisés depuis longtemps (> 90 jours)
SELECT 
    AUTHORIZATION_NAME,
    STATUS,
    USER_CLASS_NAME,
    PREVIOUS_SIGNON,
    DAYS_SINCE_LAST_SIGNON,
    DAYS_USED_COUNT,
    SPECIAL_AUTHORITIES,
    CASE 
        WHEN DAYS_SINCE_LAST_SIGNON > 180 THEN '✗ CRITIQUE: > 6 mois'
        WHEN DAYS_SINCE_LAST_SIGNON > 90 THEN '⚠ ATTENTION: > 3 mois'
        ELSE '✓ Actif'
    END AS ACTIVITY_STATUS
FROM (
    SELECT 
        AUTHORIZATION_NAME,
        STATUS,
        USER_CLASS_NAME,
        PREVIOUS_SIGNON,
        DAYS_BETWEEN(PREVIOUS_SIGNON, CURRENT_DATE) AS DAYS_SINCE_LAST_SIGNON,
        DAYS_USED_COUNT,
        SPECIAL_AUTHORITIES
    FROM QSYS2.USER_INFO
    WHERE STATUS = '*ENABLED'
      AND PREVIOUS_SIGNON IS NOT NULL
)
WHERE DAYS_SINCE_LAST_SIGNON > 90
ORDER BY DAYS_SINCE_LAST_SIGNON DESC;
```

### 2.4 Profils Utilisateurs par Défaut IBM

```sql
-- Vérifier les profils IBM par défaut (doivent être désactivés)
SELECT 
    AUTHORIZATION_NAME,
    STATUS,
    USER_CLASS_NAME,
    SPECIAL_AUTHORITIES,
    NO_PASSWORD_INDICATOR,
    CASE 
        WHEN STATUS = '*DISABLED' THEN '✓ Désactivé (OK)'
        WHEN NO_PASSWORD_INDICATOR = 'YES' THEN '✗ CRITIQUE: Actif sans mot de passe'
        ELSE '⚠ Actif - À vérifier'
    END AS SECURITY_STATUS
FROM QSYS2.USER_INFO
WHERE AUTHORIZATION_NAME IN (
    'QSECOFR', 'QSYSOPR', 'QPGMR', 'QSRV', 'QSVR',
    'QTCP', 'QUSER', 'QAUTPROF', 'QDBSHR', 'QDBSHRDO',
    'QDOC', 'QDSNX', 'QGATE', 'QMSF', 'QNETSPLF',
    'QNFSANON', 'QNTP', 'QPEX', 'QRJE', 'QSNADS',
    'QSPL', 'QTFTP', 'QTMHHTP1', 'QTMHHTTP', 'QYPSJSVR'
)
ORDER BY 
    CASE 
        WHEN STATUS = '*ENABLED' AND NO_PASSWORD_INDICATOR = 'YES' THEN 1
        WHEN STATUS = '*ENABLED' THEN 2
        ELSE 3
    END,
    AUTHORIZATION_NAME;
```

---

## 3. Autorisations et Privilèges

### 3.1 Objets avec Autorisation *PUBLIC

```sql
-- ⚠️ Objets accessibles à tous (*PUBLIC)
SELECT 
    SYSTEM_OBJECT_SCHEMA,
    SYSTEM_OBJECT_NAME,
    OBJECT_TYPE,
    OBJECT_AUTHORITY,
    AUTHORIZATION_NAME,
    CASE 
        WHEN OBJECT_AUTHORITY IN ('*ALL', '*CHANGE') THEN '✗ CRITIQUE'
        WHEN OBJECT_AUTHORITY = '*USE' THEN '⚠ ATTENTION'
        WHEN OBJECT_AUTHORITY = '*EXCLUDE' THEN '✓ OK'
        ELSE '? À vérifier'
    END AS RISK_LEVEL,
    OBJECT_OPERATIONAL,
    OBJECT_MANAGEMENT,
    OBJECT_EXISTENCE,
    OBJECT_ALTER,
    OBJECT_REFERENCE
FROM QSYS2.OBJECT_PRIVILEGES
WHERE AUTHORIZATION_NAME = '*PUBLIC'
  AND OBJECT_AUTHORITY <> '*EXCLUDE'
  AND SYSTEM_OBJECT_SCHEMA NOT IN ('QSYS', 'QSYS2', 'QUSRSYS')
ORDER BY 
    CASE OBJECT_AUTHORITY
        WHEN '*ALL' THEN 1
        WHEN '*CHANGE' THEN 2
        WHEN '*USE' THEN 3
        ELSE 4
    END,
    SYSTEM_OBJECT_SCHEMA,
    SYSTEM_OBJECT_NAME;
```

### 3.2 Listes d'Autorisation Critiques

```sql
-- Utilisateurs dans les listes d'autorisation sensibles
SELECT 
    AUTHORIZATION_LIST_NAME,
    USER_NAME,
    OBJECT_AUTHORITY,
    OBJECT_OPERATIONAL,
    OBJECT_MANAGEMENT,
    OBJECT_EXISTENCE,
    DATA_READ,
    DATA_ADD,
    DATA_UPDATE,
    DATA_DELETE,
    CASE 
        WHEN OBJECT_AUTHORITY = '*ALL' THEN '✗ CRITIQUE'
        WHEN OBJECT_AUTHORITY = '*CHANGE' THEN '⚠ ÉLEVÉ'
        ELSE '✓ NORMAL'
    END AS RISK_LEVEL
FROM QSYS2.AUTHORIZATION_LIST_USER_INFO
WHERE AUTHORIZATION_LIST_NAME IN (
    'QPGMR', 'QSECOFR', 'QSYSOPR', 'QSRVBAS'
)
   OR OBJECT_AUTHORITY IN ('*ALL', '*CHANGE')
ORDER BY 
    CASE OBJECT_AUTHORITY
        WHEN '*ALL' THEN 1
        WHEN '*CHANGE' THEN 2
        ELSE 3
    END,
    AUTHORIZATION_LIST_NAME,
    USER_NAME;
```

### 3.3 Programmes Adoptant des Autorités

```sql
-- Programmes avec USRPRF(*OWNER) - Risque d'élévation de privilèges
SELECT 
    OBJLIB AS LIBRARY,
    OBJNAME AS PROGRAM,
    OBJTYPE AS TYPE,
    OBJOWNER AS OWNER,
    OBJDEFINER AS DEFINER,
    USER_PROFILE,
    CASE 
        WHEN OBJOWNER IN ('QSECOFR', 'QSYS') AND USER_PROFILE = '*OWNER' 
            THEN '✗ CRITIQUE: Adoption QSECOFR'
        WHEN USER_PROFILE = '*OWNER' 
            THEN '⚠ ATTENTION: Adoption propriétaire'
        ELSE '✓ Normal'
    END AS RISK_LEVEL,
    OBJCREATED AS CREATED_DATE,
    LAST_USED_TIMESTAMP
FROM TABLE(QSYS2.OBJECT_STATISTICS('*ALL', '*PGM')) 
WHERE USER_PROFILE = '*OWNER'
  AND OBJLIB NOT IN ('QSYS', 'QSYS2')
ORDER BY 
    CASE 
        WHEN OBJOWNER IN ('QSECOFR', 'QSYS') THEN 1
        ELSE 2
    END,
    OBJLIB, OBJNAME;
```

---

## 4. Audit et Journalisation

### 4.1 Configuration de l'Audit

```sql
-- Vérifier la configuration de l'audit système
SELECT 
    SYSTEM_VALUE_NAME,
    CURRENT_CHARACTER_VALUE,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QAUDCTL' THEN 
            CASE WHEN CURRENT_CHARACTER_VALUE LIKE '%*AUDLVL%' THEN '✓' ELSE '✗' END
        WHEN 'QAUDLVL' THEN 
            CASE WHEN CURRENT_CHARACTER_VALUE <> '*NONE' THEN '✓' ELSE '✗' END
        WHEN 'QAUDENDACN' THEN 
            CASE WHEN CURRENT_CHARACTER_VALUE = '*NOTIFY' THEN '✓' ELSE '⚠' END
        ELSE '?'
    END AS STATUS,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QAUDCTL' THEN 'Contrôle audit (doit inclure *AUDLVL)'
        WHEN 'QAUDLVL' THEN 'Niveau audit (ne doit pas être *NONE)'
        WHEN 'QAUDENDACN' THEN 'Action fin audit (*NOTIFY recommandé)'
        WHEN 'QCRTOBJAUD' THEN 'Audit création objets'
        ELSE ''
    END AS DESCRIPTION
FROM QSYS2.SYSTEM_VALUE_INFO
WHERE SYSTEM_VALUE_NAME IN ('QAUDCTL', 'QAUDLVL', 'QAUDENDACN', 'QCRTOBJAUD')
ORDER BY SYSTEM_VALUE_NAME;
```

### 4.2 Objets Non Audités

```sql
-- Objets sensibles sans audit activé
SELECT 
    OBJLIB AS LIBRARY,
    OBJNAME AS OBJECT_NAME,
    OBJTYPE AS TYPE,
    OBJOWNER AS OWNER,
    OBJAUDITING_VALUE AS AUDIT_VALUE,
    '✗ Audit désactivé' AS STATUS,
    OBJCREATED AS CREATED
FROM TABLE(QSYS2.OBJECT_STATISTICS('*ALL', '*ALL'))
WHERE OBJAUDITING_VALUE = '*NONE'
  AND OBJTYPE IN ('*PGM', '*FILE', '*DTAARA', '*USRPRF')
  AND OBJLIB NOT IN ('QSYS', 'QSYS2', 'QUSRSYS', 'QTEMP')
ORDER BY OBJLIB, OBJNAME
FETCH FIRST 100 ROWS ONLY;
```

### 4.3 Événements d'Audit Récents

```sql
-- Derniers événements de sécurité dans le journal d'audit
SELECT 
    ENTRY_TIMESTAMP,
    ENTRY_TYPE,
    USER_PROFILE,
    JOB_NAME,
    PROGRAM_NAME,
    PROGRAM_LIBRARY,
    OBJECT_NAME,
    OBJECT_LIBRARY,
    OBJECT_TYPE,
    VIOLATION_TYPE,
    CASE ENTRY_TYPE
        WHEN 'AF' THEN '✗ Échec autorisation'
        WHEN 'PW' THEN '⚠ Changement mot de passe'
        WHEN 'SW' THEN '⚠ Changement valeur système'
        WHEN 'CA' THEN 'Changement autorité'
        WHEN 'CD' THEN 'Changement objet'
        ELSE ENTRY_TYPE
    END AS EVENT_DESCRIPTION
FROM TABLE(QSYS2.DISPLAY_JOURNAL(
    'QAUDJRN', 
    'QSYS',
    STARTING_TIMESTAMP => CURRENT_TIMESTAMP - 7 DAYS
))
WHERE ENTRY_TYPE IN ('AF', 'PW', 'SW', 'CA', 'CD', 'DO', 'OR', 'OM')
ORDER BY ENTRY_TIMESTAMP DESC
FETCH FIRST 100 ROWS ONLY;
```

---

## 5. Mots de Passe et Authentification

### 5.1 Politique de Mots de Passe

```sql
-- Configuration de la politique de mots de passe
SELECT 
    SYSTEM_VALUE_NAME,
    CURRENT_NUMERIC_VALUE,
    CURRENT_CHARACTER_VALUE,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QPWDMINLEN' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE >= 8 THEN '✓ OK' ELSE '✗ Trop court' END
        WHEN 'QPWDMAXLEN' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE >= 10 THEN '✓ OK' ELSE '⚠ Court' END
        WHEN 'QPWDEXPITV' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE BETWEEN 30 AND 90 THEN '✓ OK' 
                 WHEN CURRENT_NUMERIC_VALUE = 0 THEN '✗ Pas d\'expiration'
                 ELSE '⚠ À ajuster' END
        WHEN 'QPWDRQDDIF' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE >= 1 THEN '✓ OK' ELSE '✗ Pas de différence requise' END
        WHEN 'QPWDRQDDGT' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE = 1 THEN '✓ OK' ELSE '⚠ Chiffre non requis' END
        WHEN 'QMAXSIGN' THEN 
            CASE WHEN CURRENT_NUMERIC_VALUE <= 3 THEN '✓ OK' ELSE '⚠ Trop permissif' END
        ELSE '?'
    END AS EVALUATION,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QPWDMINLEN' THEN 'Longueur minimale (8+ recommandé)'
        WHEN 'QPWDMAXLEN' THEN 'Longueur maximale (10+ recommandé)'
        WHEN 'QPWDEXPITV' THEN 'Expiration en jours (30-90 recommandé)'
        WHEN 'QPWDRQDDIF' THEN 'Positions différentes requises'
        WHEN 'QPWDRQDDGT' THEN 'Chiffre requis (1=Oui)'
        WHEN 'QPWDPOSDIF' THEN 'Différence position caractères'
        WHEN 'QPWDLVL' THEN 'Niveau validation (2 ou 3 recommandé)'
        WHEN 'QMAXSIGN' THEN 'Tentatives max (3 recommandé)'
        WHEN 'QINACTITV' THEN 'Inactivité max en minutes'
        ELSE ''
    END AS DESCRIPTION
FROM QSYS2.SYSTEM_VALUE_INFO
WHERE SYSTEM_VALUE_NAME IN (
    'QPWDMINLEN', 'QPWDMAXLEN', 'QPWDEXPITV', 'QPWDRQDDIF',
    'QPWDRQDDGT', 'QPWDPOSDIF', 'QPWDLVL', 'QMAXSIGN', 'QINACTITV'
)
ORDER BY SYSTEM_VALUE_NAME;
```

### 5.2 Utilisateurs avec Mots de Passe Faibles

```sql
-- Utilisateurs nécessitant un changement de mot de passe
SELECT 
    AUTHORIZATION_NAME,
    STATUS,
    USER_CLASS_NAME,
    PASSWORD_CHANGE_DATE,
    PASSWORD_EXPIRATION_DATE,
    DAYS_UNTIL_PASSWORD_EXPIRES,
    NO_PASSWORD_INDICATOR,
    SET_PASSWORD_TO_EXPIRE,
    CASE 
        WHEN NO_PASSWORD_INDICATOR = 'YES' THEN '✗ CRITIQUE: Pas de mot de passe'
        WHEN PASSWORD_EXPIRATION_DATE < CURRENT_DATE THEN '✗ Expiré'
        WHEN DAYS_UNTIL_PASSWORD_EXPIRES <= 0 THEN '✗ Expiré'
        WHEN DAYS_UNTIL_PASSWORD_EXPIRES <= 7 THEN '⚠ Expire dans ' || DAYS_UNTIL_PASSWORD_EXPIRES || ' jours'
        WHEN SET_PASSWORD_TO_EXPIRE = 'YES' THEN '⚠ Marqué pour expiration'
        ELSE '✓ OK'
    END AS PASSWORD_STATUS,
    SPECIAL_AUTHORITIES
FROM QSYS2.USER_INFO
WHERE STATUS = '*ENABLED'
  AND (
      NO_PASSWORD_INDICATOR = 'YES'
      OR PASSWORD_EXPIRATION_DATE < CURRENT_DATE
      OR DAYS_UNTIL_PASSWORD_EXPIRES <= 7
      OR SET_PASSWORD_TO_EXPIRE = 'YES'
  )
ORDER BY 
    CASE 
        WHEN NO_PASSWORD_INDICATOR = 'YES' THEN 1
        WHEN PASSWORD_EXPIRATION_DATE < CURRENT_DATE THEN 2
        WHEN DAYS_UNTIL_PASSWORD_EXPIRES <= 7 THEN 3
        ELSE 4
    END,
    AUTHORIZATION_NAME;
```

---

## 6. Objets Sensibles

### 6.1 Fichiers de Données Sensibles

```sql
-- Fichiers physiques sans protection adéquate
SELECT 
    TABLE_SCHEMA AS LIBRARY,
    TABLE_NAME AS FILE_NAME,
    TABLE_OWNER AS OWNER,
    RECORD_COUNT,
    CASE 
        WHEN TABLE_SCHEMA = 'QSYS' THEN '⚠ Bibliothèque système'
        WHEN RECORD_COUNT > 100000 THEN '⚠ Fichier volumineux'
        ELSE '✓ Normal'
    END AS RISK_INDICATOR
FROM QSYS2.SYSTABLES
WHERE TABLE_TYPE = 'P'  -- Physical files
  AND TABLE_SCHEMA NOT IN ('QSYS', 'QSYS2', 'QUSRSYS', 'QTEMP')
  AND (
      TABLE_NAME LIKE '%PASS%'
      OR TABLE_NAME LIKE '%PWD%'
      OR TABLE_NAME LIKE '%USER%'
      OR TABLE_NAME LIKE '%CUST%'
      OR TABLE_NAME LIKE '%CARD%'
      OR TABLE_NAME LIKE '%SECU%'
  )
ORDER BY RECORD_COUNT DESC
FETCH FIRST 50 ROWS ONLY;
```

### 6.2 Programmes Système Modifiés

```sql
-- Programmes dans QSYS modifiés récemment (potentielle compromission)
SELECT 
    OBJLIB AS LIBRARY,
    OBJNAME AS PROGRAM,
    OBJTYPE AS TYPE,
    OBJOWNER AS OWNER,
    OBJCREATED AS CREATED,
    LAST_USED_TIMESTAMP,
    DAYS_USED_COUNT,
    '⚠ Programme système modifié' AS ALERT
FROM TABLE(QSYS2.OBJECT_STATISTICS('QSYS', '*PGM'))
WHERE OBJCREATED > CURRENT_DATE - 30 DAYS
   OR LAST_USED_TIMESTAMP > CURRENT_TIMESTAMP - 7 DAYS
ORDER BY OBJCREATED DESC;
```

---

## 7. Connexions et Sessions

### 7.1 Sessions Actives

```sql
-- Sessions utilisateurs actives
SELECT 
    JOB_NAME,
    AUTHORIZATION_NAME AS USER,
    JOB_TYPE,
    JOB_STATUS,
    SUBSYSTEM,
    CLIENT_IP_ADDRESS,
    JOB_ENTERED_SYSTEM_TIME,
    ELAPSED_TIME,
    CPU_TIME,
    FUNCTION,
    CASE 
        WHEN AUTHORIZATION_NAME IN ('QSECOFR', 'QSYSOPR') THEN '⚠ Utilisateur privilégié'
        WHEN JOB_TYPE = 'INT' THEN '✓ Interactif'
        WHEN JOB_TYPE = 'BCH' THEN 'Batch'
        ELSE JOB_TYPE
    END AS SESSION_TYPE
FROM TABLE(QSYS2.ACTIVE_JOB_INFO(
    JOB_NAME_FILTER => '*ALL'
))
WHERE JOB_TYPE IN ('INT', 'BCH')
  AND JOB_STATUS = 'ACTIVE'
ORDER BY JOB_ENTERED_SYSTEM_TIME DESC;
```

### 7.2 Tentatives de Connexion Échouées

```sql
-- Utilisateurs avec tentatives de connexion échouées
SELECT 
    AUTHORIZATION_NAME,
    STATUS,
    SIGN_ON_ATTEMPTS_NOT_VALID AS FAILED_ATTEMPTS,
    PREVIOUS_SIGNON,
    DAYS_USED_COUNT,
    SPECIAL_AUTHORITIES,
    CASE 
        WHEN SIGN_ON_ATTEMPTS_NOT_VALID >= 3 THEN '✗ CRITIQUE: Compte bloqué possible'
        WHEN SIGN_ON_ATTEMPTS_NOT_VALID > 0 THEN '⚠ Tentatives échouées'
        ELSE '✓ OK'
    END AS SECURITY_STATUS
FROM QSYS2.USER_INFO
WHERE SIGN_ON_ATTEMPTS_NOT_VALID > 0
  AND STATUS = '*ENABLED'
ORDER BY SIGN_ON_ATTEMPTS_NOT_VALID DESC, AUTHORIZATION_NAME;
```

### 7.3 Historique des Connexions

```sql
-- Historique des connexions récentes (via journal d'audit)
SELECT 
    ENTRY_TIMESTAMP,
    USER_PROFILE,
    JOB_NAME,
    ENTRY_TYPE,
    CASE ENTRY_TYPE
        WHEN 'PW' THEN 'Changement mot de passe'
        WHEN 'SV' THEN 'Violation sécurité'
        WHEN 'AF' THEN 'Échec autorisation'
        ELSE ENTRY_TYPE
    END AS EVENT_TYPE,
    PROGRAM_NAME,
    PROGRAM_LIBRARY
FROM TABLE(QSYS2.DISPLAY_JOURNAL(
    'QAUDJRN',
    'QSYS',
    STARTING_TIMESTAMP => CURRENT_TIMESTAMP - 7 DAYS
))
WHERE ENTRY_TYPE IN ('PW', 'SV', 'AF')
ORDER BY ENTRY_TIMESTAMP DESC
FETCH FIRST 100 ROWS ONLY;
```

---

## 8. Conformité et Recommandations

### 8.1 Score de Sécurité Global

```sql
-- Calcul d'un score de sécurité global
WITH SECURITY_CHECKS AS (
    SELECT 
        'Niveau sécurité' AS CHECK_NAME,
        CASE WHEN CURRENT_NUMERIC_VALUE >= 40 THEN 1 ELSE 0 END AS PASSED
    FROM QSYS2.SYSTEM_VALUE_INFO WHERE SYSTEM_VALUE_NAME = 'QSECURITY'
    
    UNION ALL
    
    SELECT 
        'Expiration mot de passe',
        CASE WHEN CURRENT_NUMERIC_VALUE BETWEEN 30 AND 90 THEN 1 ELSE 0 END
    FROM QSYS2.SYSTEM_VALUE_INFO WHERE SYSTEM_VALUE_NAME = 'QPWDEXPITV'
    
    UNION ALL
    
    SELECT 
        'Longueur min mot de passe',
        CASE WHEN CURRENT_NUMERIC_VALUE >= 8 THEN 1 ELSE 0 END
    FROM QSYS2.SYSTEM_VALUE_INFO WHERE SYSTEM_VALUE_NAME = 'QPWDMINLEN'
    
    UNION ALL
    
    SELECT 
        'Audit activé',
        CASE WHEN CURRENT_CHARACTER_VALUE <> '*NONE' THEN 1 ELSE 0 END
    FROM QSYS2.SYSTEM_VALUE_INFO WHERE SYSTEM_VALUE_NAME = 'QAUDLVL'
    
    UNION ALL
    
    SELECT 
        'Restauration sécurité',
        CASE WHEN CURRENT_CHARACTER_VALUE = '1' THEN 1 ELSE 0 END
    FROM QSYS2.SYSTEM_VALUE_INFO WHERE SYSTEM_VALUE_NAME = 'QRETSVRSEC'
)
SELECT 
    CHECK_NAME,
    CASE WHEN PASSED = 1 THEN '✓ PASS' ELSE '✗ FAIL' END AS STATUS,
    PASSED
FROM SECURITY_CHECKS
UNION ALL
SELECT 
    '--- SCORE GLOBAL ---' AS CHECK_NAME,
    CAST(ROUND((SUM(PASSED) * 100.0 / COUNT(*)), 0) AS VARCHAR(10)) || '%' AS STATUS,
    SUM(PASSED) AS PASSED
FROM SECURITY_CHECKS;
```

### 8.2 Rapport de Conformité Complet

```sql
-- Génération d'un rapport de conformité
SELECT 
    'CONFIGURATION SYSTÈME' AS CATEGORY,
    SYSTEM_VALUE_NAME AS ITEM,
    COALESCE(CURRENT_CHARACTER_VALUE, CAST(CURRENT_NUMERIC_VALUE AS VARCHAR(10))) AS VALUE,
    CASE SYSTEM_VALUE_NAME
        WHEN 'QSECURITY' THEN CASE WHEN CURRENT_NUMERIC_VALUE >= 40 THEN 'CONFORME' ELSE 'NON CONFORME' END
        WHEN 'QPWDEXPITV' THEN CASE WHEN CURRENT_NUMERIC_VALUE BETWEEN 30 AND 90 THEN 'CONFORME' ELSE 'À AJUSTER' END
        WHEN 'QPWDMINLEN' THEN CASE WHEN CURRENT_NUMERIC_VALUE >= 8 THEN 'CONFORME' ELSE 'NON CONFORME' END
        WHEN 'QAUDLVL' THEN CASE WHEN CURRENT_CHARACTER_VALUE <> '*NONE' THEN 'CONFORME' ELSE 'NON CONFORME' END
        ELSE 'À VÉRIFIER'
    END AS COMPLIANCE_STATUS
FROM QSYS2.SYSTEM_VALUE_INFO
WHERE SYSTEM_VALUE_NAME IN (
    'QSECURITY', 'QPWDEXPITV', 'QPWDMINLEN', 'QPWDMAXLEN',
    'QMAXSIGN', 'QRETSVRSEC', 'QAUDLVL', 'QAUDCTL'
)

UNION ALL

SELECT 
    'UTILISATEURS À RISQUE',
    AUTHORIZATION_NAME,
    'Privilèges: ' || SPECIAL_AUTHORITIES,
    CASE 
        WHEN NO_PASSWORD_INDICATOR = 'YES' THEN 'CRITIQUE'
        WHEN SPECIAL_AUTHORITIES LIKE '%*ALLOBJ%' THEN 'ATTENTION'
        ELSE 'NORMAL'
    END
FROM QSYS2.USER_INFO
WHERE STATUS = '*ENABLED'
  AND (
      NO_PASSWORD_INDICATOR = 'YES'
      OR SPECIAL_AUTHORITIES LIKE '%*ALLOBJ%'
      OR SPECIAL_AUTHORITIES LIKE '%*SECADM%'
  )
FETCH FIRST 20 ROWS ONLY;
```

---

## Utilisation avec Ansible

### Exemple de Playbook

```yaml
---
- name: Audit de Sécurité IBM i
  hosts: ibmi_servers
  gather_facts: no
  
  tasks:
    - name: Vérifier niveau de sécurité
      ibm.power_ibmi.ibmi_sql_query:
        sql: |
          SELECT SYSTEM_VALUE_NAME, CURRENT_NUMERIC_VALUE
          FROM QSYS2.SYSTEM_VALUE_INFO
          WHERE SYSTEM_VALUE_NAME = 'QSECURITY'
      register: security_level
      
    - name: Afficher résultat
      debug:
        msg: "Niveau de sécurité: {{ security_level.row[0].CURRENT_NUMERIC_VALUE }}"
```

---

## Recommandations de Sécurité

### Priorité CRITIQUE

1. **QSECURITY >= 40** (idéalement 50)
2. **Désactiver les profils IBM par défaut** (QSECOFR, QSYSOPR, etc.)
3. **Activer l'audit** (QAUDLVL, QAUDCTL)
4. **Politique de mots de passe forte** (longueur, expiration, complexité)
5. **Limiter *ALLOBJ et *SECADM**

### Priorité ÉLEVÉE

6. Désactiver les comptes inactifs (> 90 jours)
7. Restreindre *PUBLIC sur les objets sensibles
8. Auditer les programmes avec USRPRF(*OWNER)
9. Surveiller les tentatives de connexion échouées
10. Activer QRETSVRSEC

### Priorité MOYENNE

11. Réviser les listes d'autorisation
12. Documenter les utilisateurs privilégiés
13. Mettre en place une rotation des mots de passe
14. Surveiller les modifications dans QSYS
15. Former les utilisateurs à la sécurité

---

## Ressources

- [IBM i Security Reference](https://www.ibm.com/docs/en/i/7.5?topic=security)
- [QSYS2 Services](https://www.ibm.com/docs/en/i/7.5?topic=services-db2-i)
- [IBM i Security Best Practices](https://www.ibm.com/support/pages/ibm-i-security-best-practices)

---

**Version**: 1.0  
**Date**: 2026-05-06  
**Auteur**: Guide de Sécurité IBM i