from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from app.models import User, Role, Organization


class UserForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[Optional(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    organization = SelectField('Organization', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save User')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
        self.organization.choices = [(0, '— None —')] + [
            (o.id, o.name) for o in Organization.query.order_by(Organization.name).all()
        ]

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data.lower()).first()
        if user is not None:
            if self.user is None or user.id != self.user.id:
                raise ValidationError('Email already registered.')


class OrganizationForm(FlaskForm):
    name = StringField('Organization Name', validators=[DataRequired(), Length(min=2, max=150)])
    type = SelectField('Type', choices=[
        ('supplier', 'Supplier'),
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('auditor', 'Auditor / Certification Body'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    registration_no = StringField('Registration No.', validators=[Optional(), Length(max=100)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=120)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=30)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    country = StringField('Country', validators=[Optional(), Length(max=80)])
    is_verified = BooleanField('Verified', default=False)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Organization')


class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired(), Length(min=2, max=64)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    is_default = BooleanField('Default Role for new users')
    submit = SubmitField('Save Role')

    def __init__(self, role=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role

    def validate_name(self, field):
        existing = Role.query.filter_by(name=field.data).first()
        if existing is not None:
            if self.role is None or existing.id != self.role.id:
                raise ValidationError('Role name already exists.')


class SystemSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)], default='TracePass')
    support_email = StringField('Support Email', validators=[Optional(), Email()])
    allow_public_registration = BooleanField('Allow Public Registration', default=True)
    submit = SubmitField('Save Settings')