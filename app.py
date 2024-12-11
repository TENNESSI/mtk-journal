from datetime import datetime
from itertools import count

from flask import Flask, render_template, url_for, request, redirect, flash, get_flashed_messages, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'secretkey'
app.config['UPLOAD_FOLDER'] = 'uploadimg'
db = SQLAlchemy(app)
times = ['11:00','11:15','11:30','11:45','12:00','12:15','12:30','12:45','13:00','13:15','13:30','13:45','14:00','14:15','14:30','14:45','15:00','15:15','15:30','15:45','16:00','16:15','16:30','16:45','17:00','17:15','17:30','17:45','18:00']

class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer(), primary_key=True)
    admin_name = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(127))

    def get_id(self):
        return (self.admin_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Goods(db.Model):
    __tablename__ = 'goods'
    goods_id = db.Column(name='goods_id', type_=db.Integer(), primary_key=True)
    time = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(), nullable=True)
    size_id = db.Column(db.Integer(), nullable=True)
    category_id = db.Column(db.Integer(), nullable=True)
    date = db.Column(db.Integer(), nullable=True)
    peoples = db.Column(db.Integer(), nullable=True)
    orgname = db.Column(db.String(100), nullable=True)
    fio = db.Column(db.String(), nullable=True)
    autor = db.Column(db.String, nullable=False)
    description = db.Column(db.String(), nullable=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.goods_id, self.date)

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(60), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

