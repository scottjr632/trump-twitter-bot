import requests
import json


class _AuthInfo:
    """ _AuthInfo is a private class used to store
    credentials from a auth file """
    url = ''
    username = ''
    password = ''
    token_name = ''


def _read_auth_info_from_file(file_path) -> _AuthInfo:
    """ _read_auth_info_from_file is a private function that reads a file  
    that holds credentials and stores them in a _AuthInfo object which is returned """
    auth_info = _AuthInfo()
    with open(file_path, 'r') as file:
        auth_info.__dict__ = json.loads(file.read())

    return auth_info


class Authentication(object):
    def __init__(self, auth_file_path='auth.json', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._file_path = auth_file_path
        self.auth_token = None

    def get_auth_token(self) -> int:
        """ 
        Uses credentials stores in file given as `file_path`
        it will try to authenticate to the url given with the given credentials
        ans then set the `auth_token` value. It returns the response code """
        auth_info = _read_auth_info_from_file(self._file_path)
        body = {'email': auth_info.username, 'password': auth_info.password}
        resp = requests.post(auth_info.url, json=body)
        if resp.status_code != 200:
            return resp.status_code

        self.auth_token = resp.json()[auth_info.token_name]
        return resp.status_code

    def get_bearer_header(self) -> dict:
        """ Returns a dict with the Authentication header. E.G. Authorization Bearer {auth_token} """
        return {'Authorization': 'Bearer %s' % self.auth_token}

    def rebounce_on_401(self, fn, *args, **kwargs) -> int:
        """ 
        Accepts a function and its arguments that returns a status code.

        If the returned status code is 401 this will try to re-authenticate
        and then try the requests again. 
        
        It will return the response code after 10 attempts """
        attempts = 0
        resp_code = fn(*args, **kwargs)
        while resp_code == 401 and attempts < 10:
            print('Trying to authenticate %s\t Attempts: %s' % (resp_code, attempts))
            self.get_auth_token()
            resp_code = fn(*args, **kwargs)
            attempts += 1

        return resp_code
