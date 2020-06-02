from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Regexp, NumberRange


class CasesForm(FlaskForm):

    datestamp = StringField(u'datestamp',
                            validators=[
                                DataRequired(
                                    message="enter date/time in 24hr format MM/DD/YYYY HH:MM")
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


class PPEForm(FlaskForm):

    datestamp = StringField(u'datestamp',
                            validators=[
                                DataRequired(
                                    message="enter date/time in 24hr format MM/DD/YYYY HH:MM")
                            ])

    facility = StringField(u'facility', default="Clatsop", validators=[
        DataRequired(message="enter facility name")
    ])

    # NB IntegerField() would not accept 0 as input!!
    # NumberRange is not working the way I expect

    n95 = StringField(u'n95', default="0", validators=[
                      DataRequired(message="enter n95 supply")])
    n95_burn = StringField(u'n95_burn', default="0", validators=[
        DataRequired(message="enter n95 burn rate")])

    mask = StringField(u'mask', default="0", validators=[
                      DataRequired(message="enter surgical mask supply")])
    mask_burn = StringField(u'mask_burn', default="0", validators=[
        DataRequired(message="enter surgical mask burn rate")])

    shield = StringField(u'shield', default="0", validators=[
                      DataRequired(message="enter shield supply")])
    shield_burn = StringField(u'shield_burn', default="0", validators=[
        DataRequired(message="enter shield burn rate")])

    glove = StringField(u'glove', default="0", validators=[
                      DataRequired(message="enter glove supply")])
    glove_burn = StringField(u'glove_burn', default="0", validators=[
        DataRequired(message="enter glove burn rate")])

    gown = StringField(u'gown', default="0", validators=[
                      DataRequired(message="enter gown supply")])
    gown_burn = StringField(u'gown_burn', default="0", validators=[
        DataRequired(message="enter gown burn rate")])

    submit = SubmitField(u"Submit")

# That's all!
