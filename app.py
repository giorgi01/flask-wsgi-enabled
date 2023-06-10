# საჭირო ბიბლიოთეკების იმპორტი
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from form import MyForm

# flask აპლიკაციის შექმნა, რომელსაც ერქმევა ფაილის იდენტური სახელი
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# შექმნილი აპლიკაციისთვის ბაზის მისამართის გაწერა, აქვე ბაზას ვარქმევთ სახელს
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'

# ვქმნით app-ზე მორგებულ ბაზის პითონურ ობიექტს
db = SQLAlchemy(app)


# ქვემოთ Student(db.Model)-ის საშუალებით SQLAlchemy-ს აღვუწერთ, თუ რა სახით უნდა შეინახოს სტუდენტის ობიექტი მონაცემთა ბაზაში.
# db.Model კლასის შვილობილ კლასებს ფლასკში ვეძახით მოდელებს, მოდელები აღწერენ ობიექტის წარმოდგენას ბაზაში.
class Student(db.Model):
    __tablename__ = 'students'  # ობიექტის table-ს უნდა ერქვას students
    id = db.Column(db.Integer, primary_key=True)  # id ველი უნდა იყოს integer და primary key შეზღუდვა ედოს
    name = db.Column(db.String(100))  # name ველი უნდა იყოს ტექსტი, მაქსიმუმ 100 სიმბოლო
    gpa = db.Column(db.Float)  # "--"

    # to_dict მეთოდს ვქმნით Student მოდელის ლექსიკონად გადაქასთვის ფუნქციონალისთვის
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gpa': self.gpa
        }


# get_students მეთოდი გამოიძახება მხოლოდ იმ შემთხვევაში თუ:
# მომხმარებელი გადავა აპლიკაციის / ან /students მისამართზე
# მეთოდს ბაზიდან მოაქვს ყველა სტუდენტის ობიექტი გადაქასთავს ლექსიკონებად და უბრუნებს მომხმარებელს, HTTP 200 კოდთან ერთად
# თუ url არის /api/students?name=Someone, მეთოდი წამოიღებს მხოლოდ სტუდენტებს დასახელებით Someone
@app.route('/api/students')
def get_students():
    student_name = request.args.get('name')
    if student_name:
        students = [student.to_dict() for student in Student.query.filter(Student.name == student_name)]
    else:
        students = [student.to_dict() for student in Student.query.all()]
    return {'students': students, 'status_code': 200}


@app.route('/api/students/<int:id>')
def get_student(id):
    student = Student.query.get(id)
    return {'student': student, 'status_code': 200}


# create_students მეთოდი გამოიძახება მხოლოდ იმ შემთხვევაში თუ:
# მომხმარებელი ჩვენს API-ს მიმართავს POST რექუესტით
# რექუესტიდან ვიღებთ საჭირო ინფორმაციას და ვქმნით ობიექტს ბაზაში
# ბოლოს ვაბრუნებთ ინფოსა და 201 HTTP კოდს
@app.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json()
    name = data['name']
    gpa = data['gpa']
    student = Student(name=name, gpa=gpa)
    db.session.add(student)
    db.session.commit()
    return "Successfully created", 201


# update_student მეთოდი გამოიძახება მხოლოდ იმ შემთხვევაში თუ:
# მომხმარებელი ჩვენს API-ს მიმართავს PUT რექუესტით
# რექუესტიდან ვიღებთ ობიექტის id-ს, რომელიც უნდა შევცვალოთ
# და განახლებულ ინფორმაცია ობიექტის შესახებ, შემდეგ ვაახლებთ ობიექტს და ვინახავთ ბაზაში ამ სახით.
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    name = data['name']
    gpa = data['gpa']
    student = Student.query.get(id)
    if student is not None:
        student.name = name
        student.gpa = gpa
        db.session.commit()
    return "Successfully updated", 200


# delete_student მეთოდი გამოიძახება მხოლოდ იმ შემთხვევაში თუ:
# მომხმარებელი ჩვენს API-ს მიმართავს DELETE რექუესტით
# რექუესტიდან ვიღებთ ობიექტის id-ს და ვშლით ბაზიდან ამ კონკრეტულ ობიექტს
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return "Successfully delete", 200


@app.route('/')
def index():
    students = [student.to_dict() for student in Student.query.all()]
    return render_template('index.html', students=students)


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = MyForm()
    if form.validate_on_submit():
        name = form.name.data
        gpa = form.gpa.data
        student = Student(name=name, gpa=gpa)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('create.html', form=form)


@app.route('/success')
def success():
    return 'Form submitted successfully!'


# ქვემოთ ვქმნით აპლიკაციის კონტექსტს
# ამ კონტექსტში ვწერთ თუ როგორ უნდა დაისტარტოს ჩვენი API
# db.create_all() გადაიკითხავს ზემოთ განმარტებულ მოდელს და შექმნის მონაცემთა ბაზას ცხრილით students
# შემდეგ app.run() გაუშვებს აპლიკაციას დეფოლტ პორტზე 127.0.0.1:5000

with app.app_context():
    db.create_all()
