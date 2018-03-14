import os
import six

import json
import requests

from notify import consts


class NotifyClient(object):
    """
        Notify service client
    """

    SERVICE_URL = consts.SERVICE_URL

    NOTIFY_RESOURCE_URL = "rest/notify/"
    CONTACT_RESOURCE_URL = "rest/contact/"
    CONTACT_GROUP_RESOURCE_URL = "rest/contact_group/"
    BALANCE_RESOURCE_URL = "rest/balance/"

    DEFAULT_DELAY = 0.5  # seconds
    JSON_DUMP_TYPES = (list, dict)

    def __init__(self, message=None, audio_file=None, audio_file_url=None, phone_numbers=None, delay=None, answers=None,
                 auth_token=None, handler_url=None, handler_token=None, handler_data=None):
        """
        Note: The data for the query can be defined both during initialization and when calling the required method.
              Priority will be given to the latter.

        :param audio_file: file object (ogg, mp3 only)
        :param audio_file_url: str (ogg, mp3 only)
        :param phone_numbers: list
        :param message: str
        :param delay: float
        :param answers: dict ({'text': str, 'tone_code': int})
        :param handler_url: str
        :param handler_token: str
        :param handler_data: dict or list
        """

        assert auth_token is not None
        assert message is None or isinstance(message, six.string_types)
        assert audio_file is None or isinstance(audio_file, six.BytesIO)
        assert delay is None or isinstance(delay, (six.integer_types, float))
        assert answers is None or isinstance(answers, list)
        assert phone_numbers is None or isinstance(phone_numbers, list)
        assert audio_file_url is None or isinstance(audio_file_url, six.string_types)
        assert handler_token is None or isinstance(handler_token, six.string_types)
        assert handler_url is None or isinstance(handler_url, six.string_types)
        assert handler_data is None or isinstance(handler_data, self.JSON_DUMP_TYPES)

        self.delay = delay or self.DEFAULT_DELAY

        self.message = message
        self.audio_file_url = audio_file_url
        self.audio_file = audio_file

        self.answers = answers or []
        self.phone_numbers = phone_numbers or []

        self.handler_token = handler_token
        self.handler_url = handler_url
        self.handler_data = handler_data

        self.auth_token = auth_token

    def create_call(self, message=None, answers=None, phone_numbers=None, delay=None, audio_file=None,
                    audio_file_url=None, handler_token=None, handler_url=None, handler_data=None):
        """
            Make call
        """

        audio_file = audio_file or self.get_audio_file()
        audio_file_url = audio_file_url or self.get_audio_file_url()
        message = message or self.get_message()        
        
        files = {}
        notify_data = {
            'type': consts.CALL_TYPE,
            'answers': answers or self.get_answers(),
            'delay': delay or self.get_delay(),
            'phones': phone_numbers or self.get_phone_numbers(),
            
            'handler_token': handler_token or self.get_handler_token(),
            'handler_url': handler_url or self.get_handler_url(),
            'handler_data': self._dump_data(handler_data or self.get_handler_data())
        }
        
        if audio_file:
            files['record_file'] = audio_file
        elif audio_file_url:
            notify_data['record_file_url'] = audio_file_url
        elif message:
            notify_data['message'] = message

        data = self.preparation_data(
            data=notify_data,
            files=files
        )

        return create_notify(data)

    def create_message(self, message=None, phone_numbers=None, handler_token=None, handler_url=None, handler_data=None):
        """
            Make sms message
        """

        message = message or self.get_message()
        phones = phone_numbers or self.get_phone_numbers()
        handler_token = handler_token or self.get_handler_token()
        handler_url = handler_url or self.get_handler_url()
        handler_data = handler_data or self.get_handler_data()

        assert isinstance(message, six.string_types)
        assert isinstance(phones, list)
        assert handler_token is None or isinstance(handler_token, six.string_types)
        assert handler_url is None or isinstance(handler_url, six.string_types)
        assert handler_data is None or isinstance(handler_data, self.JSON_DUMP_TYPES)

        data = self.preparation_data(
            data={
                'type': consts.MESSAGE_TYPE,
                'message': message,
                'phones': phones,
                'handler_token': handler_token,
                'handler_url': handler_url,
                'handler_data': self._dump_data(handler_data)
            }

        )

        return create_notify(data)

    def create_notify(self, **request_data):

        try:
            response = requests.post(url=self.get_notify_url(), headers=self.get_headers(), **request_data)
            result = response.json()
        except requests.ConnectionError:
            result = self.make_error(consts.CONNECTION_ERROR_MESSAGE)
        except ValueError:
            result = self.make_error(consts.JSON_ERROR_MESSAGE)

        return result

    def get_headers(self):
        return {
            'Authorization': 'Token %s' % self.get_auth_token(),
            'Content-Type': 'application/json'
        }

    def get_phone_numbers(self):
        return self.phone_numbers

    def get_answers(self):
        return self.answers

    def get_message(self):
        return self.message

    def get_delay(self):
        return self.delay

    def get_audio_file(self):
        return self.audio_file

    def get_audio_file_url(self):
        return self.audio_file_url

    def get_handler_url(self):
        return self.handler_url

    def get_handler_token(self):
        return self.handler_token

    def get_handler_data(self):
        return self.handler_data

    def get_service_url(self):
        return self.SERVICE_URL

    def get_notify_url(self):
        return os.path.join(self.get_service_url().strip('/'), self.NOTIFY_RESOURCE_URL.strip('/')) + '/'

    def get_auth_token(self):
        return self.auth_token

    @staticmethod
    def make_error(message):
        return {
            'error': message
        }


    def preparation_data(self, **request_data):
        data = request_data.get('data')
        files = request_data.get('files', '')

        assert data
        assert data.get('phones')
        assert data.get('message') or files.get('record_file') or files.get('record_file_url')

        if data.get('handler_data') == None:
            data.pop('handler_data')

        data = self._dump_data(data)

        return {
            'data': data,
            'files': files
        }

    @staticmethod
    def _dump_data(data=None):
        return json.dumps(data) if data is not None else data
