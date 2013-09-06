
import os
import web
import urllib
import urllib2
import json

from nose.tools import assert_in, assert_not_in, assert_equals
import nose

# Swtich into a testing environment
os.environ['WEBPY_ENV'] = 'test'

# Import app to test
from code import app


class TestBrowser(web.browser.AppBrowser):
    '''Subclassed AppBrowser to add @method param'''

    def open(self, url, data=None, headers={}, method='GET'):
        """Opens the specified url."""
        url = urllib.basejoin(self.url, url)
        req = urllib2.Request(url, data, headers)
        req.get_method = lambda: method
        return self.do_request(req)

    @property
    def json_data(self):
        return json.loads(self.data)


class TestApi():

    def setup(self):
        self.b = TestBrowser(app)

    def teardown(self):
        self.b.reset()

    def test_list_todos(self):
        response = self.b.open('/api/todos')
        assert_equals(self.b.status, 200)
        assert_equals(response.headers['Content-Type'], 'application/json')
        todos = self.b.json_data
        assert_equals(isinstance(todos, list), True)

    def test_create_and_get_todo(self):
        # Create todo
        self.b.open(
            '/api/todos',
            data='{"content": "Test TODO"}',
            method='POST'
        )
        todo = self.b.json_data
        assert_equals(todo['content'], 'Test TODO')
        self.b.open('/api/todos/%(id)d' % todo)
        todo2 = self.b.json_data
        assert_equals(todo2['content'], 'Test TODO')

    def test_create_and_update_todo(self):
        # Create todo
        self.b.open(
            '/api/todos',
            data='{"content": "Test TODO"}',
            method='POST'
        )
        todo = self.b.json_data
        assert_equals(todo['content'], 'Test TODO')
        assert_equals(todo['is_done'], False)
        # Update todo and ensure it was changed
        self.b.open(
            '/api/todos/%(id)d' % todo,
            data='{"content": "Test TODO 2", "is_done": true}',
            method='PUT'
        )
        todo2 = self.b.json_data
        assert_equals(todo2['content'], 'Test TODO 2')
        assert_equals(todo2['is_done'], True)

    def test_create_and_delete_todo(self):
        # Create todo to ensure db is not empty
        self.b.open(
            '/api/todos',
            data='{"content": "Test TODO"}',
            method='POST'
        )
        # Select all todos
        self.b.open('/api/todos')
        # Delete first todo
        todo = self.b.json_data[0]
        self.b.open('/api/todos/%(id)d' % todo, method='DELETE')
        # Select todos again
        self.b.open('/api/todos')
        # Ensure deleted todo is not present in list
        todos = self.b.json_data
        assert_equals(any(t['id'] == todo['id'] for t in todos), False)
