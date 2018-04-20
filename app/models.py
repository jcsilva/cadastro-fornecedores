# -*- coding: utf-8 -*-
from datetime import datetime
from app import db

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(256), index=True, unique=True)
    contacts = db.Column(db.String(256))
    portfolio = db.Column(db.String(512))
    transactions = db.relationship('Transaction', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<Provider {}>'.format(self.name)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))

    def __repr__(self):
        return '<Transaction {}>'.format(self.products)