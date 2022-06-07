import unittest
from werkzeug.security import generate_password_hash
from typing import Dict, Optional
from app import create_app
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from App.models import Base, User, Tasks, Role
from flask import current_app
from App.utils import DatabaseTableMixin, BaseMapper


class TestApplication(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(configuration_file='configuration.TestingConfig')
        self.app.context = self.app.app_context()
        self.app.context.push()
        Base.metadata.create_all(create_engine('sqlite:///test.db'))
        self.basePath = os.path.abspath(os.path.dirname(__file__))
        self.client = self.app.test_client(use_cookies=True)
        self.userManager = DatabaseTableMixin(User)
        self.TaskManager = DatabaseTableMixin(Tasks)
        self.RoleManager = DatabaseTableMixin(Role)
        self.roleMapper = BaseMapper()
        self.roleMapper.create_role_permission()

    def tearDown(self) -> None:
        self.app.context.pop()
        Base.metadata.drop_all(bind=create_engine('sqlite:///test.db'))
        os.unlink(os.path.join(self.basePath, 'test.db'))

    def testApplicationCreation(self):
        self.assertNotEqual(self.app, None)

    def testApplicationConfigurations(self):
        self.assertEqual(current_app.config['ENVIRONMENT'], 'testing')

    def testDatabaseCreation(self):
        self.assertIn('test.db', os.listdir(self.basePath))

    def testUserCreation(self):
        self.assertEqual(0, len([item for item in iter(self.userManager)]))
        self.assertEqual(self.userManager[1], None)
        self.assertIsNone(self.userManager.__create_item__({
            "name" : "Lumuli",
            "email": "lumuli@gmail.com",
            "phone": "+254794784462",
            "password": generate_password_hash('Lumuli1234#')
        }))
        lumuli = self.userManager[1]
        self.assertDictEqual({
            "phone": "+254794784462",
            'name': 'Lumuli',
            'email': 'lumuli@gmail.com',
            'Amount': 0,
            'permission': 0
        },
            lumuli.__getitem__('User').to_json()
        )
        self.assertEqual(1, len([item for item in iter(self.userManager)]))
        self.assertIsNotNone(lumuli)
        self.assertGreater(len(self.userManager), 0)

    def testTaskCreation(self):
        self.assertEqual(0, len([items for items in iter(self.TaskManager)]))
        task_1payload: Dict[str, str] = {
            "description": "Create a latex file to edit the below configurations and present it in a nice looking userinterface",
            "Amount": int(30000),
            "creator_id": 1
        }
        self.assertIsNone(self.TaskManager.__create_item__(task_1payload))
        self.assertGreater(len(self.TaskManager), 0)
        self.assertEqual(len(self.TaskManager), 1)

        self.task_1 = self.TaskManager[1]
        self.assertIsNotNone(self.task_1)

        task_2payload: Dict[str, Optional[str, int]] = {
            "description": "Create a python file to send email asynchronously",
            "Amount": int(3000),
            "creator_id": 1
        }

        self.TaskManager.__create_item__(task_2payload)
        self.assertEqual(len(self.TaskManager), 2)
        self.task_2 = self.TaskManager[2]

        self.assertGreater(self.task_1, self.task_2)
        self.TaskManager.__delitem__(2)
        self.assertEqual(len(self.TaskManager), 1)

    def testTaskClaiming(self):
        pass

    def testDetailsUpdate(self):
        pass

    def testRoleAssignment(self):
        pass

    def testSuperAdminRoles(self):
        pass

    def testWorkerRole(self):
        pass

    def testClientRole(self):
        self.assertGreater(len(self.RoleManager), 2)

    def testResponse(self):
        response = self.client.get('/index')
        self.assertTrue(response.status_code, 200)
        self.assertIsInstance(response.data, bytes)

    def testUserEndpoints(self):
        response = self.client.get('/users', headers={
            'content-type': 'application/json'
        })
        json_data = response.json
        self.assertIsInstance(json_data, dict)
        self.assertGreater(len(json_data['users']), 0)
        self.assertEqual(response.status_code, 200)

    def testTaskEndpoints(self):
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
