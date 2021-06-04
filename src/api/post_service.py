#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 07/05/2021

@author: diego.hahn
'''

import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import logging

import time
import requests
import os
import json
import glob

DB_API = 'http://ims1436:5000/api/v1/track'
DB_PATH = "C:/mnf-data"

def scandirs(path):
    files = []
    for currentFile in glob.glob( os.path.join(path, '*') ):
        if os.path.isdir(currentFile):
            files += scandirs(currentFile)
        else:
            files.append(currentFile)
    return files

class DBPostService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TrackStepsPostSvc"
    _svc_display_name_ = "TrackSteps Post Service"

    def __init__(self, args = None):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        self.Main()
        
    def Main(self):

        if not os.path.isdir(DB_PATH):
            os.makedirs(DB_PATH)

        while True:
            files = scandirs(DB_PATH)        
            for f in files:
                try:
                    success = False
                    with open(f) as fd:
                        jdb = json.load(fd)            
                        x = requests.post(DB_API, json = jdb)
                        if "success" in x.text:
                            success = True
    
                    if success :
                        os.unlink(f)
                except:
                    pass
            time.sleep(10.0)


if __name__ == "__main__": 
    win32serviceutil.HandleCommandLine(DBPostService)