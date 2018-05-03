from app import app
from app import db
from flask import render_template, flash, redirect, request, url_for
from app.forms import SupplierForm, OrderForm, ItemForm, PreOrderForm, OrderItemForm
from app.models import Supplier, Order, Item, Status, OrderItem
from datetime import datetime
from math import isclose


@app.route('/')
@app.route('/index')
def index():
    suppliers = Supplier.query.filter(Supplier.status != Status.DELETED).order_by('name')
    return render_template('index.html', title='Fornecedores', the_data=suppliers)


@app.route('/newitem', methods=['GET', 'POST'])
def new_item():
    form = ItemForm()
    try:
        if form.validate_on_submit():
            item = Item(name=form.name.data)
            db.session.add(item)
            db.session.commit()
            flash('Novo item cadastrado {}'.format(form.name.data))
            return redirect(url_for('list_items'))
    except Exception as err:
        db.session.rollback()
        flash('ERRO: O produto "{}" já foi cadastrado! Detalhes: {}'.format(form.name.data, str(err)))
    return render_template('quickform.html', title='Cadastrar item', form=form)


@app.route('/listitems')
def list_items():
    items = Item.query.order_by('name')
    return render_template('listitems.html', items=items)


@app.route('/newsupplier', methods=['GET', 'POST'])
def new_supplier():
    form = SupplierForm()
    form.portfolio.choices = [(g.id, g.name) for g in Item.query.order_by('name')]
    if form.validate_on_submit():
        supplier = Supplier.query.filter_by(name=form.name.data).first()
        item_list = []
        choices = dict(form.portfolio.choices)
        for item_idx in form.portfolio.data:
            item_name = choices.get(item_idx)
            item_list.append(Item.query.filter_by(name=item_name).first())
        # if I try to add a new supplier, but it was deleted (status==DELETED),
        # I should update its variables instead of creating a new record
        if supplier:
            # we never update name! It avoids problems because the name
            # must be unique in our database
            supplier.contacts = form.contacts.data
            supplier.address = form.address.data
            supplier.portfolio = item_list
            supplier.status = Status.ACTIVE
        else:
            p = Supplier(name=form.name.data,
                         address=form.address.data,
                         contacts=form.contacts.data,
                         portfolio=item_list,
                         status=Status.ACTIVE)
            db.session.add(p)
        db.session.commit()
        flash('Novo fornecedor cadastrado {}, endereço={}, contato={}, produtos={}'.format(
            form.name.data, form.address.data, form.contacts.data, item_list))
        return redirect(url_for('index'))
    return render_template('supplierform.html', title="Cadastrar fornecedor", form=form)


@app.route('/editsupplier/<supplierid>', methods=['GET', 'POST'])
def edit_supplier(supplierid):
    supplier = Supplier.query.filter_by(id=supplierid).first_or_404()
    if request.method == 'POST':
        form = SupplierForm(obj=supplier)
        form.portfolio.choices = [(g.id, g.name) for g in Item.query.order_by('name')]
        if form.validate_on_submit():
            item_list = []
            choices = dict(form.portfolio.choices)
            for item_idx in form.portfolio.data:
                item_name = choices.get(item_idx)
                item_list.append(Item.query.filter_by(name=item_name).first())
            supplier.contacts = form.contacts.data
            supplier.address = form.address.data
            supplier.portfolio = item_list
            db.session.commit()
            return redirect(url_for('detail_supplier',
                                    supplierid=supplier.id))
    else:
        form = SupplierForm(obj=supplier)
        form.portfolio.choices = [(g.id, g.name) for g in Item.query.order_by('name')]
        form.portfolio.data = [item.id for item in supplier.portfolio]
    return render_template('supplierform.html', title="Editar fornecedor", form=form, edit=True)


@app.route('/deletesupplier/<supplierid>', methods=['GET', 'POST'])
def delete_supplier(supplierid):
    supplier = Supplier.query.filter_by(id=supplierid).first_or_404()
    if request.method == 'POST':
        supplier.status = Status.DELETED
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('deleteform.html', supplier=supplier)


@app.route('/detailsupplier/<supplierid>')
def detail_supplier(supplierid):
    supplier = Supplier.query.filter_by(id=supplierid).first_or_404()
    return render_template('detailsupplier.html', title='Detalhes',
                           supplier=supplier)


