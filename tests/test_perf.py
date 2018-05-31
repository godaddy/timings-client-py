from unittest import TestCase

import requests
import requests_mock
from flexmock import flexmock
from nose_parameterized import parameterized

from timingsclient.perf import Perf
from . import data


class TestPerfClient(TestCase):
    def setUp(self):
        self.perf_client = Perf()

    def test_call_api_happy_path(self):
        url = 'http://bunkendpoint.com/'
        api_timeout = 3
        self.perf_client._conf = {
            'PERF_API_URL': url,
            'api_timeout': api_timeout
        }
        data = {'some': 'data'}
        endpoint = "navtiming"
        expected_response = {'diditwork': True}

        with requests_mock.Mocker() as m:
            m.post(url + endpoint, json=expected_response, status_code=201)
            response = self.perf_client._call_api(data=data, endpoint=endpoint)

        self.assertEqual(response, expected_response)

    def test_call_api_bad_status_code_from_api(self):
        url = 'http://bunkendpoint.com/'
        api_timeout = 0
        self.perf_client._conf = {
            'PERF_API_URL': url,
            'api_timeout': api_timeout
        }
        data = {'some': 'data'}
        endpoint = "navtiming"
        fake_error = "something went wrong"
        expected_response = {'error': "Error: Unexpected response '{}'".format(fake_error)}

        with requests_mock.Mocker() as m:
            m.post(url + endpoint, text=fake_error, status_code=400)
            response = self.perf_client._call_api(data=data, endpoint=endpoint)

        self.assertEqual(response, expected_response)

    def test_call_api_request_exception(self):
        url = 'http://bunkendpoint.com/'
        api_timeout = 3
        self.perf_client._conf = {
            'PERF_API_URL': url,
            'api_timeout': api_timeout
        }
        data = {'some': 'data'}
        endpoint = "navtiming"
        fake_error = "something went wrong"
        expected_response = {'error': fake_error}

        flexmock(requests).should_receive('post').and_raise(requests.exceptions.RequestException, fake_error)

        response = self.perf_client._call_api(data=data, endpoint=endpoint)

        self.assertEqual(response, expected_response)

    def test_usertiming_assert_not_in_response(self):
        api_params = {}
        flexmock(self.perf_client).should_receive("_call_api").with_args(api_params, 'usertiming').and_return({})
        response = self.perf_client.usertiming(data.INJECT_JS, api_params=api_params)
        self.assertFalse(response)

    @parameterized.expand([(assertion_value,) for assertion_value in [True, False]])
    def test_usertiming_assert_in_response(self, assertion_value):
        api_params = {}
        flexmock(self.perf_client).should_receive("_call_api").with_args(api_params, 'usertiming').and_return({'assert': assertion_value})
        response = self.perf_client.usertiming(data.INJECT_JS, api_params=api_params)
        self.assertEqual(response['assert'], assertion_value)
