#!/usr/bin/env python
#coding=utf8
#  use:for web deploy models
__author__ = 'vzer'


import datetime
import uuid
from xml.etree import ElementTree as ET
from .import db
import hashlib



class ServerInfo(db.Model):
    __tablename__='serverinfo'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    hostname=db.Column(db.String(50))
    ip=db.Column(db.String(50))
    account=db.Column(db.String(50))
    password=db.Column(db.String(50))
    servicename=db.Column(db.String(50))
    environment=db.Column(db.String(50))



class User(db.Model):
    __tablename__='user'
    id=db.Column(db.String(50),primary_key=True,unique=True)
    user_account=db.Column(db.String(50),unique=True)
    user_password=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    nick_name=db.Column(db.String(50))
    isactive=db.Column(db.Boolean,default=False)
    isadmin=db.Column(db.Boolean,default=False)
    createdate=db.Column(db.DateTime)

    def __init__(self,user_account,user_password,email,nick_name):
        self.id=createWorkOrder()
        self.user_account=user_account
        self.user_password=makeMd5(user_password)
        self.email=email
        self.nick_name=nick_name
        self.isactive=True
        self.isadmin=True
        self.createdate=db.func.now()

    def __repr__(self):
        return "<User '{:s}'> ".format(self.nick_name)

class Permission_Group(db.Model):
    __tablename__='permission_group'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    group_name=db.Column(db.String(50),unique=True)

class TaskLogs(db.Model):
    __tablename__='tasklog'
    id=db.Column(db.String(50),primary_key=True,unique=True)
    user_id=db.Column(db.String(50))
    deploytype=db.Column(db.String(50))
    family=db.Column(db.String(50))
    models=db.Column(db.String(50))
    version=db.Column(db.String(50))
    status=db.Column(db.String(50))
    failure_times=db.Column(db.Integer)
    logtime=db.Column(db.DateTime,default=datetime.datetime.now())
    context=db.Column(db.Text)

class DeployType(db.Model):
    __tablename__='deploytype'
    type_id=db.Column(db.String(50),primary_key=True,unique=True)
    type_name=db.Column(db.String(50),unique=True)

class Models(db.Model):
    __tablename__='models'
    model_id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    type_id=db.Column(db.String(50))
    deploy_type=db.Column(db.String(50))
    type_name=db.Column(db.String(50))
    mode_name=db.Column(db.String(50))
    mode_pet=db.Column(db.String(50),unique=True)
    remote_path=db.Column(db.String(50))
    git_url=db.Column(db.String(50))



######################################################################################################################
#订单生成器
def createWorkOrder():
    try:
        workOrder=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return uuid.uuid3(uuid.NAMESPACE_DNS,workOrder)
    except Exception,msg:
        print str(msg)
#######################################################################################################################
def resoveXml(xmlpath):
    tree=ET.parse(xmlpath)
    root=tree.getroot()
    for key in root:
        if key.tag=="{http://maven.apache.org/POM/4.0.0}version":
            return str(key.text)
#密码加密
def makeMd5(password):
    md=hashlib.md5()
    md.update(password)
    return md.hexdigest()

#时间处理
def dodatetime(date):
    print date.strftime("%Y-%m-%d")
    return date.strftime("%Y-%m-%d")
if __name__ == '__main__':
    db.create_all()