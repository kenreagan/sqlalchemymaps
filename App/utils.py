from abc import ABC
from collections.abc import MutableMapping
from App.databasemanager import DatabaseContextManager
from App.models import Base, User, Worker
from typing import Iterable, List, Dict, Any, Union
from sqlalchemy import insert, update, select
from functools import wraps
from flask import request, make_response, current_app
import jwt
from prometheus_client import Summary
import requests
from App import mpesa
import queue

request_timer = Summary(
    'time_request_summary',
    'track endpoint request summary to track the slow endpoints'
)

def verify_worker_request_headers(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "Authorization" in request.headers:
            token = request.headers['Authorization'].split(' ')[-1]
            try:
                validator = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                with DatabaseContextManager() as context:
                    current_user = context.session.query(
                        Worker
                    ).filter(
                        Worker.id == int(validator['sub'])
                    ).first()
            except:
                return {
                    "message": "error decoding token"
                }
        else:
            return make_response({
                "Message": "Token Missing"
            }, 401)
        return func(current_user, *args, **kwargs)

    return wrapper

def verify_request_headers(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "Authorization" in request.headers:
            token = request.headers['Authorization'].split(' ')[-1]
            try:
                validator = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                with DatabaseContextManager() as context:
                    current_user = context.session.query(
                        User
                    ).filter(
                        User.id == int(validator['sub'])
                    ).first()
            except:
                return {
                    "message": "error decoding token"
                }
        else:
            return make_response({
                "Message": "Token Missing"
            }, 401)
        return func(current_user, *args, **kwargs)

    return wrapper

class DatabaseTableMixin(MutableMapping, ABC):

    def __init__(self, table: Base):
        self.table = table

    def __getitem__(self, item: int):
        with DatabaseContextManager() as contextmanager:
            response = contextmanager.session.query(self.table).filter_by(
                id=item
            ).first()
        return response

    def __create_item__(self, value: Dict[str, Any]):
        with DatabaseContextManager() as contextmanager:
            statement = insert(self.table).values(
                **value
            )
            try:
                contextmanager.session.execute(statement)
                contextmanager.commit()
            except Exception as e:
                print(f"{e!r}")
            finally:
                contextmanager.commit()

    def __setitem__(self, key, value: Dict[str, str]) -> Dict[str, str]:
        with DatabaseContextManager() as contextmanager:
            statement = update(self.table).where(
                self.table.id == key
            ).values(**value)
            contextmanager.session.execute(statement)
            contextmanager.commit()
        return value

    def __len__(self) -> int:
        with DatabaseContextManager() as contextmanager:
            return contextmanager.session.query(self.table).filter_by().count()

    def __iter__(self):
        with DatabaseContextManager() as contextmanager:
            for elements in contextmanager.session.query(self.table):
                yield elements

    def __delitem__(self, key):
        instance = self[key]
        with DatabaseContextManager() as contextmanager:
            contextmanager.session.delete(instance)
            contextmanager.commit()


def fetch_status(transaction_code) -> Union[None, Dict]:
    status = None
    if isinstance(transaction_code, str):
        data = mpesa.check_lipa_na_mpesa_status(
            transaction_code
        )
        return data
    return status