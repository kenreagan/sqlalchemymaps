from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseContextManager:
	def __init__(self):
		self.Session = sessionmaker(bind=create_engine('sqlite:///test.db'))

	def __enter__(self):
		self.session = self.Session()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is not None:
			print(f"{exc_type}")
			self.session.rollback()
			self.session.close()
		self.session.close()

	def commit(self):
		self.session.commit()

	def rollback(self):
		self.session.rollback()