@app.route('/preorder/', methods=['GET', 'POST'])
def pre_order():
    form = PreOrderForm()
    # TODO: o filtro de ACTIVE deveria estar dentro da classe Supplier?
    form.supplier.choices = [(g.id, g.name) for g in Supplier.query.filter(Supplier.status == Status.ACTIVE).order_by('name')]
    if request.method == 'POST':
        supplier = Supplier.query.filter_by(name=dict(form.supplier.choices).get(form.supplier.data)).first()
        return redirect(url_for('new_order', supplierid=supplier.id))
    return render_template('quickform.html', title='Escolher fornecedor', form=form)


def create_order(form, supplier, order=None):
    total = 0
    order_items = []
    for item in form.order_items.data:
        total += item['quantity'] * item['unit_price']
        order_item = OrderItem(item=item['item'],
                               quantity=item['quantity'],
                               unity=item['unity'],
                               unit_price=item['unit_price'])
        order_items.append(order_item)

    if isclose(total, 0, rel_tol=1e-5):
        # don't register the order if total value is zero!
        return None

    day = form.timestamp.data
    if day:
        hours = datetime.utcnow().timetz()
        timestamp = datetime.combine(day, hours)
    else:
        timestamp = datetime.utcnow()

    if order:
        order.freight_company = form.freight_company.data
        order.freight_value = form.freight_value.data
        order.obs = form.obs.data
        order.order_items = order_items
        order.timestamp = timestamp
    else:
        order = Order(supplier_id=supplier.id,
                      freight_company=form.freight_company.data,
                      freight_value=form.freight_value.data,
                      obs=form.obs.data,
                      order_items=order_items,
                      timestamp=timestamp)
    return order


@app.route('/neworder/<supplierid>', methods=['GET', 'POST'])
def new_order(supplierid):
    supplier = Supplier.query.filter_by(id=supplierid).first_or_404()
    form = OrderForm()
    try:
        if form.is_submitted():
            # when a post is submitted, we first check if all fields are valid
            if form.validate():
                order = create_order(form, supplier)
                if order:
                    db.session.add(order)
                    db.session.commit()
                    return redirect(url_for('detail_supplier',
                                            supplierid=supplier.id))
                else:
                    flash("A compra não foi registrada porque o valor total dos produtos foi R$0,00!")
                    return redirect(url_for('detail_supplier',
                                            supplierid=supplier.id))
            else:
                # when a field is not valid, we flash a message with the error.
                flash("Erro! Detalhes: {}".format(str(form.errors)))
        # when the page is loaded, a GET is executed.
        # In this case, we only fill table fields.
        else:
            for item in supplier.portfolio:
                order_item_form = OrderItemForm()
                order_item_form.item = item.name
                order_item_form.quantity = 0
                order_item_form.unit_price = 0
                order_item_form.unity = ""
                form.order_items.append_entry(order_item_form)
    except Exception as err:
        db.session.rollback()
        flash('ERRO: {}'.format(str(err)))
    return render_template('orderform.html', title="Cadastrar compra",
                           form=form, supplier=supplier)


@app.route('/editorder/<orderid>', methods=['GET', 'POST'])
def edit_order(orderid):
    order = Order.query.filter_by(id=orderid).first_or_404()
    supplier = Supplier.query.filter_by(id=order.supplier_id).first_or_404()
    form = OrderForm(obj=order)
    try:
        if form.is_submitted():
            # when a post is submitted, we first check if all fields are valid
            if form.validate():
                order = create_order(form, supplier, order)
                if order:
                    db.session.commit()
                    return redirect(url_for('detail_supplier',
                                            supplierid=supplier.id))
                else:
                    flash("A compra não foi alterada porque o valor total dos produtos foi R$0,00!")
                    return redirect(url_for('detail_supplier',
                                            supplierid=supplier.id))
            else:
                # when a field is not valid, we flash a message with the error.
                flash("Erro! Detalhes: {}".format(str(form.errors)))
        else:
            for item in supplier.portfolio:
                if not order.has_item(item):
                    order_item_form = OrderItemForm()
                    order_item_form.item = item.name
                    order_item_form.quantity = 0
                    order_item_form.unit_price = 0
                    order_item_form.unity = ""
                    form.order_items.append_entry(order_item_form)
    except Exception as err:
        db.session.rollback()
        flash('ERRO: {}'.format(str(err)))
    return render_template('orderform.html', title="Editar compra",
                           form=form, supplier=supplier)


@app.route('/deleteorder/<orderid>', methods=['GET', 'POST'])
def delete_order(orderid):
    order = Order.query.filter_by(id=orderid).first_or_404()
    if request.method == 'POST':
        db.session.delete(order)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('deleteform.html', order=order)
