from app import app
from app import db
from flask import render_template, flash, redirect, url_for
from app.forms import ProviderForm, TransactionForm
from app.models import Provider, Transaction

@app.route('/')
@app.route('/index')
def index():
    row_titles = ['Nome', 'Endereço']
    providers = Provider.query.all()
    data = []
    for p in providers:
        p_dict = {}
        p_dict['name'] = p.name
        p_dict['address'] = p.address
        data.append(p_dict)
    return render_template('index.html', title='Fornecedores', the_row_titles=row_titles, the_data=data)


@app.route('/newprovider', methods=['GET', 'POST'])
def new_provider():
    form = ProviderForm()
    if form.validate_on_submit():
        p = Provider(name=form.name.data, address=form.address.data)
        db.session.add(p)
        db.session.commit()
        flash('Novo fornecedor cadastrado {}, endereço={}'.format(
            form.name.data, form.address.data))
        return redirect(url_for('index'))
    return render_template('newprovider.html', title='Cadastrar', form=form)


@app.route('/provider/<providername>')
def provider(providername):
    provider = Provider.query.filter_by(name=providername).first_or_404()
    return render_template('provider.html', title='Detalhes', provider=provider)



@app.route('/newtransaction', methods=['GET', 'POST'])
def new_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        t = Transaction(company=form.company.data, products=form.products.data)
        db.session.add(t)
        db.session.commit()
        flash('Nova transação cadastrada! Empresa={}, produtos={}'.format(
            form.company.data, form.products.data))
        return redirect(url_for('index'))
    return render_template('newtransaction.html', title='Cadastrar', form=form)

