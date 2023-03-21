import unittest
from werkzeug.security import generate_password_hash
from typing import Dict, Optional
from app import create_app
import os
from sqlalchemy import create_engine
from App.models import Base, User, Tasks, Worker
from flask import current_app
from App.utils import DatabaseTableMixin


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
        self.WorkerManager = DatabaseTableMixin(Worker)

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
        },
            lumuli.to_json()
        )
        self.assertEqual(1, len([item for item in iter(self.userManager)]))
        self.assertIsNotNone(lumuli)
        self.assertGreater(len(self.userManager), 0)

        response = self.client.get('/users', headers={
            'content-type': 'application/json'
        })
        json_data = response.json
        self.assertIsInstance(json_data, dict)
        self.assertGreater(len(json_data['users']), 0)
        self.assertEqual(response.status_code, 200)

    def testTaskCreation(self):
        self.assertEqual(0, len([items for items in iter(self.TaskManager)]))
        task_1payload: Dict[str, str] = {
            "description": "Create a latex file to edit the below configurations and present it in a nice looking userinterface",
            "Amount": int(30000),
            "creator_id": 1,
            "title": "great content"
        }
        self.assertIsNone(self.TaskManager.__create_item__(task_1payload))
        self.assertGreater(len(self.TaskManager), 0)
        self.assertEqual(len(self.TaskManager), 1)

        self.task_1 = self.TaskManager[1]
        self.assertIsNotNone(self.task_1)
        

        #test task claimingq by worker

        # Worker creation

        worker_payload = {
            "name": "lumuli",
            "email": "lumulikenreagan@gmail.com",
            "password": "test",
            "phone": "254710850362"
        }
    
        self.WorkerManager.__create_item__(worker_payload)
        self.assertEqual(len(self.WorkerManager), 1)

        # claim task by worker
        task_2payload: Dict[str, Optional[str, int]] = {
            "description": "Create a python file to send email asynchronously",
            "Amount": int(3000),
            "creator_id": 1
        }

        self.worker = self.client.get('/worker/')
        self.assertTrue(self.worker.status_code, 200)
        print(self.worker)

        self.TaskManager.__create_item__(task_2payload)
        self.assertEqual(len(self.TaskManager), 1)
        self.assertEqual(len(self.TaskManager), 1)

    def testResponse(self):
        response = self.client.get('/index')
        self.assertTrue(response.status_code, 200)
        self.assertIsInstance(response.data, bytes)

    def testTaskEndpoints(self):
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)

        # test task creation

if __name__ == '__main__':
    unittest.main()
