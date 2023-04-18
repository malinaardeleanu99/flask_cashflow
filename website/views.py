from io import BytesIO
from flask import Blueprint, render_template, request, flash, redirect, send_file, url_for
from flask_login import login_required, current_user
from .models import Partener, Transaction,Sold
from . import db
from datetime import date, datetime
import flask_excel as excel
from openpyxl import Workbook

views = Blueprint('views', __name__)

def download_excel(transactions, file_name):
    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'TIP', 'DATA', 'PARTENER', 'SUMA', 'STATUS'])
    for trans in transactions:
        ws.append([trans.id, trans.trans_type, trans.trans_date, trans.trans_partener, trans.trans_sum, trans.trans_status])
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return send_file(file_stream, download_name=f"{file_name}.xlsx", as_attachment=True)

def transform(transactions):
    transactions_new = transactions
    for transaction in transactions_new:
        partener_id = transaction.trans_partener
        partener = Partener.query.filter_by(id = partener_id).first()
        transaction.trans_partener = partener.partener_name
        if transaction.trans_type == 1:
            transaction.trans_type = "PLATA"
        else:
            transaction.trans_type = "INCASARE"
    return transactions_new


@views.route('/', methods = ['GET','POST'])
@login_required
def home():
    transactions_today = Transaction.query.filter_by(trans_date = date.today()).all()
    transactions_today_new = transform(transactions_today)
    sum_plati = 0
    sum_incasari = 0
    no_pending = 0
    sold = Sold.query.order_by(Sold.id.desc()).first().sold_banca
    for trans in transactions_today_new:
        if trans.trans_type =='PLATA':
            sum_plati += trans.trans_sum
        else:
            sum_incasari += trans.trans_sum
        if trans.trans_status == 'Pending':
            no_pending +=1
    sold = sold + sum_incasari - sum_plati
    if request.method == 'POST':
        if request.form.get('excel') == 'download':
            return download_excel(transactions_today_new, "transactions_today")
    return render_template("home.html", user=current_user, trans_today=transactions_today_new, sum_incasari=sum_incasari, sum_plati=sum_plati, date = date.today(), no_pending = no_pending, sold = sold)

@views.route('/add_transaction', methods = ['GET','POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        trans_type = request.form.get('trans_type')
        trans_partener = request.form.get('trans_partener')
        trans_sum = request.form.get('trans_sum')
        trans_date = request.form.get('trans_date')
        trans_date_ok = datetime.strptime(trans_date, '%Y-%m-%d').date()
        if request.form.get('check_status'):
            trans_status = 'Completed'
        else:
            trans_status = 'Pending'
        new_transaction = Transaction(trans_type = trans_type, trans_partener=trans_partener, trans_sum = trans_sum, trans_date = trans_date_ok, trans_status=trans_status)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Tranzactie creata', category= 'success')
        return redirect(url_for('views.home'))
    parteners = Partener.query.order_by(Partener.partener_name).all()
    return render_template("add_transaction.html", user=current_user, parteners = parteners)


@views.route('/all_transactions', methods = ['GET','POST'])
@login_required
def all_transactions():
    transactions_all = Transaction.query.order_by(Transaction.trans_date).all()
    parteners = Partener.query.order_by(Partener.partener_name).all()
    transactions_all_new = transform(transactions_all)
    sum_plati = 0
    sum_incasari = 0
    no_pending = 0
    for trans in transactions_all_new:
        if trans.trans_type =='PLATA':
            sum_plati += trans.trans_sum
        else:
            sum_incasari += trans.trans_sum
        if trans.trans_status == 'Pending':
            no_pending +=1

    if request.method == 'POST':
        if request.form.get('excel') == 'download':
            return download_excel(transactions_all_new, "transactions_all")
           
    return render_template("all_transactions.html", user=current_user, parteners = parteners, trans_all=transactions_all_new, sum_incasari=sum_incasari, sum_plati=sum_plati, no_pending = no_pending)

@views.route('update/<pk>/', methods = ['GET','POST'])
@login_required
def update_transaction(pk):
    transaction = Transaction.query.filter_by(id = int(pk)).first()
    partener = Partener.query.filter_by(id = transaction.trans_partener).first().partener_name
    if transaction.trans_type == 1:
        t_type = 'PLATA'
    else:
        t_type = 'INCASARE'
    if request.method == 'POST':
        transaction.trans_sum = request.form.get('trans_sum')
        trans_date = request.form.get('trans_date')
        trans_date_ok = datetime.strptime(trans_date, '%Y-%m-%d').date()
        transaction.trans_date = trans_date_ok
        if request.form.get('check_status'):
            transaction.trans_status = 'Completed'
        else:
            transaction.trans_status = 'Pending'
        db.session.commit()

        flash('Tranzactie modificata', category= 'success')
        return redirect(url_for('views.home'))
    
    return render_template("update_transaction.html", user=current_user, trans_id = transaction.id, trans_type = t_type, trans_partener = partener, trans_sum = transaction.trans_sum, trans_status = transaction.trans_status, trans_date = transaction.trans_date)


@views.route('delete/<pk>/', methods = ['GET','POST'])
@login_required
def delete_transaction(pk):
    transaction = Transaction.query.filter_by(id = int(pk)).first()
    if request.method == 'POST':
        if request.form.get('da') == 'da':
            db.session.delete(transaction)
            db.session.commit()
            flash('Tranzactie stearsa', category= 'success')
            return redirect(url_for('views.home'))
        elif  request.form.get('nu') == 'nu':
            return redirect(url_for('views.home'))
    return render_template("delete_transaction.html", user=current_user)


@views.route('/select_period/', methods = ['GET', 'POST'])
@login_required
def select_period():
    if request.method == 'POST':
        start = request.form.get('trans_start')
        finish = request.form.get('trans_finish')
        start_ok = datetime.strptime(start, '%Y-%m-%d').date()
        finish_ok = datetime.strptime(finish, '%Y-%m-%d').date()
        return redirect(url_for('views.period_transactions', start = start_ok, finish = finish_ok))
     
    return render_template("select_period.html", user = current_user)

@views.route('/period_transactions/<start> <finish>/', methods = ['GET','POST'])
@login_required
def period_transactions(start, finish):
    transactions_period = Transaction.query.filter(Transaction.trans_date <= finish).filter(Transaction.trans_date >= start).all()
    transactions_period_ok = transform(transactions_period)
    if request.method == 'POST':
        if request.form.get('excel') == 'download':
            return download_excel(transactions_period_ok, f"transactions_{start}_{finish}")
    return render_template("period_transactions.html", user = current_user, transactions=transactions_period_ok)
