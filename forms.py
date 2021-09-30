from flask_wtf import FlaskForm
from wtforms import DecimalField,SubmitField
from wtforms.validators import DataRequired

class changemaxdistanceform(FlaskForm):
    #username = StringField("Username",validators = [DataRequired()])
    maxDistance = DecimalField('max distance', validators=[DataRequired()])
    submit = SubmitField("change max distance")

