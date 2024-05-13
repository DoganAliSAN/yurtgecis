from flask import Flask, render_template, jsonify,redirect,url_for,request
import time
from box_rfid import rfid
import lcd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'  # Specify the table name explicitly
    OGRENCI_NO = db.Column(db.String)
    ADI_SOYADI = db.Column(db.String)
    SINIF_ADI = db.Column(db.String)
    rfid_id = db.Column(db.String,primary_key=True)
    check_time = db.Column(db.String(100))
    status = db.Column(db.Boolean)
    def toggle_status(self):
        self.status = not self.status
        db.session.commit()
    def change_check_time(self,check_time_new):
        self.check_time = check_time_new
        db.session.commit()
# Function to get student information
def get_student_info(rfid_id):
    students = Student.query.filter_by(rfid_id=rfid_id).all()
    if students:
        return [{
            'adi_soyadi': student.ADI_SOYADI,
            'ogrenci_no': student.OGRENCI_NO,
            'sinif_adi': student.SINIF_ADI,
            'rfid_id': student.rfid_id,
            'check_time': student.check_time,
            'status': student.status
        } for student in students]
    else:
        return {'error': 'No student found with the specified RFID ID'}


@app.route('/')
def index():
    # Retrieve all students from the database
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route("/ogrenciekle")
def ogrenciekle():
    return render_template("ogrenciekle.html")

@app.route("/inside")
def inside():
    students = Student.query.filter_by(status=True).all()
    return render_template('index.html', students= students)
@app.route("/outside")
def outside():
    students = Student.query.filter(or_(Student.status == False, Student.status == None)).all()

    return render_template('index.html', students= students)

@app.route('/add_new_student',methods=["POST"])
def add_new_student():
    name = request.args.get("name").upper()
    number = request.args.get("number")
    class_ = request.args.get("class").upper()
    card_id = request.args.get("card_id").lstrip('0')
    
    # Check if a student with the same RFID ID already exists
    existing_student = Student.query.filter_by(rfid_id=card_id).first()
    if existing_student:
        student_to_be_updated = Student.query.filter_by(rfid_id=card_id).first()
        student_to_be_updated.change_check_time(check_time)
        return "Student with this RFID ID already exists"


    try:
        # Create a new student object
        new_student = Student(ADI_SOYADI = name, SINIF_ADI=class_, OGRENCI_NO= number,rfid_id=card_id, check_time=datetime.datetime.now(), status=0)

        # Add the new student to the session
        db.session.add(new_student)
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('index'))  # Redirect to the homepage
    except Exception as e:
        # Handle any errors
        print(e)
        db.session.rollback()
        return "Error occurred while adding student"
@app.route('/add_student/<string:rfid_id>/<string:check_time>')
def add_student(rfid_id, check_time):
    # Check if a student with the same RFID ID already exists
    existing_student = Student.query.filter_by(rfid_id=rfid_id).first()
    if existing_student:
        student_to_be_updated = Student.query.filter_by(rfid_id=rfid_id).first()
        student_to_be_updated.change_check_time(check_time)
        return "Student with this RFID ID already exists"

    try:
        # Create a new student object
        new_student = Student(rfid_id=rfid_id, check_time=check_time, status=0)

        # Add the new student to the session
        db.session.add(new_student)
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('index'))  # Redirect to the homepage
    except Exception as e:
        # Handle any errors
        print(e)
        db.session.rollback()
        return "Error occurred while adding student"
@app.route('/student/<string:rfid_id>', methods=['GET'])
def student_info(rfid_id):
    student = get_student_info(rfid_id)
    return jsonify(student)
@app.route('/toggle_student/<string:rfid_id>', methods=['GET'])
def toggle_student_status_by_rfid(rfid_id):
    student = Student.query.filter_by(rfid_id=rfid_id).first()
    if student:
        student.toggle_status()
        return jsonify({'message': f"Status toggled for student with RFID ID {rfid_id}"})
    else:
        return jsonify({'error': 'Student not found with the specified RFID ID'})

@app.route('/remove_student/<string:rfid_id>')
def remove_student(rfid_id):
    # Check if the student exists
    student = Student.query.filter_by(rfid_id=rfid_id).first()
    if student:
        try:
            # Delete the student from the session
            db.session.delete(student)
            # Commit the changes to the database
            db.session.commit()
            return redirect(url_for('index'))  # Redirect to the homepage
        except Exception as e:
            # Handle any errors
            print(e)
            db.session.rollback()
            return "Error occurred while removing student"
    else:
        return "Student not found"
