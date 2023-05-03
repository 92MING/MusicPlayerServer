import socketio, asyncio

class Client(socketio.AsyncClient):
    def __init__(self):
        super().__init__()
        self.on('test', self.test)
    def test(self, data):
        print(data)
sio = Client()


async def main():
    await sio.connect('http://localhost:9192',
                headers={'id': '123', 'ip':'123', 'localIP':'123',
                         'port':'1234', 'submask':'123', 'natType': '0'},
                wait_timeout=5)
    print(sio.get_sid())

    await sio.sleep(2)
    uploadSongData = {'hash':'123',
                      'name':'123',
                      'artist':'123',
                      'album':'123',
                      'fileExt':'123',
                      'fileSize':'123'}
    print('upload song 1')
    await sio.emit('uploadSong', uploadSongData)

    await sio.sleep(3)
    uploadSongData2 = {'hash': '123',
                      'name': '123_iAmNew',
                      'artist': '123',
                      'album': '123',
                      'fileExt': '123',
                      'fileSize': '123'}
    print('upload song 2')
    await sio.emit('uploadSong', uploadSongData2)

    await sio.sleep(3)
    uploadSongData3 = {'hash': '321',
                       'name': '1abc2cde3',
                       'artist': 'aaa',
                       'album': '123',
                       'fileExt': '123',
                       'fileSize': '123'}
    print('upload song 3')
    await sio.emit('uploadSong', uploadSongData3)

    await sio.sleep(4)
    deleteSongData = {'hash':'123'}
    print('delete song ')
    await sio.emit('deleteSong', deleteSongData)

    await sio.sleep(4)
    findSongData = {'keywords':'1 2 3', 'mode':'name'}
    print('find song')
    def callback(*data):
        for i in data:
            print('found:', i)
    await sio.emit('findSong', findSongData, callback=callback)

    await sio.sleep(4)
    findSongHolderData = {'hash':'321'}
    print('find song holder')
    await sio.emit('findSongHolders', findSongHolderData, callback=callback)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
