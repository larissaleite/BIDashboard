# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, make_response, request, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import datetime
  
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:root@localhost:3306/sinfo_db?charset=utf8'
db = SQLAlchemy(app) 

months_map = { '1' : "Jan", '2' : "Feb", '3' : "Mar", '4' : "Apr", '5' : "May", '6' : "Jun", '7' : "Jul", '8' : "Aug", '9' : "Sep", '10' : "Oct" , '11' : "Nov", '12' : "Dec" }

task_type_map = { '1' : "New feature", '2' : "Enhancement", '3' : "Bug-fix" }

task_status_map = { '1' : "Open", '2' : "In progress", '3' : "Finished" }

system_map = { '1' : "SIGAA", '2' : "SIPAC", '3' : "SIGRH" }

day_of_week_map = { '1' : "Monday", '2' : "Tuesday", '3' : "Wednesday", '4' : "Thursday", '5' : "Friday", '6' : "Saturday", '7' : "Sunday" }

def get_all_users():
	sql = text('select distinct developer from commits;')
	result = db.engine.execute(sql)

	users = []

	for row in result:
		users.append(str(row["developer"]))
	return users

def get_months_ordered():
	months = []
	sql = text('select distinct MONTH(date) as month from commits;')
	result = db.engine.execute(sql)
	
	for row in result:
		months.append(int(row["month"]))
	return months

def get_months_categories():
	months = get_months_ordered()
	months_categories = []

	for month in months:
		month_name = months_map[str(month)]
		months_categories.append(month_name)
	return months_categories

def get_all_data():
	all_data = []
	sql = text('select * from commits_fact c inner join task_dim t on c.id_task = t.id_task inner join date_dim d on c.id_date = d.id_date inner join system_dim s on c.id_system = s.id_system inner join developer_dim a on c.id_developer = a.id_developer limit 25')
	result = db.engine.execute(sql)

	for row in result:
		all_data.append({ "system" : system_map[str(row["system"])], "developer" : row["developer"], 
			"added_files" : row["added_files"], "changed_files" : row["modified_files"], "deleted_files" : row["deleted_files"], 
			"date" : row["date"], "month" : months_map[str(row["month"]+1)], "day_of_week" : day_of_week_map[str(row["day_of_week"])], "task_type" : task_type_map[str(row["type"])] 
		})

	return all_data

#TEMPLATE FILES
@app.route('/')
def show_team_commits():
	sql = text('select developer, count(*) from commits group by developer order by count(*) desc;')
	result = db.engine.execute(sql)
	commits = []

	for row in result:
		author = str(row["developer"])
		commits_by_month = []

		for month in get_months_ordered():
			sql = text("select count(*) from commits where developer='"+author+"' and MONTH(date)="+str(month))
			result = db.engine.execute(sql)
			n = str(result.fetchone()[0])
			commits_by_month.append(int(n))
		commits.append({ 'data' : commits_by_month, 'name' : author })

	months_categories = get_months_categories()
	all_data = get_all_data()
	return render_template('index.html', commits=commits, months_categories=months_categories, all_data=all_data)

@app.route('/sigaa/commits')
def show_sigaa_commits():
	sql = text('select developer, count(*) from commits where system LIKE \'%SIGAA%\' group by developer order by count(*) desc;')
	result = db.engine.execute(sql)
	commits = []

	for row in result:
		author = str(row["developer"])
		commits_by_month = []

		for month in get_months_ordered():
			sql = text("select count(*) from commits where developer='"+author+"' and MONTH(date)="+str(month))
			result = db.engine.execute(sql)
			n = str(result.fetchone()[0])
			commits_by_month.append(int(n))
		commits.append({ 'data' : commits_by_month, 'name' : author })

	months_categories = get_months_categories()
	return render_template('sigaa.html', commits=commits, months_categories=months_categories)

@app.route('/sipac/commits')
def show_sipac_commits():
	sql = text('select developer, count(*) from commits where system LIKE \'%SIPAC%\' group by developer order by count(*) desc;')
	result = db.engine.execute(sql)
	commits = []

	for row in result:
		author = str(row["developer"])
		commits_by_month = []

		for month in get_months_ordered():
			sql = text("select count(*) from commits where developer='"+author+"' and MONTH(date)="+str(month))
			result = db.engine.execute(sql)
			n = str(result.fetchone()[0])
			commits_by_month.append(int(n))
		commits.append({ 'data' : commits_by_month, 'name' : author })

	months_categories = get_months_categories()
	return render_template('sipac.html', commits=commits, months_categories=months_categories)

@app.route('/sigrh/commits')
def show_sigrh_commits():
	sql = text('select developer, count(*) from commits where system LIKE \'%SIGRH%\' group by developer order by count(*) desc;')
	result = db.engine.execute(sql)
	commits = []

	for row in result:
		author = str(row["developer"])
		commits_by_month = []

		for month in get_months_ordered():
			sql = text("select count(*) from commits where developer='"+author+"' and MONTH(date)="+str(month))
			result = db.engine.execute(sql)
			n = str(result.fetchone()[0])
			commits_by_month.append(int(n))
		commits.append({ 'data' : commits_by_month, 'name' : author })

	months_categories = get_months_categories()
	return render_template('sigrh.html', commits=commits, months_categories=months_categories)

# REST API

@app.route('/api/commits', methods = ['GET'])
def get_all_commits():
	sql = text('select * from commits')
	result = db.engine.execute(sql)
	commits = []
	for row in result:
		commits.append({ 'author' : row["author"], 'date' : row["date"] })

	return commits
  
if __name__ == '__main__':
	app.secret_key = 'secret key'
	app.run(debug=True)