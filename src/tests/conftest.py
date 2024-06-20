import os
import pytest
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.test")


@pytest.fixture(scope='session')
def client():
    from main import app
    from fastapi.testclient import TestClient
    return TestClient(app)
