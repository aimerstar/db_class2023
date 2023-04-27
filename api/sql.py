from typing import Optional
from link import *

class DB():
    def connect():
        cursor = connection.cursor()
        return cursor

    def prepare(sql):
        cursor = DB.connect()
        cursor.prepare(sql)
        return cursor

    def execute(cursor, sql):
        cursor.execute(sql)
        return cursor

    def execute_input(cursor, input):
        cursor.execute(None, input)
        return cursor

    def fetchall(cursor):
        return cursor.fetchall()

    def fetchone(cursor):
        return cursor.fetchone()

    def commit():
        connection.commit()

class Member():
    def get_member(account):
        sql = "SELECT ACCOUNT, PASSWORD, MID, IDENTITY, NAME FROM MEMBER WHERE ACCOUNT = :id"
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'id' : account}))

    def get_all_member():
        sql = "SELECT * FROM MEMBER ORDER BY NAME"
        return DB.fetchall(DB.execute(DB.connect(), sql))
    
    def get_all_account():
        sql = "SELECT ACCOUNT FROM MEMBER"
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def create_member(input):
        sql = 'INSERT INTO MEMBER VALUES (null, :name, :account, :password, :identity)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    
    def get_role(userid):
        sql = 'SELECT IDENTITY, NAME FROM MEMBER WHERE MID = :id '
        return DB.fetchone(DB.execute_input( DB.prepare(sql), {'id':userid}))
    
    def get_name(account):
        sql = "SELECT NAME FROM MEMBER WHERE MID = :id"
        return DB.fetchone(DB.execute_input( DB.prepare(sql), {'id' : account}))[0]
    
    def count():
        sql = 'SELECT COUNT(*) FROM MEMBER'
        return DB.fetchone(DB.execute( DB.connect(), sql))
    
    def ex_get_member(id):
        sql = 'SELECT * FROM MEMBER WHERE MID != :id '
        return DB.fetchall(DB.execute_input( DB.prepare(sql), {'id':id}))

class Room():
    def count():
        sql = "SELECT COUNT(*) FROM ROOM WHERE INVALID='Y' "
        return DB.fetchone(DB.execute( DB.connect(), sql))
    
    def get_Room(mId):
        sql = "SELECT * FROM ROOM WHERE MID = :mId AND INVALID='Y' "
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'mId': mId}))
    
    def get_Room_by_sTime(roomId):
        sql ="SELECT * FROM ROOM WHERE ROOMID = :roomId AND INVALID='Y' "
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'roomId': roomId}))

    def get_all_room():
        sql = "SELECT * FROM ROOM WHERE INVALID='Y' "
        return DB.fetchall(DB.execute( DB.connect(), sql))

    def add_room(input):
        sql = "INSERT INTO ROOM VALUES (:mId, :roomId, :roomName, :roomNum ,'Y')"
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def update_room(input):
        sql = "UPDATE ROOM SET INVALID='N' WHERE MID=:mId and roomId=:roomId"
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

class Friend():
    def get_all_friend(id):
        sql = 'SELECT * FROM ADDFRIEND where MID = :id '
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'id': id}))
    
    def find_friend(id, friendId):
        sql = 'SELECT * FROM ADDFRIEND where MID = :id and FRIENDID LIKE :friendId '
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'id': id, 'friendId': '%' + friendId + '%'}))
    
    def count(id):
        sql = 'SELECT COUNT(*) FROM ADDFRIEND where MID = :id '
        return DB.fetchall(DB.execute_input( DB.prepare(sql), {'id':id}))[0]
    
    def add_friend(input):
        sql = 'INSERT INTO ADDFRIEND VALUES (:mId, :friendId)'
        DB.execute_input( DB.prepare(sql), input)
        DB.commit()

    def delete_friend(id, friendId):
        sql = 'DELETE FROM ADDFRIEND WHERE MID=:id and FRIENDID=:friendId '
        DB.execute_input(DB.prepare(sql), {'id': id, 'friendId':friendId})
        DB.commit()

    def check_addfriend(id,friendId):
        sql = 'SELECT * FROM ADDFRIEND WHERE MID=:id and FRIENDID=:friendId '
        DB.execute_input(DB.prepare(sql), {'id': id, 'friendId':friendId})
        DB.commit()

