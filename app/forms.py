# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Supplier


class SupplierForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    address = StringField('Endereço')
    submit = SubmitField('Cadastrar')
    

class OrderForm(FlaskForm):
    supplier = QuerySelectField(get_label='name', query_factory=lambda: Supplier.query.all())
    items = StringField('Produtos')
    submit = SubmitField('Cadastrar')


class ItemForm(FlaskForm):
    name = StringField('Produto', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')