import aiohttp
import json
import asyncio
from datetime import datetime
#Created by: Owlcept
#*Ideas: add prefix?? might keep keywords instead
#!Add async command check
cmd_list = dict()

def commands(func):
    #Add commands to list
    cmd_list[func.__name__] = func
    return func

class Replies:
    def __init__(self, message, name, number, date, replied = False):
        self.message = message.lower()
        self.name = name
        self.number = number
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.replied = replied

    def __repr__(self):
        return f"Message: {self.message} || Date: ({self.date}) || Replied: {self.replied}"
        

class Client:


    def __init__(self,API, prefix = '!'):
        ''' Build API key and base url for requests '''
        self.messages = {}
        self.loop = asyncio.get_event_loop()
        self.prefix = prefix
        self.rate_limit = 2
        self.params = {'key':API}
        self.session = aiohttp.ClientSession()
        self.url = "https://mobile-text-alerts.com/rest/?request="
        self.headers = {'Accept':'application/json'}

    async def _close(self):
        await self.session.close()
    
    def run(self):
        loop = self.loop
        try:
            loop.run_until_complete(asyncio.gather(self.get_replies(),self.check()))
        except KeyboardInterrupt:
            print('\nProgram shutting down')
        finally:
            loop.run_until_complete(self._close())
            loop.close()

    async def check(self):
        while True:
            for m in self.messages.values():
                #Check for prefix
                if m.message.startswith(self.prefix):
                    #Arg[0] = command // Arg[1] all other vars to be parsed
                    # Eliminate all white space for vars
                    cmd = m.message.strip(self.prefix).split(None,1)
                else:
                    return

                if m.replied == True:
                    return
                else:
                    if cmd[0] in cmd_list:
                        m.replied = True
                        func = cmd_list.get(cmd[0])
                        try:
                            await func(m,cmd[1])
                        except:
                            await func(m)
                    else:
                        continue
            await asyncio.sleep(self.rate_limit)


    async def send_message(self, message, number):
        '''Use this to send messages to specific number'''

        url = self.url+"send_message"
        payload = {'number':number, 'message':message, 'from_name':'me'}
        await self.session.post(url,headers = self.headers, data=payload, params=self.params)

    async def get_replies(self):
        ''' Use this to get replies
            maybe build a listen tool?'''
        while True:

            url = self.url+'export_replies'
            replies =  await self.session.get(url, headers = self.headers, params = self.params)
            messages = json.loads(await replies.read())
            x = messages['replies']
            for y in x:
                if y['number'] not in self.messages:
                    self.messages[y['number']] = Replies(y['message'],y['firstName'],y['number'],y['date_received'])
                elif y['number'] in self.messages:
                    r = self.messages[y['number']]
                    date = datetime.strptime(y['date_received'], "%Y-%m-%d %H:%M:%S")
                    if r.date < date:
                        print('here')
                        self.messages.update({y['number']:Replies(y['message'],y['date_received'])})
            print(self.messages)
            await asyncio.sleep(self.rate_limit)
        #return "Success"
