from app import app,db, Goods, Category, Podcategory

# with app.app_context():
#     tovar1 = Goods.query.get(4)
#     db.session.delete(tovar1)
#     db.session.commit()

with app.app_context():
    category = Category.query.get(5)
    try:
        db.session.delete(category)
        db.session.commit()
        print('Успех')
    except Exception as _e:
        print(f"Ошибка: {_e}")
