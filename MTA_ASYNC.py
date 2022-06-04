import asyncio
import aiohttp
import json
from datetime import datetime
#asyncio.Future() runs forever, so loop that somehow
words = dict()

def commands(func):
    words[func.__name__] = func
    return func

@commands
async def hello(ctx,num):
    reply = ctx.messages[num]
    await ctx.send_message(numbe = num, message = "hello")


class Replies:
    def __init__(self, message, number, date, replied = False):
        self.message = message
        self.number = number
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



    async def send_message(self, message, number):
        '''Use this to send messages to specific number'''

        url = self.url+"send_message"
        payload = {'number':number, 'message':message, 'from_name':'me'}
        await self.session.post(url,headers = self.headers, data=payload, params=self.params)

    async def get_replies(self):
        ''' Use this to get replies
            maybe build a listen tool?'''

        url = self.url+'export_replies'
        replies =  await self.session.get(url, headers = self.headers, params = self.params)
        messages = json.loads(await replies.read())
        x = messages['replies']
        for y in x:
            if y['number'] not in self.messages:
                self.messages[y['number']] = Replies(y['message'],['number'],y['date_received'])
            elif y['number'] in self.messages:
                self.messages.update({y['number']:Replies(y['message'],y['number'],y['date_received'])})
        return "Success"
