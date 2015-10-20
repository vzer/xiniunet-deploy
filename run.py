#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from deploy import app
import multiprocessing as mp
import deploy.pack as pack
from  development import cntl_q,data_q
if __name__ == '__main__':
    #print app.config
    #p=mp.Process(target=pack.main,args=(cntl_q,data_q))
    #p.start()
    app.run(host="0.0.0.0",port=8080)