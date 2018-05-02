from app import app
from app import db
from flask import render_template, flash, redirect, request, url_for
from app.forms import SupplierForm, OrderForm, ItemForm, PreOrderForm, OrderItemForm
from app.models import Supplier, Order, Item, Status, OrderItem

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
        flash('ERRO: O produto "{}" já foi incluído! Detalhes: {}'.format(form.name.data, str(err)))
    return render_template('newitem.html', title='Cadastrar item', form=form)


@app.route('/listitems')
def list_items():
    items = Item.query.order_by('name')
    return render_template('listitems.html', items=items)


@app.route('/newsupplier', methods=['GET', 'POST'])
def new_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier.query.filter_by(name=form.name.data).first()
        # if I try to add a new supplier, but it was deleted (status==DELETED),
        # I should update its variables instead of creating a new record
        if supplier:
            # we never update name!
            supplier.contacts = form.contacts.data
            supplier.address = form.address.data
            supplier.portfolio = form.portfolio.data
            supplier.status = Status.ACTIVE
        else:
            p = Supplier(name=form.name.data,
                         address=form.address.data,
                         contacts=form.contacts.data,
                         portfolio=form.portfolio.data,
                         status=Status.ACTIVE)
            db.session.add(p)
        db.session.commit()
        flash('Novo fornecedor cadastrado {}, endereço={}, contato={}, produtos={}'.format(
            form.name.data, form.address.data, form.contacts.data, form.portfolio.data))
        return redirect(url_for('index'))
    return render_template('newsupplier.html', title='Cadastrar', form=form)


@app.route('/editsupplier/<suppliername>', methods=['GET', 'POST'])
def edit_supplier(suppliername):
    supplier = Supplier.query.filter_by(name=suppliername).first_or_404()
    if request.method == 'POST':
        form = SupplierForm(obj=supplier)
        if form.validate_on_submit():
            supplier.contacts = form.contacts.data
            supplier.address = form.address.data
            supplier.portfolio = form.portfolio.data
            db.session.commit()
            return redirect(url_for('detail_supplier', suppliername=supplier.name))
    else:
        form = SupplierForm(obj=supplier)
    return render_template('editsupplier.html', form=form)


@app.route('/deletesupplier/<suppliername>', methods=['GET', 'POST'])
def delete_supplier(suppliername):
    supplier = Supplier.query.filter_by(name=suppliername).first_or_404()
    if request.method == 'POST':
        supplier.status = Status.DELETED
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('deletesupplier.html', supplier=supplier)


@app.route('/detailsupplier/<suppliername>')
def detail_supplier(suppliername):
    supplier = Supplier.query.filter_by(name=suppliername).first_or_404()
    return render_template('detailsupplier.html', title='Detalhes', supplier=supplier)


@app.route('/preorder/', methods=['GET', 'POST'])
def pre_order():
    form = PreOrderForm()
    # TODO: o filtro de ACTIVE deveria estar dentro da classe Supplier?
    form.supplier.choices = [(g.id, g.name) for g in Supplier.query.filter(Supplier.status == Status.ACTIVE).order_by('name')]
    if request.method == 'POST':
        supplier = Supplier.query.filter_by(name=dict(form.supplier.choices).get(form.supplier.data)).first()
        return redirect(url_for('new_order', suppliername=supplier.name))
    return render_template('choosesupplier.html', form=form)


@app.route('/neworder/<suppliername>', methods=['GET', 'POST'])
def new_order(suppliername):
    supplier = Supplier.query.filter_by(name=suppliername).first_or_404()
    form = OrderForm()
    if form.validate_on_submit():
        print(form.freight_value.data)
        order = Order(supplier_id=supplier.id,
                      freight_company=form.freight_company.data,
                      freight_value=form.freight_value.data,)
        db.session.add(order)
        db.session.commit()
        # get ID>: https://stackoverflow.com/questions/19388555/sqlalchemy-session-add-return-value
        db.session.refresh(order)
        for item in form.order_items.data:
            order_item = OrderItem(order_id=order.id,
                                   item=item['item'],
                                   quantity=item['quantity'],
                                   unit_price=item['unit_price'])
            db.session.add(order_item)
        db.session.commit()
        return redirect(url_for('detail_supplier', suppliername=supplier.name))
    for item in supplier.portfolio:
        order_item_form = OrderItemForm()
        order_item_form.item = item.name
        order_item_form.quantity = 0
        order_item_form.unit_price = 0
        form.order_items.append_entry(order_item_form)
    return render_template('neworder.html', form=form, supplier=supplier)
