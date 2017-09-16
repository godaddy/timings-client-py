"""Module for PERF-API"""
from __future__ import division
import os
import requests

from six.moves import urllib
import yaml


class Perf():

    """ Performance Functions """
    def __init__(self, filespec=None):
        self._filespec = filespec
        self._conf = self._load_conf()

    def getapiparams(self, **kwargs):
        """merge default params with user overwrites"""
        data = dict(self._conf['api_params'])
        num_args = len(kwargs)

        if num_args > 0:
            if 'sla' in kwargs:
                data['sla'] = kwargs['sla']
            if 'debug' in kwargs:
                data['flags']['debug'] = kwargs['debug']
            if 'es_trace' in kwargs:
                data['flags']['esTrace'] = kwargs['es_trace']
            if 'es_create' in kwargs:
                data['flags']['esCreate'] = kwargs['es_create']
            if 'days' in kwargs:
                data['baseline']['days'] = kwargs['days']
            if 'perc' in kwargs:
                data['baseline']['perc'] = kwargs['perc']
            if 'padding' in kwargs:
                data['baseline']['padding'] = kwargs['padding']
            if 'search_url' in kwargs:
                data['baseline']['searchUrl'] = kwargs['search_url']

            if 'log' in kwargs and isinstance(kwargs['log'], dict):
                # Add extra items to data['log']
                data['log'].update(kwargs['log'])

        return data

    def injectjs(self, inject_type, mark=''):
        """Call injectjs and return decoded JS string"""
        if not mark:
            mark = 'visual_complete'

        data = {
            'injectType': inject_type,
            'visualCompleteMark': mark
        }

        inject_js = self._call_api(data, 'injectjs')

        if 'inject_code' in inject_js:
            return urllib.parse.unquote(inject_js['inject_code'])
        else:
            return False

    def usertiming(self, inject_js, api_params):
        """Call injectjs and return decoded JS string"""
        api_params['injectJS'] = inject_js

        usertiming = self._call_api(api_params, 'usertiming')

        if 'assert' in usertiming:
            return usertiming
        else:
            return False

    def navtiming(self, inject_js, api_params):
        """Call inject_js and return decoded JS string"""
        api_params['injectJS'] = inject_js

        navtiming = self._call_api(api_params, 'navtiming')

        if 'assert' in navtiming:
            return navtiming
        else:
            return False

    def apitiming(self, timing, url, api_params):
        """Call injectjs and return decoded JS string"""
        api_params['timing'] = timing
        api_params['url'] = url

        apitiming = self._call_api(api_params, 'apitiming')

        if 'assert' in apitiming:
            return apitiming
        else:
            return False

    def _call_api(self, data, endpoint):
        """Call the API and return response or False"""
        try:
            response = requests.post(
                self._conf['PERF_API_URL'] + endpoint,
                json=data, timeout=0.5
            )
            if not 200 <= response.status_code <= 299:
                return {'error': "Error: Unexpected response {}".format(response)}

            # json_obj = response.json()
            return response.json()
        except requests.exceptions.RequestException as err:
            print(err)
            return {'error': err}

    def _load_conf(self):
        """ load default or custom config """
        if self._filespec is None:
            self._filespec = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), 'default.yaml')

        return self._read_conf()

    def _read_conf(self):
        with open(self._filespec, 'r') as stream:
            try:
                conf = yaml.load(stream)
            except yaml.YAMLError as err:
                return err

        return conf
