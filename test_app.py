import unittest
import meep_example_app

class TestApp(unittest.TestCase):
    def setUp(self):
        meep_example_app.initialize()
        app = meep_example_app.MeepExampleApp()
        self.app = app

    def test_index(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Add a message' in data[0]
        assert 'Show messages' in data[0]

    def test_add_message(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/add'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
                
        data = self.app(environ, fake_start_response)

    def test_list_messages(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/list'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
                
        data = self.app(environ, fake_start_response)
    
    def test_login(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/login'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
                
        data = self.app(environ, fake_start_response)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()