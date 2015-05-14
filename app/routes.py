# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, make_response, request, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import datetime
  
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:root@localhost:3306/sinfo_db?charset=utf8'
db = SQLAlchemy(app) 

months_map = { '1' : "Jan", '2' : "Feb", '3' : "Mar", '4' : "Apr", '5' : "May", '6' : "Jun", '7' : "Jul", '8' : "Aug", '9' : "Sep", '10' : "Oct" , '11' : "Nov", '12' : "Dec" }

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

def get_commits_user():
	commits = []
	commits_by_month = []
	for month in get_months_ordered():
		sql = text("select count(*) from commits where developer='"+user+"' and MONTH(date)="+str(month))
		result = db.engine.execute(sql)
		n = str(result.fetchone()[0])
		commits_by_month.append(int(n))

	commits.append({ 'data' : commits_by_month, 'name' : str(user) })

	return commits

def get_frequent_changed_files_user():
	files_frequency = []
	sql = text("select file, count(*) from modifications m inner join commits c on m.id_commit = c.id "
				+ "where c.developer = '"+user+"' group by file order by count(*) desc limit 10;")
	result = db.engine.execute(sql)
	for row in result:
		files_frequency.append({ 'file' : row["file"], 'frequency' : row["count(*)"] })
	return files_frequency

def get_frequent_changed_files():
	files_frequency = []
	sql = text("select file, count(*) from modifications group by file order by count(*) desc limit 50;")
	result = db.engine.execute(sql)
	for row in result:
		files_frequency.append({ 'file' : row["file"], 'frequency' : row["count(*)"] })
	return files_frequency

def get_file_type_percentages(files_frequency):
	file_type_percentage_dict = dict()
	file_type_percentage = []

	total_items_dict = 0

	for file_frequency in files_frequency:

		path = file_frequency["file"]

		if "MBean.java" in path:
			total_items_dict += 1
			if "MBean" in file_type_percentage_dict:
				file_type_percentage_dict["MBean"] += 1
			else:
				file_type_percentage_dict["MBean"] = 1
		elif "Dao.java" in path:
			total_items_dict += 1
			if "Dao" in file_type_percentage_dict:
				file_type_percentage_dict["Dao"] += 1
			else:
				file_type_percentage_dict["Dao"] = 1
		elif "Validator.java" in path:
			total_items_dict += 1
			if "Validator" in file_type_percentage_dict:
				file_type_percentage_dict["Validator"] += 1
			else:
				file_type_percentage_dict["Validator"] = 1

	total = len(files_frequency)
	for i in file_type_percentage_dict:
		file_type_percentage_dict[i] = "{0:.2f}".format((file_type_percentage_dict[i]/float(total))*100)

	file_type_percentage_dict["Other"] = "{0:.2f}".format(((total - total_items_dict)/float(total))*100)

	#turn dict into list
	for key, value in file_type_percentage_dict.iteritems():
		temp = [key,float(value)]
		file_type_percentage.append(temp)

	return file_type_percentage  

#TEMPLATE FILES
@app.route('/')
def show_team_commits():
	sql = text('select developer, count(*) from commits group by developer order by count(*) desc limit 10;')
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

		#print author
		#print commits_by_month
	months_categories = get_months_categories()
	files_frequency = get_frequent_changed_files()
	file_type_percentage = get_file_type_percentages(files_frequency)
	return render_template('index.html', commits=commits, months_categories=months_categories, files_frequency=files_frequency, file_type_percentage=file_type_percentage)

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