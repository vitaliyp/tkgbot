import shutil
import os

import pytest

import settings

db_path = ('testdata',)
db_filename = 'database'
db_dir_path = os.path.join(*db_path)

db_path_in_url = '/'.join(db_path)
settings.database_url = f'sqlite:///{db_path_in_url}/database'
settings.database_debug_output = False

import database
from models import Node


@pytest.fixture(scope='function')
def db():
    shutil.rmtree(db_dir_path, ignore_errors=True)
    os.makedirs(db_dir_path, exist_ok=True)

    database.init_db()

    yield None

    shutil.rmtree(db_dir_path, ignore_errors=False)


def test_db_creation(db):
    assert os.path.isfile(os.path.join(db_dir_path, db_filename))


def test_insertion(db):
    with database.session_scope() as session:
        node = Node(id=123, name='Test Node', parent_id=-1)
        session.add(node)

