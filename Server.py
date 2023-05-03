from __future__ import unicode_literals
from PyProjectUtils import SingleManager,SingleClass, GlobalValue, SingleEnum, MultiKeyDict
from sqlite_utils import Database, Table, NotFoundError
import os, json
from typing import Optional

# region init database & table

if not os.path.exists("database.db"):
    with open("database.db", "w") as f:
        f.close()
database : Optional[Database] = None
if GlobalValue.HasGlobalValue("database"):
    database = GlobalValue.GetGlobalValue("database")
else:
    database = Database("database.db")
    GlobalValue.SetGlobalValue("database", database)

musicFileRecordTable : Optional[Table] =None
if GlobalValue.HasGlobalValue("musicFileRecordTable"):
    musicFileRecordTable = GlobalValue.GetGlobalValue("musicFileRecordTable")
else:
    database.create_table(name="musicFileRecord",
                          columns={"hash": str, "names": str, "users": str, "albums":str,
                                   "fileSize":int, "artists":str, "fileExt":str},
                          pk=["hash"],
                          not_null=["hash"],
                          if_not_exists=True)
    musicFileRecordTable = database["musicFileRecord"]
    GlobalValue.SetGlobalValue("musicFileRecordTable", musicFileRecordTable)
    musicFileRecordTable.create_index(["hash"], if_not_exists=True)
    if musicFileRecordTable.detect_fts() is None:
        musicFileRecordTable.enable_fts(["names","artists","albums"], create_triggers=True, replace=False)
# endregion

# region classes

from PyProjectUtils import ChainFunc
MUSIC_RECORD_POOL_SIZE = 256
class MusicFileRecord(SingleClass):
    _AllRecords = {} # hash: MusicFileRecord
    _AllRecordList = []  #for Least Recently Used

    _hash = None
    _names = None
    _users = None
    _albums = None
    _artists = None
    _fileExt = None
    _fileSize = None

    def __new__(cls, hash):
        if hash in MusicFileRecord._AllRecords:
            thisObj = MusicFileRecord._AllRecords[hash]
            MusicFileRecord._AllRecordList.remove(thisObj)
            MusicFileRecord._AllRecordList.append(thisObj)
        else:
            thisObj = super().__new__(cls)
            MusicFileRecord._AllRecords[hash] = thisObj
            MusicFileRecord._AllRecordList.append(thisObj)
            thisObj._hash = hash
            thisObj._names = []
            thisObj._users = []
            thisObj._artists = []
            thisObj._albums = []
            if len(MusicFileRecord._AllRecordList) > MUSIC_RECORD_POOL_SIZE:
                lastObj = MusicFileRecord._AllRecordList[0]
                MusicFileRecord._AllRecordList.remove(lastObj)
                MusicFileRecord._AllRecords.pop(lastObj._hash)
                del lastObj
            try :
                record = musicFileRecordTable.get(hash)
                if record['names'] is not None and record['names'] != "":
                    thisObj._names = json.loads(record["names"])
                if record['users'] is not None and record['users'] != "":
                    thisObj._users = json.loads(record["users"])
                if record['artists'] is not None and record['artists'] != "":
                    thisObj._artists = json.loads(record["artists"])
                if record['albums'] is not None and record['albums'] != "":
                    thisObj._albums = json.loads(record["albums"])
                if record['fileExt'] is not None and record['fileExt'] != "":
                    thisObj._fileExt = record["fileExt"]
                if record['fileSize'] is not None and record['fileSize'] != "":
                    thisObj._fileSize = int(record["fileSize"])
            except NotFoundError:
                raise Exception(f"music file hash:{hash} not found")
        return thisObj

# region properties
    @property
    def hash(self):
        return self._hash
    @property
    def names(self):
        return tuple(self._names)
    @property
    def users(self):
        return tuple(self._users)
    @property
    def albums(self):
        return tuple(self._albums)
    @property
    def artists(self):
        return tuple(self._artists)
    @property
    def fileExt(self):
        return self._fileExt
    @property
    def fileSize(self):
        if self._fileSize is not None and not isinstance(self._fileSize, int):
            self._fileSize = int(self._fileSize)
        return self._fileSize
# endregion

