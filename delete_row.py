from app import app,db, Goods, Category

# with app.app_context():
#     tovar1 = Goods.query.get(4)
#     db.session.delete(tovar1)
#     db.session.commit()

for i in [1,2,3,4,5]:
    with app.app_context():
        category = Goods.query.get(i)
        try:
            db.session.delete(category)
            db.session.commit()
            print('Успех')
        except Exception as _e:
            print(f"Ошибка: {_e}")
