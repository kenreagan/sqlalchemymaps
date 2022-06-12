from abc import ABC
from collections.abc import MutableMapping
from App.databasemanager import DatabaseContextManager
from App.models import Base, Role
from enum import Enum
from typing import Iterable, List, Dict, Any
from sqlalchemy import insert, update, select


class Permissions(Enum):
    VIEW_TASK: int = 0  # anonymous user
    EDIT_TASK: int = 1  # worker && Client
    CREATE_TASK: int = 2  # Worker
    DELETE_TASK: int = 4  # Worker
    MODERATE_TASK: int = 8  # Superuser and Admin


class RolesManager:
    def __init__(self, name: str, value: Permissions = Permissions.VIEW_TASK):
        self.name = name
        self.value = value
        self.permissionstable: List[Permissions] = []
        self.permissionstable.append(self.value)


class RolesMapper(MutableMapping, ABC):
    class KeyListMapper:
        def __init__(self, role: str, permissions: Permissions) -> None:
            self.role = RolesManager(role)
            self.permissions = permissions


class BaseMapper(RolesMapper):
    def __init__(self):
        """
        >>> roles = [
        ...    {
        ...        "Admin": [Permissions.CREATE_TASK, Permissions.CREATE_TASK, Permissions.EDIT_TASK, Permissions.MODERATE_TASK],
        ...        'client': [Permissions.CREATE_TASK],
        ...        'worker': [Permissions.CREATE_TASK,]
        ...    }
        ...]
        >>> print(roles)
        """
        self.roles: List[RolesMapper.KeyListMapper] = []

    def __contains__(self, item) -> bool:
        for element in self.roles:
            return item in element

    def __iter__(self) -> Iterable:
        for elements in self.roles:
            yield elements

    def __len__(self):
        return len(self.roles)

    def __getitem__(self, item) -> List[Permissions]:
        """
        >>> admin = BaseMapper('Admin', [Permissions.EDIT_TASK, Permissions.CREATE_TASK, Permissions.VIEW_TASK, Permissions.DELETE_TASK, Permissions.MODERATE_TASK])
        >>> client = BaseMapper('client', [Permissions.CREATE_TASK, Permissions.VIEW_TASK, Permissions.EDIT_TASK, Permissions.DELETE_TASK])
        >>> anonymous = BaseMapper('anonymous', [Permissions.VIEW_TASK])
        >>> print(anonymous)
        ... [Permissions.VIEW_TASK]
        >>>

        :param item:
            role: str
            permissions: List[Permissions]
        :return: permissions of the users
        """
        if isinstance(item, str):
            for items in self.roles:
                if items.role.name == item:
                    return items.role.permissionstable

    def __setitem__(self, key: str, value) -> None:
        # Add permission to user administrators and superusers have more privileges
        if isinstance(value, Permissions):
            for items in self.roles:
                if items.role.name == key:
                    items.role.permissionstable.append(value)
            RolesManager(key, value)
            return self.roles.append(self.KeyListMapper(key, value))
        elif isinstance(value, list):
            for elements in value:
                self.__setitem__(key, elements)

    @staticmethod
    def create_role_permission():
        roles = BaseMapper()
        roles['Admin'] = [Permissions.VIEW_TASK, Permissions.CREATE_TASK, Permissions.DELETE_TASK,
                          Permissions.EDIT_TASK, Permissions.MODERATE_TASK]
        roles['Worker'] = [Permissions.VIEW_TASK, Permissions.EDIT_TASK]
        roles['Client'] = [Permissions.CREATE_TASK, Permissions.DELETE_TASK, Permissions.EDIT_TASK]
        roles['Visitor'] = [Permissions.VIEW_TASK]

        child = set([item.role.name for item in roles])

        for keys in child:
            with DatabaseContextManager() as contextmanager:
                role = contextmanager.session.query(Role).filter_by(rolename=keys).first()
                if role is None:
                    contextmanager.session.execute(
                        insert(
                            Role
                        ).values(
                            rolename=keys
                        )
                    )
                    contextmanager.commit()
                else:
                    role.reset_permission()
                    for permissions in roles[keys]:
                        role.add_permission(permissions)
                    role.default = (role.rolename == Permissions.VIEW_TASK.name)

                    statement = insert(Role).values(
                        rolename=keys
                    )
                    contextmanager.session.execute(statement)
                    # commit to database
                    contextmanager.commit()

    def __delitem__(self, key: Permissions):
        # downgrade the user role
        if isinstance(key, Permissions):
            pass


class DatabaseTableMixin(MutableMapping, ABC):
    """
        Allow for the indirect interaction of the application with the models
    """

    def __init__(self, table: Base):
        self.table = table

    def __getitem__(self, item: int) -> Iterable:
        with DatabaseContextManager() as contextmanager:
            statement = select(
                [self.table]
            ).where(self.table.id == item)
            response = contextmanager.session.execute(statement).first()
        return response

    def __create_item__(self, value: Dict[str, Any]):
        with DatabaseContextManager() as contextmanager:
            statement = insert(self.table).values(
                **value
            )
            try:
                contextmanager.session.execute(statement)
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
        instance = self.get(key)
        with DatabaseContextManager() as contextmanager:
            contextmanager.session.delete(instance.__getitem__(list(instance._asdict().keys())[0]))
            contextmanager.commit()
