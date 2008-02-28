# Leo colorizer control file for progress mode.
# This file is in the public domain.

# Properties for progress mode.
properties = {
	"boxComment": "**",
	"commentEnd": "*/",
	"commentStart": "/*",
	"indentCloseBrackets": "}",
	"indentNextLine": "\\s*(if|do|for|else|case|repeat|procedure|function)(\\s+.*|\\s*)",
	"indentOpenBrackets": "{",
	"lineComment": "&scop cmt ",
	"wordBreakChars": ",.;:/?^[]@",
}

# Attributes dict for progress_main ruleset.
progress_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "~",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for progress mode.
attributesDictDict = {
	"progress_main": progress_main_attributes_dict,
}

# Keywords dict for progress_main ruleset.
progress_main_keywords_dict = {
	"&": "comment2",
	"_abbreviate": "keyword2",
	"_account_expires": "keyword2",
	"_actailog": "keyword2",
	"_actbilog": "keyword2",
	"_actbuffer": "keyword2",
	"_actindex": "keyword2",
	"_actiofile": "keyword2",
	"_actiotype": "keyword2",
	"_active": "keyword2",
	"_actlock": "keyword2",
	"_actother": "keyword2",
	"_actpws": "keyword2",
	"_actrecord": "keyword2",
	"_actserver": "keyword2",
	"_actspace": "keyword2",
	"_actsummary": "keyword2",
	"_admin": "keyword2",
	"_ailog-aiwwrites": "keyword2",
	"_ailog-bbuffwaits": "keyword2",
	"_ailog-byteswritn": "keyword2",
	"_ailog-forcewaits": "keyword2",
	"_ailog-id": "keyword2",
	"_ailog-misc": "keyword2",
	"_ailog-nobufavail": "keyword2",
	"_ailog-partialwrt": "keyword2",
	"_ailog-recwriten": "keyword2",
	"_ailog-totwrites": "keyword2",
	"_ailog-trans": "keyword2",
	"_ailog-uptime": "keyword2",
	"_alt": "keyword2",
	"_area": "keyword2",
	"_area-attrib": "keyword2",
	"_area-block": "keyword2",
	"_area-blocksize": "keyword2",
	"_area-clustersize": "keyword2",
	"_area-extents": "keyword2",
	"_area-misc": "keyword2",
	"_area-name": "keyword2",
	"_area-number": "keyword2",
	"_area-recbits": "keyword2",
	"_area-recid": "keyword2",
	"_area-type": "keyword2",
	"_area-version": "keyword2",
	"_areaextent": "keyword2",
	"_areastatus": "keyword2",
	"_areastatus-areaname": "keyword2",
	"_areastatus-areanum": "keyword2",
	"_areastatus-extents": "keyword2",
	"_areastatus-freenum": "keyword2",
	"_areastatus-hiwater": "keyword2",
	"_areastatus-id": "keyword2",
	"_areastatus-lastextent": "keyword2",
	"_areastatus-rmnum": "keyword2",
	"_areastatus-totblocks": "keyword2",
	"_argtype": "keyword2",
	"_ascending": "keyword2",
	"_attribute": "keyword2",
	"_attributes1": "keyword2",
	"_auth-id": "keyword2",
	"_autoincr": "keyword2",
	"_base-col": "keyword2",
	"_base-tables": "keyword2",
	"_bfstatus-apwq": "keyword2",
	"_bfstatus-ckpmarked": "keyword2",
	"_bfstatus-ckpq": "keyword2",
	"_bfstatus-hashsize": "keyword2",
	"_bfstatus-id": "keyword2",
	"_bfstatus-lastckpnum": "keyword2",
	"_bfstatus-lru": "keyword2",
	"_bfstatus-misc": "keyword2",
	"_bfstatus-modbuffs": "keyword2",
	"_bfstatus-totbufs": "keyword2",
	"_bfstatus-usedbuffs": "keyword2",
	"_bilog-bbuffwaits": "keyword2",
	"_bilog-biwwrites": "keyword2",
	"_bilog-bytesread": "keyword2",
	"_bilog-byteswrtn": "keyword2",
	"_bilog-clstrclose": "keyword2",
	"_bilog-ebuffwaits": "keyword2",
	"_bilog-forcewaits": "keyword2",
	"_bilog-forcewrts": "keyword2",
	"_bilog-id": "keyword2",
	"_bilog-misc": "keyword2",
	"_bilog-partialwrts": "keyword2",
	"_bilog-recread": "keyword2",
	"_bilog-recwriten": "keyword2",
	"_bilog-totalwrts": "keyword2",
	"_bilog-totreads": "keyword2",
	"_bilog-trans": "keyword2",
	"_bilog-uptime": "keyword2",
	"_block": "keyword2",
	"_block-area": "keyword2",
	"_block-bkupctr": "keyword2",
	"_block-block": "keyword2",
	"_block-chaintype": "keyword2",
	"_block-dbkey": "keyword2",
	"_block-id": "keyword2",
	"_block-misc": "keyword2",
	"_block-nextdbkey": "keyword2",
	"_block-type": "keyword2",
	"_block-update": "keyword2",
	"_buffer-apwenq": "keyword2",
	"_buffer-chkpts": "keyword2",
	"_buffer-deferred": "keyword2",
	"_buffer-flushed": "keyword2",
	"_buffer-id": "keyword2",
	"_buffer-logicrds": "keyword2",
	"_buffer-logicwrts": "keyword2",
	"_buffer-lruskips": "keyword2",
	"_buffer-lruwrts": "keyword2",
	"_buffer-marked": "keyword2",
	"_buffer-misc": "keyword2",
	"_buffer-osrds": "keyword2",
	"_buffer-oswrts": "keyword2",
	"_buffer-trans": "keyword2",
	"_buffer-uptime": "keyword2",
	"_buffstatus": "keyword2",
	"_cache": "keyword2",
	"_can-create": "keyword2",
	"_can-delete": "keyword2",
	"_can-dump": "keyword2",
	"_can-load": "keyword2",
	"_can-read": "keyword2",
	"_can-write": "keyword2",
	"_casesensitive": "keyword2",
	"_charset": "keyword2",
	"_checkpoint": "keyword2",
	"_checkpoint-apwq": "keyword2",
	"_checkpoint-cptq": "keyword2",
	"_checkpoint-dirty": "keyword2",
	"_checkpoint-flush": "keyword2",
	"_checkpoint-id": "keyword2",
	"_checkpoint-len": "keyword2",
	"_checkpoint-misc": "keyword2",
	"_checkpoint-scan": "keyword2",
	"_checkpoint-time": "keyword2",
	"_chkclause": "keyword2",
	"_chkseq": "keyword2",
	"_cnstrname": "keyword2",
	"_cnstrtype": "keyword2",
	"_code-feature": "keyword2",
	"_codefeature-id": "keyword2",
	"_codefeature-res01": "keyword2",
	"_codefeature-res02": "keyword2",
	"_codefeature_name": "keyword2",
	"_codefeature_required": "keyword2",
	"_codefeature_supported": "keyword2",
	"_codepage": "keyword2",
	"_col": "keyword2",
	"_col-label": "keyword2",
	"_col-label-sa": "keyword2",
	"_col-name": "keyword2",
	"_colid": "keyword2",
	"_coll-cp": "keyword2",
	"_coll-data": "keyword2",
	"_coll-name": "keyword2",
	"_coll-segment": "keyword2",
	"_coll-sequence": "keyword2",
	"_coll-strength": "keyword2",
	"_coll-tran-subtype": "keyword2",
	"_coll-tran-version": "keyword2",
	"_collation": "keyword2",
	"_colname": "keyword2",
	"_colposition": "keyword2",
	"_connect": "keyword2",
	"_connect-2phase": "keyword2",
	"_connect-batch": "keyword2",
	"_connect-device": "keyword2",
	"_connect-disconnect": "keyword2",
	"_connect-id": "keyword2",
	"_connect-interrupt": "keyword2",
	"_connect-misc": "keyword2",
	"_connect-name": "keyword2",
	"_connect-pid": "keyword2",
	"_connect-resync": "keyword2",
	"_connect-semid": "keyword2",
	"_connect-semnum": "keyword2",
	"_connect-server": "keyword2",
	"_connect-time": "keyword2",
	"_connect-transid": "keyword2",
	"_connect-type": "keyword2",
	"_connect-usr": "keyword2",
	"_connect-wait": "keyword2",
	"_connect-wait1": "keyword2",
	"_cp-attr": "keyword2",
	"_cp-dbrecid": "keyword2",
	"_cp-name": "keyword2",
	"_cp-sequence": "keyword2",
	"_crc": "keyword2",
	"_create-limit": "keyword2",
	"_create-window": "comment2",
	"_create_date": "keyword2",
	"_createparams": "keyword2",
	"_creator": "keyword2",
	"_custom": "comment2",
	"_cycle-ok": "keyword2",
	"_data-type": "keyword2",
	"_database-feature": "keyword2",
	"_datatype": "keyword2",
	"_db": "keyword2",
	"_db-addr": "keyword2",
	"_db-coll-name": "keyword2",
	"_db-collate": "keyword2",
	"_db-comm": "keyword2",
	"_db-lang": "keyword2",
	"_db-local": "keyword2",
	"_db-misc1": "keyword2",
	"_db-misc2": "keyword2",
	"_db-name": "keyword2",
	"_db-recid": "keyword2",
	"_db-res1": "keyword2",
	"_db-res2": "keyword2",
	"_db-revision": "keyword2",
	"_db-slave": "keyword2",
	"_db-type": "keyword2",
	"_db-xl-name": "keyword2",
	"_db-xlate": "keyword2",
	"_dbaacc": "keyword2",
	"_dbfeature-id": "keyword2",
	"_dbfeature-res01": "keyword2",
	"_dbfeature-res02": "keyword2",
	"_dbfeature_active": "keyword2",
	"_dbfeature_enabled": "keyword2",
	"_dbfeature_name": "keyword2",
	"_dblink": "keyword2",
	"_dbstatus": "keyword2",
	"_dbstatus-aiblksize": "keyword2",
	"_dbstatus-biblksize": "keyword2",
	"_dbstatus-biclsize": "keyword2",
	"_dbstatus-biopen": "keyword2",
	"_dbstatus-bisize": "keyword2",
	"_dbstatus-bitrunc": "keyword2",
	"_dbstatus-cachestamp": "keyword2",
	"_dbstatus-changed": "keyword2",
	"_dbstatus-clversminor": "keyword2",
	"_dbstatus-codepage": "keyword2",
	"_dbstatus-collation": "keyword2",
	"_dbstatus-createdate": "keyword2",
	"_dbstatus-dbblksize": "keyword2",
	"_dbstatus-dbvers": "keyword2",
	"_dbstatus-dbversminor": "keyword2",
	"_dbstatus-emptyblks": "keyword2",
	"_dbstatus-fbdate": "keyword2",
	"_dbstatus-freeblks": "keyword2",
	"_dbstatus-hiwater": "keyword2",
	"_dbstatus-ibdate": "keyword2",
	"_dbstatus-ibseq": "keyword2",
	"_dbstatus-id": "keyword2",
	"_dbstatus-integrity": "keyword2",
	"_dbstatus-intflags": "keyword2",
	"_dbstatus-lastopen": "keyword2",
	"_dbstatus-lasttable": "keyword2",
	"_dbstatus-lasttran": "keyword2",
	"_dbstatus-misc": "keyword2",
	"_dbstatus-mostlocks": "keyword2",
	"_dbstatus-numareas": "keyword2",
	"_dbstatus-numlocks": "keyword2",
	"_dbstatus-numsems": "keyword2",
	"_dbstatus-prevopen": "keyword2",
	"_dbstatus-rmfreeblks": "keyword2",
	"_dbstatus-sharedmemver": "keyword2",
	"_dbstatus-shmvers": "keyword2",
	"_dbstatus-starttime": "keyword2",
	"_dbstatus-state": "keyword2",
	"_dbstatus-tainted": "keyword2",
	"_dbstatus-totalblks": "keyword2",
	"_dcm": "keyword1",
	"_decimals": "keyword2",
	"_definitions": "comment2",
	"_del": "keyword2",
	"_deleterule": "keyword2",
	"_desc": "keyword2",
	"_description": "keyword2",
	"_dfltvalue": "keyword2",
	"_dft-pk": "keyword2",
	"_dhtypename": "keyword2",
	"_disabled": "keyword2",
	"_dtype": "keyword2",
	"_dump-name": "keyword2",
	"_email": "keyword2",
	"_end-procedure-settings": "comment2",
	"_event": "keyword2",
	"_exe": "keyword2",
	"_extent": "keyword2",
	"_extent-attrib": "keyword2",
	"_extent-misc": "keyword2",
	"_extent-number": "keyword2",
	"_extent-path": "keyword2",
	"_extent-size": "keyword2",
	"_extent-system": "keyword2",
	"_extent-type": "keyword2",
	"_extent-version": "keyword2",
	"_fetch-type": "keyword2",
	"_field": "keyword2",
	"_field-map": "keyword2",
	"_field-name": "keyword2",
	"_field-physpos": "keyword2",
	"_field-recid": "keyword2",
	"_field-rpos": "keyword2",
	"_field-trig": "keyword2",
	"_fil-misc1": "keyword2",
	"_fil-misc2": "keyword2",
	"_fil-res1": "keyword2",
	"_fil-res2": "keyword2",
	"_file": "keyword2",
	"_file-label": "keyword2",
	"_file-label-sa": "keyword2",
	"_file-name": "keyword2",
	"_file-number": "keyword2",
	"_file-recid": "keyword2",
	"_file-trig": "keyword2",
	"_filelist": "keyword2",
	"_filelist-blksize": "keyword2",
	"_filelist-extend": "keyword2",
	"_filelist-id": "keyword2",
	"_filelist-logicalsz": "keyword2",
	"_filelist-misc": "keyword2",
	"_filelist-name": "keyword2",
	"_filelist-openmode": "keyword2",
	"_filelist-size": "keyword2",
	"_fire_4gl": "keyword2",
	"_fld": "keyword2",
	"_fld-case": "keyword2",
	"_fld-misc1": "keyword2",
	"_fld-misc2": "keyword2",
	"_fld-res1": "keyword2",
	"_fld-res2": "keyword2",
	"_fld-stdtype": "keyword2",
	"_fld-stlen": "keyword2",
	"_fld-stoff": "keyword2",
	"_for-allocated": "keyword2",
	"_for-cnt1": "keyword2",
	"_for-cnt2": "keyword2",
	"_for-flag": "keyword2",
	"_for-format": "keyword2",
	"_for-id": "keyword2",
	"_for-info": "keyword2",
	"_for-itype": "keyword2",
	"_for-maxsize": "keyword2",
	"_for-name": "keyword2",
	"_for-number": "keyword2",
	"_for-owner": "keyword2",
	"_for-primary": "keyword2",
	"_for-retrieve": "keyword2",
	"_for-scale": "keyword2",
	"_for-separator": "keyword2",
	"_for-size": "keyword2",
	"_for-spacing": "keyword2",
	"_for-type": "keyword2",
	"_for-xpos": "keyword2",
	"_format": "keyword2",
	"_format-sa": "keyword2",
	"_frozen": "keyword2",
	"_function": "comment2",
	"_function-forward": "comment2",
	"_given_name": "keyword2",
	"_grantee": "keyword2",
	"_grantor": "keyword2",
	"_group-by": "keyword2",
	"_group_number": "keyword2",
	"_has-ccnstrs": "keyword2",
	"_has-fcnstrs": "keyword2",
	"_has-pcnstrs": "keyword2",
	"_has-ucnstrs": "keyword2",
	"_hasresultset": "keyword2",
	"_hasreturnval": "keyword2",
	"_help": "keyword2",
	"_help-sa": "keyword2",
	"_hidden": "keyword2",
	"_host": "keyword2",
	"_i-misc1": "keyword2",
	"_i-misc2": "keyword2",
	"_i-res1": "keyword2",
	"_i-res2": "keyword2",
	"_ianum": "keyword2",
	"_id": "keyword2",
	"_idx-crc": "keyword2",
	"_idx-num": "keyword2",
	"_idxid": "keyword2",
	"_idxmethod": "keyword2",
	"_idxname": "keyword2",
	"_idxowner": "keyword2",
	"_if-misc1": "keyword2",
	"_if-misc2": "keyword2",
	"_if-res1": "keyword2",
	"_if-res2": "keyword2",
	"_included-lib": "comment2",
	"_index": "keyword2",
	"_index-create": "keyword2",
	"_index-delete": "keyword2",
	"_index-field": "keyword2",
	"_index-find": "keyword2",
	"_index-free": "keyword2",
	"_index-id": "keyword2",
	"_index-misc": "keyword2",
	"_index-name": "keyword2",
	"_index-recid": "keyword2",
	"_index-remove": "keyword2",
	"_index-seq": "keyword2",
	"_index-splits": "keyword2",
	"_index-trans": "keyword2",
	"_index-uptime": "keyword2",
	"_indexbase": "keyword2",
	"_indexstat": "keyword2",
	"_indexstat-blockdelete": "keyword2",
	"_indexstat-create": "keyword2",
	"_indexstat-delete": "keyword2",
	"_indexstat-id": "keyword2",
	"_indexstat-read": "keyword2",
	"_indexstat-split": "keyword2",
	"_initial": "keyword2",
	"_initial-sa": "keyword2",
	"_inline": "comment2",
	"_ins": "keyword2",
	"_iofile-bufreads": "keyword2",
	"_iofile-bufwrites": "keyword2",
	"_iofile-extends": "keyword2",
	"_iofile-filename": "keyword2",
	"_iofile-id": "keyword2",
	"_iofile-misc": "keyword2",
	"_iofile-reads": "keyword2",
	"_iofile-trans": "keyword2",
	"_iofile-ubufreads": "keyword2",
	"_iofile-ubufwrites": "keyword2",
	"_iofile-uptime": "keyword2",
	"_iofile-writes": "keyword2",
	"_iotype-airds": "keyword2",
	"_iotype-aiwrts": "keyword2",
	"_iotype-birds": "keyword2",
	"_iotype-biwrts": "keyword2",
	"_iotype-datareads": "keyword2",
	"_iotype-datawrts": "keyword2",
	"_iotype-id": "keyword2",
	"_iotype-idxrds": "keyword2",
	"_iotype-idxwrts": "keyword2",
	"_iotype-misc": "keyword2",
	"_iotype-trans": "keyword2",
	"_iotype-uptime": "keyword2",
	"_ispublic": "keyword2",
	"_keyvalue-expr": "keyword2",
	"_label": "keyword2",
	"_label-sa": "keyword2",
	"_lang": "keyword2",
	"_last-change": "keyword2",
	"_last-modified": "keyword2",
	"_last_login": "keyword2",
	"_latch": "keyword2",
	"_latch-busy": "keyword2",
	"_latch-hold": "keyword2",
	"_latch-id": "keyword2",
	"_latch-lock": "keyword2",
	"_latch-lockedt": "keyword2",
	"_latch-lockt": "keyword2",
	"_latch-name": "keyword2",
	"_latch-qhold": "keyword2",
	"_latch-spin": "keyword2",
	"_latch-type": "keyword2",
	"_latch-wait": "keyword2",
	"_latch-waitt": "keyword2",
	"_lic-activeconns": "keyword2",
	"_lic-batchconns": "keyword2",
	"_lic-currconns": "keyword2",
	"_lic-id": "keyword2",
	"_lic-maxactive": "keyword2",
	"_lic-maxbatch": "keyword2",
	"_lic-maxcurrent": "keyword2",
	"_lic-minactive": "keyword2",
	"_lic-minbatch": "keyword2",
	"_lic-mincurrent": "keyword2",
	"_lic-validusers": "keyword2",
	"_license": "keyword2",
	"_linkowner": "keyword2",
	"_literalprefix": "keyword2",
	"_literalsuffix": "keyword2",
	"_localtypename": "keyword2",
	"_lock": "keyword2",
	"_lock-canclreq": "keyword2",
	"_lock-chain": "keyword2",
	"_lock-downgrade": "keyword2",
	"_lock-exclfind": "keyword2",
	"_lock-excllock": "keyword2",
	"_lock-exclreq": "keyword2",
	"_lock-exclwait": "keyword2",
	"_lock-flags": "keyword2",
	"_lock-id": "keyword2",
	"_lock-misc": "keyword2",
	"_lock-name": "keyword2",
	"_lock-recgetlock": "keyword2",
	"_lock-recgetreq": "keyword2",
	"_lock-recgetwait": "keyword2",
	"_lock-recid": "keyword2",
	"_lock-redreq": "keyword2",
	"_lock-shrfind": "keyword2",
	"_lock-shrlock": "keyword2",
	"_lock-shrreq": "keyword2",
	"_lock-shrwait": "keyword2",
	"_lock-table": "keyword2",
	"_lock-trans": "keyword2",
	"_lock-type": "keyword2",
	"_lock-upglock": "keyword2",
	"_lock-upgreq": "keyword2",
	"_lock-upgwait": "keyword2",
	"_lock-uptime": "keyword2",
	"_lock-usr": "keyword2",
	"_lockreq": "keyword2",
	"_lockreq-exclfind": "keyword2",
	"_lockreq-id": "keyword2",
	"_lockreq-misc": "keyword2",
	"_lockreq-name": "keyword2",
	"_lockreq-num": "keyword2",
	"_lockreq-reclock": "keyword2",
	"_lockreq-recwait": "keyword2",
	"_lockreq-schlock": "keyword2",
	"_lockreq-schwait": "keyword2",
	"_lockreq-shrfind": "keyword2",
	"_lockreq-trnlock": "keyword2",
	"_lockreq-trnwait": "keyword2",
	"_logging": "keyword2",
	"_logging-2pc": "keyword2",
	"_logging-2pcnickname": "keyword2",
	"_logging-2pcpriority": "keyword2",
	"_logging-aibegin": "keyword2",
	"_logging-aiblksize": "keyword2",
	"_logging-aibuffs": "keyword2",
	"_logging-aicurrext": "keyword2",
	"_logging-aiextents": "keyword2",
	"_logging-aigennum": "keyword2",
	"_logging-aiio": "keyword2",
	"_logging-aijournal": "keyword2",
	"_logging-ailogsize": "keyword2",
	"_logging-ainew": "keyword2",
	"_logging-aiopen": "keyword2",
	"_logging-biblksize": "keyword2",
	"_logging-bibuffs": "keyword2",
	"_logging-bibytesfree": "keyword2",
	"_logging-biclage": "keyword2",
	"_logging-biclsize": "keyword2",
	"_logging-biextents": "keyword2",
	"_logging-bifullbuffs": "keyword2",
	"_logging-biio": "keyword2",
	"_logging-bilogsize": "keyword2",
	"_logging-commitdelay": "keyword2",
	"_logging-crashprot": "keyword2",
	"_logging-id": "keyword2",
	"_logging-lastckp": "keyword2",
	"_logging-misc": "keyword2",
	"_login_failures": "keyword2",
	"_logins": "keyword2",
	"_main-block": "comment2",
	"_mandatory": "keyword2",
	"_max_logins": "keyword2",
	"_max_tries": "keyword2",
	"_middle_initial": "keyword2",
	"_mod-sequence": "keyword2",
	"_mode": "keyword2",
	"_mstrblk": "keyword2",
	"_mstrblk-aiblksize": "keyword2",
	"_mstrblk-biblksize": "keyword2",
	"_mstrblk-biopen": "keyword2",
	"_mstrblk-biprev": "keyword2",
	"_mstrblk-bistate": "keyword2",
	"_mstrblk-cfilnum": "keyword2",
	"_mstrblk-crdate": "keyword2",
	"_mstrblk-dbstate": "keyword2",
	"_mstrblk-dbvers": "keyword2",
	"_mstrblk-fbdate": "keyword2",
	"_mstrblk-hiwater": "keyword2",
	"_mstrblk-ibdate": "keyword2",
	"_mstrblk-ibseq": "keyword2",
	"_mstrblk-id": "keyword2",
	"_mstrblk-integrity": "keyword2",
	"_mstrblk-lasttask": "keyword2",
	"_mstrblk-misc": "keyword2",
	"_mstrblk-oppdate": "keyword2",
	"_mstrblk-oprdate": "keyword2",
	"_mstrblk-rlclsize": "keyword2",
	"_mstrblk-rltime": "keyword2",
	"_mstrblk-tainted": "keyword2",
	"_mstrblk-timestamp": "keyword2",
	"_mstrblk-totblks": "keyword2",
	"_myconn-id": "keyword2",
	"_myconn-numseqbuffers": "keyword2",
	"_myconn-pid": "keyword2",
	"_myconn-usedseqbuffers": "keyword2",
	"_myconn-userid": "keyword2",
	"_myconnection": "keyword2",
	"_name_loc": "keyword2",
	"_ndx": "keyword2",
	"_nullable": "keyword2",
	"_nullflag": "keyword2",
	"_num-comp": "keyword2",
	"_numfld": "keyword2",
	"_numkcomp": "keyword2",
	"_numkey": "keyword2",
	"_numkfld": "keyword2",
	"_object-associate": "keyword2",
	"_object-associate-type": "keyword2",
	"_object-attrib": "keyword2",
	"_object-block": "keyword2",
	"_object-misc": "keyword2",
	"_object-number": "keyword2",
	"_object-root": "keyword2",
	"_object-system": "keyword2",
	"_object-type": "keyword2",
	"_odbcmoney": "keyword2",
	"_order": "keyword2",
	"_other-commit": "keyword2",
	"_other-flushmblk": "keyword2",
	"_other-id": "keyword2",
	"_other-misc": "keyword2",
	"_other-trans": "keyword2",
	"_other-undo": "keyword2",
	"_other-uptime": "keyword2",
	"_other-wait": "keyword2",
	"_override": "keyword2",
	"_owner": "keyword2",
	"_password": "keyword2",
	"_prime-index": "keyword2",
	"_proc-name": "keyword2",
	"_procbin": "keyword2",
	"_procedure": "comment2",
	"_procedure-settings": "comment2",
	"_procid": "keyword2",
	"_procname": "keyword2",
	"_proctext": "keyword2",
	"_proctype": "keyword2",
	"_property": "keyword2",
	"_pw-apwqwrites": "keyword2",
	"_pw-buffsscaned": "keyword2",
	"_pw-bufsckp": "keyword2",
	"_pw-checkpoints": "keyword2",
	"_pw-ckpqwrites": "keyword2",
	"_pw-dbwrites": "keyword2",
	"_pw-flushed": "keyword2",
	"_pw-id": "keyword2",
	"_pw-marked": "keyword2",
	"_pw-misc": "keyword2",
	"_pw-scancycles": "keyword2",
	"_pw-scanwrites": "keyword2",
	"_pw-totdbwrites": "keyword2",
	"_pw-trans": "keyword2",
	"_pw-uptime": "keyword2",
	"_pwd": "keyword2",
	"_pwd_duration": "keyword2",
	"_pwd_expires": "keyword2",
	"_record-bytescreat": "keyword2",
	"_record-bytesdel": "keyword2",
	"_record-bytesread": "keyword2",
	"_record-bytesupd": "keyword2",
	"_record-fragcreat": "keyword2",
	"_record-fragdel": "keyword2",
	"_record-fragread": "keyword2",
	"_record-fragupd": "keyword2",
	"_record-id": "keyword2",
	"_record-misc": "keyword2",
	"_record-reccreat": "keyword2",
	"_record-recdel": "keyword2",
	"_record-recread": "keyword2",
	"_record-recupd": "keyword2",
	"_record-trans": "keyword2",
	"_record-uptime": "keyword2",
	"_ref": "keyword2",
	"_ref-table": "keyword2",
	"_refcnstrname": "keyword2",
	"_referstonew": "keyword2",
	"_referstoold": "keyword2",
	"_refowner": "keyword2",
	"_reftblname": "keyword2",
	"_remowner": "keyword2",
	"_remtbl": "keyword2",
	"_repl-agent": "keyword2",
	"_repl-agentcontrol": "keyword2",
	"_repl-server": "keyword2",
	"_replagt-agentid": "keyword2",
	"_replagt-agentname": "keyword2",
	"_replagt-blocksack": "keyword2",
	"_replagt-blocksprocessed": "keyword2",
	"_replagt-blocksreceived": "keyword2",
	"_replagt-commstatus": "keyword2",
	"_replagt-connecttime": "keyword2",
	"_replagt-dbname": "keyword2",
	"_replagt-lasttrid": "keyword2",
	"_replagt-method": "keyword2",
	"_replagt-notesprocessed": "keyword2",
	"_replagt-port": "keyword2",
	"_replagt-reservedchar": "keyword2",
	"_replagt-reservedint": "keyword2",
	"_replagt-serverhost": "keyword2",
	"_replagt-status": "keyword2",
	"_replagtctl-agentid": "keyword2",
	"_replagtctl-agentname": "keyword2",
	"_replagtctl-blocksack": "keyword2",
	"_replagtctl-blockssent": "keyword2",
	"_replagtctl-commstatus": "keyword2",
	"_replagtctl-connecttime": "keyword2",
	"_replagtctl-lastblocksentat": "keyword2",
	"_replagtctl-method": "keyword2",
	"_replagtctl-port": "keyword2",
	"_replagtctl-remotedbname": "keyword2",
	"_replagtctl-remotehost": "keyword2",
	"_replagtctl-reservedchar": "keyword2",
	"_replagtctl-reservedint": "keyword2",
	"_replagtctl-status": "keyword2",
	"_replsrv-agentcount": "keyword2",
	"_replsrv-blockssent": "keyword2",
	"_replsrv-id": "keyword2",
	"_replsrv-lastblocksentat": "keyword2",
	"_replsrv-reservedchar": "keyword2",
	"_replsrv-reservedint": "keyword2",
	"_replsrv-starttime": "keyword2",
	"_resacc": "keyword2",
	"_resrc": "keyword2",
	"_resrc-id": "keyword2",
	"_resrc-lock": "keyword2",
	"_resrc-name": "keyword2",
	"_resrc-time": "keyword2",
	"_resrc-wait": "keyword2",
	"_rolename": "keyword2",
	"_rssid": "keyword2",
	"_scale": "keyword2",
	"_schemaname": "keyword2",
	"_screator": "keyword2",
	"_searchable": "keyword2",
	"_segment-bytefree": "keyword2",
	"_segment-bytesused": "keyword2",
	"_segment-id": "keyword2",
	"_segment-misc": "keyword2",
	"_segment-segid": "keyword2",
	"_segment-segsize": "keyword2",
	"_segments": "keyword2",
	"_sel": "keyword2",
	"_seq": "keyword2",
	"_seq-incr": "keyword2",
	"_seq-init": "keyword2",
	"_seq-max": "keyword2",
	"_seq-min": "keyword2",
	"_seq-misc": "keyword2",
	"_seq-name": "keyword2",
	"_seq-num": "keyword2",
	"_seq-owner": "keyword2",
	"_sequence": "keyword2",
	"_server-byterec": "keyword2",
	"_server-bytesent": "keyword2",
	"_server-currusers": "keyword2",
	"_server-id": "keyword2",
	"_server-logins": "keyword2",
	"_server-maxusers": "keyword2",
	"_server-misc": "keyword2",
	"_server-msgrec": "keyword2",
	"_server-msgsent": "keyword2",
	"_server-num": "keyword2",
	"_server-pendconn": "keyword2",
	"_server-pid": "keyword2",
	"_server-portnum": "keyword2",
	"_server-protocol": "keyword2",
	"_server-qryrec": "keyword2",
	"_server-recrec": "keyword2",
	"_server-recsent": "keyword2",
	"_server-timeslice": "keyword2",
	"_server-trans": "keyword2",
	"_server-type": "keyword2",
	"_server-uptime": "keyword2",
	"_servers": "keyword2",
	"_sname": "keyword2",
	"_sowner": "keyword2",
	"_space-allocnewrm": "keyword2",
	"_space-backadd": "keyword2",
	"_space-bytesalloc": "keyword2",
	"_space-dbexd": "keyword2",
	"_space-examined": "keyword2",
	"_space-fromfree": "keyword2",
	"_space-fromrm": "keyword2",
	"_space-front2back": "keyword2",
	"_space-frontadd": "keyword2",
	"_space-id": "keyword2",
	"_space-locked": "keyword2",
	"_space-misc": "keyword2",
	"_space-removed": "keyword2",
	"_space-retfree": "keyword2",
	"_space-takefree": "keyword2",
	"_space-trans": "keyword2",
	"_space-uptime": "keyword2",
	"_spare1": "keyword2",
	"_spare2": "keyword2",
	"_spare3": "keyword2",
	"_spare4": "keyword2",
	"_sql_properties": "keyword2",
	"_sremdb": "keyword2",
	"_startup": "keyword2",
	"_startup-aibuffs": "keyword2",
	"_startup-ainame": "keyword2",
	"_startup-apwbuffs": "keyword2",
	"_startup-apwmaxwrites": "keyword2",
	"_startup-apwqtime": "keyword2",
	"_startup-apwstime": "keyword2",
	"_startup-bibuffs": "keyword2",
	"_startup-bidelay": "keyword2",
	"_startup-biio": "keyword2",
	"_startup-biname": "keyword2",
	"_startup-bitrunc": "keyword2",
	"_startup-buffs": "keyword2",
	"_startup-crashprot": "keyword2",
	"_startup-directio": "keyword2",
	"_startup-id": "keyword2",
	"_startup-locktable": "keyword2",
	"_startup-maxclients": "keyword2",
	"_startup-maxservers": "keyword2",
	"_startup-maxusers": "keyword2",
	"_startup-misc": "keyword2",
	"_startup-spin": "keyword2",
	"_statbase": "keyword2",
	"_statbase-id": "keyword2",
	"_statementorrow": "keyword2",
	"_stbl": "keyword2",
	"_stblowner": "keyword2",
	"_storageobject": "keyword2",
	"_summary-aiwrites": "keyword2",
	"_summary-bireads": "keyword2",
	"_summary-biwrites": "keyword2",
	"_summary-chkpts": "keyword2",
	"_summary-commits": "keyword2",
	"_summary-dbaccesses": "keyword2",
	"_summary-dbreads": "keyword2",
	"_summary-dbwrites": "keyword2",
	"_summary-flushed": "keyword2",
	"_summary-id": "keyword2",
	"_summary-misc": "keyword2",
	"_summary-reccreat": "keyword2",
	"_summary-recdel": "keyword2",
	"_summary-reclock": "keyword2",
	"_summary-recreads": "keyword2",
	"_summary-recupd": "keyword2",
	"_summary-recwait": "keyword2",
	"_summary-transcomm": "keyword2",
	"_summary-undos": "keyword2",
	"_summary-uptime": "keyword2",
	"_surname": "keyword2",
	"_sys-field": "keyword2",
	"_sysattachtbls": "keyword2",
	"_sysbigintstat": "keyword2",
	"_syscalctable": "keyword2",
	"_syscharstat": "keyword2",
	"_syschkcolusage": "keyword2",
	"_syschkconstr_name_map": "keyword2",
	"_syschkconstrs": "keyword2",
	"_syscolauth": "keyword2",
	"_syscolstat": "keyword2",
	"_sysdatatypes": "keyword2",
	"_sysdatestat": "keyword2",
	"_sysdbauth": "keyword2",
	"_sysdblinks": "keyword2",
	"_sysfloatstat": "keyword2",
	"_sysidxstat": "keyword2",
	"_sysintstat": "keyword2",
	"_syskeycolusage": "keyword2",
	"_sysncharstat": "keyword2",
	"_sysnumstat": "keyword2",
	"_sysnvarcharstat": "keyword2",
	"_sysprocbin": "keyword2",
	"_sysproccolumns": "keyword2",
	"_sysprocedures": "keyword2",
	"_sysproctext": "keyword2",
	"_sysrealstat": "keyword2",
	"_sysrefconstrs": "keyword2",
	"_sysroles": "keyword2",
	"_sysschemas": "keyword2",
	"_sysseqauth": "keyword2",
	"_syssmintstat": "keyword2",
	"_syssynonyms": "keyword2",
	"_systabauth": "keyword2",
	"_systblconstrs": "keyword2",
	"_systblstat": "keyword2",
	"_systimestat": "keyword2",
	"_systinyintstat": "keyword2",
	"_systrigcols": "keyword2",
	"_systrigger": "keyword2",
	"_systsstat": "keyword2",
	"_syststzstat": "keyword2",
	"_sysvarcharstat": "keyword2",
	"_sysviews": "keyword2",
	"_sysviews_name_map": "keyword2",
	"_tablebase": "keyword2",
	"_tablestat": "keyword2",
	"_tablestat-create": "keyword2",
	"_tablestat-delete": "keyword2",
	"_tablestat-id": "keyword2",
	"_tablestat-read": "keyword2",
	"_tablestat-update": "keyword2",
	"_tbl": "keyword2",
	"_tbl-status": "keyword2",
	"_tbl-type": "keyword2",
	"_tblid": "keyword2",
	"_tblname": "keyword2",
	"_tblowner": "keyword2",
	"_telephone": "keyword2",
	"_template": "keyword2",
	"_toss-limit": "keyword2",
	"_trans": "keyword2",
	"_trans-coord": "keyword2",
	"_trans-coordtx": "keyword2",
	"_trans-counter": "keyword2",
	"_trans-duration": "keyword2",
	"_trans-flags": "keyword2",
	"_trans-id": "keyword2",
	"_trans-misc": "keyword2",
	"_trans-num": "keyword2",
	"_trans-state": "keyword2",
	"_trans-txtime": "keyword2",
	"_trans-usrnum": "keyword2",
	"_trig-crc": "keyword2",
	"_triggerevent": "keyword2",
	"_triggerid": "keyword2",
	"_triggername": "keyword2",
	"_triggertime": "keyword2",
	"_txe-id": "keyword2",
	"_txe-locks": "keyword2",
	"_txe-lockss": "keyword2",
	"_txe-time": "keyword2",
	"_txe-type": "keyword2",
	"_txe-wait-time": "keyword2",
	"_txe-waits": "keyword2",
	"_txe-waitss": "keyword2",
	"_txelock": "keyword2",
	"_typeprecision": "keyword2",
	"_u-misc1": "keyword2",
	"_u-misc2": "keyword2",
	"_uib-code-block": "comment2",
	"_uib-preprocessor-block": "comment2",
	"_unique": "keyword2",
	"_unsignedattr": "keyword2",
	"_unsorted": "keyword2",
	"_upd": "keyword2",
	"_updatable": "keyword2",
	"_user": "keyword2",
	"_user-misc": "keyword2",
	"_user-name": "keyword2",
	"_user_number": "keyword2",
	"_userid": "keyword2",
	"_userio": "keyword2",
	"_userio-airead": "keyword2",
	"_userio-aiwrite": "keyword2",
	"_userio-biread": "keyword2",
	"_userio-biwrite": "keyword2",
	"_userio-dbaccess": "keyword2",
	"_userio-dbread": "keyword2",
	"_userio-dbwrite": "keyword2",
	"_userio-id": "keyword2",
	"_userio-misc": "keyword2",
	"_userio-name": "keyword2",
	"_userio-usr": "keyword2",
	"_userlock": "keyword2",
	"_userlock-chain": "keyword2",
	"_userlock-flags": "keyword2",
	"_userlock-id": "keyword2",
	"_userlock-misc": "keyword2",
	"_userlock-name": "keyword2",
	"_userlock-recid": "keyword2",
	"_userlock-type": "keyword2",
	"_userlock-usr": "keyword2",
	"_username": "keyword2",
	"_userstatus": "keyword2",
	"_userstatus-counter": "keyword2",
	"_userstatus-objectid": "keyword2",
	"_userstatus-objecttype": "keyword2",
	"_userstatus-operation": "keyword2",
	"_userstatus-state": "keyword2",
	"_userstatus-target": "keyword2",
	"_userstatus-userid": "keyword2",
	"_val_ts": "keyword2",
	"_valexp": "keyword2",
	"_valmsg": "keyword2",
	"_valmsg-sa": "keyword2",
	"_value": "keyword2",
	"_value_ch": "keyword2",
	"_value_n": "keyword2",
	"_vcol-order": "keyword2",
	"_version": "keyword2",
	"_version-number": "comment2",
	"_view": "keyword2",
	"_view-as": "keyword2",
	"_view-col": "keyword2",
	"_view-def": "keyword2",
	"_view-name": "keyword2",
	"_view-ref": "keyword2",
	"_viewname": "keyword2",
	"_viewtext": "keyword2",
	"_where-cls": "keyword2",
	"_width": "keyword2",
	"_word-rule": "keyword2",
	"_word-rules": "keyword2",
	"_wordidx": "keyword2",
	"_wr-attr": "keyword2",
	"_wr-cp": "keyword2",
	"_wr-name": "keyword2",
	"_wr-number": "keyword2",
	"_wr-segment": "keyword2",
	"_wr-type": "keyword2",
	"_wr-version": "keyword2",
	"_xftr": "comment2",
	"abort": "keyword1",
	"absolute": "keyword1",
	"accelerator": "keyword1",
	"accept-changes": "keyword1",
	"accept-row-changes": "keyword1",
	"accum": "keyword1",
	"accumulate": "keyword1",
	"across": "keyword1",
	"active": "keyword1",
	"active-window": "keyword1",
	"actor": "keyword1",
	"add": "keyword1",
	"add-buffer": "keyword1",
	"add-calc-column": "keyword1",
	"add-columns-from": "keyword1",
	"add-events-procedure": "keyword1",
	"add-fields-from": "keyword1",
	"add-first": "keyword1",
	"add-header-entry": "keyword1",
	"add-index-field": "keyword1",
	"add-interval": "keyword1",
	"add-last": "keyword1",
	"add-like-column": "keyword1",
	"add-like-field": "keyword1",
	"add-like-index": "keyword1",
	"add-new-field": "keyword1",
	"add-new-index": "keyword1",
	"add-relation": "keyword1",
	"add-source-buffer": "keyword1",
	"add-super-procedure": "keyword1",
	"adm-container": "comment2",
	"adm-data": "keyword1",
	"adm-supported-links": "comment2",
	"advise": "keyword1",
	"after-buffer": "keyword1",
	"after-record-fill": "invalid",
	"after-rowid": "keyword1",
	"after-table": "keyword1",
	"alert-box": "keyword1",
	"alias": "keyword1",
	"all": "keyword1",
	"allow-column-searching": "keyword1",
	"allow-replication": "keyword1",
	"alter": "keyword1",
	"alternate-key": "keyword1",
	"always-on-top": "keyword1",
	"ambiguous": "keyword1",
	"analyze-resume": "comment2",
	"analyze-suspend": "comment2",
	"and": "keyword1",
	"ansi-only": "keyword1",
	"any": "keyword1",
	"any-key": "keyword3",
	"any-printable": "keyword3",
	"anywhere": "keyword1",
	"append": "keyword1",
	"append-child": "keyword1",
	"append-line": "keyword1",
	"appl-alert-boxes": "keyword1",
	"application": "keyword1",
	"apply": "keyword1",
	"apply-callback": "keyword1",
	"appserver-info": "keyword1",
	"appserver-password": "keyword1",
	"appserver-userid": "keyword1",
	"array-message": "keyword1",
	"as": "keyword1",
	"as-cursor": "keyword1",
	"asc": "keyword1",
	"ascending": "keyword1",
	"ask-overwrite": "keyword1",
	"assign": "keyword1",
	"async-request-count": "keyword1",
	"async-request-handle": "keyword1",
	"asynchronous": "keyword1",
	"at": "keyword1",
	"attach": "keyword1",
	"attach-data-source": "keyword1",
	"attachment": "keyword1",
	"attr-space": "keyword1",
	"attribute-names": "keyword1",
	"attribute-type": "keyword1",
	"authorization": "keyword1",
	"auto-completion": "keyword1",
	"auto-delete": "keyword1",
	"auto-delete-xml": "keyword1",
	"auto-end-key": "keyword1",
	"auto-endkey": "keyword1",
	"auto-go": "keyword1",
	"auto-indent": "keyword1",
	"auto-resize": "keyword1",
	"auto-return": "keyword1",
	"auto-validate": "keyword1",
	"auto-zap": "keyword1",
	"automatic": "keyword1",
	"avail": "keyword1",
	"available": "keyword1",
	"available-formats": "keyword1",
	"average": "keyword1",
	"avg": "keyword1",
	"back-tab": "keyword3",
	"background": "keyword1",
	"backspace": "keyword3",
	"backwards": "keyword1",
	"base-ade": "keyword1",
	"base-key": "keyword1",
	"base64": "keyword1",
	"basic-logging": "keyword1",
	"batch-mode": "comment2",
	"before-buffer": "keyword1",
	"before-hide": "keyword1",
	"before-record-fill": "invalid",
	"before-rowid": "keyword1",
	"before-table": "keyword1",
	"begins": "keyword1",
	"bell": "keyword3",
	"between": "keyword1",
	"bgcolor": "keyword1",
	"big-endian": "keyword1",
	"binary": "keyword1",
	"bind-where": "keyword1",
	"blank": "keyword1",
	"blob": "keyword1",
	"block": "keyword1",
	"block-iteration-display": "keyword1",
	"border-bottom": "keyword1",
	"border-bottom-chars": "keyword1",
	"border-bottom-pixels": "keyword1",
	"border-left": "keyword1",
	"border-left-chars": "keyword1",
	"border-left-pixels": "keyword1",
	"border-right": "keyword1",
	"border-right-chars": "keyword1",
	"border-right-pixels": "keyword1",
	"border-top": "keyword1",
	"border-top-chars": "keyword1",
	"border-top-pixels": "keyword1",
	"both": "keyword1",
	"bottom": "keyword1",
	"bottom-column": "keyword1",
	"box": "keyword1",
	"box-selectable": "keyword1",
	"break": "keyword1",
	"break-line": "keyword1",
	"browse": "keyword1",
	"browse-column-data-types": "keyword1",
	"browse-column-formats": "keyword1",
	"browse-column-labels": "keyword1",
	"browse-header": "keyword1",
	"browse-name": "comment2",
	"btos": "invalid",
	"buffer": "keyword1",
	"buffer-chars": "keyword1",
	"buffer-compare": "keyword1",
	"buffer-copy": "keyword1",
	"buffer-create": "keyword1",
	"buffer-delete": "keyword1",
	"buffer-field": "keyword1",
	"buffer-handle": "keyword1",
	"buffer-lines": "keyword1",
	"buffer-name": "keyword1",
	"buffer-release": "keyword1",
	"buffer-validate": "keyword1",
	"buffer-value": "keyword1",
	"button": "keyword1",
	"buttons": "keyword1",
	"by": "keyword1",
	"by-pointer": "keyword1",
	"by-reference": "keyword1",
	"by-value": "keyword1",
	"by-variant-pointer": "keyword1",
	"byte": "keyword1",
	"bytes-read": "keyword1",
	"bytes-written": "keyword1",
	"cache": "keyword1",
	"cache-size": "keyword1",
	"call": "keyword1",
	"call-name": "keyword1",
	"call-type": "keyword1",
	"can-create": "keyword1",
	"can-delete": "keyword1",
	"can-do": "keyword1",
	"can-find": "keyword1",
	"can-query": "keyword1",
	"can-read": "keyword1",
	"can-set": "keyword1",
	"can-write": "keyword1",
	"cancel-break": "keyword1",
	"cancel-button": "keyword1",
	"cancel-pick": "keyword1",
	"cancel-requests": "keyword1",
	"cancelled": "keyword1",
	"caps": "keyword1",
	"careful-paint": "keyword1",
	"case": "keyword1",
	"case-sensitive": "keyword1",
	"cdecl": "keyword1",
	"centered": "keyword1",
	"chained": "keyword1",
	"char": "keyword1",
	"character": "keyword1",
	"character_length": "keyword1",
	"charset": "keyword1",
	"check": "keyword1",
	"checked": "keyword1",
	"child-buffer": "keyword1",
	"child-num": "keyword1",
	"choices": "keyword1",
	"choose": "invalid",
	"chr": "keyword1",
	"clear": "keyword1",
	"clear-selection": "keyword1",
	"client-connection-id": "keyword1",
	"client-type": "keyword1",
	"clipboard": "keyword1",
	"clob": "keyword1",
	"clone-node": "keyword1",
	"close": "keyword1",
	"code": "keyword1",
	"codebase-locator": "keyword1",
	"codepage": "keyword1",
	"codepage-convert": "keyword1",
	"col": "keyword1",
	"col-of": "keyword1",
	"collate": "keyword1",
	"colon": "keyword1",
	"colon-aligned": "keyword1",
	"color": "keyword1",
	"color-table": "keyword1",
	"column": "keyword1",
	"column-bgcolor": "keyword1",
	"column-codepage": "keyword1",
	"column-dcolor": "keyword1",
	"column-fgcolor": "keyword1",
	"column-font": "keyword1",
	"column-label": "keyword1",
	"column-label-bgcolor": "keyword1",
	"column-label-dcolor": "keyword1",
	"column-label-fgcolor": "keyword1",
	"column-label-font": "keyword1",
	"column-label-height-chars": "keyword1",
	"column-label-height-pixels": "keyword1",
	"column-movable": "keyword1",
	"column-of": "keyword1",
	"column-pfcolor": "keyword1",
	"column-read-only": "keyword1",
	"column-resizable": "keyword1",
	"column-scrolling": "keyword1",
	"columns": "keyword1",
	"com-handle": "keyword1",
	"com-self": "keyword1",
	"combo-box": "keyword1",
	"command": "keyword1",
	"compares": "keyword1",
	"compile": "keyword1",
	"compiler": "keyword1",
	"complete": "keyword1",
	"component-handle": "keyword1",
	"component-self": "keyword1",
	"config-name": "keyword1",
	"connect": "keyword1",
	"connected": "keyword1",
	"constrained": "keyword1",
	"container-event": "keyword3",
	"contains": "keyword1",
	"contents": "keyword1",
	"context": "keyword1",
	"context-help": "keyword1",
	"context-help-file": "keyword1",
	"context-help-id": "keyword1",
	"context-popup": "keyword1",
	"control": "keyword1",
	"control-box": "keyword1",
	"control-container": "keyword1",
	"control-frame": "keyword1",
	"convert": "keyword1",
	"convert-3d-colors": "keyword1",
	"convert-to-offset": "keyword1",
	"copy": "keyword1",
	"copy-lob": "keyword1",
	"count": "keyword1",
	"count-of": "keyword1",
	"coverage": "keyword1",
	"cpcase": "keyword1",
	"cpcoll": "keyword1",
	"cpinternal": "keyword1",
	"cplog": "keyword1",
	"cpprint": "keyword1",
	"cprcodein": "keyword1",
	"cprcodeout": "keyword1",
	"cpstream": "keyword1",
	"cpterm": "keyword1",
	"crc-value": "keyword1",
	"create": "keyword1",
	"create-like": "keyword1",
	"create-node": "keyword1",
	"create-node-namespace": "keyword1",
	"create-on-add": "keyword1",
	"create-result-list-entry": "keyword1",
	"create-test-file": "keyword1",
	"ctos": "invalid",
	"current": "keyword1",
	"current-changed": "keyword1",
	"current-column": "keyword1",
	"current-environment": "keyword1",
	"current-iteration": "keyword1",
	"current-language": "keyword1",
	"current-result-row": "keyword1",
	"current-row-modified": "keyword1",
	"current-value": "keyword1",
	"current-window": "keyword1",
	"current_date": "keyword1",
	"cursor": "keyword1",
	"cursor-char": "keyword1",
	"cursor-down": "keyword1",
	"cursor-left": "keyword1",
	"cursor-line": "keyword1",
	"cursor-offset": "keyword1",
	"cursor-right": "keyword1",
	"cursor-up": "keyword1",
	"cut": "keyword1",
	"data-bind": "keyword1",
	"data-entry-return": "keyword1",
	"data-refresh-line": "keyword1",
	"data-refresh-page": "keyword1",
	"data-relation": "keyword1",
	"data-source": "keyword1",
	"data-type": "keyword1",
	"database": "keyword1",
	"dataservers": "keyword1",
	"dataset": "keyword1",
	"dataset-handle": "keyword1",
	"date": "keyword1",
	"date-format": "keyword1",
	"datetime": "keyword1",
	"datetime-tz": "keyword1",
	"day": "keyword1",
	"db-references": "keyword1",
	"dbcodepage": "keyword1",
	"dbcollation": "keyword1",
	"dbname": "keyword1",
	"dbparam": "keyword1",
	"dbrestrictions": "keyword1",
	"dbtaskid": "keyword1",
	"dbtype": "keyword1",
	"dbversion": "keyword1",
	"dcolor": "keyword1",
	"dde": "keyword1",
	"dde-error": "keyword1",
	"dde-id": "keyword1",
	"dde-item": "keyword1",
	"dde-name": "keyword1",
	"dde-notify": "keyword3",
	"dde-topic": "keyword1",
	"deblank": "keyword1",
	"debug": "keyword1",
	"debug-alert": "keyword1",
	"debug-list": "keyword1",
	"debugger": "keyword1",
	"dec": "keyword1",
	"decimal": "keyword1",
	"decimals": "keyword1",
	"declare": "keyword1",
	"def": "keyword1",
	"default": "keyword1",
	"default-action": "keyword3",
	"default-buffer-handle": "keyword1",
	"default-button": "keyword1",
	"default-commit": "keyword1",
	"default-extension": "keyword1",
	"default-noxlate": "keyword1",
	"default-pop-up": "keyword1",
	"default-string": "keyword1",
	"default-window": "keyword1",
	"defer-lob-fetch": "keyword1",
	"define": "keyword1",
	"defined": "comment2",
	"del": "keyword3",
	"delete": "keyword1",
	"delete-char": "keyword3",
	"delete-character": "keyword3",
	"delete-column": "keyword1",
	"delete-current-row": "keyword1",
	"delete-end-line": "keyword1",
	"delete-field": "keyword1",
	"delete-header-entry": "keyword1",
	"delete-line": "keyword1",
	"delete-node": "keyword1",
	"delete-result-list-entry": "keyword1",
	"delete-selected-row": "keyword1",
	"delete-selected-rows": "keyword1",
	"delete-word": "keyword1",
	"delimiter": "keyword1",
	"descending": "keyword1",
	"description": "keyword1",
	"deselect": "keyword3",
	"deselect-extend": "keyword1",
	"deselect-focused-row": "keyword1",
	"deselect-rows": "keyword1",
	"deselect-selected-row": "keyword1",
	"deselection": "keyword3",
	"deselection-extend": "keyword1",
	"detach": "keyword1",
	"detach-data-source": "keyword1",
	"dialog-box": "keyword1",
	"dialog-help": "keyword1",
	"dict": "keyword1",
	"dictionary": "keyword1",
	"dir": "keyword1",
	"directory": "keyword1",
	"disable": "keyword1",
	"disable-auto-zap": "keyword1",
	"disable-connections": "keyword1",
	"disable-dump-triggers": "keyword1",
	"disable-load-triggers": "keyword1",
	"disabled": "keyword1",
	"disconnect": "keyword1",
	"dismiss-menu": "keyword1",
	"disp": "keyword1",
	"display": "keyword1",
	"display-message": "keyword1",
	"display-timezone": "keyword1",
	"display-type": "keyword1",
	"displayed-fields": "comment2",
	"displayed-objects": "comment2",
	"distinct": "keyword1",
	"do": "keyword1",
	"dos": "invalid",
	"dos-end": "keyword1",
	"double": "keyword1",
	"down": "keyword1",
	"drag-enabled": "keyword1",
	"drop": "keyword1",
	"drop-down": "keyword1",
	"drop-down-list": "keyword1",
	"drop-file-notify": "keyword3",
	"drop-target": "keyword1",
	"dump": "keyword1",
	"dump-logging-now": "keyword1",
	"dyn-function": "keyword1",
	"dynamic": "keyword1",
	"dynamic-current-value": "keyword1",
	"dynamic-function": "keyword1",
	"dynamic-next-value": "keyword1",
	"each": "keyword1",
	"echo": "keyword1",
	"edge": "keyword1",
	"edge-chars": "keyword1",
	"edge-pixels": "keyword1",
	"edit-can-paste": "keyword1",
	"edit-can-undo": "keyword1",
	"edit-clear": "keyword1",
	"edit-copy": "keyword1",
	"edit-cut": "keyword1",
	"edit-paste": "keyword1",
	"edit-undo": "keyword1",
	"editing": "invalid",
	"editor": "keyword1",
	"editor-backtab": "keyword1",
	"editor-tab": "keyword1",
	"else": "comment2",
	"elseif": "comment2",
	"empty": "keyword1",
	"empty-dataset": "keyword1",
	"empty-selection": "keyword3",
	"empty-temp-table": "keyword1",
	"enable": "keyword1",
	"enable-connections": "keyword1",
	"enabled": "keyword1",
	"enabled-fields": "comment2",
	"enabled-fields-in-query": "comment2",
	"enabled-objects": "comment2",
	"enabled-tables": "comment2",
	"enabled-tables-in-query": "comment2",
	"encode": "keyword1",
	"encoding": "keyword1",
	"end": "keyword3",
	"end-box-selection": "keyword3",
	"end-error": "keyword3",
	"end-file-drop": "keyword1",
	"end-key": "keyword1",
	"end-move": "keyword3",
	"end-resize": "keyword3",
	"end-row-resize": "keyword1",
	"end-search": "keyword3",
	"end-user-prompt": "keyword1",
	"endif": "comment2",
	"endkey": "keyword3",
	"enter-menubar": "keyword1",
	"entered": "keyword1",
	"entry": "keyword3",
	"entry-types-list": "keyword1",
	"eq": "keyword1",
	"error": "keyword3",
	"error-column": "keyword1",
	"error-object-detail": "keyword1",
	"error-row": "keyword1",
	"error-status": "keyword1",
	"error-string": "keyword1",
	"escape": "keyword1",
	"etime": "keyword1",
	"event-procedure": "keyword1",
	"event-procedure-context": "keyword1",
	"event-type": "keyword1",
	"events": "keyword1",
	"except": "keyword1",
	"excl": "keyword1",
	"exclusive": "keyword1",
	"exclusive-id": "keyword1",
	"exclusive-lock": "keyword1",
	"exclusive-web-user": "keyword1",
	"execute": "keyword1",
	"execution-log": "keyword1",
	"exists": "keyword1",
	"exit": "keyword1",
	"exp": "keyword1",
	"expand": "keyword1",
	"expandable": "keyword1",
	"explicit": "keyword1",
	"export": "keyword1",
	"extended": "keyword1",
	"extent": "keyword1",
	"external": "keyword1",
	"external-tables": "comment2",
	"extract": "keyword1",
	"false": "keyword1",
	"fetch": "keyword1",
	"fetch-selected-row": "keyword1",
	"fgcolor": "keyword1",
	"field": "keyword1",
	"field-group": "keyword1",
	"field-pairs": "comment2",
	"field-pairs-in-query": "comment2",
	"fields": "keyword1",
	"fields-in-query": "comment2",
	"file": "keyword1",
	"file-access-date": "keyword1",
	"file-access-time": "keyword1",
	"file-create-date": "keyword1",
	"file-create-time": "keyword1",
	"file-info": "keyword1",
	"file-information": "keyword1",
	"file-mod-date": "keyword1",
	"file-mod-time": "keyword1",
	"file-name": "comment2",
	"file-offset": "keyword1",
	"file-size": "keyword1",
	"file-type": "keyword1",
	"filename": "keyword1",
	"fill": "keyword1",
	"fill-in": "keyword1",
	"fill-mode": "keyword1",
	"fill-where-string": "keyword1",
	"filled": "keyword1",
	"filters": "keyword1",
	"find": "keyword1",
	"find-by-rowid": "keyword1",
	"find-case-sensitive": "keyword1",
	"find-current": "keyword1",
	"find-first": "keyword1",
	"find-global": "keyword1",
	"find-last": "keyword1",
	"find-next": "keyword1",
	"find-next-occurrence": "keyword1",
	"find-prev-occurrence": "keyword1",
	"find-previous": "keyword1",
	"find-select": "keyword1",
	"find-unique": "keyword1",
	"find-wrap-around": "keyword1",
	"finder": "keyword1",
	"first": "keyword1",
	"first-async-request": "keyword1",
	"first-buffer": "keyword1",
	"first-child": "keyword1",
	"first-column": "keyword1",
	"first-data-source": "keyword1",
	"first-dataset": "keyword1",
	"first-external-table": "comment2",
	"first-of": "keyword1",
	"first-procedure": "keyword1",
	"first-query": "keyword1",
	"first-server": "keyword1",
	"first-server-socket": "keyword1",
	"first-socket": "keyword1",
	"first-tab-item": "keyword1",
	"first-table-in-query": "comment2",
	"fit-last-column": "keyword1",
	"fix-codepage": "keyword1",
	"fixed-only": "keyword1",
	"flat-button": "keyword1",
	"float": "keyword1",
	"focus": "keyword1",
	"focus-in": "keyword1",
	"focused-row": "keyword1",
	"focused-row-selected": "keyword1",
	"font": "keyword1",
	"font-based-layout": "keyword1",
	"font-table": "keyword1",
	"for": "keyword1",
	"force-file": "keyword1",
	"foreground": "keyword1",
	"form": "keyword1",
	"form-input": "keyword1",
	"format": "keyword1",
	"forward": "keyword1",
	"forward-only": "keyword1",
	"forwards": "keyword1",
	"frame": "keyword1",
	"frame-col": "keyword1",
	"frame-db": "keyword1",
	"frame-down": "keyword1",
	"frame-field": "keyword1",
	"frame-file": "keyword1",
	"frame-index": "keyword1",
	"frame-line": "keyword1",
	"frame-name": "comment2",
	"frame-row": "keyword1",
	"frame-spacing": "keyword1",
	"frame-value": "keyword1",
	"frame-x": "keyword1",
	"frame-y": "keyword1",
	"frequency": "keyword1",
	"from": "keyword1",
	"from-chars": "keyword1",
	"from-current": "keyword1",
	"from-pixels": "keyword1",
	"fromnoreorder": "keyword1",
	"full-height": "keyword1",
	"full-height-chars": "keyword1",
	"full-height-pixels": "keyword1",
	"full-pathname": "keyword1",
	"full-width-chars": "keyword1",
	"full-width-pixels": "keyword1",
	"funct": "keyword1",
	"function": "keyword1",
	"function-call-type": "keyword1",
	"gateways": "invalid",
	"ge": "keyword1",
	"generate-md5": "keyword1",
	"get": "keyword1",
	"get-attr-call-type": "keyword1",
	"get-attribute": "keyword1",
	"get-attribute-node": "keyword1",
	"get-bits": "keyword1",
	"get-blue-value": "keyword1",
	"get-browse-column": "keyword1",
	"get-buffer-handle": "keyword1",
	"get-byte": "keyword1",
	"get-byte-order": "keyword1",
	"get-bytes": "keyword1",
	"get-bytes-available": "keyword1",
	"get-cgi-list": "keyword1",
	"get-cgi-value": "keyword1",
	"get-changes": "keyword1",
	"get-child": "keyword1",
	"get-child-relation": "keyword1",
	"get-codepages": "keyword1",
	"get-collations": "keyword1",
	"get-config-value": "keyword1",
	"get-current": "keyword1",
	"get-dataset-buffer": "keyword1",
	"get-dir": "keyword1",
	"get-document-element": "keyword1",
	"get-double": "keyword1",
	"get-dropped-file": "keyword1",
	"get-dynamic": "keyword1",
	"get-file": "keyword1",
	"get-first": "keyword1",
	"get-float": "keyword1",
	"get-green-value": "keyword1",
	"get-header-entry": "keyword1",
	"get-index-by-namespace-name": "keyword1",
	"get-index-by-qname": "keyword1",
	"get-iteration": "keyword1",
	"get-key-value": "keyword1",
	"get-last": "keyword1",
	"get-localname-by-index": "keyword1",
	"get-long": "keyword1",
	"get-message": "keyword1",
	"get-next": "keyword1",
	"get-node": "keyword1",
	"get-number": "keyword1",
	"get-parent": "keyword1",
	"get-pointer-value": "keyword1",
	"get-prev": "keyword1",
	"get-printers": "keyword1",
	"get-qname-by-index": "keyword1",
	"get-red-value": "keyword1",
	"get-relation": "keyword1",
	"get-repositioned-row": "keyword1",
	"get-rgb-value": "keyword1",
	"get-selected-widget": "keyword1",
	"get-serialized": "keyword1",
	"get-short": "keyword1",
	"get-signature": "keyword1",
	"get-size": "keyword1",
	"get-socket-option": "keyword1",
	"get-source-buffer": "keyword1",
	"get-string": "keyword1",
	"get-tab-item": "keyword1",
	"get-text-height": "keyword1",
	"get-text-height-chars": "keyword1",
	"get-text-height-pixels": "keyword1",
	"get-text-width": "keyword1",
	"get-text-width-chars": "keyword1",
	"get-text-width-pixels": "keyword1",
	"get-top-buffer": "keyword1",
	"get-type-by-index": "keyword1",
	"get-type-by-namespace-name": "keyword1",
	"get-type-by-qname": "keyword1",
	"get-unsigned-short": "keyword1",
	"get-uri-by-index": "keyword1",
	"get-value-by-index": "keyword1",
	"get-value-by-namespace-name": "keyword1",
	"get-value-by-qname": "keyword1",
	"get-wait-state": "keyword1",
	"getbyte": "keyword1",
	"glob": "comment2",
	"global": "keyword1",
	"global-define": "comment2",
	"go": "keyword3",
	"go-on": "keyword1",
	"go-pending": "invalid",
	"goto": "keyword1",
	"grant": "keyword1",
	"graphic-edge": "keyword1",
	"grayed": "keyword1",
	"grid-factor-horizontal": "keyword1",
	"grid-factor-vertical": "keyword1",
	"grid-set": "keyword1",
	"grid-snap": "keyword1",
	"grid-unit-height": "keyword1",
	"grid-unit-height-chars": "keyword1",
	"grid-unit-height-pixels": "keyword1",
	"grid-unit-width": "keyword1",
	"grid-unit-width-chars": "keyword1",
	"grid-unit-width-pixels": "keyword1",
	"grid-visible": "keyword1",
	"group": "keyword1",
	"gt": "keyword1",
	"handle": "keyword1",
	"handler": "keyword1",
	"has-lobs": "keyword1",
	"has-records": "keyword1",
	"having": "keyword1",
	"header": "keyword1",
	"height": "keyword1",
	"height-chars": "keyword1",
	"height-pixels": "keyword1",
	"help": "keyword3",
	"help-context": "keyword1",
	"help-topic": "keyword1",
	"helpfile-name": "keyword1",
	"hidden": "keyword1",
	"hide": "keyword1",
	"hint": "keyword1",
	"home": "keyword3",
	"horiz-end": "keyword1",
	"horiz-home": "keyword1",
	"horiz-scroll-drag": "keyword1",
	"horizontal": "keyword1",
	"host-byte-order": "keyword1",
	"html-charset": "keyword1",
	"html-end-of-line": "keyword1",
	"html-end-of-page": "keyword1",
	"html-frame-begin": "keyword1",
	"html-frame-end": "keyword1",
	"html-header-begin": "keyword1",
	"html-header-end": "keyword1",
	"html-title-begin": "keyword1",
	"html-title-end": "keyword1",
	"hwnd": "keyword1",
	"icfparameter": "keyword1",
	"icon": "keyword1",
	"if": "comment2",
	"ignore-current-modified": "keyword1",
	"image": "keyword1",
	"image-down": "keyword1",
	"image-insensitive": "keyword1",
	"image-size": "keyword1",
	"image-size-chars": "keyword1",
	"image-size-pixels": "keyword1",
	"image-up": "keyword1",
	"immediate-display": "keyword1",
	"import": "keyword1",
	"import-node": "keyword1",
	"in": "keyword1",
	"in-handle": "keyword1",
	"include": "comment2",
	"increment-exclusive-id": "keyword1",
	"index": "keyword1",
	"index-field": "keyword1",
	"index-hint": "keyword1",
	"index-information": "keyword1",
	"indexed-reposition": "keyword1",
	"indicator": "keyword1",
	"info": "keyword1",
	"information": "keyword1",
	"init": "keyword1",
	"initial": "keyword1",
	"initial-dir": "keyword1",
	"initial-filter": "keyword1",
	"initialize-document-type": "keyword1",
	"initiate": "keyword1",
	"inner": "keyword1",
	"inner-chars": "keyword1",
	"inner-lines": "keyword1",
	"input": "keyword1",
	"input-output": "keyword1",
	"input-value": "keyword1",
	"insert": "keyword1",
	"insert-backtab": "keyword1",
	"insert-before": "keyword1",
	"insert-column": "keyword1",
	"insert-field": "keyword1",
	"insert-field-data": "keyword1",
	"insert-field-label": "keyword1",
	"insert-file": "keyword1",
	"insert-mode": "keyword1",
	"insert-row": "keyword1",
	"insert-string": "keyword1",
	"insert-tab": "keyword1",
	"instantiating-procedure": "keyword1",
	"int": "keyword1",
	"integer": "keyword1",
	"internal-entries": "keyword1",
	"internal-tables": "comment2",
	"interval": "keyword1",
	"into": "keyword1",
	"invoke": "keyword1",
	"is": "keyword1",
	"is-attr-space": "invalid",
	"is-codepage-fixed": "keyword1",
	"is-column-codepage": "keyword1",
	"is-lead-byte": "keyword1",
	"is-open": "keyword1",
	"is-parameter-set": "keyword1",
	"is-row-selected": "keyword1",
	"is-selected": "keyword1",
	"is-xml": "keyword1",
	"iso-date": "keyword1",
	"item": "keyword1",
	"items-per-row": "keyword1",
	"iteration-changed": "invalid",
	"join": "keyword1",
	"join-by-sqldb": "keyword1",
	"kblabel": "keyword1",
	"keep-connection-open": "keyword1",
	"keep-frame-z-order": "keyword1",
	"keep-messages": "keyword1",
	"keep-security-cache": "keyword1",
	"keep-tab-order": "keyword1",
	"key": "keyword1",
	"key-code": "keyword1",
	"key-function": "keyword1",
	"key-label": "keyword1",
	"keycode": "keyword1",
	"keyfunction": "keyword1",
	"keylabel": "keyword1",
	"keys": "keyword1",
	"keyword": "keyword1",
	"keyword-all": "keyword1",
	"label": "keyword1",
	"label-bgcolor": "keyword1",
	"label-dcolor": "keyword1",
	"label-fgcolor": "keyword1",
	"label-font": "keyword1",
	"label-pfcolor": "keyword1",
	"labels": "keyword1",
	"landscape": "keyword1",
	"languages": "keyword1",
	"large": "keyword1",
	"large-to-small": "keyword1",
	"last": "keyword1",
	"last-async-request": "keyword1",
	"last-child": "keyword1",
	"last-event": "keyword1",
	"last-key": "keyword1",
	"last-of": "keyword1",
	"last-procedure": "keyword1",
	"last-server": "keyword1",
	"last-server-socket": "keyword1",
	"last-socket": "keyword1",
	"last-tab-item": "keyword1",
	"lastkey": "keyword1",
	"layout-variable": "comment2",
	"lc": "keyword1",
	"ldbname": "keyword1",
	"le": "keyword1",
	"leading": "keyword1",
	"leave": "keyword3",
	"left": "keyword1",
	"left-aligned": "keyword1",
	"left-end": "keyword1",
	"left-trim": "keyword1",
	"length": "keyword1",
	"library": "keyword1",
	"like": "keyword1",
	"line": "keyword1",
	"line-counter": "keyword1",
	"line-down": "keyword1",
	"line-left": "keyword1",
	"line-number": "comment2",
	"line-right": "keyword1",
	"line-up": "keyword1",
	"list-1": "comment2",
	"list-2": "comment2",
	"list-3": "comment2",
	"list-4": "comment2",
	"list-5": "comment2",
	"list-6": "comment2",
	"list-events": "keyword1",
	"list-item-pairs": "keyword1",
	"list-items": "keyword1",
	"list-query-attrs": "keyword1",
	"list-set-attrs": "keyword1",
	"list-widgets": "keyword1",
	"listing": "keyword1",
	"listings": "keyword1",
	"literal": "keyword1",
	"literal-question": "keyword1",
	"little-endian": "keyword1",
	"load": "keyword1",
	"load-control": "keyword1",
	"load-from": "keyword1",
	"load-icon": "keyword1",
	"load-image": "keyword1",
	"load-image-down": "keyword1",
	"load-image-insensitive": "keyword1",
	"load-image-up": "keyword1",
	"load-mouse-pointer": "keyword1",
	"load-picture": "keyword1",
	"load-small-icon": "keyword1",
	"lob-dir": "keyword1",
	"local-host": "keyword1",
	"local-name": "keyword1",
	"local-port": "keyword1",
	"locator-column-number": "keyword1",
	"locator-line-number": "keyword1",
	"locator-public-id": "keyword1",
	"locator-system-id": "keyword1",
	"locator-type": "keyword1",
	"locked": "keyword1",
	"log": "keyword1",
	"log-entry-types": "keyword1",
	"log-id": "keyword1",
	"log-manager": "keyword1",
	"log-threshold": "keyword1",
	"logfile-name": "keyword1",
	"logging-level": "keyword1",
	"logical": "keyword1",
	"long": "keyword1",
	"longchar": "keyword1",
	"longchar-to-node-value": "keyword1",
	"lookahead": "keyword1",
	"lookup": "keyword1",
	"lower": "keyword1",
	"lt": "keyword1",
	"machine-class": "keyword1",
	"main-menu": "keyword1",
	"mandatory": "keyword1",
	"manual-highlight": "keyword1",
	"map": "keyword1",
	"margin-extra": "keyword1",
	"margin-height": "keyword1",
	"margin-height-chars": "keyword1",
	"margin-height-pixels": "keyword1",
	"margin-width": "keyword1",
	"margin-width-chars": "keyword1",
	"margin-width-pixels": "keyword1",
	"matches": "keyword1",
	"max": "keyword1",
	"max-button": "keyword1",
	"max-chars": "keyword1",
	"max-data-guess": "keyword1",
	"max-height": "keyword1",
	"max-height-chars": "keyword1",
	"max-height-pixels": "keyword1",
	"max-rows": "keyword1",
	"max-size": "keyword1",
	"max-value": "keyword1",
	"max-width": "keyword1",
	"max-width-chars": "keyword1",
	"max-width-pixels": "keyword1",
	"maximize": "keyword1",
	"maximum": "keyword1",
	"md5-value": "keyword1",
	"member": "keyword1",
	"memptr": "keyword1",
	"memptr-to-node-value": "keyword1",
	"menu": "keyword1",
	"menu-bar": "keyword1",
	"menu-drop": "keyword3",
	"menu-item": "keyword1",
	"menu-key": "keyword1",
	"menu-mouse": "keyword1",
	"menubar": "keyword1",
	"merge-changes": "keyword1",
	"merge-row-changes": "keyword1",
	"message": "comment2",
	"message-area": "keyword1",
	"message-area-font": "keyword1",
	"message-line": "keyword1",
	"message-lines": "keyword1",
	"min-button": "keyword1",
	"min-column-width-chars": "keyword1",
	"min-column-width-pixels": "keyword1",
	"min-height": "keyword1",
	"min-height-chars": "keyword1",
	"min-height-pixels": "keyword1",
	"min-row-height": "keyword1",
	"min-row-height-chars": "keyword1",
	"min-row-height-pixels": "keyword1",
	"min-schema-marshall": "keyword1",
	"min-size": "keyword1",
	"min-value": "keyword1",
	"min-width": "keyword1",
	"min-width-chars": "keyword1",
	"min-width-pixels": "keyword1",
	"minimum": "keyword1",
	"mod": "keyword1",
	"modified": "keyword1",
	"modulo": "keyword1",
	"month": "keyword1",
	"mouse": "keyword1",
	"mouse-pointer": "keyword1",
	"movable": "keyword1",
	"move": "keyword1",
	"move-after-tab-item": "keyword1",
	"move-before-tab-item": "keyword1",
	"move-column": "keyword1",
	"move-to-bottom": "keyword1",
	"move-to-eof": "keyword1",
	"move-to-top": "keyword1",
	"mpe": "keyword1",
	"mtime": "keyword1",
	"multiple": "keyword1",
	"multiple-key": "keyword1",
	"multitasking-interval": "keyword1",
	"must-exist": "keyword1",
	"must-understand": "keyword1",
	"name": "keyword1",
	"namespace-prefix": "keyword1",
	"namespace-uri": "keyword1",
	"native": "keyword1",
	"ne": "keyword1",
	"needs-appserver-prompt": "keyword1",
	"needs-prompt": "keyword1",
	"nested": "keyword1",
	"new": "comment2",
	"new-line": "keyword1",
	"new-row": "keyword1",
	"next": "keyword1",
	"next-column": "keyword1",
	"next-error": "keyword1",
	"next-frame": "keyword1",
	"next-prompt": "keyword1",
	"next-sibling": "keyword1",
	"next-tab-item": "keyword1",
	"next-value": "keyword1",
	"next-word": "keyword1",
	"no": "keyword1",
	"no-apply": "keyword1",
	"no-array-message": "keyword1",
	"no-assign": "keyword1",
	"no-attr": "keyword1",
	"no-attr-list": "keyword1",
	"no-attr-space": "keyword1",
	"no-auto-validate": "keyword1",
	"no-bind-where": "keyword1",
	"no-box": "keyword1",
	"no-column-scrolling": "keyword1",
	"no-console": "keyword1",
	"no-convert": "keyword1",
	"no-convert-3d-colors": "keyword1",
	"no-current-value": "keyword1",
	"no-debug": "keyword1",
	"no-drag": "keyword1",
	"no-echo": "keyword1",
	"no-empty-space": "keyword1",
	"no-error": "keyword1",
	"no-fill": "keyword1",
	"no-focus": "keyword1",
	"no-help": "keyword1",
	"no-hide": "keyword1",
	"no-index-hint": "keyword1",
	"no-join-by-sqldb": "keyword1",
	"no-label": "keyword1",
	"no-labels": "keyword1",
	"no-lobs": "keyword1",
	"no-lock": "keyword1",
	"no-lookahead": "keyword1",
	"no-map": "keyword1",
	"no-message": "keyword1",
	"no-pause": "keyword1",
	"no-prefetch": "keyword1",
	"no-return-value": "keyword1",
	"no-row-markers": "keyword1",
	"no-schema-marshall": "keyword1",
	"no-scrollbar-vertical": "keyword1",
	"no-scrolling": "keyword1",
	"no-separate-connection": "keyword1",
	"no-separators": "keyword1",
	"no-tab-stop": "keyword1",
	"no-underline": "keyword1",
	"no-undo": "keyword1",
	"no-validate": "keyword1",
	"no-wait": "keyword1",
	"no-word-wrap": "keyword1",
	"node-type": "keyword1",
	"node-value": "keyword1",
	"node-value-to-longchar": "keyword1",
	"node-value-to-memptr": "keyword1",
	"none": "keyword1",
	"normalize": "keyword1",
	"not": "keyword1",
	"now": "keyword1",
	"null": "keyword1",
	"num-aliases": "keyword1",
	"num-buffers": "keyword1",
	"num-buttons": "keyword1",
	"num-child-relations": "keyword1",
	"num-children": "keyword1",
	"num-columns": "keyword1",
	"num-copies": "keyword1",
	"num-dbs": "keyword1",
	"num-dropped-files": "keyword1",
	"num-entries": "keyword1",
	"num-fields": "keyword1",
	"num-formats": "keyword1",
	"num-header-entries": "keyword1",
	"num-items": "keyword1",
	"num-iterations": "keyword1",
	"num-lines": "keyword1",
	"num-locked-columns": "keyword1",
	"num-log-files": "keyword1",
	"num-messages": "keyword1",
	"num-parameters": "keyword1",
	"num-relations": "keyword1",
	"num-replaced": "keyword1",
	"num-results": "keyword1",
	"num-selected": "keyword1",
	"num-selected-rows": "keyword1",
	"num-selected-widgets": "keyword1",
	"num-source-buffers": "keyword1",
	"num-tabs": "keyword1",
	"num-to-retain": "keyword1",
	"num-top-buffers": "keyword1",
	"num-visible-columns": "keyword1",
	"numeric": "keyword1",
	"numeric-decimal-point": "keyword1",
	"numeric-format": "keyword1",
	"numeric-separator": "keyword1",
	"object": "keyword1",
	"octet_length": "keyword1",
	"of": "keyword1",
	"off": "keyword1",
	"off-end": "keyword3",
	"off-home": "keyword3",
	"ok": "keyword1",
	"ok-cancel": "keyword1",
	"old": "keyword1",
	"ole-invoke-locale": "keyword1",
	"ole-names-locale": "keyword1",
	"on": "keyword1",
	"on-frame-border": "keyword1",
	"open": "keyword1",
	"open-browsers-in-query": "comment2",
	"open-line-above": "keyword1",
	"open-query": "comment2",
	"opsys": "comment2",
	"option": "keyword1",
	"options": "keyword1",
	"or": "keyword1",
	"ordered-join": "keyword1",
	"ordinal": "keyword1",
	"orientation": "keyword1",
	"origin-handle": "keyword1",
	"origin-rowid": "keyword1",
	"os-append": "keyword1",
	"os-command": "keyword1",
	"os-copy": "keyword1",
	"os-create-dir": "keyword1",
	"os-delete": "keyword1",
	"os-dir": "keyword1",
	"os-drives": "keyword1",
	"os-error": "keyword1",
	"os-getenv": "keyword1",
	"os-rename": "keyword1",
	"os2": "invalid",
	"os400": "invalid",
	"otherwise": "keyword1",
	"out-of-data": "keyword1",
	"outer": "keyword1",
	"outer-join": "keyword1",
	"output": "keyword1",
	"overlay": "keyword1",
	"override": "keyword1",
	"owner": "keyword1",
	"owner-document": "keyword1",
	"page": "keyword1",
	"page-bottom": "keyword1",
	"page-down": "keyword1",
	"page-left": "keyword1",
	"page-number": "keyword1",
	"page-right": "keyword1",
	"page-right-text": "keyword1",
	"page-size": "keyword1",
	"page-top": "keyword1",
	"page-up": "keyword1",
	"page-width": "keyword1",
	"paged": "keyword1",
	"parameter": "keyword1",
	"parent": "keyword1",
	"parent-buffer": "keyword1",
	"parent-relation": "keyword1",
	"parent-window-close": "keyword3",
	"parse-status": "keyword1",
	"partial-key": "keyword1",
	"pascal": "keyword1",
	"password-field": "keyword1",
	"paste": "keyword1",
	"pathname": "keyword1",
	"pause": "keyword1",
	"pdbname": "keyword1",
	"performance": "keyword1",
	"persistent": "keyword1",
	"persistent-cache-disabled": "keyword1",
	"persistent-procedure": "keyword1",
	"pfcolor": "keyword1",
	"pick": "keyword1",
	"pick-area": "keyword1",
	"pick-both": "keyword1",
	"pixels": "keyword1",
	"pixels-per-column": "keyword1",
	"pixels-per-row": "keyword1",
	"popup-menu": "keyword1",
	"popup-only": "keyword1",
	"portrait": "keyword1",
	"position": "keyword1",
	"precision": "keyword1",
	"prepare-string": "keyword1",
	"prepared": "keyword1",
	"preprocess": "keyword1",
	"preselect": "keyword1",
	"prev": "keyword1",
	"prev-column": "keyword1",
	"prev-frame": "keyword1",
	"prev-sibling": "keyword1",
	"prev-tab-item": "keyword1",
	"prev-word": "keyword1",
	"prim": "keyword1",
	"primary": "keyword1",
	"printer": "keyword1",
	"printer-control-handle": "keyword1",
	"printer-hdc": "keyword1",
	"printer-name": "keyword1",
	"printer-port": "keyword1",
	"printer-setup": "keyword1",
	"private": "keyword1",
	"private-data": "keyword1",
	"privileges": "keyword1",
	"proc-handle": "keyword1",
	"proc-status": "keyword1",
	"procedure": "keyword1",
	"procedure-call-type": "keyword1",
	"procedure-complete": "keyword3",
	"procedure-name": "keyword1",
	"procedure-type": "comment2",
	"process": "keyword1",
	"profile-file": "keyword1",
	"profiler": "keyword1",
	"profiling": "keyword1",
	"program-name": "keyword1",
	"progress": "keyword1",
	"progress-source": "keyword1",
	"prompt": "keyword1",
	"prompt-for": "invalid",
	"promsgs": "keyword1",
	"propath": "keyword1",
	"proversion": "keyword1",
	"proxy": "keyword1",
	"proxy-password": "keyword1",
	"proxy-userid": "keyword1",
	"public-id": "keyword1",
	"publish": "keyword1",
	"published-events": "keyword1",
	"put": "keyword1",
	"put-bits": "keyword1",
	"put-byte": "keyword1",
	"put-bytes": "keyword1",
	"put-double": "keyword1",
	"put-float": "keyword1",
	"put-key-value": "keyword1",
	"put-long": "keyword1",
	"put-short": "keyword1",
	"put-string": "keyword1",
	"put-unsigned-short": "keyword1",
	"putbyte": "keyword1",
	"query": "keyword1",
	"query-close": "keyword1",
	"query-name": "comment2",
	"query-off-end": "keyword1",
	"query-open": "keyword1",
	"query-prepare": "keyword1",
	"query-tuning": "keyword1",
	"question": "keyword1",
	"quit": "keyword1",
	"quoter": "keyword1",
	"r-index": "keyword1",
	"radio-buttons": "keyword1",
	"radio-set": "keyword1",
	"random": "keyword1",
	"raw": "keyword1",
	"raw-transfer": "keyword1",
	"rcode-info": "keyword1",
	"rcode-information": "keyword1",
	"read": "keyword1",
	"read-available": "keyword1",
	"read-exact-num": "keyword1",
	"read-file": "keyword1",
	"read-only": "keyword1",
	"read-response": "keyword3",
	"readkey": "invalid",
	"real": "keyword1",
	"recall": "keyword3",
	"recid": "keyword1",
	"record-length": "keyword1",
	"rectangle": "keyword1",
	"recursive": "keyword1",
	"refresh": "keyword1",
	"refreshable": "keyword1",
	"reject-changes": "keyword1",
	"reject-row-changes": "keyword1",
	"rejected": "keyword1",
	"relation-fields": "keyword1",
	"relations-active": "keyword1",
	"release": "keyword1",
	"remote": "keyword1",
	"remote-host": "keyword1",
	"remote-port": "keyword1",
	"remove-attribute": "keyword1",
	"remove-child": "keyword1",
	"remove-events-procedure": "keyword1",
	"remove-super-procedure": "keyword1",
	"repeat": "keyword1",
	"replace": "keyword1",
	"replace-child": "keyword1",
	"replace-selection-text": "keyword1",
	"replication-create": "keyword1",
	"replication-delete": "keyword1",
	"replication-write": "keyword1",
	"reports": "keyword1",
	"reposition": "keyword1",
	"reposition-backwards": "keyword1",
	"reposition-forwards": "keyword1",
	"reposition-mode": "invalid",
	"reposition-parent-relation": "keyword1",
	"reposition-to-row": "keyword1",
	"reposition-to-rowid": "keyword1",
	"request": "keyword1",
	"resizable": "keyword1",
	"resize": "keyword1",
	"result": "keyword1",
	"resume-display": "keyword1",
	"retain": "keyword1",
	"retain-shape": "keyword1",
	"retry": "keyword1",
	"retry-cancel": "keyword1",
	"return": "keyword3",
	"return-inserted": "keyword1",
	"return-to-start-dir": "keyword1",
	"return-value": "keyword1",
	"return-value-data-type": "keyword1",
	"returns": "keyword1",
	"reverse-from": "keyword1",
	"revert": "keyword1",
	"revoke": "keyword1",
	"rgb-value": "keyword1",
	"right": "keyword1",
	"right-aligned": "keyword1",
	"right-end": "keyword1",
	"right-trim": "keyword1",
	"round": "keyword1",
	"row": "keyword1",
	"row-created": "keyword1",
	"row-deleted": "keyword1",
	"row-display": "keyword3",
	"row-entry": "keyword3",
	"row-height": "keyword1",
	"row-height-chars": "keyword1",
	"row-height-pixels": "keyword1",
	"row-leave": "keyword3",
	"row-markers": "keyword1",
	"row-modified": "keyword1",
	"row-of": "keyword1",
	"row-resizable": "keyword1",
	"row-state": "keyword1",
	"row-unmodified": "keyword1",
	"rowid": "keyword1",
	"rule": "keyword1",
	"rule-row": "keyword1",
	"rule-y": "keyword1",
	"run": "keyword1",
	"run-procedure": "keyword1",
	"save": "keyword1",
	"save-as": "keyword1",
	"save-file": "keyword1",
	"save-row-changes": "keyword1",
	"save-where-string": "keyword1",
	"sax-attributes": "keyword1",
	"sax-complete": "keyword1",
	"sax-parse": "keyword1",
	"sax-parse-first": "keyword1",
	"sax-parse-next": "keyword1",
	"sax-parser-error": "keyword1",
	"sax-reader": "keyword1",
	"sax-running": "keyword1",
	"sax-uninitialized": "keyword1",
	"sax-xml": "keyword1",
	"schema": "keyword1",
	"schema-change": "keyword1",
	"schema-path": "keyword1",
	"scop": "comment2",
	"scoped-define": "comment2",
	"screen": "keyword1",
	"screen-io": "keyword1",
	"screen-lines": "keyword1",
	"screen-value": "keyword1",
	"scroll": "invalid",
	"scroll-bars": "keyword1",
	"scroll-delta": "keyword1",
	"scroll-left": "keyword1",
	"scroll-mode": "keyword1",
	"scroll-notify": "keyword3",
	"scroll-offset": "keyword1",
	"scroll-right": "keyword1",
	"scroll-to-current-row": "keyword1",
	"scroll-to-item": "keyword1",
	"scroll-to-selected-row": "keyword1",
	"scrollable": "keyword1",
	"scrollbar-drag": "keyword1",
	"scrollbar-horizontal": "keyword1",
	"scrollbar-vertical": "keyword1",
	"scrolled-row-position": "keyword1",
	"scrolling": "keyword1",
	"sdbname": "keyword1",
	"search": "keyword1",
	"search-self": "keyword1",
	"search-target": "keyword1",
	"section": "keyword1",
	"seek": "keyword1",
	"select": "keyword3",
	"select-all": "keyword1",
	"select-extend": "keyword1",
	"select-focused-row": "keyword1",
	"select-next-row": "keyword1",
	"select-prev-row": "keyword1",
	"select-repositioned-row": "keyword1",
	"select-row": "keyword1",
	"selectable": "keyword1",
	"selected": "keyword1",
	"selected-items": "keyword1",
	"selection": "keyword3",
	"selection-end": "keyword1",
	"selection-extend": "keyword1",
	"selection-list": "keyword1",
	"selection-start": "keyword1",
	"selection-text": "keyword1",
	"self": "keyword1",
	"self-name": "comment2",
	"send": "keyword1",
	"sensitive": "keyword1",
	"separate-connection": "keyword1",
	"separator-fgcolor": "keyword1",
	"separators": "keyword1",
	"sequence": "comment2",
	"server": "keyword1",
	"server-connection-bound": "keyword1",
	"server-connection-bound-request": "keyword1",
	"server-connection-context": "keyword1",
	"server-connection-id": "keyword1",
	"server-operating-mode": "keyword1",
	"server-socket": "keyword1",
	"session": "keyword1",
	"session-end": "keyword1",
	"set": "keyword1",
	"set-actor": "keyword1",
	"set-attr-call-type": "keyword1",
	"set-attribute": "keyword1",
	"set-attribute-node": "keyword1",
	"set-blue-value": "keyword1",
	"set-break": "keyword1",
	"set-buffers": "keyword1",
	"set-byte-order": "keyword1",
	"set-callback-procedure": "keyword1",
	"set-cell-focus": "keyword1",
	"set-commit": "keyword1",
	"set-connect-procedure": "keyword1",
	"set-contents": "keyword1",
	"set-dynamic": "keyword1",
	"set-green-value": "keyword1",
	"set-input-source": "keyword1",
	"set-must-understand": "keyword1",
	"set-node": "keyword1",
	"set-numeric-format": "keyword1",
	"set-parameter": "keyword1",
	"set-pointer-value": "keyword1",
	"set-read-response-procedure": "keyword1",
	"set-red-value": "keyword1",
	"set-repositioned-row": "keyword1",
	"set-rgb-value": "keyword1",
	"set-rollback": "keyword1",
	"set-selection": "keyword1",
	"set-serialized": "keyword1",
	"set-size": "keyword1",
	"set-socket-option": "keyword1",
	"set-wait-state": "keyword1",
	"settings": "keyword1",
	"setuserid": "keyword1",
	"share": "keyword1",
	"share-lock": "invalid",
	"shared": "keyword1",
	"short": "keyword1",
	"show-in-taskbar": "keyword1",
	"show-stats": "keyword1",
	"side-label": "keyword1",
	"side-label-handle": "keyword1",
	"side-labels": "keyword1",
	"silent": "keyword1",
	"simple": "keyword1",
	"single": "keyword1",
	"size": "keyword1",
	"size-chars": "keyword1",
	"size-pixels": "keyword1",
	"skip": "keyword1",
	"skip-deleted-record": "keyword1",
	"skip-schema-check": "keyword1",
	"slider": "keyword1",
	"small-icon": "keyword1",
	"small-title": "keyword1",
	"smallint": "keyword1",
	"soap-fault": "keyword1",
	"soap-fault-actor": "keyword1",
	"soap-fault-code": "keyword1",
	"soap-fault-detail": "keyword1",
	"soap-fault-string": "keyword1",
	"soap-header": "keyword1",
	"soap-header-entryref": "keyword1",
	"socket": "keyword1",
	"some": "keyword1",
	"sort": "keyword1",
	"source": "keyword1",
	"source-procedure": "keyword1",
	"space": "keyword1",
	"sql": "keyword1",
	"sqrt": "keyword1",
	"start": "keyword1",
	"start-box-selection": "keyword3",
	"start-extend-box-selection": "keyword1",
	"start-move": "keyword3",
	"start-resize": "keyword3",
	"start-row-resize": "keyword1",
	"start-search": "keyword3",
	"starting": "keyword1",
	"startup-parameters": "keyword1",
	"status": "keyword1",
	"status-area": "keyword1",
	"status-area-font": "keyword1",
	"stdcall": "keyword1",
	"stop": "keyword1",
	"stop-display": "keyword1",
	"stop-parsing": "keyword1",
	"stopped": "keyword1",
	"stored-procedure": "keyword1",
	"stream": "keyword1",
	"stream-io": "keyword1",
	"stretch-to-fit": "keyword1",
	"string": "keyword1",
	"string-value": "keyword1",
	"string-xref": "keyword1",
	"sub-average": "keyword1",
	"sub-count": "keyword1",
	"sub-maximum": "keyword1",
	"sub-menu": "keyword1",
	"sub-menu-help": "keyword1",
	"sub-minimum": "keyword1",
	"sub-total": "keyword1",
	"subscribe": "keyword1",
	"substitute": "keyword1",
	"substr": "keyword1",
	"substring": "keyword1",
	"subtype": "keyword1",
	"sum": "keyword1",
	"summary": "keyword1",
	"super": "keyword1",
	"super-procedures": "keyword1",
	"suppress-namespace-processing": "keyword1",
	"suppress-warnings": "keyword1",
	"synchronize": "keyword1",
	"system-alert-boxes": "keyword1",
	"system-dialog": "keyword1",
	"system-help": "keyword1",
	"system-id": "keyword1",
	"tab": "keyword3",
	"tab-position": "keyword1",
	"tab-stop": "keyword1",
	"table": "keyword1",
	"table-crc-list": "keyword1",
	"table-handle": "keyword1",
	"table-list": "keyword1",
	"table-number": "keyword1",
	"tables-in-query": "comment2",
	"target": "keyword1",
	"target-procedure": "keyword1",
	"temp-directory": "keyword1",
	"temp-table": "keyword1",
	"temp-table-prepare": "keyword1",
	"term": "keyword1",
	"terminal": "keyword1",
	"terminate": "keyword1",
	"text": "keyword1",
	"text-cursor": "keyword1",
	"text-seg-growth": "keyword1",
	"text-selected": "keyword1",
	"then": "comment2",
	"this-procedure": "keyword1",
	"three-d": "keyword1",
	"through": "keyword1",
	"thru": "keyword1",
	"tic-marks": "keyword1",
	"time": "keyword1",
	"time-source": "keyword1",
	"timezone": "keyword1",
	"title": "keyword1",
	"title-bgcolor": "keyword1",
	"title-dcolor": "keyword1",
	"title-fgcolor": "keyword1",
	"title-font": "keyword1",
	"to": "keyword1",
	"to-rowid": "keyword1",
	"today": "keyword1",
	"toggle-box": "keyword1",
	"tooltip": "keyword1",
	"tooltips": "keyword1",
	"top": "keyword1",
	"top-column": "keyword1",
	"top-only": "keyword1",
	"topic": "keyword1",
	"total": "keyword1",
	"trace-filter": "keyword1",
	"tracing": "keyword1",
	"tracking-changes": "keyword1",
	"trailing": "keyword1",
	"trans": "keyword1",
	"trans-init-procedure": "keyword1",
	"transaction": "keyword1",
	"transaction-mode": "keyword1",
	"transparent": "keyword1",
	"trigger": "keyword1",
	"triggers": "keyword1",
	"trim": "keyword1",
	"true": "keyword1",
	"truncate": "keyword1",
	"ttcodepage": "keyword1",
	"type": "keyword1",
	"uib_is_running": "comment2",
	"unbuffered": "keyword1",
	"undefine": "comment2",
	"underline": "keyword1",
	"undo": "keyword1",
	"unformatted": "keyword1",
	"union": "keyword1",
	"unique": "keyword1",
	"unique-id": "keyword1",
	"unique-match": "keyword1",
	"unix": "invalid",
	"unix-end": "keyword1",
	"unless-hidden": "keyword1",
	"unload": "keyword1",
	"unsigned-short": "keyword1",
	"unsubscribe": "keyword1",
	"up": "keyword1",
	"update": "keyword1",
	"upper": "keyword1",
	"url": "keyword1",
	"url-decode": "keyword1",
	"url-encode": "keyword1",
	"url-password": "keyword1",
	"url-userid": "keyword1",
	"use": "keyword1",
	"use-dict-exps": "keyword1",
	"use-filename": "keyword1",
	"use-index": "invalid",
	"use-revvideo": "keyword1",
	"use-text": "keyword1",
	"use-underline": "keyword1",
	"user": "keyword1",
	"user-data": "keyword1",
	"userid": "keyword1",
	"using": "keyword1",
	"utc-offset": "keyword1",
	"v6display": "keyword1",
	"v6frame": "keyword1",
	"valid-event": "keyword1",
	"valid-handle": "keyword1",
	"validate": "invalid",
	"validate-expression": "keyword1",
	"validate-message": "keyword1",
	"validate-xml": "keyword1",
	"validation-enabled": "keyword1",
	"value": "keyword1",
	"value-changed": "keyword3",
	"values": "keyword1",
	"var": "keyword1",
	"variable": "keyword1",
	"verbose": "keyword1",
	"vertical": "keyword1",
	"view": "keyword1",
	"view-as": "keyword1",
	"view-first-column-on-reopen": "keyword1",
	"virtual-height": "keyword1",
	"virtual-height-chars": "keyword1",
	"virtual-height-pixels": "keyword1",
	"virtual-width": "keyword1",
	"virtual-width-chars": "keyword1",
	"virtual-width-pixels": "keyword1",
	"visible": "keyword1",
	"vms": "invalid",
	"wait": "keyword1",
	"wait-for": "keyword1",
	"warning": "keyword1",
	"web-context": "keyword1",
	"web-notify": "keyword1",
	"weekday": "keyword1",
	"when": "keyword1",
	"where": "keyword1",
	"where-string": "keyword1",
	"while": "keyword1",
	"widget": "keyword1",
	"widget-enter": "keyword1",
	"widget-handle": "keyword1",
	"widget-leave": "keyword1",
	"widget-pool": "keyword1",
	"width": "keyword1",
	"width-chars": "keyword1",
	"width-pixels": "keyword1",
	"window": "keyword1",
	"window-close": "keyword3",
	"window-delayed-minimize": "keyword1",
	"window-maximized": "keyword3",
	"window-minimized": "keyword3",
	"window-name": "comment2",
	"window-normal": "keyword1",
	"window-resized": "keyword3",
	"window-restored": "keyword3",
	"window-state": "keyword1",
	"window-system": "comment2",
	"with": "keyword1",
	"word-index": "keyword1",
	"word-wrap": "keyword1",
	"work-area-height-pixels": "keyword1",
	"work-area-width-pixels": "keyword1",
	"work-area-x": "keyword1",
	"work-area-y": "keyword1",
	"work-table": "keyword1",
	"workfile": "keyword1",
	"write": "keyword1",
	"write-data": "keyword1",
	"x": "keyword1",
	"x-document": "keyword1",
	"x-noderef": "keyword1",
	"x-of": "keyword1",
	"xcode": "keyword1",
	"xml-schema-path": "keyword1",
	"xml-suppress-namespace-processing": "keyword1",
	"xref": "keyword1",
	"y": "keyword1",
	"y-of": "keyword1",
	"year": "keyword1",
	"year-offset": "keyword1",
	"yes": "keyword1",
	"yes-no": "keyword1",
	"yes-no-cancel": "keyword1",
}

