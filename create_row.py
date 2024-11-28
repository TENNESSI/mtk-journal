from app import Size, db, app

with app.app_context():
	size_names = ["б/пл", "нал", "б/н"]
	for size_ in size_names:
		try:
			size = Size(size_name=size_)
			db.session.add(size)
			db.session.commit()
			print("успех")
		except Exception as e:
			print(f'Ошибка при регистрации пользователя: {e}')