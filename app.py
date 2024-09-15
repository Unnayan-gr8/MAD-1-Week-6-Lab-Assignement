from sys import argv
from flask import Flask, render_template, request, redirect, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, fields, marshal_with, reqparse
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
db = SQLAlchemy(app)
api = Api(app)

#--------------------------------------------Database---------------------------------------------------------------------

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    course_name = db.Column(db.String(), nullable = False)
    course_code = db.Column(db.String(), nullable = False, unique = True)
    course_description = db.Column(db.String())

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String(), unique = True, nullable = False)
    first_name = db.Column(db.String(), nullable = False)
    last_name = db.Column(db.String())
    enroll = db.relationship('Course', secondary = 'enrollment')

class Enrollment(db.Column):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable = False)
#-----------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------Routes-------------------------------------------------------------------
class NotFoundError(HTTPException):
    def __init__(self, status_code, response):
        self.response = make_response(jsonify(response), status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code" : error_code, "error_message" : error_message}
        self.response = make_response(jsonify(message), status_code)

class AlreadyExist(HTTPException):
    def __init__(self, status_code, response):
        self.response = make_response(jsonify(response), status_code)

student = {"student_id" : fields.Integer, "roll_number" : fields.String, "first_name" : fields.String, "last_name" : fields.String} 
parser = reqparse.RequestParser()
parser.add_argument('roll_number')
parser.add_argument('first_name')
parser.add_argument('last_name')

class StudentApi(Resource):
    @marshal_with(student)
    def get(self,id):
        s = db.session.query(Student).filter(Student.student_id == id).first()
        if s:
            return s
        raise NotFoundError(status_code = 404, response = "Student not found!")
    

    @marshal_with(student)
    def post(self):
        args = parser.parse_args()
        roll = args.get('roll_number', None)
        f_name = args.get('first_name', None)
        l_name = args.get('last_name', None)
        if roll is None or roll.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'STUDENT001', error_message = 'Roll Number is required')
        if f_name is None or f_name.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'STUDENT002', error_message = 'First Name is required')
        
        stud = db.session.query(Student).filter(Student.roll_number == roll).first()

        if stud:
            raise AlreadyExist(status_code = 409)
        entry = Student(roll_number = roll, first_name = f_name, last_name = l_name)
        db.session.add(entry)
        db.session.commit()
        return entry,201

    @marshal_with(student)
    def put(self, id):
        args = parser.parse_args()
        roll = args.get('roll_number', None)
        f_name = args.get('first_name', None)
        l_name = args.get('last_name', None)
        if roll is None or roll.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'STUDENT001', error_message = 'Roll Number is required')
        if f_name is None or f_name.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'STUDENT002', error_message = 'First Name is required')
        stud = Student.query.filter_by(roll_number = roll)
        if stud:
            raise NotFoundError(status_code = 404)
        stud.roll_number = roll
        stud.first_name = f_name
        stud.last_name = l_name
        db.session.commit()
        return stud, 200
    
    def delete(self, id):
        args = parser.parse_args()
        roll = args.get('roll_number', None)
        f_name = args.get('first_name', None)
        l_name = args.get('last_name', None)
        if roll is None or roll.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'STUDENT001', error_message = 'Roll Number is required')
        if f_name is None or f_name.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'STUDENT002', error_message = 'First Name is required')
        stud = db.session.query(Student).filter(Student.roll_number == roll).first()
        if stud is None:
            raise NotFoundError(status_code = 404)
        db.session.delete(stud)
        db.session.commit()
        return make_response("")

course = {"course_id" : fields.Integer, "course_name" : fields.String, "course_code" : fields.String, "course_description" : fields.String} 
c_parser = reqparse.RequestParser()
c_parser.add_argument('course_name')
c_parser.add_argument('course_code')
c_parser.add_argument('course_description')

