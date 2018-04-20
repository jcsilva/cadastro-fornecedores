# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Provider


class ProviderForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    address = StringField('Endereço')
    submit = SubmitField('Cadastrar')
    

class TransactionForm(FlaskForm):
    company = QuerySelectField(query_factory=lambda: Provider.query.all())
    products = StringField('Produtos')
    submit = SubmitField('Cadastrar')