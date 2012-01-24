import meeplib
import traceback
import cgi

def initialize():
    # create a default user
    u = meeplib.User('test', 'foo')

    # create a single message
    meeplib.Message('my title', 'This is my message!', 0, u)

    # done.

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])

        username = 'test'

        return ["""
                   you are logged in as user: %s.
                   <p><a href='/m/add'>Add a message</a>
                   <p><a href='/login'>Log in</a>
                   <p><a href='/logout'>Log out</a>
                   <p><a href='/m/list'>Show messages</a>
                """ % (username,)]

    def login(self, environ, start_response):
        # hard code the username for now; this should come from Web input!
        username = 'test'

        # retrieve user
        user = meeplib.get_user(username)

        # set content-type
        headers = [('Content-type', 'text/html')]
        
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def logout(self, environ, start_response):
        # does nothing
        headers = [('Content-type', 'text/html')]

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()
        replies = meeplib.get_all_replies()

        s = []
        for m in messages:
            s.append('id: %d<p>' % (m.id,))
            s.append('title: %s<p>' % (m.title))
            s.append('message: %s<p>' % (m.post))
            s.append('author: %s<p>' % (m.author.username))
            s.append('RANK: %d<p>' % (m.rank))
            s.append(
                     """<form action='add_reply' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Reply to Message">
                        </form>
                     """ % (m.id))
            s.append(
                     """
                        <form action='increase_msg_rank' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Upvote Message">
                        </form>
                     """ % (m.id))
            s.append(
                     """
                        <form action='decrease_msg_rank' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Downvote Message">
                        </form>
                     """ % (m.id))
            s.append(
                     """                    
                        <form action='delete_message_action' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Delete Message">
                        </form>
                     """ % (m.id))
            print m.id
            
            for r in replies:
                if r.id_num ==  m.id:
                    s.append('title: RE:%s<p>' % (m.title))
                    s.append('reply: %s<p>' % (r.reply))
                    s.append('author: %s<p>' % (r.author.username))
                    s.append('RANK: %d<p>' % (r.rank))
                    s.append(
                     """
                        <form action='increase_reply_rank' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Upvote Reply">
                        </form>
                     """ % (r.id))
                    s.append(
                     """
                        <form action='decrease_reply_rank' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Downvote Reply">
                        </form>
                     """ % (r.id))
                    s.append(
                     """<form action='delete_reply_action' method='GET'>
                        <input type='hidden' value='%d' name='id_num'>
                        <input type='submit' value="Delete Reply">
                        </form>
                     """ % (r.id))
                    s.append('<hr>')

        s.append("<a href='../../'>index</a>")
            
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        
        return ["".join(s)]

    def add_message(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)

        return """<form action='add_message_action' method='POST'>
                  Title: <input type='text' name='title'><br>
                  Message: <input type='text' name='message'>
                  <input type='hidden' value='0' name='rank'>
                  <br><input type='submit'></form>
               """

    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        rank = form['rank'].value
        rank = int(rank)
        
        username = 'test'
        user = meeplib.get_user(username)
        
        new_message = meeplib.Message(title, message, rank, user)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]

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
                      '/login': self.login,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_message_action': self.add_message_action,
                      '/m/delete_message_action': self.delete_message_action,
                      '/m/add_reply': self.add_reply,
                      '/m/add_reply_action': self.add_reply_action,
                      '/m/delete_reply_action': self.delete_reply_action,
                      '/m/increase_msg_rank': self.increase_message_rank,
                      '/m/decrease_msg_rank': self.decrease_message_rank,
                      '/m/increase_reply_rank':self.increase_reply_rank,
                      '/m/decrease_reply_rank':self.decrease_reply_rank
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

#updated 1/24/2012