from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/gotoemployee")
def gotoemployee():
    return render_template('HomeEmp.html')

@app.route("/gotoaddemployee")
def gotoaddemployee():
    return render_template('AddEmp.html')

@app.route("/gotosearchemployee")
def gotosearchemployee():
    return render_template('GetEmp.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.png"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("GetEmp.html")

@app.route("/toEditemp", methods=['GET', 'POST'])
def ToEditEmp():
    return render_template("EditEmp.html")

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    sqlCmd = "SELECT * FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    if emp_id == "":
        return "Please enter an employee ID"

    try:
        #Getting Employee Data
        cursor.execute(sqlCmd, (emp_id))
        row = cursor.fetchone()
        dEmpID = row[0]
        dFirstName = row[1]
        dLastName = row[2]
        dPriSkill = row[3]
        dLocation = row[4]

        key = "emp-id-" + str(emp_id) + "_image_file.png"

        # Get Image URL
        # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        # s3_location = (bucket_location['LocationConstraint'])

        url = "https://%s.s3.amazonaws.com/%s" % (custombucket, key)

    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()

    return render_template("GetEmpOutput.html", id=dEmpID, fname=dFirstName, 
    lname=dLastName, interest=dPriSkill, location=dLocation, image_url=url)

@app.route("/delemp", methods=['POST'])
def DelEmp():
    # Get Employee
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    selectCmd = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    deleteCmd = "DELETE FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()
    cursor1 = db_conn.cursor()
    key = "emp-id-" + str(emp_id) + "_image_file.png"
    s3 = boto3.client('s3')

    try:
        cursor.execute(selectCmd, {'emp_id': int(emp_id)})
        cursor1.execute(deleteCmd, {'emp_id': int(emp_id)})
        # FETCH ONLY ONE ROWS OUTPUT
        row = cursor.fetchone()
        dFirstName = row[1]
        dLastName = row[2]
        emp_name = "" + dFirstName + " " + dLastName
        db_conn.commit()

        s3.delete_object(Bucket=custombucket, Key=key)
    except Exception as e:
        db_conn.rollback()
        return str(e)

    finally:
        cursor.close()
        cursor1.close()

    return render_template('DeleteEmpOutput.html', name=emp_name)

@app.route("/fetchdataToEdit", methods=['GET', 'POST'])
def FetchDataToEdit():
    emp_id = request.form['emp_id']
    sqlCmd = "SELECT * FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    if emp_id == "":
        return "Please enter an employee ID"

    try:
        #Getting Employee Data
        cursor.execute(sqlCmd, (emp_id))
        row = cursor.fetchone()
        dEmpID = row[0]
        dFirstName = row[1]
        dLastName = row[2]
        dPriSkill = row[3]
        dLocation = row[4]

        key = "emp-id-" + str(emp_id) + "_image_file.png"

        # Get Image URL
        # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        # s3_location = (bucket_location['LocationConstraint'])

        url = "https://%s.s3.amazonaws.com/%s" % (custombucket, key)

    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()

    return render_template("EditEmp.html", id=dEmpID, fname=dFirstName, 
    lname=dLastName, interest=dPriSkill, location=dLocation, image_url=url)

@app.route("/editemp", methods=['POST'])
def EditEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    edit_sql = "UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s, location=%s WHERE emp_id=%s"
    cursor = db_conn.cursor()
    
    if emp_image_file.filename == "":
        key = "emp-id-" + str(emp_id) + "_image_file.png"
        url = "https://%s.s3.amazonaws.com/%s" % (custombucket, key)

    try:
        cursor.execute(edit_sql, (first_name, last_name, pri_skill, location, emp_id))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.png"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('EditEmpOutput.html', name=emp_name, id=emp_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