class Size(db.Model):
    size_id = db.Column(db.Integer, primary_key=True)
    size_name = db.Column(db.String(60), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

@login.user_loader
def load_user(id):
    return db.session.get(Admin, int(id))

@app.route('/')
@app.route('/index')
def index():
    goods = []
    for good in Goods.query.order_by(desc(Goods.created_on)).all():
        goods.append(good.date)
    goods = list(dict.fromkeys(goods))
    sizes = {}
    categories = {}
    for size in Size.query.order_by(desc(Size.created_on)).all():
        sizes.update({size.size_id: size.size_name})
    for category in Category.query.order_by(desc(Category.created_on)).all():
        categories.update({category.category_id: category.category_name})
    return render_template('index.html', goods=goods, categories=categories, sizes=sizes)

@app.route('/<string:date>')
def show_goods(date):
    goods = Goods.query.filter_by(date=date).all()
    sizes = {}
    categories = {}
    for size in Size.query.order_by(desc(Size.created_on)).all():
        sizes.update({size.size_id: size.size_name})
    for category in Category.query.order_by(desc(Category.created_on)).all():
        categories.update({category.category_id: category.category_name})
    return render_template('goodcard_noadmin.html', goods=goods, sizes=sizes, categories=categories,date=date)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = db.session.query(Admin).filter(Admin.admin_name == request.form['admin_name']).first()

        if admin is not None:
            if not admin.check_password(request.form['password']):
                flash('Пароль неверный')
                return render_template('admin_login.html')

            login_user(admin)
            session['username'] = admin.admin_name
            autor = session['username']
            return render_template('admin_panel.html',autor=autor)
        else:
            flash('Пользователя не существует.')
    if 'username' not in session:
        return render_template('admin_login.html')
    else:
        autor = session['username']
        return render_template('admin_panel.html',autor=autor)

@app.route('/out')
def out():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/categories', methods=['GET'])
def categories():
    if 'username' not in session:
        return redirect('/admin')
    else:
        categories = Category.query.order_by(desc(Category.created_on)).all()
        autor = session['username']
        return render_template('categories.html',categories=categories, autor=autor)

@app.route('/admin/categories/add', methods=['GET','POST'])
def add_category():
    if 'username' not in session:
        return redirect('/admin')
    else:
        if request.method == 'POST':
            category_name = request.form['category_name']
            if len(category_name) > 0 and len(category_name) < 256:
                category = Category(category_name=category_name)
                try:
                    db.session.add(category)
                    db.session.commit()
                except Exception as e:
                    flash(f'Возникла ошибка при записи в базу данных: {e}')
                else:
                    return redirect((url_for('categories')))
            else:
                flash('Ошибка, длина полей не соответствует стандартам.')
        autor = session['username']
        return render_template('newcategory.html',autor=autor)

@app.route('/admin/goods', methods=['GET','POST'])
def goods():
    if 'username' not in session:
        return redirect('/admin')
    else:
        autor = session['username']
        goods = []
        for good in Goods.query.order_by(desc(Goods.created_on)).all():
            goods.append(good.date)
        goods = list(dict.fromkeys(goods))
        sizes = {}
        categories = {}
        for size in Size.query.order_by(desc(Size.created_on)).all():
            sizes.update({size.size_id: size.size_name})
        for category in Category.query.order_by(desc(Category.created_on)).all():
            categories.update({category.category_id: category.category_name})
        return render_template('goods.html', goods=goods, categories=categories, sizes=sizes, autor=autor)

@app.route('/admin/goods/add', methods=['GET', 'POST'])
def new_good():
    if 'username' not in session:
        return redirect('/admin')
    else:
        if request.method == 'POST':
            time = request.form['time']
            orgname =  request.form['orgname']
            size_id = request.form['size_id']
            peoples = request.form['peoples']
            category_id = request.form['category_id']
            phone = request.form['phone']
            fio = request.form['fio']
            autor = session['username']
            date = request.form['date']
            description = request.form['description']

            if len(time) > 0 and len(orgname) < 256:
                goods = Goods(time=time, orgname=orgname, size_id=size_id, peoples=peoples, category_id=category_id, phone=phone, fio=fio, autor=autor,date=date,description=description)

                try:
                    db.session.add(goods)
                    db.session.commit()
                except Exception as e:
                    flash(f'Возникла ошибка при записи в базу данных: {e}')
                else:
                    return redirect((url_for('goods')))
            else:
                flash('Ошибка, длина полей не соответствует стандартам.')
        autor = session['username']
        categories = Category.query.order_by(desc(Category.created_on)).all()
        sizes = Size.query.order_by(desc(Size.created_on)).all()
        return render_template('newgood.html', categories = categories, sizes=sizes,autor=autor,times=times)

@app.route('/admin/sizes', methods = ['GET'])
def sizes():
    if 'username' not in session:
        return redirect('/admin')
    else:
        sizes = Size.query.order_by(desc(Size.created_on)).all()
        return render_template('sizes.html', sizes=sizes)

@app.route('/admin/sizes/add', methods = ['GET', 'POST'])
def add_sizes():
    if 'username' not in session:
        return redirect('/admin')
    else:
        if request.method == 'POST':
            size_name = request.form['size_name']
            if len(size_name) > 0 and len(size_name) < 256:
                size = Size(size_name=size_name)
                try:
                    db.session.add(size)
                    db.session.commit()
                except Exception as e:
                    flash(f'Возникла ошибка при записи в базу данных: {e}')
                else:
                    return redirect((url_for('sizes')))
            else:
                flash('Ошибка, длина полей не соответствует стандартам.')
        return render_template('newsize.html')

@app.route('/admin/goods/<string:date>', methods = ['GET'])
def get_good_for_date(date):
    if 'username' not in session:
        return redirect('/admin')
    else:
        goods = Goods.query.filter_by(date=date).all()
        sizes = {}
        categories = {}
        for size in Size.query.order_by(desc(Size.created_on)).all():
            sizes.update({size.size_id: size.size_name})
        for category in Category.query.order_by(desc(Category.created_on)).all():
            categories.update({category.category_id: category.category_name})
        return render_template('goodcard.html', goods=goods,sizes=sizes,categories=categories)

@app.route('/admin/goods/<string:date>/<int:goods_id>', methods = ['GET','POST'])
def edit(goods_id,date):
    if 'username' not in session:
        return redirect('/admin')
    else:
        good = Goods.query.get(goods_id)
        if request.method == 'POST':
            good.time = request.form['time']
            good.orgname = request.form['orgname']
            good.size_id = request.form['size_id']
            good.peoples = request.form['peoples']
            good.category_id = request.form['category_id']
            good.phone = request.form['phone']
            good.fio = request.form['fio']
            good.autor = session['username']
            good.date = request.form['date']
            good.description = request.form['description']

            if len(good.time) > 0 and len(good.orgname) < 256:
                try:
                    db.session.commit()
                except Exception as e:
                    flash(f'Возникла ошибка при записи в базу данных: {e}')
                else:
                    return redirect(f'/admin/goods/{date}')
            else:
                flash('Ошибка, длина полей не соответствует стандартам.')
        autor = session['username']
        categories = Category.query.order_by(desc(Category.created_on)).all()
        sizes = Size.query.order_by(desc(Size.created_on)).all()
        return render_template('edit.html', categories=categories, sizes=sizes, autor=autor, good=good, times=times)

@app.route('/admin/goods/<string:date>/<int:goods_id>/delete', methods = ['GET'])
def delete(goods_id,date):
    if 'username' not in session:
        return redirect('/admin')
    else:
        good = Goods.query.get(goods_id)
        try:
            db.session.delete(good)
            db.session.commit()
        except Exception as _e:
            flash(f'Ошибка удаления записи: {_e}')
            return redirect(f'/admin/goods/{date}')
        else:
            if Goods.query.filter_by(date=date).all() == []:
                return redirect('/admin/goods')
            else:
                return redirect(f'/admin/goods/{date}')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)