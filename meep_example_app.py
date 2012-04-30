import meeplib
import traceback
import cgi
import pickle
import meepcookie
import Cookie
import mimetypes

from jinja2 import Environment, FileSystemLoader

def initialize():
    try:
        meeplib._messages = {}
        meeplib._users = {}
        meeplib._user_ids = {}
        meeplib._openMeep()
    except IOError:
        # create default users
        u = meeplib.User('test', 'foo')
        a = meeplib.User('Anonymous', 'password')
        meeplib.Message('my title', 'This is my message!', u, -1)
        
env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
    template = env.get_template(filename)
    x = template.render(**variables)
    return str(x)

mimetypes.init()

class FileServer(object):
    def __init__(self, filename):
        self.content_type = mimetypes.guess_type(filename)[0]
        self.filename = filename

    def __call__(self, environ, start_response):
        try:
            fp = open(self.filename)
        except OSError:
            start_response("404 not found", [('Content-type', 'text/html'),])
            return 'file not found'

        data = fp.read()
        start_response("200 OK", [('Content-type', self.content_type),])
        return [data]

class MeepExampleApp(object):
    """
    WSGI app object.
    """

    def authHandler(self, environ):
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
            return meeplib.get_user(username)
        except:
            return None

    def index(self, environ, start_response):
        user = self.authHandler(environ)
        
        start_response("200 OK", [('Content-type', 'text/html')])
        
        return [ render_page('index.html', user = user) ]
        
    def login(self, environ, start_response):
        user = self.authHandler(environ)
        
        headers = [('Content-type', 'text/html')]
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        try:
            username = form['username'].value
            user = meeplib.get_user(username)
            password = form['password'].value
        except:
            password = None
               
        if ((user is not None) and 
            (password is not None) and 
            (user.password == password)):
            k = 'Location'
            v = '/'
            headers.append((k, v))
            cookie_name, cookie_val = meepcookie.make_set_cookie_header('username', user.username)
            headers.append((cookie_name, cookie_val))
            
        start_response('302 Found', headers)
        return [ render_page('login.html') ]

    def login_failed(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)
        
        return [ render_page('login_failed.html') ]

    def create_user(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        return [ render_page("create_user.html") ]
       
        
    def create_user_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        
        try:
            username = form['username'].value
            password = form['password'].value
            u = meeplib.User(username, password)
        except:
            pass

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers = [('Content-type', 'text/html')]
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return ["no such content"]

    def logout(self, environ, start_response):
        # does nothing
        headers = [('Content-type', 'text/html')]
        
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        cookie_name, cookie_val = meepcookie.make_set_cookie_header('username','')
        headers.append((cookie_name, cookie_val))
        start_response('302 Found', headers)
        
        return ["no such content"]

    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()
        replies = meeplib.get_all_replies()
            
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        
        return [render_page('list_messages.html', messages = messages, replies = replies)]

    def add_message(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)

        return [ render_page('add_message.html') ]

    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        rank = form['rank'].value
        rank = int(rank)
     
        user = meeplib.get_user(meeplib.get_current_user())
        new_message = meeplib.Message(title, message, rank, user)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]

    def delete_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        id_num = form['id_num'].value
        #print "form"
        #print (id,)
        id_number = int(id_num)
        
        meeplib.delete_message(meeplib.get_message(id_number))

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message deleted"]

    def add_reply(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        headers = [('Content-type', 'text/html')]

        id_num = form['id_num'].value
        id_num = int(id_num)
        
        start_response("200 OK", headers)

        return """<form action='add_reply_action' method='POST'>
                  Reply: <input type='text' name='reply'>
                  <input type='hidden' value='%d' name='id_num'>
                  <input type='hidden' value='0' name='rank'>
                  <br><input type='submit'></form>
               """ % id_num

    def add_reply_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        id_num = form['id_num'].value
        id_num = int(id_num)
        reply = form['reply'].value
        rank = form['rank'].value
        rank = int(rank)
        
        username = 'test'
        user = meeplib.get_user(username)
        
        new_reply = meeplib.Reply(id_num, reply, rank, user)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["reply added"]

    def delete_reply_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        id_num = form['id_num'].value
        #print "form"
        #print (id,)
        id_number = int(id_num)
        
        meeplib.delete_reply(meeplib.get_reply(id_number))

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["reply deleted"]

    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      #'/home': self.home,
                      '/create_user': self.create_user,
                      '/create_user_action': self.create_user_action,
                      '/login': self.login,
                      '/login_failed': self.login_failed,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_message_action': self.add_message_action,
                      '/m/delete_message_action': self.delete_message_action,
                      '/m/add_reply': self.add_reply,
                      '/m/add_reply_action': self.add_reply_action,
                      '/m/delete_reply_action': self.delete_reply_action,
                      '/_stylesheets/style.css': FileServer('_stylesheets/style.css'),
                      '/_images/background.jpg': FileServer('_images/background.jpg'),
                      '/_images/header.jpg': FileServer('_images/header.jpg')
                      ##'/m/increase_msg_rank': self.increase_message_rank,
                      ##'/m/decrease_msg_rank': self.decrease_message_rank,
                      ##'/m/increase_reply_rank':self.increase_reply_rank,
                      ##'/m/decrease_reply_rank':self.decrease_reply_rank
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        fn = call_dict.get(url)

        if fn is None:
            start_response("404 Not Found", [('Content-type', 'text/html')])
            return ["Page not found."]

        try:
            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]

## Disable Message Ranking
'''
    def increase_message_rank(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        msg_id = form['id_num'].value
        msg_id = int(msg_id)
        meeplib.inc_msg_rank(meeplib.get_message(msg_id))

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message upvoted"]

    def decrease_message_rank(self,environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        msg_id = form['id_num'].value
        msg_id = int(msg_id)
        meeplib.dec_msg_rank(meeplib.get_message(msg_id))

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message upvoted"]
'''
## Disable ranking 
'''
    def increase_reply_rank(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        msg_id = form['id_num'].value
        msg_id = int(msg_id)
        meeplib.inc_reply_rank(meeplib.get_reply(msg_id))

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message upvoted"]

    def decrease_reply_rank(self,environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        msg_id = form['id_num'].value
        msg_id = int(msg_id)
        meeplib.dec_reply_rank(meeplib.get_reply(msg_id))

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message upvoted"]
'''