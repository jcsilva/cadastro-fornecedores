# -*- coding: utf-8 -*-
from datetime import datetime
from app import db

stock = db.Table('stock',
    db.Column('supplier_id', db.Integer, db.ForeignKey('supplier.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(256), index=True, unique=True)
    contacts = db.Column(db.String(256))
    portfolio = db.relationship('Item', secondary=stock, lazy='subquery',
                                backref=db.backref('suppliers', lazy=True))
    orders = db.relationship('Order', backref='supplier', lazy='dynamic')
    def __repr__(self):
        return '<Supplier {}>'.format(self.name)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    def __repr__(self):
        return '<Item {}>'.format(self.name)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    freight_company = db.Column(db.String(256))
    freight_value = db.Column(db.Numeric(10,2))
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic')
    def __repr__(self):
        return '<Order {}>'.format(self.supplier_id)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    item = db.Column(db.String(64))
    quantity = db.Column(db.Numeric(10,3))
    unit_price = db.Column(db.Numeric(10,2))
    def __repr__(self):
        return '<OrderItem {}, {}, {}>'.format(self.item, self.quantity, self.unit_price)

