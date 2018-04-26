from app import app
from app import db
from flask import render_template, flash, redirect, request, url_for
from app.forms import SupplierForm, OrderForm, ItemForm
from app.models import Supplier, Order, Item, Status

@app.route('/')
@app.route('/index')
def index():
    row_titles = ['Nome', 'Endereço']
    suppliers = Supplier.query.all()
    data = []
    for p in suppliers:
        if p.status != Status.DELETED:
            p_dict = {}
            p_dict['name'] = p.name
            p_dict['address'] = p.address
            data.append(p_dict)
    return render_template('index.html', title='Fornecedores', the_row_titles=row_titles, the_data=data)


@app.route('/newitem', methods=['GET', 'POST'])
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data)
        db.session.add(item)
        db.session.commit()
        flash('Novo item cadastrado {}'.format(form.name.data))
        return redirect(url_for('index'))
    return render_template('newitem.html', title='Cadastrar item', form=form)


@app.route('/listitems')
def list_items():
    items = Item.query.order_by('name')
    item_list = []
    for item in items:
        item_list.append(item.name)
    return render_template('listitems.html', data=item_list)


@app.route('/newsupplier', methods=['GET', 'POST'])
def new_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier.query.filter_by(name=form.name.data).first()
        # if I try to add a new supplier, but it was deleted (status = DELETED),
        # I should update its variables instead of creating a new record
        if supplier:
            supplier.contacts = form.contacts.data
            supplier.address = form.contacts.data
            supplier.portfolio = form.portfolio.data
            supplier.status = Status.ACTIVE
        else:
            p = Supplier(name=form.name.data, address=form.address.data,
                     contacts=form.contacts.data,portfolio=form.portfolio.data,
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
            supplier.address = form.contacts.data
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


@app.route('/neworder', methods=['GET', 'POST'])
def new_order():
    form = OrderForm()
    form.supplier.choices = [(g.id, g.name) for g in Supplier.query.filter(Supplier.status == Status.ACTIVE).order_by('name')]
    if form.validate_on_submit():
        supplier = Supplier.query.filter_by(name=form.supplier.data).first_or_404()
        t = Order(supllier_id=supplier.id)
        db.session.add(t)
        db.session.commit()
        flash('Nova transação cadastrada! Empresa={}, produtos={}'.format(
            form.supplier.data, form.items.data))
        return redirect(url_for('index'))
    return render_template('neworder.html', form=form)
