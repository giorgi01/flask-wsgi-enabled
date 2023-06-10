from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, validators


class MyForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired(), validators.Length(min=3, max=50)])
    gpa = FloatField('GPA', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')
