#!/usr/bin/env python
#coding=utf8

from flask import Flask,render_template,request,redirect,url_for,session,flash
from models import TaskLogs,Models,User,createWorkOrder,makeMd5
from . import app ,db
from development import cntl_q,data_q
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    totlelogs=TaskLogs.query.count()
    todaylogs=TaskLogs.query.filter(db.func.to_days(TaskLogs.logtime)==db.func.to_days(db.func.now()))
    todaylogscount=todaylogs.count()
    todaylogslist=todaylogs.all()
    return render_template("index.html",totlelogs=totlelogs,todaylogscount=todaylogscount,todaylogslist=todaylogslist)

@app.route(("/view/"))
@app.route("/view/<workOrder>")
def viewWorkOrder(workOrder=None):
    if workOrder==None:
        logList=None
    else:
        logList=TaskLogs.query.filter_by(id=workOrder).first()
    return render_template("show-wordorder.html",logList=logList)

@app.route("/add/",methods=['GET', 'POST'])
@app.route("/add/<deployType>",methods=['GET', 'POST'])
def add(deployType="ALL"):
    workOrder=createWorkOrder()
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method=="GET":
        if deployType=="ALL":
            modelMap=Models.query.order_by(Models.model_id.desc()).all()
        else:
            modelMap=Models.query.filter_by(deploy_type=deployType).order_by(Models.mode_pet.desc()).all()
        return render_template("add.html",deployType=deployType,workorder=workOrder,modelmap=modelMap)
    elif request.method=="POST":
        print deployType
        modelPet=request.form["models"]
        versionNumber=request.form["version_number"]
        sql_list=Models.query.filter_by(mode_pet=modelPet).first()
        modelName=sql_list.mode_name
        typeName=sql_list.type_name
        remote_path=sql_list.remote_path
        git_url=sql_list.git_url
        cntl_q.put({'event':'data'})
        data_q.put({'workOrder':workOrder,'typename':typeName,'modelname':modelName,'versionnumber':versionNumber,'remote_path':remote_path,'git_url':git_url[7:],"user_account":session["user_account"],"deployType":deployType})
        flash('发布任务添加成功！！')
        return redirect(url_for("viewWorkOrder",workOrder=workOrder))


@app.route("/login/",methods=["GET","POST"])
def login():
    error=None
    if request.method=="GET":
        return render_template("login.html")
    elif request.method=="POST":
        username=request.form["username"]
        password=makeMd5(request.form["password"])
        kk=User.query.filter_by(user_account=username).first()
        if kk==None:
            error="用户不存在"
        elif kk.user_password!=password:
            error="用户密码不正确"
        else:
            session['logged_in'] = True
            session["username"]=kk.nick_name
            session["user_account"]=kk.user_account
            flash('hi,%s 你已经登录成功。'%session["username"])
            return redirect(url_for('add'))
        return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('baibai,%s,欢迎下次使用。'%session["username"])
    return redirect(url_for("add"))

@app.route("/regedit/",methods=["GET","POST"])
def regedit():
    if request.method=="GET":
        return render_template("regedit.html")
    elif request.method=="POST":
        nickname=request.form["firstname"]
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        user=User(user_account=username,user_password=password,email=email,nick_name=nickname)
        print user
        db.session.add(user)
        db.session.commit()
        #session["logged_in"]=True
        flash("用户注册成功,请登录。")
        return redirect(url_for("login"))

@app.route("/statis/")
def statis():
    thisweekmodel=db.session.query(TaskLogs.deploytype,TaskLogs.models,db.func.count(TaskLogs.models).label("count")).filter(db.func.yearweek(db.func.date_format(TaskLogs.logtime,"%Y-%m-%d"))==db.func.yearweek(db.func.now()),TaskLogs.status=="SUCCESS").group_by(TaskLogs.deploytype,TaskLogs.models)
    thisweektotal=thisweekmodel.count()
    thisweeklist=thisweekmodel.all()

    lastweekmodel=db.session.query(TaskLogs.deploytype,TaskLogs.models,db.func.count(TaskLogs.models).label("count")).filter(db.func.yearweek(db.func.date_format(TaskLogs.logtime,"%Y-%m-%d"))==db.func.yearweek(db.func.now())-1,TaskLogs.status=="SUCCESS").group_by(TaskLogs.deploytype,TaskLogs.models)
    lastweektotal=lastweekmodel.count()
    lastweeklist=lastweekmodel.all()
    #stmt=db.session.query(TaskLogs.deploytype.label("deploytype"),TaskLogs.models.label("models"),db.func.max(TaskLogs.logtime).label("logtime")).group_by(TaskLogs.deploytype,TaskLogs.models).subquery()
    #current_version=db.session.query(TaskLogs.deploytype,TaskLogs.family,TaskLogs.models,TaskLogs.version,TaskLogs.logtime).join(stmt,TaskLogs.deploytype==stmt.deploytype,TaskLogs.models==stmt.models,TaskLogs.logtime==stmt.logtime).filter(TaskLogs.status=="SUCCESS").order_by(TaskLogs.logtime).all()
    current_version=db.session.execute("""SELECT A.deploytype,A.family,A.models,A.version,A.logtime FROM tasklog AS A INNER JOIN(
	SELECT deploytype as deploytype,models as models,MAX(logtime) AS logtime FROM tasklog GROUP BY deploytype,models
) as B
on A.deploytype=B.deploytype and A.models=B.models AND A.logtime=B.logtime
WHERE `status`='SUCCESS' ORDER BY logtime desc""")
    current_datetime=datetime.datetime.now()
    return render_template("statistics.html",thisweektotal=thisweektotal,thisweeklist=thisweeklist,lastweektotal=lastweektotal,lastweeklist=lastweeklist,current_datetime=current_datetime,current_version=current_version)


