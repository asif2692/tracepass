from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    brand = StringField('Brand', validators=[Optional(), Length(max=100)])
    model = StringField('Model', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    manufacturer_org_id = SelectField('Manufacturer Organization', coerce=int, validators=[DataRequired()])
    origin_country = StringField('Origin Country', validators=[Optional(), Length(max=80)])
    submit = SubmitField('Save Product')


class BatchForm(FlaskForm):
    batch_no = StringField('Batch / Lot No.', validators=[DataRequired(), Length(max=80)])
    manufacture_date = DateField('Manufacture Date', validators=[Optional()])
    production_location = StringField('Production Location', validators=[Optional(), Length(max=150)])
    quantity = FloatField('Quantity', validators=[Optional(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[Optional(), Length(max=30)], default='units')
    submit = SubmitField('Save Batch')


class MaterialForm(FlaskForm):
    name = StringField('Material Name', validators=[DataRequired(), Length(max=150)])
    category = StringField('Category', validators=[Optional(), Length(max=80)])
    origin_country = StringField('Origin Country', validators=[Optional(), Length(max=80)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Material')


class ProductMaterialForm(FlaskForm):
    material_id = SelectField('Material', coerce=int, validators=[DataRequired()])
    supplier_org_id = SelectField('Supplier Organization', coerce=int, validators=[Optional()])
    quantity = FloatField('Quantity', validators=[Optional(), NumberRange(min=0)])
    percentage = FloatField('Percentage %', validators=[Optional(), NumberRange(min=0, max=100)])
    unit = StringField('Unit', validators=[Optional(), Length(max=30)])
    submit = SubmitField('Add Material')
