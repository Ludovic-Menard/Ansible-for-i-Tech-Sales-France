/* ================================================================== */
/* Script CL: Création de ligne de communication SR-IOV              */
/* Description: Crée une ligne Ethernet pour SR-IOV sur IBM i        */
/* Généré par: Ansible                                                */
/* Date: {{ ansible_date_time.iso8601 }}                             */
/* ================================================================== */

PGM

/* Variables */
DCL VAR(&LIND) TYPE(*CHAR) LEN(10) VALUE('{{ line_description }}')
DCL VAR(&RSRC) TYPE(*CHAR) LEN(10) VALUE('{{ resource_name }}')
DCL VAR(&MSGID) TYPE(*CHAR) LEN(7)
DCL VAR(&MSGDTA) TYPE(*CHAR) LEN(512)

/* Message de début */
SNDPGMMSG MSG('Création de la ligne SR-IOV: {{ line_description }}') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

/* Vérifier si la ligne existe déjà */
CHKOBJ OBJ(QSYS/{{ line_description }}) OBJTYPE(*LIND)
MONMSG MSGID(CPF9801) EXEC(GOTO CMDLBL(CREATE))

/* La ligne existe - la supprimer d'abord */
SNDPGMMSG MSG('Ligne existante détectée - suppression...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

VRYCFG CFGOBJ({{ line_description }}) CFGTYPE(*LIN) STATUS(*OFF)
MONMSG MSGID(CPF0000)

DLTLINETH LIND({{ line_description }})
MONMSG MSGID(CPF0000)

/* Créer la nouvelle ligne */
CREATE:
SNDPGMMSG MSG('Création de la nouvelle ligne...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

CRTLINETH LIND({{ line_description }}) +
          RSRCNAME({{ resource_name }}) +
          LINESPEED({{ line_speed }}) +
          DUPLEX({{ duplex_mode }}) +
          AUTOSTART({{ auto_start }}) +
          MAXFRAME({{ max_frame_size }}) +
          TEXT('Ligne SR-IOV créée par Ansible')

MONMSG MSGID(CPF0000) EXEC(GOTO CMDLBL(ERROR))

/* Succès */
SNDPGMMSG MSG('✓ Ligne {{ line_description }} créée avec succès') +
          TOPGMQ(*EXT) MSGTYPE(*COMP)

GOTO CMDLBL(END)

/* Gestion des erreurs */
ERROR:
RCVMSG MSGTYPE(*EXCP) MSGDTA(&MSGDTA) MSGID(&MSGID)
SNDPGMMSG MSG('✗ Erreur lors de la création: ' *CAT &MSGID *CAT ' - ' *CAT &MSGDTA) +
          TOPGMQ(*EXT) MSGTYPE(*ESCAPE)

END:
ENDPGM

; Made with Bob
