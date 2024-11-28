from app import Admin, db, app

with app.app_context():
	username = "Константин"
	password = "12345"
	try:
		admin = Admin(admin_name=username)
		admin.set_password(password)
		db.session.add(admin)
		db.session.commit()
		print("успех")
	except Exception as e:
		print(f'Ошибка при регистрации пользователя: {e}')