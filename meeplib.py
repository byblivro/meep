import pickle

"""
meeplib - A simple message board back-end implementation.

Functions and classes:

 * u = User(username, password) - creates & saves a User object.  u.id
     is a guaranteed unique integer reference.

 * m = Message(title, post, author) - creates & saves a Message object.
     'author' must be a User object.  'm.id' guaranteed unique integer.

 * get_all_messages() - returns a list of all Message objects.

 * get_all_users() - returns a list of all User objects.

 * delete_message(m) - deletes Message object 'm' from internal lists.

 * delete_user(u) - deletes User object 'u' from internal lists.

 * get_user(username) - retrieves User object for user 'username'.

 * get_message(msg_id) - retrieves Message object for message with id msg_id.

"""

__all__ = ['Message', 'get_all_messages', 'get_message', 'delete_message',
           'User', 'set_current_user', 'get_current_user', 'get_user',
           'get_all_users', 'delete_user', 'is_user']

###
# internal data structures & functions; please don't access these
# directly from outside the module.  Note, I'm not responsible for
# what happens to you if you do access them directly.  CTB

# a dictionary, storing all messages by a (unique, int) ID -> Message object.
_messages = {}

# a dictionary, storing all replies by unique ID and Message ID
_replies = {}

def _get_next_message_id():
    if _messages:
        return max(_messages.keys()) + 1
    return 0

def _get_next_reply_id():
    if _replies:
        return max(_replies.keys()) + 1
    return 0

# a dictionary, storing all users by a (unique, int) ID -> User object.
_user_ids = {}

# a dictionary, storing all users by username
_users = {}

#a string that holds the username of the current logged in user
_current_user = ''

def _get_next_user_id():
    if _users:

        return max(_user_ids.keys()) + 1 

    return 0

def _reset():
    """
    Clean out all persistent data structures, for testing purposes.
    """
    global _messages, _users, _user_ids, _replies, current_user
    _messages = {}
    _users = {}
    _user_ids = {}
    _replies = {}
    _current_user = ''

###

class Message(object):
    """
    Simple "Message" object, containing title/post/rank/author.

    'author' must be an object of type 'User'.
    
    """
    def __init__(self, title, post, author):
        self.title = title
        self.post = post
        ##self.rank = rank

        assert isinstance(author, User)
        self.author = author

        self._save_message()
        _saveMeep()

    def _save_message(self):
        self.id = _get_next_message_id()
        
        # register this new message with the messages list:
        _messages[self.id] = self
        _saveMeep()

def get_all_messages(sort_by='id'):
    return _messages.values()

def get_message(id):
    return _messages[id]

## Disable Message Ranking
'''
def inc_msg_rank(msg):
    _messages[msg.id].rank += 1
    _saveMeep()

def dec_msg_rank(msg):
    _messages[msg.id].rank -= 1
    _saveMeep()
'''

def delete_message(msg):
    assert isinstance(msg, Message)
    del _messages[msg.id]
    _saveMeep()

class Reply(object):
    """
    Simple "Reply" object, containing Post ID number/reply/author.

    'author' must be an object of type 'User'.
    
    """
    def __init__(self, id_num, reply, author):
        self.id_num = id_num
        self.reply = reply
        ##self.rank = rank

        assert isinstance(author, User)
        self.author = author

        self._save_reply()
        _saveMeep()

    def _save_reply(self):
        self.id = _get_next_reply_id()
        print id
        
        # register this new message with the messages list:
        _replies[self.id] = self
        _saveMeep()

def get_all_replies(sort_by='id'):
    return _replies.values()

def get_reply(id):
    return _replies[id]

## Disable reply ranking
'''
def inc_reply_rank(reply):
    _replies[reply.id].rank += 1
    _saveMeep()

def dec_reply_rank(reply):
    _replies[reply.id].rank -= 1
    _saveMeep()
'''

def delete_reply(reply):
    assert isinstance(reply, Reply)
    del _replies[reply.id]
    _saveMeep()

###

class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password    
        self._save_user()
        
    def __cmp__(self, other):
        if (other.username != self.username or other.password != self.password):
            return -1
        else:
            return 0

    def _save_user(self):
        self.id = _get_next_user_id()
        _user_ids[self.id] = self
        _users[self.username] = self
        _saveMeep()

def set_current_user(username):
    print "----"
    print username
    global _current_user
    _current_user = username
    print _current_user
    print "-----"
    _saveMeep()

def get_current_user():
    print "xxxx"
    print _current_user
    print "xxxx"
    return _current_user
    _saveMeep()

def get_user(username):
    return _users.get(username)         # return None if no such user

def get_all_users():
    return _users.values()

def delete_user(user):
    del _users[user.username]
    del _user_ids[user.id]
    _saveMeep()

def is_user(username, password):
    try:
        thisUser = get_user(username)
        #print 'success1'
    except NameError:
        thisUser = None
        #print 'fail1'

    #print thisUser.password
    #print password
    if thisUser is not None:
        if str(thisUser.password) == str(password):
            #print "true"
            return True
        #print "false1"
    else:
        #print "false2"
        return False
    _saveMeep()

def _saveMeep():
    obj = (_messages, _replies, _users, _user_ids, _current_user)
    filename = "meep.pickle"
    fp = open(filename, "w")
    pickle.dump(obj, fp)
    fp.close()

def _openMeep():
    global _messages, _replies, _users, _user_ids, _current_user
    fp = open("meep.pickle", "r")
    obj = pickle.load(fp)
    (_messages, _replies, _users, user_ids, _current_user) = obj
    fp.close()