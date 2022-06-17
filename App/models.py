from __future__ import annotations

from typing import Dict, Optional
from flask import current_app
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship, backref
import datetime
import jwt

Base = declarative_base()


class AuthenticationMixin:
    def generate_token(self, userid: int):
        payload: Dict[str, Optional] = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=2, minutes=0),
            "iat": datetime.datetime.utcnow(),
            "sub": userid
        }
        return jwt.encode(payload, key=current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, key=current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return {
                "code": 404,
                "status": "ExpiredSignatureError",
                "message": "Expired token",
                "errors": {
                    "": ""
                }
            }
        except jwt.InvalidTokenError:
            return {
                "code": 403,
                "status": "InvalidTokenError",
                "message": "Invalid token used",
                "errors": {
                    "": ""
                }
            }

class Worker(Base):
    __tablename__ = 'workers'
    id = Column(Integer, primary_key = True)
    userid = Column(Integer, ForeignKey('user.id'), nullable=False)
    taskid = Column(Integer, ForeignKey('tasks.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        #validate user

    def __repr__(self):
        return f"{self.__class__.__qualname__}(" \
                f"userid={self.userid}"\
               f"taskid={self.taskid})"


class User(AuthenticationMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String)
    account = Column(Integer, nullable=False, default=0)
    is_admin = Column(Boolean, default=False)
    tasks = relationship('Worker', lazy='dynamic', backref=backref('taskclaimed'))
    permission = Column(Integer, ForeignKey('roles.id'), nullable=False, default=0)
    task_created = relationship('Tasks', lazy='dynamic', backref=backref('creator'), cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs) -> None:
        super(User, self).__init__(*args, **kwargs)
        if self.permission is None:
            self.permission = 1

    def __repr__(self):
        return f'{self.__class__.__qualname__}(name={self.name!r}, email={self.email!r},' \
               f'phone={self.phone!r}, account={self.account!r})'

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            pass
        raise NotImplementedError('Incomporable task')

    def __lt__(self, other) -> bool:
        pass

    def __gt__(self):
        pass

    def __hash__(self):
        return hash((self.name, self.email, self.phone, self.permission,))

    def is_able(self, permission) -> bool:
        """
        >>> from App.utils import Permissions
        >>> x = User().isable(Permissions.EDIT_TASK)
        >>> print(x)
        ... False
        :param permission:
        :return: bool
        """
        return self.permission is not None


    def to_json(self):
        return {
            'name': self.name,
            'email': self.email,
            'Amount': 0,
            'permission': self.permission,
            'phone': self.phone
        }


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, nullable=False)
    rolename = Column(String)
    default = Column(Boolean, index=True)
    permission = Column(Integer)
    user = relationship('User', lazy='joined', backref=backref('roles'), cascade="all, delete-orphan")

    def to_json(self):
        return {
            'id': self.id,
            'name': self.rolename,
            'permission': self.permission
        }

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.rolename}, permission={self.permission!r})"

    def add_permission(self, permission):
        if isinstance(permission, list):
            for permissions in permission:
                self.add_permission(permissions.value)
        else:
            if not self.has_permission(permission.value):
                self.permission += permission.value

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permission -= permission

    def reset_permission(self):
        self.permission = 1

    def has_permission(self, permission):
        return self.permission & permission == permission


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, nullable=False, primary_key=True)
    description = Column(String, nullable=False)
    Amount = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    attachment = relationship('Attachment', lazy='dynamic', backref='task', cascade="all, delete-orphan")
    payment_status = Column(String, default='paid')
    progress_status = Column(String, default="unclaimed")
    worker = relationship('Worker', lazy='dynamic', backref=backref('worker'))

    def __repr__(self):
        return f"{self.__class__.__qualname__}(Amount={self.Amount}, creator id={self.creator_id})"

    def __eq__(self, other) -> bool:
        if self.__class__ == other.__class__:
            return self.Amount == other.Amount
        raise NotImplementedError('Incomparable Types')

    def __gt__(self, other) -> bool:
        if self.__class__ == other.__class__:
            return self.Amount > other.Amount
        raise NotImplementedError('Incomparable Types')

    def __lt__(self, other) -> bool:
        if self.__class__ == other.__class__:
            return self.Amount < other.Amount
        raise NotImplementedError('Incomparable Types')

    def __ne__(self, other) -> bool:
        if self.__class__ == other.__class__:
            return self.Amount != other.Amount
        raise NotImplementedError('Incomparable Types')

    def __hash__(self):
        return hash((self.Amount, self.description,))

    def to_json(self):
        return {
            "Amount": self.Amount,
            "description": self.description,
            "creator_id": self.creator_id
        }


class Attachment(Base):
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key=True, nullable=False)
    attachment_name = Column(String, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)

    def __repr__(self):
        pass
