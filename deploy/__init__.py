#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from flask import Flask
from flask_login import LoginManager
from development import Development
from flask.ext.sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config.from_object(Development)
db=SQLAlchemy(app)
from . import views
