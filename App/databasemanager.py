from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from App.models import Base

Base.metadata.create_all(create_engine('mysql+pymysql://ken:Lumuli1234#@localhost/Workersite'))


class DatabaseContextManager:
    def __init__(self):
        self.databasefilename: str = 'sqlite:///test.db' if current_app.config['ENVIRONMENT'] == 'testing' else 'mysql+pymysql://ken:Lumuli1234#@localhost/Workersite'
        self.engine = create_engine(self.databasefilename, echo=True)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

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
