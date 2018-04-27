# -*- coding: utf-8 -*-
from datetime import datetime
from app import db

stock = db.Table('stock',
                 db.Column('supplier_id', db.Integer, db.ForeignKey('supplier.id')),
                 db.Column('item_id', db.Integer, db.ForeignKey('item.id')))


class Status():
    ACTIVE = 0
    DELETED = 1


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(256), index=True)
    status = db.Column(db.Integer, index=True)
    contacts = db.Column(db.String(256))
    portfolio = db.relationship('Item', secondary=stock, lazy='subquery',
                                backref=db.backref('suppliers', lazy=True))
    orders = db.relationship('Order', backref='supplier', lazy='dynamic')

    def __repr__(self):
        return '<Supplier {}>'.format(self.name)

    def is_active(self):
        if self.status == Status.ACTIVE:
            return True
        else:
            return False


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
    freight_value = db.Column(db.Numeric(10, 2), nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic')

    def __repr__(self):
        return '<Order {}>'.format(self.supplier_id)

    def total_value(self):
        total = self.freight_value
        for order_item in self.order_items:
            total += order_item.quantity * order_item.unit_price
        return total


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    item = db.Column(db.String(64))
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return '<OrderItem {}, {}, {}>'.format(self.item, self.quantity,
                                               self.unit_price)
