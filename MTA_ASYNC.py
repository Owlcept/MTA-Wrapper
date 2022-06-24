import aiohttp
import json
import asyncio
from datetime import datetime
#Created by: Owlcept
#*Ideas: add prefix?? might keep keywords instead
#!Add async command check
cmd_list = dict()

def check(client):
    #Check for command and if replied
    for n, m in client.items():
        if m.replied == True:
            return
        else:
            if m.message in cmd_list:
                func = cmd_list.get(m.message)
                return func,n,m

def commands(func):
    #Add commands to list
    cmd_list[func.__name__] = func
    return func

class Replies:
    def __init__(self, message, date, replied = False):
        self.message = message.lower()
        self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.replied = replied

    def __repr__(self):
        return f"Message: {self.message} || Date: ({self.date}) || Replied: {self.replied}"
        

class Client:


    def __init__(self,API):
        ''' Build API key and base url for requests '''
        self.messages = {}
        self.params = {'key':API}
        self.session = aiohttp.ClientSession()
        self.url = "https://mobile-text-alerts.com/rest/?request="
        self.headers = {'Accept':'application/json'}

    async def _close(self):
        await self.session.close()

    async def check(self):
        for n,m in self.messages.items():
            if m.replied == True:
                return
            else:
                if m.message in cmd_list:
                    func = cmd_list.get(m.message)
                    func(n)
                    m.replied == True
                else:
                    continue


    async def send_message(self, message, number):
        '''Use this to send messages to specific number'''

        url = self.url+"send_message"
        payload = {'number':number, 'message':message, 'from_name':'me'}
        await self.session.post(url,headers = self.headers, data=payload, params=self.params)

    async def get_replies(self):
        ''' Use this to get replies
            maybe build a listen tool?'''
        rate_limit = 2
        while True:

            url = self.url+'export_replies'
            replies =  await self.session.get(url, headers = self.headers, params = self.params)
            messages = json.loads(await replies.read())
            x = messages['replies']
            for y in x:
                if y['number'] not in self.messages:
                    self.messages[y['number']] = Replies(y['message'],y['date_received'])
                elif y['number'] in self.messages:
                    r = self.messages[y['number']]
                    date = datetime.strptime(y['date_received'], "%Y-%m-%d %H:%M:%S")
                    if r.date < date:
                        self.messages.update({y['number']:Replies(y['message'],y['date_received'])})
            print(self.messages)
            await asyncio.sleep(rate_limit)
        #return "Success"
