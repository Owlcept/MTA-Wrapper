import requests
import json
from datetime import datetime
'''
'''

class Replies:
    def __init__(self, message, number, date, replied = False):
        self.message = message
        self.number = number
        self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.replied = replied

    def __repr__(self):
        return f"{self.message}, ({self.date}), Replied:{self.replied}"

class Client:


    def __init__(self,API):
        ''' Build API key and base url for requests '''
        self.messages = {}
        self.params = {'key':API}
        self.url = "https://mobile-text-alerts.com/rest/?request="
        self.headers = {'Accept':'application/json'}

    def send_message(self, message, number):
        '''Use this to send messages to specific number'''

        url = self.url+"send_message"
        payload = {'number':number, 'message':message, 'from_name':'me'}
        requests.post(url,headers = self.headers, data=payload, params=self.params)

    def get_replies(self):
        ''' Use this to get replies
            maybe build a listen tool?'''

        url = self.url+'export_replies'
        replies = requests.get(url, headers = self.headers, params = self.params)
        messages = json.loads(replies.text)
        return messages
