/* ================================================================== */
/* Script CL: Configuration TCP/IP pour SR-IOV                        */
/* Description: Configure l'interface TCP/IP pour la ligne SR-IOV    */
/* Généré par: Ansible                                                */
/* Date: {{ ansible_date_time.iso8601 }}                             */
/* ================================================================== */

PGM

/* Variables */
DCL VAR(&IPADDR) TYPE(*CHAR) LEN(15) VALUE('{{ ip_address }}')
DCL VAR(&SUBNET) TYPE(*CHAR) LEN(15) VALUE('{{ subnet_mask }}')
DCL VAR(&LIND) TYPE(*CHAR) LEN(10) VALUE('{{ line_description }}')
DCL VAR(&INTNAME) TYPE(*CHAR) LEN(10) VALUE('{{ interface_name }}')
DCL VAR(&GATEWAY) TYPE(*CHAR) LEN(15) VALUE('{{ gateway }}')
DCL VAR(&MSGID) TYPE(*CHAR) LEN(7)
DCL VAR(&MSGDTA) TYPE(*CHAR) LEN(512)

/* Message de début */
SNDPGMMSG MSG('Configuration TCP/IP pour SR-IOV: {{ interface_name }}') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

/* Vérifier si l'interface existe déjà */
SNDPGMMSG MSG('Vérification de l''interface existante...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

/* Supprimer l'interface si elle existe */
RMVTCPIFC INTNETADR('{{ ip_address }}')
MONMSG MSGID(TCP0000 TCP2400) /* Interface n'existe pas */

/* Attendre un peu */
DLYJOB DLY(2)

/* Ajouter la nouvelle interface TCP/IP */
ADDTCP:
SNDPGMMSG MSG('Ajout de l''interface TCP/IP...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

ADDTCPIFC INTNETADR('{{ ip_address }}') +
          LIND({{ line_description }}) +
          SUBNETMASK('{{ subnet_mask }}') +
          INTNETADRDSC('{{ interface_name }}') +
          AUTOSTART(*YES) +
{% if type_of_service is defined %}
          TYPEOFSERVICE({{ type_of_service }}) +
{% endif %}
          TEXT('Interface SR-IOV créée par Ansible')

MONMSG MSGID(CPF0000 TCP0000) EXEC(GOTO CMDLBL(ERROR))

/* Attendre que l'interface soit prête */
DLYJOB DLY(3)

/* Démarrer l'interface */
STARTIFC:
SNDPGMMSG MSG('Démarrage de l''interface...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

STRTCPIFC INTNETADR('{{ ip_address }}')
MONMSG MSGID(CPF0000 TCP0000) EXEC(GOTO CMDLBL(ERROR))

/* Attendre que l'interface soit active */
DLYJOB DLY(5)

/* Configurer la route par défaut */
ROUTE:
SNDPGMMSG MSG('Configuration de la route par défaut...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

/* Essayer d'ajouter la route */
ADDTCPRTE RTEDEST(*DFTROUTE) NEXTHOP('{{ gateway }}')
MONMSG MSGID(TCP2400) EXEC(DO) /* Route existe déjà */
  /* Changer la route existante */
  CHGTCPRTE RTEDEST(*DFTROUTE) NEXTHOP('{{ gateway }}')
  MONMSG MSGID(CPF0000)
ENDDO

{% if dns_servers is defined and dns_servers | length > 0 %}
/* Configuration DNS */
DNS:
SNDPGMMSG MSG('Configuration des serveurs DNS...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

{% for dns in dns_servers %}
CHGTCPDMN INTNETADR('{{ dns }}'){% if dns_domain is defined %} DMNNAME('{{ dns_domain }}'){% endif %}

MONMSG MSGID(CPF0000)
{% endfor %}
{% endif %}

{% if enable_vlan | default(false) and vlan_id is defined %}
/* Configuration VLAN */
VLAN:
SNDPGMMSG MSG('Configuration du VLAN {{ vlan_id }}...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

CHGLINETH LIND({{ line_description }}) VLANID({{ vlan_id }})
MONMSG MSGID(CPF0000)
{% endif %}

/* Vérification finale */
VERIFY:
SNDPGMMSG MSG('Vérification de la configuration...') +
          TOPGMQ(*EXT) MSGTYPE(*STATUS)

/* Ping vers la passerelle */
PING RMTSYS('{{ gateway }}') NBRPKT(3)
MONMSG MSGID(CPF0000) EXEC(DO)
  SNDPGMMSG MSG('⚠ Avertissement: Impossible de pinguer la passerelle') +
            TOPGMQ(*EXT) MSGTYPE(*INFO)
ENDDO

/* Succès */
SUCCESS:
SNDPGMMSG MSG('✓ Configuration TCP/IP terminée avec succès') +
          TOPGMQ(*EXT) MSGTYPE(*COMP)
SNDPGMMSG MSG('  Interface: {{ interface_name }}') +
          TOPGMQ(*EXT) MSGTYPE(*COMP)
SNDPGMMSG MSG('  Adresse IP: {{ ip_address }}') +
          TOPGMQ(*EXT) MSGTYPE(*COMP)
SNDPGMMSG MSG('  Passerelle: {{ gateway }}') +
          TOPGMQ(*EXT) MSGTYPE(*COMP)

GOTO CMDLBL(END)

/* Gestion des erreurs */
ERROR:
RCVMSG MSGTYPE(*EXCP) MSGDTA(&MSGDTA) MSGID(&MSGID)
SNDPGMMSG MSG('✗ Erreur lors de la configuration: ' *CAT &MSGID *CAT ' - ' *CAT &MSGDTA) +
          TOPGMQ(*EXT) MSGTYPE(*ESCAPE)

END:
ENDPGM

; Made with Bob
