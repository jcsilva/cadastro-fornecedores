from app import app
from app import db
from flask import render_template, flash, redirect, url_for
from app.forms import SupplierForm, OrderForm, ItemForm
from app.models import Supplier, Order, Item

@app.route('/')
@app.route('/index')
def index():
    row_titles = ['Nome', 'Endereço']
    suppliers = Supplier.query.all()
    data = []
    for p in suppliers:
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
    items = Item.query.all()
    item_list = []
    for item in items:
        item_list.append(item.name)        
    return render_template('listitems.html', data=item_list)
    
    
@app.route('/newsupplier', methods=['GET', 'POST'])
def new_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        p = Supplier(name=form.name.data, address=form.address.data)
        db.session.add(p)
        db.session.commit()
        flash('Novo fornecedor cadastrado {}, endereço={}'.format(
            form.name.data, form.address.data))
        return redirect(url_for('index'))
    return render_template('newsupplier.html', title='Cadastrar', form=form)
    

@app.route('/supplier/<suppliername>')
def supplier(suppliername):
    supplier = Supplier.query.filter_by(name=suppliername).first_or_404()
    return render_template('supplier.html', title='Detalhes', supplier=supplier)



@app.route('/neworder', methods=['GET', 'POST'])
def new_order():
    form = OrderForm()
    if form.validate_on_submit():
        supplier = Supplier.query.filter_by(name=form.supplier_name.data).first_or_404()
        t = Order(supllier_id=supplier.id)
        db.session.add(t)
        db.session.commit()
        flash('Nova transação cadastrada! Empresa={}, produtos={}'.format(
            form.company.data, form.items.data))
        return redirect(url_for('index'))
    return render_template('neworder.html', title='Cadastrar', form=form)