# Dictionary of keywords dictionaries for progress mode.
keywordsDictDict = {
	"progress_main": progress_main_keywords_dict,
}

# Rules for progress_main ruleset.

def progress_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def progress_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def progress_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def progress_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="{&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=",",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=".",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="?",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="@",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="^",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule16(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule17(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule18(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule19(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule20(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
        at_line_start=False, at_whitespace_end=True, at_word_start=False, exclude_match=True)

def progress_rule21(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":accelerator",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule22(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":accept-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule23(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":accept-row-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule24(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-buffer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule25(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-calc-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule26(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-columns-from",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule27(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-events-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule28(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-fields-from",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule29(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-first",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule30(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-index-field",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule31(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-last",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule32(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-like-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule33(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-like-field",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule34(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-like-index",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule35(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-new-field",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule36(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-new-index",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule37(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":add-super-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule38(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":adm-data",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule39(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":after-buffer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule40(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":after-rowid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule41(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":after-table",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule42(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":allow-column-searching",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule43(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":always-on-top",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule44(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":ambiguous",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule45(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":append-child",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule46(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":appl-alert-boxes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule47(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":apply-callback",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule48(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":appserver-info",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule49(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":appserver-password",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule50(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":appserver-userid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule51(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":async-request-count",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule52(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":async-request-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule53(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":asynchronous",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule54(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":attach-data-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule55(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":attr-space",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule56(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":attribute-names",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule57(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-completion",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule58(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-delete",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule59(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-delete-xml",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule60(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-end-key",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule61(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-go",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule62(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-indent",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule63(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-resize",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule64(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-return",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule65(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-validate",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule66(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":auto-zap",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule67(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":available",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule68(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":available-formats",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule69(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":background",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule70(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":base-ade",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule71(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":basic-logging",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule72(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":batch-mode",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule73(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":before-buffer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule74(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":before-rowid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule75(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":before-table",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule76(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":bgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule77(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":blank",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule78(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":block-iteration-display",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule79(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-bottom-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule80(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-bottom-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule81(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-left-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule82(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-left-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule83(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-right-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule84(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-right-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule85(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-top-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule86(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":border-top-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule87(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":box",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule88(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":box-selectable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule89(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":browse-column-data-types",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule90(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":browse-column-formats",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule91(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":browse-column-labels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule92(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule93(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-compare",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule94(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-copy",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule95(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-create",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule96(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-delete",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule97(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-field",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule98(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule99(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-lines",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule100(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule101(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-release",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule102(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-validate",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule103(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":buffer-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule104(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":bytes-read",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule105(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":bytes-written",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule106(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cache",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule107(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":call-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule108(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":call-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule109(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":can-create",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule110(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":can-delete",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule111(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":can-read",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule112(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":can-write",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule113(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cancel-break",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule114(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cancel-button",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule115(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cancel-requests",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule116(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cancelled",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule117(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":careful-paint",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule118(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":case-sensitive",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule119(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":centered",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule120(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":character_length",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule121(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":charset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule122(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":checked",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule123(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":child-num",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule124(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":clear",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule125(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":clear-selection",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule126(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":client-connection-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule127(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":client-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule128(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":clone-node",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule129(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":code",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule130(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":codepage",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule131(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-bgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule132(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-dcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule133(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-fgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule134(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-font",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule135(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-label",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule136(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-movable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule137(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-pfcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule138(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-read-only",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule139(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-resizable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule140(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":column-scrolling",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule141(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":columns",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule142(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":com-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule143(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":complete",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule144(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":config-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule145(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":connect",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule146(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":connected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule147(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":context-help",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule148(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":context-help-file",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule149(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":context-help-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule150(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":control-box",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule151(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":convert-3d-colors",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule152(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":convert-to-offset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule153(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":coverage",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule154(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cpcase",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule155(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cpcoll",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule156(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cplog",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule157(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cpprint",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule158(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cprcodein",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule159(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cprcodeout",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule160(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cpstream",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule161(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cpterm",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule162(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":crc-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule163(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":create-like",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule164(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":create-node",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule165(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":create-node-namespace",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule166(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":create-on-add",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule167(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":create-result-list-entry",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule168(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-changed",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule169(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule170(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-environment",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule171(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-iteration",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule172(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-result-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule173(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-row-modified",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule174(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":current-window",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule175(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cursor-char",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule176(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cursor-line",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule177(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":cursor-offset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule178(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":data-entry-return",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule179(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":data-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule180(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":data-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule181(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dataset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule182(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":date-format",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule183(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":db-references",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule184(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dbname",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule185(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule186(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dde-error",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule187(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dde-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule188(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dde-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule189(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dde-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule190(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dde-topic",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule191(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":deblank",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule192(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":debug",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule193(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":debug-alert",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule194(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":decimals",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule195(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":default",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule196(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":default-buffer-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule197(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":default-button",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule198(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":default-commit",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule199(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":default-string",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule200(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule201(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete-current-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule202(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete-line",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule203(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete-node",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule204(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete-result-list-entry",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule205(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete-selected-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule206(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delete-selected-rows",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule207(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":delimiter",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule208(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":description",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule209(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":deselect-focused-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule210(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":deselect-rows",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule211(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":deselect-selected-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule212(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":detach-data-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule213(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":directory",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule214(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":disable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule215(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":disable-auto-zap",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule216(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":disable-connections",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule217(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":disable-dump-triggers",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule218(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":disable-load-triggers",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule219(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":disconnect",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule220(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":display-message",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule221(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":display-timezone",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule222(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":display-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule223(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":down",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule224(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":drag-enabled",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule225(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":drop-target",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule226(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dump-logging-now",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule227(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":dynamic",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule228(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edge-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule229(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edge-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule230(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-can-paste",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule231(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-can-undo",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule232(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-clear",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule233(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-copy",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule234(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-cut",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule235(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-paste",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule236(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":edit-undo",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule237(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":empty",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule238(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":empty-temp-table",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule239(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":enable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule240(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":enable-connections",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule241(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":enabled",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule242(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":encoding",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule243(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":end-file-drop",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule244(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":end-user-prompt",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule245(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":error-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule246(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":error-object-detail",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule247(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":error-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule248(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":error-string",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule249(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":event-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule250(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":event-procedure-context",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule251(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":event-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule252(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":exclusive-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule253(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":execution-log",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule254(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":expand",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule255(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":expandable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule256(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":export",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule257(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":extent",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule258(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":fetch-selected-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule259(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":fgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule260(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-create-date",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule261(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-create-time",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule262(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-mod-date",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule263(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-mod-time",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule264(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule265(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-offset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule266(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-size",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule267(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":file-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule268(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":fill",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule269(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":fill-mode",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule270(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":filled",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule271(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":find-by-rowid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule272(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":find-current",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule273(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":find-first",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule274(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":find-last",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule275(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":find-unique",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule276(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-async-request",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule277(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-buffer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule278(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-child",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule279(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule280(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-data-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule281(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-dataset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule282(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule283(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-query",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule284(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-server",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule285(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-server-socket",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule286(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-socket",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule287(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":first-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule288(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":fit-last-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule289(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":flat-button",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule290(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":focused-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule291(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":focused-row-selected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule292(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":font",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule293(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":font-based-layout",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule294(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":foreground",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule295(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":form-input",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule296(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":format",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule297(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":forward-only",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule298(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule299(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame-col",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule300(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule301(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule302(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame-spacing",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule303(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame-x",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule304(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frame-y",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule305(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":frequency",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule306(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":full-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule307(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":full-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule308(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":full-pathname",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule309(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":full-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule310(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":full-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule311(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":function",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule312(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-attribute",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule313(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-attribute-node",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule314(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-blue-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule315(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-browse-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule316(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-buffer-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule317(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-bytes-available",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule318(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-cgi-list",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule319(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-cgi-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule320(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule321(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-child",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule322(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-child-relation",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule323(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-config-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule324(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-current",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule325(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-document-element",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule326(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-dropped-file",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule327(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-dynamic",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule328(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-first",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule329(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-green-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule330(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-iteration",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule331(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-last",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule332(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-message",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule333(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-next",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule334(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-number",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule335(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-parent",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule336(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-prev",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule337(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-printers",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule338(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-red-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule339(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-repositioned-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule340(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-rgb-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule341(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-selected-widget",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule342(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-signature",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule343(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-socket-option",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule344(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule345(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-text-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule346(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-text-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule347(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-text-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule348(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-text-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule349(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":get-wait-state",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule350(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":graphic-edge",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule351(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-factor-horizontal",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule352(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-factor-vertical",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule353(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-snap",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule354(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-unit-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule355(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-unit-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule356(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-unit-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule357(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-unit-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule358(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":grid-visible",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule359(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule360(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":handler",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule361(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":has-lobs",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule362(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":has-records",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule363(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule364(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule365(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":hidden",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule366(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":horizontal",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule367(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-charset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule368(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-end-of-line",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule369(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-end-of-page",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule370(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-frame-begin",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule371(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-frame-end",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule372(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-header-begin",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule373(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-header-end",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule374(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-title-begin",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule375(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":html-title-end",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule376(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":hwnd",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule377(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":icfparameter",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule378(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":icon",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule379(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":image",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule380(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":image-down",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule381(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":image-insensitive",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule382(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":image-up",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule383(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":immediate-display",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule384(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":import-node",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule385(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":in-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule386(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":increment-exclusive-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule387(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":index",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule388(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":index-information",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule389(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":initial",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule390(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":initialize-document-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule391(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":initiate",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule392(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":inner-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule393(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":inner-lines",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule394(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":input-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule395(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule396(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert-backtab",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule397(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert-before",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule398(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert-file",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule399(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule400(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert-string",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule401(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":insert-tab",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule402(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":instantiating-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule403(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":internal-entries",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule404(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":invoke",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule405(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":is-open",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule406(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":is-parameter-set",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule407(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":is-row-selected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule408(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":is-selected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule409(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":is-xml",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule410(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":items-per-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule411(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":keep-connection-open",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule412(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":keep-frame-z-order",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule413(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":keep-security-cache",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule414(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":key",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule415(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":label",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule416(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":label-bgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule417(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":label-dcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule418(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":label-fgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule419(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":label-font",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule420(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":labels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule421(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":languages",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule422(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":large",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule423(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":large-to-small",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule424(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-async-request",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule425(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-child",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule426(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule427(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-server",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule428(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-server-socket",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule429(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-socket",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule430(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":last-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule431(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":line",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule432(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":list-item-pairs",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule433(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":list-items",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule434(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":listings",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule435(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":literal-question",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule436(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule437(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-icon",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule438(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-image",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule439(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-image-down",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule440(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-image-insensitive",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule441(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-image-up",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule442(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-mouse-pointer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule443(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":load-small-icon",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule444(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":local-host",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule445(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":local-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule446(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":local-port",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule447(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":locator-column-number",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule448(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":locator-line-number",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule449(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":locator-public-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule450(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":locator-system-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule451(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":locator-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule452(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":locked",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule453(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":log-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule454(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":longchar-to-node-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule455(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":lookup",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule456(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":mandatory",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule457(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":manual-highlight",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule458(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":margin-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule459(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":margin-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule460(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":margin-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule461(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":margin-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule462(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-button",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule463(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule464(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-data-guess",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule465(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule466(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule467(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule468(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule469(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":max-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule470(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":md5-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule471(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":memptr-to-node-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule472(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":menu-bar",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule473(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":menu-key",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule474(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":menu-mouse",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule475(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":merge-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule476(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":merge-row-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule477(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":message-area",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule478(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":message-area-font",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule479(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-button",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule480(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-column-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule481(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-column-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule482(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule483(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule484(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-schema-marshall",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule485(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule486(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule487(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":min-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule488(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":modified",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule489(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":mouse-pointer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule490(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":movable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule491(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":move-after-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule492(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":move-before-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule493(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":move-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule494(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":move-to-bottom",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule495(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":move-to-eof",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule496(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":move-to-top",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule497(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":multiple",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule498(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":multitasking-interval",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule499(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule500(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":namespace-prefix",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule501(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":namespace-uri",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule502(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":needs-appserver-prompt",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule503(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":needs-prompt",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule504(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":new",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule505(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":new-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule506(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":next-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule507(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":next-sibling",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule508(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":next-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule509(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":no-current-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule510(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":no-empty-space",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule511(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":no-focus",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule512(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":no-schema-marshall",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule513(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":no-validate",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule514(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":node-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule515(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":node-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule516(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":node-value-to-longchar",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule517(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":node-value-to-memptr",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule518(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":normalize",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule519(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-buffers",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule520(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-buttons",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule521(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-child-relations",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule522(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-children",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule523(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-columns",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule524(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-dropped-files",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule525(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-entries",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule526(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-fields",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule527(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-formats",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule528(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-items",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule529(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-iterations",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule530(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-lines",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule531(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-locked-columns",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule532(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-messages",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule533(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-parameters",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule534(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-replaced",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule535(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-results",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule536(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-selected-rows",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule537(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-selected-widgets",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule538(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-tabs",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule539(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-to-retain",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule540(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":num-visible-columns",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule541(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":numeric-decimal-point",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule542(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":numeric-format",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule543(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":numeric-separator",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule544(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":ole-invoke-locale",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule545(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":ole-names-locale",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule546(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":on-frame-border",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule547(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":origin-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule548(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":origin-rowid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule549(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":overlay",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule550(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":owner",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule551(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":owner-document",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule552(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":page-bottom",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule553(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":page-top",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule554(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":parameter",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule555(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":parent",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule556(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":parent-relation",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule557(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":parse-status",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule558(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":password-field",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule559(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":pathname",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule560(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":persistent",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule561(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":persistent-cache-disabled",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule562(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":persistent-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule563(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":pfcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule564(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":pixels-per-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule565(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":pixels-per-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule566(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":popup-menu",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule567(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":popup-only",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule568(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":position",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule569(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":prepare-string",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule570(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":prepared",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule571(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":prev-column",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule572(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":prev-sibling",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule573(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":prev-tab-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule574(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":primary",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule575(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":printer-control-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule576(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":printer-hdc",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule577(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":printer-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule578(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":printer-port",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule579(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":private-data",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule580(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":procedure-name",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule581(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":profiling",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule582(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":progress-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule583(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":proxy",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule584(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":proxy-password",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule585(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":proxy-userid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule586(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":public-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule587(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":published-events",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule588(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":query",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule589(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":query-close",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule590(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":query-off-end",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule591(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":query-open",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule592(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":query-prepare",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule593(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":quit",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule594(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":radio-buttons",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule595(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":raw-transfer",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule596(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":read",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule597(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":read-file",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule598(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":read-only",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule599(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":recid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule600(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":record-length",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule601(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":refresh",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule602(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":refreshable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule603(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reject-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule604(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reject-row-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule605(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":rejected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule606(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remote",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule607(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remote-host",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule608(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remote-port",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule609(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remove-attribute",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule610(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remove-child",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule611(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remove-events-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule612(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":remove-super-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule613(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":replace",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule614(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":replace-child",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule615(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":replace-selection-text",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule616(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reposition-backwards",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule617(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reposition-forwards",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule618(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reposition-parent-relation",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule619(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reposition-to-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule620(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":reposition-to-rowid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule621(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":resizable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule622(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":resize",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule623(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":retain-shape",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule624(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":return-inserted",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule625(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":return-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule626(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":return-value-data-type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule627(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule628(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":row-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule629(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":row-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule630(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":row-markers",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule631(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":row-resizable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule632(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":row-state",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule633(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":rowid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule634(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":rule-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule635(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":rule-y",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule636(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":save",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule637(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":save-file",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule638(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":save-row-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule639(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sax-parse",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule640(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sax-parse-first",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule641(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sax-parse-next",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule642(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sax-xml",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule643(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":schema-change",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule644(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":schema-path",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule645(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":screen-lines",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule646(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":screen-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule647(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scroll-bars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule648(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scroll-delta",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule649(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scroll-offset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule650(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scroll-to-current-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule651(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scroll-to-item",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule652(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scroll-to-selected-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule653(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scrollable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule654(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scrollbar-horizontal",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule655(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":scrollbar-vertical",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule656(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":search",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule657(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":select-all",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule658(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":select-focused-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule659(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":select-next-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule660(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":select-prev-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule661(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":select-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule662(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":selectable",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule663(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":selected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule664(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":selection-end",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule665(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":selection-start",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule666(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":selection-text",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule667(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sensitive",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule668(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":separator-fgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule669(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":separators",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule670(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":server",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule671(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":server-connection-bound",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule672(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":server-connection-bound-request",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule673(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":server-connection-context",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule674(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":server-connection-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule675(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":server-operating-mode",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule676(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":session-end",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule677(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-attribute",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule678(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-attribute-node",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule679(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-blue-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule680(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-break",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule681(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-buffers",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule682(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-callback-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule683(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-commit",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule684(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-connect-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule685(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-dynamic",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule686(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-green-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule687(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-input-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule688(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-numeric-format",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule689(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-parameter",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule690(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-read-response-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule691(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-red-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule692(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-repositioned-row",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule693(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-rgb-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule694(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-rollback",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule695(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-selection",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule696(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-socket-option",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule697(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":set-wait-state",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule698(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":show-in-taskbar",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule699(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":side-label-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule700(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":side-labels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule701(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":skip-deleted-record",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule702(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":small-icon",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule703(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":small-title",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule704(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sort",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule705(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":startup-parameters",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule706(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":status-area",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule707(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":status-area-font",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule708(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":stop",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule709(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":stop-parsing",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule710(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":stopped",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule711(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":stretch-to-fit",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule712(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":string-value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule713(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":sub-menu-help",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule714(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":subtype",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule715(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":super-procedures",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule716(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":suppress-namespace-processing",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule717(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":suppress-warnings",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule718(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":synchronize",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule719(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":system-alert-boxes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule720(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":system-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule721(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tab-position",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule722(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tab-stop",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule723(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":table",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule724(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":table-crc-list",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule725(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":table-handle",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule726(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":table-list",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule727(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":table-number",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule728(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":temp-directory",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule729(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":temp-table-prepare",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule730(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":text-selected",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule731(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":three-d",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule732(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tic-marks",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule733(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":time-source",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule734(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":title",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule735(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":title-bgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule736(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":title-dcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule737(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":title-fgcolor",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule738(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":title-font",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule739(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":toggle-box",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule740(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tooltip",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule741(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tooltips",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule742(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":top-only",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule743(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":trace-filter",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule744(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tracing",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule745(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":tracking-changes",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule746(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":trans-init-procedure",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule747(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":transaction",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule748(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":transparent",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule749(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":type",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule750(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":undo",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule751(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":unique-id",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule752(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":unique-match",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule753(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":url",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule754(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":url-decode",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule755(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":url-encode",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule756(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":url-password",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule757(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":url-userid",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule758(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":user-data",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule759(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":v6display",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule760(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":validate",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule761(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":validate-expression",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule762(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":validate-message",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule763(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":validate-xml",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule764(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":validation-enabled",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule765(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":value",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule766(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":view-first-column-on-reopen",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule767(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":virtual-height-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule768(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":virtual-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule769(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":virtual-width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule770(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":virtual-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule771(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":visible",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule772(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":warning",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule773(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":widget-enter",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule774(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":widget-leave",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule775(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":width-chars",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule776(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule777(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":window",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule778(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":window-state",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule779(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":window-system",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule780(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":word-wrap",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule781(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":work-area-height-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule782(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":work-area-width-pixels",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule783(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":work-area-x",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule784(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":work-area-y",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule785(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":write",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule786(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":write-data",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule787(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":x",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule788(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":x-document",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule789(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":xml-schema-path",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule790(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":xml-suppress-namespace-processing",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule791(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":y",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule792(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":year-offset",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule793(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":_dcm",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule794(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="invalid", regexp="put\\s+screen",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule795(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="invalid", pattern=":WHERE-STRING",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule796(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="invalid", pattern=":REPOSITION-PARENT-RELATION",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def progress_rule797(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword3", regexp="choose\\s+of",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def progress_rule798(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for progress_main ruleset.
rulesDict1 = {
	"\"": [progress_rule2,],
	"&": [progress_rule798,],
	"'": [progress_rule1,],
	"(": [progress_rule15,],
	")": [progress_rule16,],
	"*": [progress_rule4,],
	"+": [progress_rule5,],
	",": [progress_rule6,],
	"-": [progress_rule798,],
	".": [progress_rule7,],
	"/": [progress_rule0,progress_rule8,],
	"0": [progress_rule798,],
	"1": [progress_rule798,],
	"2": [progress_rule798,],
	"3": [progress_rule798,],
	"4": [progress_rule798,],
	"5": [progress_rule798,],
	"6": [progress_rule798,],
	"7": [progress_rule798,],
	"8": [progress_rule798,],
	"9": [progress_rule798,],
	":": [progress_rule20,progress_rule21,progress_rule22,progress_rule23,progress_rule24,progress_rule25,progress_rule26,progress_rule27,progress_rule28,progress_rule29,progress_rule30,progress_rule31,progress_rule32,progress_rule33,progress_rule34,progress_rule35,progress_rule36,progress_rule37,progress_rule38,progress_rule39,progress_rule40,progress_rule41,progress_rule42,progress_rule43,progress_rule44,progress_rule45,progress_rule46,progress_rule47,progress_rule48,progress_rule49,progress_rule50,progress_rule51,progress_rule52,progress_rule53,progress_rule54,progress_rule55,progress_rule56,progress_rule57,progress_rule58,progress_rule59,progress_rule60,progress_rule61,progress_rule62,progress_rule63,progress_rule64,progress_rule65,progress_rule66,progress_rule67,progress_rule68,progress_rule69,progress_rule70,progress_rule71,progress_rule72,progress_rule73,progress_rule74,progress_rule75,progress_rule76,progress_rule77,progress_rule78,progress_rule79,progress_rule80,progress_rule81,progress_rule82,progress_rule83,progress_rule84,progress_rule85,progress_rule86,progress_rule87,progress_rule88,progress_rule89,progress_rule90,progress_rule91,progress_rule92,progress_rule93,progress_rule94,progress_rule95,progress_rule96,progress_rule97,progress_rule98,progress_rule99,progress_rule100,progress_rule101,progress_rule102,progress_rule103,progress_rule104,progress_rule105,progress_rule106,progress_rule107,progress_rule108,progress_rule109,progress_rule110,progress_rule111,progress_rule112,progress_rule113,progress_rule114,progress_rule115,progress_rule116,progress_rule117,progress_rule118,progress_rule119,progress_rule120,progress_rule121,progress_rule122,progress_rule123,progress_rule124,progress_rule125,progress_rule126,progress_rule127,progress_rule128,progress_rule129,progress_rule130,progress_rule131,progress_rule132,progress_rule133,progress_rule134,progress_rule135,progress_rule136,progress_rule137,progress_rule138,progress_rule139,progress_rule140,progress_rule141,progress_rule142,progress_rule143,progress_rule144,progress_rule145,progress_rule146,progress_rule147,progress_rule148,progress_rule149,progress_rule150,progress_rule151,progress_rule152,progress_rule153,progress_rule154,progress_rule155,progress_rule156,progress_rule157,progress_rule158,progress_rule159,progress_rule160,progress_rule161,progress_rule162,progress_rule163,progress_rule164,progress_rule165,progress_rule166,progress_rule167,progress_rule168,progress_rule169,progress_rule170,progress_rule171,progress_rule172,progress_rule173,progress_rule174,progress_rule175,progress_rule176,progress_rule177,progress_rule178,progress_rule179,progress_rule180,progress_rule181,progress_rule182,progress_rule183,progress_rule184,progress_rule185,progress_rule186,progress_rule187,progress_rule188,progress_rule189,progress_rule190,progress_rule191,progress_rule192,progress_rule193,progress_rule194,progress_rule195,progress_rule196,progress_rule197,progress_rule198,progress_rule199,progress_rule200,progress_rule201,progress_rule202,progress_rule203,progress_rule204,progress_rule205,progress_rule206,progress_rule207,progress_rule208,progress_rule209,progress_rule210,progress_rule211,progress_rule212,progress_rule213,progress_rule214,progress_rule215,progress_rule216,progress_rule217,progress_rule218,progress_rule219,progress_rule220,progress_rule221,progress_rule222,progress_rule223,progress_rule224,progress_rule225,progress_rule226,progress_rule227,progress_rule228,progress_rule229,progress_rule230,progress_rule231,progress_rule232,progress_rule233,progress_rule234,progress_rule235,progress_rule236,progress_rule237,progress_rule238,progress_rule239,progress_rule240,progress_rule241,progress_rule242,progress_rule243,progress_rule244,progress_rule245,progress_rule246,progress_rule247,progress_rule248,progress_rule249,progress_rule250,progress_rule251,progress_rule252,progress_rule253,progress_rule254,progress_rule255,progress_rule256,progress_rule257,progress_rule258,progress_rule259,progress_rule260,progress_rule261,progress_rule262,progress_rule263,progress_rule264,progress_rule265,progress_rule266,progress_rule267,progress_rule268,progress_rule269,progress_rule270,progress_rule271,progress_rule272,progress_rule273,progress_rule274,progress_rule275,progress_rule276,progress_rule277,progress_rule278,progress_rule279,progress_rule280,progress_rule281,progress_rule282,progress_rule283,progress_rule284,progress_rule285,progress_rule286,progress_rule287,progress_rule288,progress_rule289,progress_rule290,progress_rule291,progress_rule292,progress_rule293,progress_rule294,progress_rule295,progress_rule296,progress_rule297,progress_rule298,progress_rule299,progress_rule300,progress_rule301,progress_rule302,progress_rule303,progress_rule304,progress_rule305,progress_rule306,progress_rule307,progress_rule308,progress_rule309,progress_rule310,progress_rule311,progress_rule312,progress_rule313,progress_rule314,progress_rule315,progress_rule316,progress_rule317,progress_rule318,progress_rule319,progress_rule320,progress_rule321,progress_rule322,progress_rule323,progress_rule324,progress_rule325,progress_rule326,progress_rule327,progress_rule328,progress_rule329,progress_rule330,progress_rule331,progress_rule332,progress_rule333,progress_rule334,progress_rule335,progress_rule336,progress_rule337,progress_rule338,progress_rule339,progress_rule340,progress_rule341,progress_rule342,progress_rule343,progress_rule344,progress_rule345,progress_rule346,progress_rule347,progress_rule348,progress_rule349,progress_rule350,progress_rule351,progress_rule352,progress_rule353,progress_rule354,progress_rule355,progress_rule356,progress_rule357,progress_rule358,progress_rule359,progress_rule360,progress_rule361,progress_rule362,progress_rule363,progress_rule364,progress_rule365,progress_rule366,progress_rule367,progress_rule368,progress_rule369,progress_rule370,progress_rule371,progress_rule372,progress_rule373,progress_rule374,progress_rule375,progress_rule376,progress_rule377,progress_rule378,progress_rule379,progress_rule380,progress_rule381,progress_rule382,progress_rule383,progress_rule384,progress_rule385,progress_rule386,progress_rule387,progress_rule388,progress_rule389,progress_rule390,progress_rule391,progress_rule392,progress_rule393,progress_rule394,progress_rule395,progress_rule396,progress_rule397,progress_rule398,progress_rule399,progress_rule400,progress_rule401,progress_rule402,progress_rule403,progress_rule404,progress_rule405,progress_rule406,progress_rule407,progress_rule408,progress_rule409,progress_rule410,progress_rule411,progress_rule412,progress_rule413,progress_rule414,progress_rule415,progress_rule416,progress_rule417,progress_rule418,progress_rule419,progress_rule420,progress_rule421,progress_rule422,progress_rule423,progress_rule424,progress_rule425,progress_rule426,progress_rule427,progress_rule428,progress_rule429,progress_rule430,progress_rule431,progress_rule432,progress_rule433,progress_rule434,progress_rule435,progress_rule436,progress_rule437,progress_rule438,progress_rule439,progress_rule440,progress_rule441,progress_rule442,progress_rule443,progress_rule444,progress_rule445,progress_rule446,progress_rule447,progress_rule448,progress_rule449,progress_rule450,progress_rule451,progress_rule452,progress_rule453,progress_rule454,progress_rule455,progress_rule456,progress_rule457,progress_rule458,progress_rule459,progress_rule460,progress_rule461,progress_rule462,progress_rule463,progress_rule464,progress_rule465,progress_rule466,progress_rule467,progress_rule468,progress_rule469,progress_rule470,progress_rule471,progress_rule472,progress_rule473,progress_rule474,progress_rule475,progress_rule476,progress_rule477,progress_rule478,progress_rule479,progress_rule480,progress_rule481,progress_rule482,progress_rule483,progress_rule484,progress_rule485,progress_rule486,progress_rule487,progress_rule488,progress_rule489,progress_rule490,progress_rule491,progress_rule492,progress_rule493,progress_rule494,progress_rule495,progress_rule496,progress_rule497,progress_rule498,progress_rule499,progress_rule500,progress_rule501,progress_rule502,progress_rule503,progress_rule504,progress_rule505,progress_rule506,progress_rule507,progress_rule508,progress_rule509,progress_rule510,progress_rule511,progress_rule512,progress_rule513,progress_rule514,progress_rule515,progress_rule516,progress_rule517,progress_rule518,progress_rule519,progress_rule520,progress_rule521,progress_rule522,progress_rule523,progress_rule524,progress_rule525,progress_rule526,progress_rule527,progress_rule528,progress_rule529,progress_rule530,progress_rule531,progress_rule532,progress_rule533,progress_rule534,progress_rule535,progress_rule536,progress_rule537,progress_rule538,progress_rule539,progress_rule540,progress_rule541,progress_rule542,progress_rule543,progress_rule544,progress_rule545,progress_rule546,progress_rule547,progress_rule548,progress_rule549,progress_rule550,progress_rule551,progress_rule552,progress_rule553,progress_rule554,progress_rule555,progress_rule556,progress_rule557,progress_rule558,progress_rule559,progress_rule560,progress_rule561,progress_rule562,progress_rule563,progress_rule564,progress_rule565,progress_rule566,progress_rule567,progress_rule568,progress_rule569,progress_rule570,progress_rule571,progress_rule572,progress_rule573,progress_rule574,progress_rule575,progress_rule576,progress_rule577,progress_rule578,progress_rule579,progress_rule580,progress_rule581,progress_rule582,progress_rule583,progress_rule584,progress_rule585,progress_rule586,progress_rule587,progress_rule588,progress_rule589,progress_rule590,progress_rule591,progress_rule592,progress_rule593,progress_rule594,progress_rule595,progress_rule596,progress_rule597,progress_rule598,progress_rule599,progress_rule600,progress_rule601,progress_rule602,progress_rule603,progress_rule604,progress_rule605,progress_rule606,progress_rule607,progress_rule608,progress_rule609,progress_rule610,progress_rule611,progress_rule612,progress_rule613,progress_rule614,progress_rule615,progress_rule616,progress_rule617,progress_rule618,progress_rule619,progress_rule620,progress_rule621,progress_rule622,progress_rule623,progress_rule624,progress_rule625,progress_rule626,progress_rule627,progress_rule628,progress_rule629,progress_rule630,progress_rule631,progress_rule632,progress_rule633,progress_rule634,progress_rule635,progress_rule636,progress_rule637,progress_rule638,progress_rule639,progress_rule640,progress_rule641,progress_rule642,progress_rule643,progress_rule644,progress_rule645,progress_rule646,progress_rule647,progress_rule648,progress_rule649,progress_rule650,progress_rule651,progress_rule652,progress_rule653,progress_rule654,progress_rule655,progress_rule656,progress_rule657,progress_rule658,progress_rule659,progress_rule660,progress_rule661,progress_rule662,progress_rule663,progress_rule664,progress_rule665,progress_rule666,progress_rule667,progress_rule668,progress_rule669,progress_rule670,progress_rule671,progress_rule672,progress_rule673,progress_rule674,progress_rule675,progress_rule676,progress_rule677,progress_rule678,progress_rule679,progress_rule680,progress_rule681,progress_rule682,progress_rule683,progress_rule684,progress_rule685,progress_rule686,progress_rule687,progress_rule688,progress_rule689,progress_rule690,progress_rule691,progress_rule692,progress_rule693,progress_rule694,progress_rule695,progress_rule696,progress_rule697,progress_rule698,progress_rule699,progress_rule700,progress_rule701,progress_rule702,progress_rule703,progress_rule704,progress_rule705,progress_rule706,progress_rule707,progress_rule708,progress_rule709,progress_rule710,progress_rule711,progress_rule712,progress_rule713,progress_rule714,progress_rule715,progress_rule716,progress_rule717,progress_rule718,progress_rule719,progress_rule720,progress_rule721,progress_rule722,progress_rule723,progress_rule724,progress_rule725,progress_rule726,progress_rule727,progress_rule728,progress_rule729,progress_rule730,progress_rule731,progress_rule732,progress_rule733,progress_rule734,progress_rule735,progress_rule736,progress_rule737,progress_rule738,progress_rule739,progress_rule740,progress_rule741,progress_rule742,progress_rule743,progress_rule744,progress_rule745,progress_rule746,progress_rule747,progress_rule748,progress_rule749,progress_rule750,progress_rule751,progress_rule752,progress_rule753,progress_rule754,progress_rule755,progress_rule756,progress_rule757,progress_rule758,progress_rule759,progress_rule760,progress_rule761,progress_rule762,progress_rule763,progress_rule764,progress_rule765,progress_rule766,progress_rule767,progress_rule768,progress_rule769,progress_rule770,progress_rule771,progress_rule772,progress_rule773,progress_rule774,progress_rule775,progress_rule776,progress_rule777,progress_rule778,progress_rule779,progress_rule780,progress_rule781,progress_rule782,progress_rule783,progress_rule784,progress_rule785,progress_rule786,progress_rule787,progress_rule788,progress_rule789,progress_rule790,progress_rule791,progress_rule792,progress_rule793,progress_rule795,progress_rule796,],
	"<": [progress_rule18,progress_rule19,],
	"=": [progress_rule9,],
	">": [progress_rule17,],
	"?": [progress_rule10,],
	"@": [progress_rule11,progress_rule798,],
	"A": [progress_rule798,],
	"B": [progress_rule798,],
	"C": [progress_rule798,],
	"D": [progress_rule798,],
	"E": [progress_rule798,],
	"F": [progress_rule798,],
	"G": [progress_rule798,],
	"H": [progress_rule798,],
	"I": [progress_rule798,],
	"J": [progress_rule798,],
	"K": [progress_rule798,],
	"L": [progress_rule798,],
	"M": [progress_rule798,],
	"N": [progress_rule798,],
	"O": [progress_rule798,],
	"P": [progress_rule798,],
	"Q": [progress_rule798,],
	"R": [progress_rule798,],
	"S": [progress_rule798,],
	"T": [progress_rule798,],
	"U": [progress_rule798,],
	"V": [progress_rule798,],
	"W": [progress_rule798,],
	"X": [progress_rule798,],
	"Y": [progress_rule798,],
	"Z": [progress_rule798,],
	"[": [progress_rule12,],
	"]": [progress_rule13,],
	"^": [progress_rule14,],
	"_": [progress_rule798,],
	"a": [progress_rule798,],
	"b": [progress_rule798,],
	"c": [progress_rule797,progress_rule798,],
	"d": [progress_rule798,],
	"e": [progress_rule798,],
	"f": [progress_rule798,],
	"g": [progress_rule798,],
	"h": [progress_rule798,],
	"i": [progress_rule798,],
	"j": [progress_rule798,],
	"k": [progress_rule798,],
	"l": [progress_rule798,],
	"m": [progress_rule798,],
	"n": [progress_rule798,],
	"o": [progress_rule798,],
	"p": [progress_rule794,progress_rule798,],
	"q": [progress_rule798,],
	"r": [progress_rule798,],
	"s": [progress_rule798,],
	"t": [progress_rule798,],
	"u": [progress_rule798,],
	"v": [progress_rule798,],
	"w": [progress_rule798,],
	"x": [progress_rule798,],
	"y": [progress_rule798,],
	"z": [progress_rule798,],
	"{": [progress_rule3,],
}

# x.rulesDictDict for progress mode.
rulesDictDict = {
	"progress_main": rulesDict1,
}

# Import dict for progress mode.
importDict = {}

