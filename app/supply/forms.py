from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class EventForm(FlaskForm):
    event_type = SelectField('Event Type', choices=[
        ('sourcing', 'Sourcing'),
        ('processing', 'Processing'),
        ('manufacturing', 'Manufacturing'),
        ('shipment', 'Shipment'),
        ('receipt', 'Receipt'),
        ('sale', 'Sale'),
        ('recall', 'Recall'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    event_date = DateField('Event Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=150)])
    organization_id = SelectField('Organization', coerce=int, validators=[Optional()])
    batch_id = SelectField('Batch (optional)', coerce=int, validators=[Optional()])
    reference_no = StringField('Reference No.', validators=[Optional(), Length(max=80)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Event')


class ShipmentForm(FlaskForm):
    from_org_id = SelectField('From Organization', coerce=int, validators=[DataRequired()])
    to_org_id = SelectField('To Organization', coerce=int, validators=[DataRequired()])
    batch_id = SelectField('Batch (optional)', coerce=int, validators=[Optional()])
    shipped_date = DateField('Shipped Date', validators=[Optional()])
    received_date = DateField('Received Date', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    tracking_no = StringField('Tracking No.', validators=[Optional(), Length(max=80)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Shipment')