# region funcs
    @ChainFunc
    def addName(self, name:str):
        if name not in self._names:
            self._names.append(name)
    @ChainFunc
    def removeName(self, name:str):
        if name in self._names:
            self._names.remove(name)
    @ChainFunc
    def addArtist(self, artist:str):
        if artist not in self._artists:
            self._artists.append(artist)
    @ChainFunc
    def removeArtist(self, artist:str):
        if artist in self._artists:
            self._artists.remove(artist)
    @ChainFunc
    def addAlbum(self, album:str):
        if album not in self._albums:
            self._albums.append(album)
    @ChainFunc
    def removeAlbum(self, album:str):
        if album in self._albums:
            self._albums.remove(album)
    @ChainFunc
    def addUser(self, user:str):
        if not isinstance(user, str):
            raise TypeError(f"user ID must be str. {type(user)} given")
        if user not in self._users:
            self._users.append(user)
    @ChainFunc
    def removeUser(self, user:str):
        if not isinstance(user, str):
            raise TypeError(f"user ID must be str. {type(user)} given")
        if user in self._users:
            self._users.remove(user)
    @ChainFunc
    def setFileExt(self, fileExt:str):
        if fileExt is not None and (self._fileExt is None or fileExt != self._fileExt):
            self._fileExt = fileExt
    @ChainFunc
    def setFileSize(self, fileSize):
        _fileSize = int(fileSize)
        if fileSize is not None and (self._fileSize is None or _fileSize > self.fileSize):
            self._fileSize = _fileSize

    def serialize(self):
        data  = {
            "hash": self._hash,
            "names": json.dumps(self._names),
            "users": json.dumps(self._users),
            "artists": json.dumps(self._artists),
            "albums": json.dumps(self._albums),
            "fileExt": self._fileExt,
            "fileSize": self._fileSize
        }
        return data

    @ChainFunc.final
    def save(self):
        data = self.serialize()
        hash = data.pop("hash")
        musicFileRecordTable.update(hash, data)
# endregion

class NATType(SingleEnum):
    Unknown = 0
    Blocked = 1
    OpenInternet = 2
    FullCone = 3
    SymmetricUDPFirewall = 4
    RestrictNAT = 5
    RestrictPortNAT = 6
    SymmetricNAT = 7
class User(SingleClass):
    _CurrentUsers = MultiKeyDict("id", "sid")  #(id / sid) -> User

    _sid:str = None  #session id
    _id:str = None  #user id
    _ip:str = None  #global ip
    _localIP:str = None  #local ip
    _port:int = None  #port for node connection
    _submask:str = None  #submask
    _natType:NATType = NATType.Unknown

    TURN_connecting = [] #IDs

    def __new__(cls, id:str):
        if ('id',id) in User._CurrentUsers:
            thisObj = User._CurrentUsers['id',id]
        else:
            thisObj = super().__new__(cls)
            thisObj._id = id
            thisObj.TURN_connecting = []
            User._CurrentUsers.add({'id':id}, thisObj)
        return thisObj

    @staticmethod
    def AllCurrentUsers():
        return User._CurrentUsers.values()
    @staticmethod
    def RemoveUserByID(id:str):
        try:
            User._CurrentUsers.pop('id', id)
        except KeyError:
            print(f"User.RemoveUserByID: id:{id} not found")
    @staticmethod
    def RemoveUserBySID(sid:str):
        try:
            User._CurrentUsers.pop('sid', sid)
        except KeyError:
            print(f"User.RemoveUserBySID: sid:{sid} not found")
    @staticmethod
    def HasCurrentUser(id:str):
        return ('id',id) in User._CurrentUsers
    @staticmethod
    def FindUserBySID(sid:str):
        '''find user by sid, if not found, raise exception.
        For getting user by id, use User(id) instead.'''
        try:
            return User._CurrentUsers['sid', sid]
        except KeyError:
            raise Exception(f"User.FindUserBySID: sid:{sid} not found")
    @property
    def sid(self):
        return self._sid
    @property
    def id(self):
        return self._id
    @property
    def ip(self):
        return self._ip
    @property
    def dictID(self):
        return User._CurrentUsers.getID('id', self.id)
    @property
    def localIP(self):
        return self._localIP
    @property
    def port(self):
        return self._port
    @property
    def submask(self):
        return self._submask
    @property
    def natType(self):
        return self._natType

    def login(self, sid:str, ip:str, localIP:str, port:int, submask:str, natType:NATType = None):
        self._sid = sid
        self._ip = ip
        self._localIP = localIP
        self._port = port
        self._submask = submask
        User._CurrentUsers.setKey(self.dictID, 'sid', sid)
        if natType is not None:
            self._natType = natType

# endregion

# region server

import flask
from flask_socketio import SocketIO, emit
from PyProjectUtils.NetworkUtils import checkIpInSameSubnet
from functools import partial

USER_TRACK_LIMIT = 5

class ConnectionFailReason(SingleEnum):
    UserNotFound = 0

