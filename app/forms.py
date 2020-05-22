from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Regexp, NumberRange

class CasesForm(FlaskForm):

    # TODO: If I checked yesterdays numbers I could use them here
    # to prefill the fields and to valid them

    datestamp  = StringField(u'datestamp',
        validators=[
            DataRequired(message="enter date/time in 24hr format MM/DD/YYYY HH:MM")
    ])

    # NB IntegerField() would not accept 0 as input!!
    # NumberRange is not working the way I expect

    positive = StringField(u'positive', default="0", validators=[
        DataRequired(message="enter cases"),
#        NumberRange(min=0, max=100000, message="'cases' is out of range")
    ])
    
    negative = StringField(u'negative', default="0",  validators=[
        DataRequired(message="enter negative tests"),
#        NumberRange(min=0, max=100000, message="'negative' is out of range")
    ])
    
    recovered = StringField(u'recovered', default="0", validators=[
        DataRequired(message="enter recovered"),
#        NumberRange(min=0, max=100000, message="'recovered' is out of range")
    ])

    deaths = StringField(u'deaths', default="0", validators=[
        DataRequired(message="enter deaths"),
#        NumberRange(min=0, max=100000, message="'deaths' is out of range")
    ])

    submit = SubmitField(u"Submit")

# That's all!