class CourseApi(Resource):
    @marshal_with(course)
    def get(self,id):
        s = db.session.query(Course).filter(Course.course_id == id).first()
        if s:
            return s
        raise NotFoundError(status_code = 404, response = "Course not found!")
    

    @marshal_with(course)
    def post(self):
        args = c_parser.parse_args()
        name = args.get('course_name', None)
        code = args.get('course_code', None)
        desc = args.get('course_description', None)
        if name is None or name.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'Course001', error_message = 'Course Name is required')
        if code is None or code.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'Course002', error_message = 'Course Code is required')
        
        cou = db.session.query(Course).filter(Course.name == name).first()

        if cou:
            raise AlreadyExist(status_code = 409)
        entry = Course(course_name = name, course_code = code, course_description = desc)
        db.session.add(entry)
        db.session.commit()
        return entry,201

    @marshal_with(course)
    def put(self, id):
        args = c_parser.parse_args()
        name = args.get('course_name', None)
        code = args.get('course_code', None)
        desc = args.get('course_description', None)
        if name is None or name.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'Course001', error_message = 'Course Name is required')
        if code is None or code.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'Course002', error_message = 'Course Code required')
        cou = Course.query.filter_by(course_name = name)
        if cou:
            raise NotFoundError(status_code = 404)
        cou.course_name = name
        cou.course_code = code
        cou.course_description = desc
        db.session.commit()
        return cou, 200
    
    def delete(self, id):
        args = c_parser.parse_args()
        name = args.get('course_name', None)
        code = args.get('course_code', None)
        desc = args.get('course_description', None)
        if name is None or name.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'Course001', error_message = 'Course Name is required')
        if code is None or code.strip() == '':
            raise BusinessValidationError(status_code = 400, error_code = 'Course002', error_message = 'Course Code required')
        cou = Course.query.filter_by(course_name = name)
        if cou:
            raise NotFoundError(status_code = 404)
        db.session.delete(cou)
        db.session.commit()
        return make_response("")
    
enroll = {'enrollment_id' : fields.Integer, 'student_id' : fields.Integer, 'course_id' : fields.Integer}
e_parser = reqparse.RequestParser()
e_parser.add_argument('course_id')

class EnrollmentApi(Resource):
    @marshal_with(enroll)
    def get(self, id):
        s = Student.query.filter_by(student_id = id).first()
        if s is None:
            raise NotFoundError(status_code = 404)
        e = Enrollment.query.filter_by(student_id = id).all()
        if e == []:
            raise NotFoundError(status_code = 404, response = "Student is not enrolled in the courses")
        return e
    
    @marshal_with(enroll)
    def post(self, id):
        args = e_parser.parse_args()
        c_id = int(args.get('course_id', None))
        s = db.session.query(Student).filter(Student.student_id == id).firt()
        if s is None:
            raise NotFoundError(status_code = 404, response = "Student not found")
        c = db.session.query(Course).filter(Course.course_id == c_id).firt()
        if c is None:
            raise BusinessValidationError(status_code = 400, error_code = "ENROLLMENT001", error_message = 'Course does not exist')
        s.enroll.append(c)
        db.session.commit()
        e = Enrollment.query.filter_by(student_id = id).all()
        return e,201
    
    def delete(self, id, cid):
        s = db.session.query(Student).filter(Student.student_id == id).firt()
        if s is None:
            raise NotFoundError(status_code = 404, response = "Student not found")
        c = db.session.query(Course).filter(Course.course_id == cid).firt()
        if c is None:
            raise BusinessValidationError(status_code = 400, error_code = "ENROLLMENT001", error_message = 'Course does not exist')
        e = db.session.query(Enrollment),filter(student_id = id, course_id = cid)
        if e is None:
            raise NotFoundError(status_code = 404)
        db.session.delete(e)
        db.session.commit()
        return make_response("")


api.add_resource(CourseApi, '/api/course', '/api/course/<int:id>')
api.add_resource(StudentApi, '/api/student', '/api/student/<int:id>')
api.add_resource(EnrollmentApi, '/api/student/<int:id>/course', '/api/student/<int:id>/course/<int:cid>')

if __name__ == "__main__":
    app.run(debug = True)
