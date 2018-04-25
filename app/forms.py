# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Supplier, Item
    

class OrderForm(FlaskForm):
    supplier = QuerySelectField(get_label='name', query_factory=lambda: Supplier.query.all())
    items = StringField('Produtos')
    submit = SubmitField('Cadastrar')


class ItemForm(FlaskForm):
    name = StringField('Produto', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')


class ItemField(StringField):
    def _value(self):
        if self.data:
            # Display tags as a comma-separated list.
            return ', '.join([item.name for item in self.data])
        return ''

    def get_tags_from_string(self, item_string):
        raw_items = item_string.split(',')
        # Filter out any empty tag names.
        item_names = [name.strip() for name in raw_items if name.strip()]
        # Query the database and retrieve any tags we have already saved.
        existing_items = Item.query.filter(Item.name.in_(item_names))
        # Determine which tag names are new.
        new_names = set(item_names) - set([item.name for item in existing_items])
        # Create a list of unsaved Tag instances for the new tags.
        new_items = [Item(name=name) for name in new_names]
        # Return all the existing tags + all the new, unsaved tags.
        return list(existing_items) + new_items

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.get_tags_from_string(valuelist[0])
        else:
            self.data = []


class SupplierForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    address = TextAreaField('Endereço')
    contacts = TextAreaField('Contato') 
    portfolio = ItemField('Produtos', description='Listar produtos separados por vírgula.')
    submit = SubmitField('Cadastrar')
    