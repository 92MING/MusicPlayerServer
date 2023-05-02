import socketio, asyncio

class Client(socketio.AsyncClient):
    def __init__(self):
        super().__init__()
        self.on('test', self.test)
    def test(self, data):
        print('test received:', data)

sio = Client()

async def main():
    await sio.connect('http://localhost:9192',
                headers={'id': '123', 'ip':'123', 'localIP':'123',
                         'port':'1234', 'submask':'123', 'natType': '0'},
                wait_timeout=5)
    print(sio.get_sid())
    returnValue = None
    def setReturnValue(x):
        nonlocal returnValue
        returnValue = x
    await sio.emit('test', 'test', callback=setReturnValue)
    print('hi')

    #wait until returnValue is not None
    async def waitReturnValue():
        while returnValue is None:
            await asyncio.sleep(0.5)
        print('returnValue:', returnValue)
    await asyncio.wait_for(waitReturnValue(), 5)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
