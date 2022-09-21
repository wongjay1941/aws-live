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
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


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
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
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

        key = "emp-id-" + str(emp_id) + "_image_file"

        # s3 = boto3.resource('s3')
        # bkt = s3.bucket(custombucket)
        # for obj in bkt.objects.all():
        #     if(obj.key[8:9] == emp_id):
        #         image = obj.get()['Body'].read()
        #         break

        # s3_client = boto3.client('s3')
        # public_urls = []
        # try:
        #     for item in s3_client.list_objects(Bucket=bucket)['Contents']:
        #         presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
        #         public_urls.append(presigned_url)
        # except Exception as e:
        #     pass
        # # print("[INFO] : The contents inside show_image = ", public_urls)
        # return public_urls

        # Get Image URL
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])

        if s3_location is None:
            s3_location = ''
        else:
            s3_location = '-' + s3_location

        url = "https://%s.s3.amazonaws.com/%s" % (custombucket, key)

        
    finally:
        cursor.close()

    return render_template("GetEmpOutput.html", id=dEmpID, fname=dFirstName, 
    lname=dLastName, interest=dPriSkill, location=dLocation, image_url=url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