class BlackFriend():
    def get_all_friend(id):
        sql = 'SELECT * FROM ADDBLACK where MID = :id '
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'id': id}))
    
    def find_friend(id, friendId):
        sql = 'SELECT * FROM ADDBLACK where MID = :id and BLACKID LIKE :friendId '
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'id': id, 'friendId': '%' + friendId + '%'}))
    
    def count(id):
        sql = 'SELECT COUNT(*) FROM ADDBLACK where MID = :id '
        return DB.fetchall(DB.execute_input( DB.prepare(sql), {'id':id}))[0]
    
    def add_friend(input):
        sql = 'INSERT INTO ADDBLACK VALUES (:mId, :friendId)'
        DB.execute_input( DB.prepare(sql), input)
        DB.commit()
    
    def delete_friend(id, friendId):
        sql = 'DELETE FROM ADDBLACK WHERE MID=:id and BLACKID=:friendId '
        DB.execute_input(DB.prepare(sql), {'id': id, 'friendId':friendId})
        DB.commit()

class Join():
    def find_join(id):
        sql = 'SELECT * FROM JOINGAME where MID = :id '
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'id': id}))
    
    def find_self_join(id):
        sql = 'SELECT * FROM JOINGAME where MID = :id '
        return DB.fetchone( DB.execute_input( DB.prepare(sql), {'id': id}))

    def add_join(input):
        sql = "INSERT INTO JOINGAME VALUES (:mId, :roomId, TO_DATE(:jTime, 'yyyy/mm/dd hh24:mi:ss' ))"
        DB.execute_input( DB.prepare(sql), input)
        DB.commit()

    def find_same_room_num(roomId):
        sql = "SELECT COUNT(*) FROM JOINGAME where roomId=:roomId "
        return DB.fetchone( DB.execute_input( DB.prepare(sql), {'roomId': roomId }))[0]
    
    def find_same_room(roomId):
        sql = "SELECT * FROM JOINGAME where roomId=:roomId "
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'roomId': roomId}))
    
    def count():
        sql = 'SELECT COUNT(*) FROM JOINGAME'
        return DB.fetchone(DB.execute( DB.connect(), sql))
    
    def update_join(input):
        sql = "UPDATE JOINGAME SET ROOMID=:roomId, JTIME=TO_DATE(:jTime, 'yyyy/mm/dd hh24:mi:ss') WHERE mId=:mId"
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    
    def delete_join(id):
        sql = 'DELETE FROM JOINGAME WHERE MID=:id '
        DB.execute_input(DB.prepare(sql), {'id': id})
        DB.commit()
    
class Record():
    def get_all_record(id):
        sql = 'SELECT * FROM RECORD where MID = :id ORDER BY SCORE DESC '
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'id': id}))
    
    def count(id):
        sql = 'SELECT COUNT(*) FROM RECORD where MID = :id '
        return DB.fetchall(DB.execute_input( DB.prepare(sql), {'id':id}))[0]
    
    def member_score_count():
        sql = 'SELECT SUM(SCORE), RECORD.MID, MEMBER.NAME FROM RECORD, MEMBER WHERE RECORD.MID = MEMBER.MID GROUP BY RECORD.MID, MEMBER.NAME ORDER BY SUM(SCORE) DESC'
        return DB.fetchall( DB.execute( DB.connect(), sql))
    
    def member_join_count():
        sql = 'SELECT COUNT(*), RECORD.MID, MEMBER.NAME FROM RECORD, MEMBER WHERE RECORD.MID = MEMBER.MID GROUP BY RECORD.MID, MEMBER.NAME ORDER BY COUNT(*) DESC'
        return DB.fetchall( DB.execute( DB.connect(), sql))
    
    def add_record(input):
        sql = "INSERT INTO RECORD VALUES (:mId, :roomId, :gameId, :gameTime, :score)"
        DB.execute_input( DB.prepare(sql), input)
        DB.commit()
    
    
