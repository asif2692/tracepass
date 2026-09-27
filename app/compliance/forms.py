from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileField, FileAllowed


class CertificateForm(FlaskForm):
    cert_type = StringField('Certificate Type', validators=[DataRequired(), Length(max=100)])
    issuer = StringField('Issuer', validators=[Optional(), Length(max=150)])
    issue_date = DateField('Issue Date', validators=[Optional()])
    expiry_date = DateField('Expiry Date', validators=[Optional()])
    organization_id = SelectField('Organization', coerce=int, validators=[Optional()])
    product_id = SelectField('Product (optional)', coerce=int, validators=[Optional()])
    file = FileField('Upload File', validators=[Optional(), FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'PDF/Images only')])
    submit = SubmitField('Save Certificate')


class RuleForm(FlaskForm):
    name = StringField('Rule Name', validators=[DataRequired(), Length(max=150)])
    category = StringField('Category', validators=[Optional(), Length(max=80)])
    rule_definition = TextAreaField('Rule Definition / Description', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Rule')


class ReviewForm(FlaskForm):
    decision = SelectField('Decision', choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject'),
        ('request_correction', 'Request Correction')
    ], validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional()])
    submit = SubmitField('Submit Review')


class RecallForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    batch_id = SelectField('Batch (optional)', coerce=int, validators=[Optional()])
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(min=10)])
    severity = SelectField('Severity', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')
    submit = SubmitField('Issue Recall')
