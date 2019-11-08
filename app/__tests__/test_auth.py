import logging

import requests
import pytest

from app.auth import Authentication, _read_auth_info_from_file, _AuthInfo


class MockedResponse:
    status_code = 600
    
    def __repr__(self):
        return '<Response [%s]>' % self.status_code


@pytest.fixture
def auth_service():
    yield Authentication()


@pytest.fixture
def patch_file_open_for_auth_info(monkeypatch):
    class open:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self, *args, **kwargs):
            return self
        def __exit__(self, *args, **kwargs):
            return self
        def read(self):
            return '{"url": "test", "username": "hello", "password": "test", "token_name": "token"}'

    monkeypatch.setattr('builtins.open', open)


@pytest.fixture
def mock_get_requests(monkeypatch):
    old_get = requests.get
    def mock_get(uri, *args, **kwargs):
        return MockedResponse()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture
def mock_post_authentication_valid(monkeypatch):
    class MockedAuthResponse(MockedResponse):
        status_code = 200
        def json(self):
            return {
                'token': 'token'
            }

    def mocked_post(*args, **kwargs):
        return MockedAuthResponse()

    monkeypatch.setattr(requests, 'post', mocked_post)


@pytest.fixture
def mock_post_authentication_invalid(monkeypatch):
    class MockedUnAuthResponse(MockedResponse):
        status_code = 401

    def mocked_post(*args, **kwargs):
        return MockedUnAuthResponse()

    monkeypatch.setattr(requests, 'post', mocked_post)


def test_read_auth_info_from_file(patch_file_open_for_auth_info):
    auth_info = _read_auth_info_from_file('test file')
    assert auth_info.url == 'test'
    assert auth_info.username == 'hello'
    assert auth_info.password == 'test'
    assert auth_info.token_name == 'token'


def test_get_auth_token_valid(mock_post_authentication_valid, patch_file_open_for_auth_info, auth_service):
    status = auth_service.get_auth_token()
    assert status == 200
    assert auth_service.auth_token == 'token'


def test_get_auth_token_invalid(mock_post_authentication_invalid, patch_file_open_for_auth_info, auth_service):
    status = auth_service.get_auth_token()
    assert status != 200
    assert auth_service.auth_token is None


def test_rebounce_on_401_valid(mock_post_authentication_valid, patch_file_open_for_auth_info, auth_service):
    status = auth_service.rebounce_on_401(lambda *args, **kwargs: 401)
    assert auth_service.auth_token == 'token'


def test_rebounce_on_401_invalid_creds(mock_post_authentication_invalid, patch_file_open_for_auth_info, auth_service):
    with pytest.raises(Exception):
        status = auth_service.rebounce_on_401(lambda *args, **kwargs: 401)
        
        assert status == 401
        assert auth_service.auth_token is None


def test_get_bearer_header(auth_service):
    test_token = 'test-token'
    auth_service.auth_token = test_token
    assert auth_service.get_bearer_header() == {'Authorization': 'Bearer %s' % test_token}


def test_fixture(auth_service):
    assert auth_service.auth_token is None


def test_merge_kwargs_with_headers(auth_service):
    table = [
        {
            'vars': {'a': 'b', 'c': 'd'}, 
            'expect': {
                'a': 'b', 'c': 'd',
                'headers': {
                    'Authorization': 'Bearer %s' % auth_service.auth_token
                }
            }
        },
    ]

    for test in table:
        assert auth_service._merge_kwargs_with_headers(**test['vars']) == test['expect']