class Game():
    def get_name(id):
        sql = "SELECT GAMENAME FROM GAME WHERE GAMEID = :id "
        return DB.fetchone(DB.execute_input( DB.prepare(sql), {'id' : id}))[0]

    def get_all_game():
        sql = 'SELECT * FROM GAME'
        return DB.fetchall(DB.execute( DB.connect(), sql))

class Play():
    def add_play(input):
        sql = "INSERT INTO PLAY VALUES (:mId, :roomId, :gameId, TO_DATE(:sTime, 'yyyy/mm/dd hh24:mi:ss'))"
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    
    def update_play(input):
        sql = "UPDATE PLAY SET STIME=TO_DATE(:sTime, 'yyyy/mm/dd hh24:mi:ss') WHERE mId=:mId and roomId=:roomId and gameId=:gameId"
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    
    def get_play(id, roomId):
        sql = "SELECT * FROM PLAY where MID=:id and roomId=:roomId"
        return DB.fetchone( DB.execute_input( DB.prepare(sql), {'id': id, 'roomId': roomId}))
    
    def get_play_poly(id, roomId, gameId):
        sql = "SELECT * FROM PLAY where MID=:id and roomId=:roomId and gameId=:gameId"
        return DB.fetchone( DB.execute_input( DB.prepare(sql), {'id': id, 'roomId': roomId, 'gameId': gameId}))
    
#後台:會員管理
class Member_List():
    def get_member():
        sql = 'SELECT MID, NAME, ACCOUNT,IDENTITY FROM MEMBER WHERE IDENTITY = :identity'
        return DB.fetchall( DB.execute_input( DB.prepare(sql), {'identity':'user'}))
    
    def get_memberdetail():
        sql = 'SELECT A.MID, A.FRIENDID, M.NAME, M.ACCOUNT FROM ADDFRIEND A, MEMBER M WHERE A.FRIENDID = M.MID'
        return DB.fetchall(DB.execute(DB.connect(), sql))
    
    def get_blackdetail():
        sql = 'SELECT B.MID, B.BLACKID, M.NAME, M.ACCOUNT FROM ADDBLACK B, MEMBER M WHERE B.BLACKID = M.MID'
        return DB.fetchall(DB.execute(DB.connect(), sql))

#後台:遊戲管理
class Game_List():
    def get_gameid(gid):
        sql ='SELECT * FROM GAME WHERE GAMEID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': gid}))

    def get_all_gamelist():
        sql = 'SELECT * FROM GAME'
        return DB.fetchall(DB.execute( DB.connect(), sql))
    
    def get_gname(gid):
        sql = 'SELECT GAMENAME FROM GAME WHERE GAMEID = :id'
        return DB.fetchone(DB.execute_input( DB.prepare(sql), {'id':gid}))[0]

    def add_gamelist(input):
        sql = 'INSERT INTO GAME VALUES (:gid, :name, :description)'

        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    
    def delete_recordcheck(gid):
        sql = 'SELECT * FROM RECORD WHERE GAMEID=:gid'
        return DB.fetchone(DB.execute_input( DB.prepare(sql), {'gid':gid}))
    
    def delete_gamelist(gid):
        sql = 'DELETE FROM GAME WHERE GAMEID = :id '
        DB.execute_input(DB.prepare(sql), {'id': gid})
        DB.commit()

    def update_gamelist(input):
        sql = 'UPDATE GAME SET GAMENAME=:name, GAMEDESC=:description WHERE GAMEID=:gid'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()