#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 01/06/2021

@author: diego.hahn
'''

import os
import json
import re
import time
import hashlib

__exe__ = "Post Steps"
__version__ = "1.0.0"

RE_PATTERN_IMS_QRCODE_LABEL = r'^IMS#\w+#(\w{4,5})-(\w{2})-(\w{4})-(\w{3})-(\w{1})-\w{1}#\w+#\w+#\w+$'
#RE_PATTERN_IMS_CONF = r'^(\w{4,5})-(\w{2})-(\w{4})-(\w{3})-(\w{1})-\w{1}$'
#RE_PATTERN_IMS_JSON

STEP = [u"MONTAGEM",u"PRÉ-CALIBRAÇÃO",u"CALIBRAÇÃO",u"PRÉ-ESTUFA",u"ESTUFA",u"PÓS-ESTUFA",u"RUNIN",u"FINALIZAÇÃO",u"FIM"]
DB_PATH = "C:/mnf-data"

if __name__ == "__main__":
    
    while True:
        try:
            while True:
                print "\r\n>> Informe a etapa: ".decode("utf-8"),
                step = int(raw_input())
                assert (step >= 0) and (step < len(STEP)), "Etapa inválida"            
              
                while True:                              
                    print "\r\n>> Leia o QRCode da IOP ou Etiqueta: ".decode("utf-8"),
                    conf = raw_input()    
                    #conf = "PQA7-60-5C6G-D3K-7-3"
                    # Valida o configurador
                    if conf == "0-EXIT-1":
                        break
                        
                    elif re.match(RE_PATTERN_IMS_QRCODE_LABEL, conf) :                
                        # IMS#00887766#PQA7-60-5C6G-D3K-7-3#IOP109234#20210601#220303      
                        qrcode = conf
                        _, ns, _, _, _, _ = qrcode.split("#")
                        
                        payload = { "serialNumber": int(ns),
                                    "step": STEP[step],
                                    "timestamp":int(time.time()) }
                                    
                        content = json.dumps(payload)
                        with open(os.path.join(DB_PATH,"%s.json" % hashlib.md5(content).hexdigest()), 'w') as out:
                            out.write(content)                                                           
                    
                    else:
                        # {"iop":"IOP128589","serialNumber":327422,"exec":7,"client":"Dama","equipment":"PowerNET PQA-700"}
                        # Tenta ler o padrão como um json
                        master = json.loads(conf)
                        for i in range(master["exec"]):
                            payload = { "serialNumber": int(master["serialNumber"])+i,
                                        "step": STEP[step],
                                        "timestamp":int(time.time()),
                                        "equipment": str(master["equipment"]),
                                        "client": str(master["client"]),
                                        "iop": str(master["iop"])}
                            content = json.dumps(payload)
                            with open(os.path.join(DB_PATH,"%s.json" % hashlib.md5(content).hexdigest()), 'w') as out:
                                out.write(content)

        except Exception, e:
            print "\r\n>> " + str(e).decode("windows-1252")
            raw_input()