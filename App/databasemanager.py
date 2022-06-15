from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from App.models import Base
#
# Base.metadata.create_all(create_engine('sqlite:///master.sqlite'))


class DatabaseContextManager:
    def __init__(self):
        self.databasefilename: str = 'sqlite:///test.db' if current_app.config['ENVIRONMENT'] == 'testing' else 'sqlite:///master.sqlite'
        self.engine = create_engine(self.databasefilename,connect_args={
                "check_same_thread": False
            }
        )
        self.Session = sessionmaker(bind=self.engine)

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
