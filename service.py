'''highly obfuscated'''

import requests
import json


class Service(object):
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip,deflate',
        }
        self.token = ''  # // Session token for making API calls, call login on instantiation.

    def post_api(self, url=None, params=None, headers=None, url_prefix=None):
        count = 0
        while count < 2:
            prefix_url = url_prefix + 'Response'
            try:
                req = requests.post(url, params=params, headers=headers, timeout=10)
            except requests.exceptions.Timeout:
                count += 1
                continue
            if req.status_code == 403:
                self.token = ''
                token = self.login()
                params['token'] = token
                count += 1
            else:
                if req.text:
                    text = json.loads(req.text)
                    try:
                        return 400, text[prefix_url]['error']
                    except KeyError:
                        return req.status_code, text[prefix_url]['result']
                    except TypeError:
                        return req.status_code, req.text
                else:
                    return req.status_code, req.text

        return 408, 'Request timed out.'

    def get_api(self, url=None):
        req = requests.get(url)
        count = 0
        while count < 2:
            try:
                return json.loads(req.text)
            except Exception as e:
                count += 1
        return {'result': 'failed', 'status': 'failed', 'code': 400, 'enabled': 'failed'}

    def login(self):
        if not self.token:
            # // Used to login, in this case this is called automatically to generate a session when instantiating
            #   the class
            data = {'username': 'XXXXX', 'password': 'XXXXX', 'response': 'json'}
            url = 'https://service.com/api/Login'
            status_code, resp = self.post_api(url, params=data, headers=self.headers, url_prefix='Login')
            try:
                self.token = resp['token']
                print(status_code)
                return resp['token']
            except KeyError:
                return resp
            except AttributeError:
                return resp


    def domain_list(self, customer_name):
        # // Used to get a list of all domains given a selected customer name
        data = {'customername': customer_name, 'token': self.token, 'response': 'json'}
        url = 'https://service.com/api/GetDomainList'
        status_code, resp = self.post_api(url, params=data, headers=self.headers, url_prefix='GetDomainList')
        print(status_code)
        return resp

    def get_domain(self, domain_name):
        # // Used to get domain information given a specific domain name (useless).
        data = {'domainname': domain_name, 'token': self.token, 'response': 'json'}
        url = 'https://service.com/api/GetDomain'
        status_code, resp = self.post_api(url, params=data, headers=self.headers, url_prefix='GetDomain')
        print(status_code)
        return resp

    def enabled_products(self, domain_name):
        # // Used to get enabled products for a specific customer (I think - the API docs doesn't specify whether
        #    to provide a customer or domain name.
        data = {'domainname': domain_name, 'token': self.token, 'response': 'json'}
        url = 'https://service.com/api/GetEnabledProducts'
        status_code, resp = self.post_api(url, params=data, headers=self.headers, url_prefix='GetEnabledProducts')
        try:
            print(status_code)
            return resp['GetEnabledProductsResponse']['result']
        except KeyError:
            return resp

    def enabled_services(self, domain_name):
        # // Used to get enabled products for a specific customer (I think - the API docs doesn't specify whether
        #    to provide a customer or domain name - could just be for a domain.
        data = {'domainname': domain_name, 'token': self.token, 'response': 'json'}
        url = 'https://service.com/api/GetEnabledServices'
        status_code, resp = self.post_api(url, params=data, headers=self.headers, url_prefix='GetEnabledServices')
        print(status_code)
        return resp