class Server(SingleManager):

    def __init__(self):
        self.app = flask.Flask("Music Player Server")
        self.socketio = SocketIO(self.app, ping_timeout=5, ping_interval=5, cors_allowed_origins="*")

        @self.socketio.on('connect')
        def login():
            sid = flask.request.sid
            headers = flask.request.headers
            id = headers.get('id', None)
            ip = headers.get('ip', None)
            localIP = headers.get('localIP', None)
            port = headers.get('port', None)
            submask = headers.get('submask', None)
            if id is None:
                print('no id, deny connection')
                return False  # deny connection
            if ip is None:
                print('no ip, deny connection')
                return False
            if localIP is None:
                print('no localIP, deny connection')
                return False
            if port is None:
                print('no port, deny connection')
                return False
            if submask is None:
                print('no submask, deny connection')
                return False
            if User.HasCurrentUser(id):
                print('already logged in, deny connection')
                return False
            natType = headers.get('natType', None)
            if natType is not None:
                natType =NATType(int(natType))
            if port is not None:
                port = int(port)
            print(f'login, id:{id}, ip:{ip}, localIP:{localIP}, port:{port}, submask:{submask}, natType:{natType.name if natType is not None else None}')
            User(id).login(sid, ip, localIP, port, submask, natType)
        @self.socketio.on('disconnect')
        def logout():
            sid = flask.request.sid
            user = User.FindUserBySID(sid)
            print(f'logout, id:{user.id}, localIP:{user.localIP}, sid:{user.sid}')
            for userID in user.TURN_connecting:
                other = User(userID)
                if user.id in other.TURN_connecting:
                    other.TURN_connecting.remove(user.id)
                    emit('TURN_disconnect', {'id':user.id}, to=other.sid)
            User.RemoveUserBySID(sid)
        @self.socketio.on('uploadSong')
        def uploadSong(data):
            '''data = {"hash", "name", "artist", "album", "fileExt", "fileSize"}'''
            user = User.FindUserBySID(flask.request.sid)
            hash = data["hash"]
            name = data["name"]
            artist = data["artist"]
            album = data["album"]
            fileExt = data["fileExt"]
            fileSize = data["fileSize"]
            print(f"uploadSong, hash:{hash}, name:{name}, artist:{artist}, album:{album},"
                  f"fileExt:{fileExt}, fileSize:{fileSize}")
            try:
                _ = musicFileRecordTable.get(hash)
                record = MusicFileRecord(hash)
                record.addName(name).addUser(user.id).addArtist(artist).addAlbum(album).setFileExt(fileExt).setFileSize(fileSize)
            except NotFoundError:
                print(f'no muisc {hash} found, create new record')
                musicFileRecordTable.insert({
                    "hash": hash,
                    "names": json.dumps([name]) if name is not None else None,
                    "users": json.dumps([user.id]),
                    "artists": json.dumps([artist]) if artist is not None else None,
                    "albums": json.dumps([album]) if album is not None else None,
                    "fileExt": fileExt,
                    "fileSize": int(fileSize) if fileSize is not None else None
                })
                MusicFileRecord(hash)
        @self.socketio.on('deleteSong')
        def deleteSong(data):
            '''data = {"hash":hash}'''
            hash = data["hash"]
            user = User.FindUserBySID(flask.request.sid)
            print(f"deleteSong, hash:{hash}")
            record = MusicFileRecord(hash)
            record.removeUser(user.id)
            #no need to delete record if no user holds it
        @self.socketio.on('findSong')
        def findSong(data):
            '''Return songs in json format(list[dict]). Each dict contains hash, names, artists, fileExt, fileSize'''
            keywords = data['keywords'].split(" ")
            mode = data['mode'].lower() # "name" or "artist" or "album"
            if mode[-1]!='s':
                mode += 's'
            findSQL = "%" + "%".join(keywords) + "%"
            result = musicFileRecordTable.find(mode, "LIKE", findSQL, toTuple=True)
            print('findSong, keywords:', keywords, ', mode:', mode, ', result:', result)
            if result is None:
                return tuple()
            return tuple(result)
        @self.socketio.on('findSongHolders')
        def findSongHolders(data):
            '''return userIDs holding the resources'''
            hash = data['hash'] #song hash
            recordHolderIDs = MusicFileRecord(hash).users
            result = []
            for user in User.AllCurrentUsers():
                if user.id in recordHolderIDs:
                    result.append(dict(id=user.id, ip=user.ip, localIP=user.localIP, natType=user.natType.value))
                if len(result) == USER_TRACK_LIMIT:
                    break
            print(f'findSongHolders, hash:{hash}, holders:{recordHolderIDs}, result:{result}')
            return tuple(result)
        @self.socketio.on('requestSong')
        def help_connect_to(data):
            '''help user to connect to other users'''
            targetID = data['targetID']
            selfID = User.FindUserBySID(flask.request.sid).id

            if not User.HasCurrentUser(targetID):
                ret ={'reason':ConnectionFailReason.UserNotFound.name, 'code':ConnectionFailReason.UserNotFound.value}
                return json.dumps(ret)

            targetUser = User(targetID)
            thisUser = User(selfID)
            print(f'help_connect_to, targetID:{targetID}, targetIP:{targetUser.ip}, '
                  f'selfID:{selfID}, selfIP:{thisUser.ip}, targetNatType:{targetUser.natType.name}, selfNatType:{thisUser.natType.name}')

            if checkIpInSameSubnet(targetUser.ip, thisUser.ip, targetUser.submask):
                print(f'maybe same subnet, try direct connect')
                #try directly connect
                def onDirectConnectFailHandler(result):
                    if not result:
                        print(f'direct connect failed, trying TURN')
                        #direct connect failed, try TURN
                        self.help_TURN_connect(targetUser, thisUser)
                    else:
                        print(f'subnet direct connect success')
                self.help_direct_connect(targetUser.localIP, targetUser.port, thisUser, onDirectConnectFailHandler)
                return

            if (targetUser.natType == NATType.SymmetricNAT or thisUser.natType == NATType.SymmetricNAT
                or targetUser.natType == NATType.Unknown or thisUser.natType == NATType.Unknown
                or targetUser.natType == NATType.SymmetricUDPFirewall or thisUser.natType == NATType.SymmetricUDPFirewall):
                #TURN mode
                print('some user is SymmetricNAT or Unknown or SymmetricUDPFirewall, trying TURN')
                self.help_TURN_connect(targetUser, thisUser)

            elif targetUser.natType == NATType.RestrictPortNAT or targetUser.natType == NATType.RestrictNAT:
                print('target user is RestrictPortNAT or RestrictNAT, trying repeat UDP hole punch')
                self.help_repeat_udp_hole_punch(targetUser, thisUser)

            elif thisUser.natType == NATType.RestrictPortNAT or targetUser.natType == NATType.RestrictNAT:
                print('request user is RestrictPortNAT or RestrictNAT, trying repeat UDP hole punch')
                self.help_repeat_udp_hole_punch(thisUser, targetUser)

            elif targetUser.natType == NATType.FullCone:
                print('target user is FullCone, trying normal UDP hole punch')
                self.help_normal_udp_hole_punch(targetUser, thisUser)

            elif thisUser.natType == NATType.FullCone:
                print('request user is FullCone, trying normal UDP hole punch')
                self.help_normal_udp_hole_punch(thisUser, targetUser)

            else:
                #both open internet
                print('both open internet, trying direct connect')
                self.help_direct_connect(targetUser.ip, targetUser.port, thisUser)

    def help_TURN_connect(self, user1:User, user2:User):
        if user2.id in user1.TURN_connecting or user1.id in user2.TURN_connecting:
            return
        def TURNFailHandler(target, failer, result):
            if not result:
                #TURN failed, give up
                if failer.id in target.TURN_connecting:
                    target.TURN_connecting.remove(failer.id)
                    emit("TURN_disconnect", {'sid': failer.sid, 'id':failer.id}, to=target.sid)
        user1Handler = partial(TURNFailHandler, user2, user1)
        user2Handler = partial(TURNFailHandler, user1, user2)
        emit("TURN_connect", {'sid': user1.sid, 'id':user1.id}, to=user2.sid, callback=user1Handler)
        emit("TURN_connect", {'sid': user2.sid, 'id':user2.id}, to=user1.sid, callback=user2Handler)
        user1.TURN_connecting.append(user2.sid)
        user2.TURN_connecting.append(user1.sid)

    def help_direct_connect(self, targetIP:str, targetPort:int, connector:User, callback=None):
        if callback:
            emit("direct_connect", {'ip': targetIP, 'port': targetPort}, to=connector.sid, callback=callback)
        else:
            emit("direct_connect", {'ip': targetIP, 'port': targetPort}, to=connector.sid)

    def help_repeat_udp_hole_punch(self, targetIP:str, targetPort:int, puncher:User):
        # UDP hole punch by sending udp repeatedly
        emit("udpHolePunch_repeat", {'ip': targetIP, 'port': targetPort}, to=puncher.sid)
    def help_normal_udp_hole_punch(self, targetIP:str, targetPort:int, puncher:User):
        # normal udp hole punch, only send once
        emit("udpHolePunch_once", {'ip': targetIP, 'port': targetPort}, to=puncher.sid)

        # endregion

    def run(self):
        self.socketio.run(self.app, debug=True, host='0.0.0.0', port=9192, allow_unsafe_werkzeug=True)

# endregion

if __name__ == '__main__':
    server = Server()
    server.run()