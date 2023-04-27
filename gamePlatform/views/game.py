import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import timedelta, datetime
from numpy import identity, product
import random, string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Member, Record, Friend, BlackFriend, Room, Join, Game, Play
import uuid

game = Blueprint('game', __name__, template_folder='../templates')

@game.route('/', methods=['GET', 'POST'])
@login_required
def room():
    result = Room.count()
    count = math.ceil(result[0]/9)
    flag = 0

    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    # 加入房間
    if 'addRoom' in request.form:
        mid = request.values.get('addRoom').split(",")[0] # 房主MID
        roomId = request.values.get('addRoom').split(",")[1] # 房間編碼
        join_data = Join.find_join(current_user.id)
        room_num = Join.find_same_room_num(roomId)
        num = Room.get_Room(mid)[3]
        blackFriend = BlackFriend.find_friend(mid, current_user.id)

        if (join_data is not None and len(join_data)!=0):
            msg = '已經進入房間無法再進入另一個'
            roomId = join_data[0][1]
        elif (room_num > num):
            msg = '超過人數上限無法進入'
            return redirect(url_for('game.room'))
        elif (blackFriend is not None and len(blackFriend)!=0):
            msg = '你在房主的黑名單中無法進入'
            return redirect(url_for('game.room'))
        else:    
            data = Room.get_Room(mid)
            msg = ''
            jTime = str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

            Join.add_join(
                {
                    'mId' : current_user.id,
                    'roomId' : data[1],
                    'jTime' : jTime
                }
            )

        game_row = Game.get_all_game()
        game_data = []

        for i in game_row:
            game = {
                '遊戲編號': i[0],
                '遊戲名稱': i[1]
            }
            game_data.append(game)

        join_row = Join.find_same_room(roomId)
        join_data = []

        for i in join_row:
            friendName = Member.get_name(i[0])
            friend = {
                '會員編號': i[0],
                '會員名稱': friendName
            }
            join_data.append(friend)
            
        return render_template('joinList.html', join_data=join_data, game_data=game_data, user=current_user.name, msg=msg)
    

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        keyword = search
        
        cursor.prepare("SELECT * FROM ROOM WHERE ROOMNAME LIKE :search and INVALID='Y'")
        cursor.execute(None, {'search': '%' + keyword + '%'})
        room_row = cursor.fetchall()
        room_data = []
        final_data = []
        
        for i in room_row:
            friendName = Member.get_name(i[0])
            room_num = Join.find_same_room_num(i[1])
            room = {
                '房間名稱': i[2],
                '房間總人數': i[3],
                '房間現在人數': room_num,
                '房主編碼': i[0],
                '房間編碼': i[1],
                '房主名稱': friendName
            }
            room_data.append(room)
            total = total + 1
        
        if(len(room_data) < end):
            end = len(room_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(room_data[j])
            
        count = math.ceil(total/9)
        
        return render_template('room.html', single=single, keyword=search, room_data=room_data, user=current_user.name, page=1, flag=flag, count=count)    

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        
        room_row = Room.get_all_room()
        room_data = []
        final_data = []
        
        for i in room_row:
            friendName = Member.get_name(i[0])
            room_num = Join.find_same_room_num(i[1])
            room = {
                '房間名稱': i[2],
                '房間總人數': i[3],
                '房間現在人數': room_num,
                '房主編碼': i[0],
                '房間編碼': i[1],
                '房主名稱': friendName
            }
            room_data.append(room)
            
        if(len(room_data) < end):
            end = len(room_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(room_data[j])
        
        return render_template('room.html', room_data=final_data, user=current_user.name, page=page, flag=flag, count=count)    
    
    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.prepare("SELECT * FROM ROOM WHERE ROOMNAME LIKE :search and INVALID='Y'")
        cursor.execute(None, {'search': '%' + keyword + '%'})
        room_row = cursor.fetchall()
        room_data = []
        total = 0
        
        for i in room_row:
            friendName = Member.get_name(i[0])
            room_num = Join.find_same_room_num(i[1])
            room = {
                '房間名稱': i[2],
                '房間總人數': i[3],
                '房間現在人數': room_num,
                '房主編碼': i[0],
                '房間編碼': i[1],
                '房主名稱': friendName
            }

            room_data.append(room)
            total = total + 1
            
        if(len(room_data) < 9):
            flag = 1
        
        count = math.ceil(total/9)    
        
        return render_template('room.html', keyword=search, single=single, room_data=room_data, user=current_user.name, page=1, flag=flag, count=count)    
    
    else:
        room_row = Room.get_all_room()
        room_data = []
        for i in room_row:
            friendName = Member.get_name(i[0])
            room_num = Join.find_same_room_num(i[1])
            room = {
                '房間名稱': i[2],
                '房間總人數': i[3],
                '房間現在人數': room_num,
                '房主編碼': i[0],
                '房間編碼': i[1],
                '房主名稱': friendName
            }
            if len(room_data) < 9:
                room_data.append(room)
        
        return render_template('room.html', room_data=room_data, user=current_user.name, page=1, flag=flag, count=count)

@game.route('/createRoom', methods=['GET', 'POST'])
@login_required
def createRoom():
    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    elif request.method == 'POST':
        # 創建房間
        if "create" in request.form :
            roomName = request.values.get('roomName')
            roomNum = request.values.get('roomNum')
            room = Room.get_Room(current_user.id)
            join = Join.find_join(current_user.id)
            msg = ''
            if (room is not None and len(room)!=0):
                msg = '已經建立房間無法再建立，直接進入房間'
            elif (join is not None and len(join)!=0):
                msg = '已經參加一個房間無法再建立另一個'
            else:
                roomId = str(uuid.uuid4()).replace('-','')
                jTime = str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                Room.add_room(
                    {
                        'mId' : current_user.id,
                        'roomId' : roomId,
                        'roomName' : roomName,
                        'roomNum' : roomNum
                    }
                )

                Join.add_join(
                    {
                        'mId' : current_user.id,
                        'roomId' : roomId,
                        'jTime' : jTime
                    }
                )

            roomId = Join.find_self_join(current_user.id)[1]
            join_row = Join.find_same_room(roomId)
            join_data = []

            for i in join_row:
                friendName = Member.get_name(i[0])
                friend = {
                    '會員編號': i[0],
                    '會員名稱': friendName
                }
                join_data.append(friend)
            
            game_row = Game.get_all_game()
            game_data = []

            for i in game_row:
                game = {
                    '遊戲編號': i[0],
                    '遊戲名稱': i[1]
                }
                game_data.append(game)

            return render_template('joinList.html', join_data=join_data, game_data=game_data, user=current_user.name, msg=msg)
        
        # 返回房間大廳
        elif "back" in request.form:
            return redirect(url_for('game.room'))
        
    return render_template('createRoom.html', user=current_user.name)    

@game.route('/joinList', methods=['GET', 'POST'])
@login_required
def joinList():
    msg = ''
    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    game_row = Game.get_all_game()
    game_data = []

    for i in game_row:
        game = {
            '遊戲編號': i[0],
            '遊戲名稱': i[1]
        }
        game_data.append(game)

    # 開始遊戲
    if "start" in request.form :
        join = Join.find_self_join(current_user.id)
        if (join is None):
            msg = '尚未參加任何一個房間'
            return redirect(url_for('game.room'))
        gameId = request.form['gameId']
        roomId = join[1]
        join_row = Join.find_same_room(roomId)
        for i in join_row:
            play = Play.get_play_poly(i[0], roomId, gameId)
            if(play is not None):
                Play.update_play(
                    {
                        'mId' : i[0],
                        'roomId' : roomId,
                        'gameId' : gameId,
                        'sTime' : str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    }
                )
            else:
                Play.add_play(
                    {
                        'mId' : i[0],
                        'roomId' : roomId,
                        'gameId' : gameId,
                        'sTime' : str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    }
                )
        return render_template('game.html', user=current_user.name, gameId = gameId)
    elif "end" in request.form :
        print('end')
        # 只有房主可以結束房間
        # 房主結束房間後 刪除房間資料以及所有參加紀錄
    elif "leave" in request.form :
        print('leave')
        join = Join.find_self_join(current_user.id)
        print(join)
        if (join is None):
            msg = '尚未參加任何一個房間'
            return redirect(url_for('game.room'))
        roomId = join[1]
        print(roomId)
        Join.delete_join(current_user.id)
        # 如果沒間都沒有參加人，房間作廢
        # TODO 如果房主離開也要更新房間
        room_num = Join.find_same_room_num(roomId)
        print(room_num)
        if(room_num==0):
            mId = Room.get_Room_by_sTime(roomId)[0]
            Room.update_room(
            {
                'mId' : mId,
                'roomId' : roomId
            }
        )

    elif "delete" in request.form :
        print('delete')
        friendId = request.values.get('delete')
        if(friendId==current_user.id):
            msg = '不可以自己踢掉自己'
        # TODO 不可以踢掉房主
        else:
            Join.delete_join(friendId)
    
    # 房間大廳 返回房間
    join = Join.find_self_join(current_user.id)
    if (join is None):
        msg = '尚未參加任何一個房間'
        return redirect(url_for('game.room'))
    
    roomId = join[1]
    join_row = Join.find_same_room(roomId)
    join_data = []

    for i in join_row:
        friendName = Member.get_name(i[0])
        friend = {
            '會員編號': i[0],
            '會員名稱': friendName
        }
        join_data.append(friend)
            
    return render_template('joinList.html', join_data=join_data, game_data=game_data, user=current_user.name, msg=msg)

@game.route('/gameStart', methods=['GET', 'POST'])
@login_required
def gameStart():
    msg = ''
    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    game_row = Game.get_all_game()
    game_data = []

    for i in game_row:
        game = {
            '遊戲編號': i[0],
            '遊戲名稱': i[1]
        }
        game_data.append(game)

    if "end" in request.form :
        # 結束遊戲，自動生成每個參與者遊戲紀錄
        roomId = Join.find_self_join(current_user.id)[1]
        join_row = Join.find_same_room(roomId)
        gameId = Play.get_play(current_user.id, roomId)[2]
        mId = Room.get_Room_by_sTime(roomId)[0]
        roomName = Room.get_Room_by_sTime(roomId)[2]
        roomNum = Room.get_Room_by_sTime(roomId)[3]
        roomId_new = str(uuid.uuid4()).replace('-','')
        for i in join_row:
            sTime = Play.get_play(i[0], roomId)[3]
            Record.add_record(
                {
                    'mId' : i[0],
                    'roomId' : roomId,
                    'gameId' : gameId,
                    'gameTime' : (datetime.now() - sTime).seconds,
                    'score' : random.randint(1,100)
                }
            )
            # 因為需要回到原本的房間，可以玩重複的遊戲，所以更新join stime
            Join.update_join(
                {
                    'mId' : i[0],
                    'roomId' : roomId_new,
                    'jTime' : str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                }
            )
        # 更新原本房間
        Room.update_room(
            {
                'mId' : mId,
                'roomId' : roomId
            }
        )

        Room.add_room(
            {
                'mId' : mId,
                'roomId' : roomId_new,
                'roomName' : roomName,
                'roomNum' : roomNum
            }
        )

        msg = '遊戲結束'
        join_row = Join.find_same_room(roomId_new)
        join_data = []

        for i in join_row:
            friendName = Member.get_name(i[0])
            friend = {
                '會員編號': i[0],
                '會員名稱': friendName
            }
            join_data.append(friend)
        return render_template('joinList.html', join_data=join_data, game_data=game_data, user=current_user.name, msg=msg)     
            
    return render_template('game.html', user=current_user.name, msg=msg)

@game.route('/member', methods=['GET', 'POST'])
@login_required
def member():
    result = Member.count()
    count = math.ceil(result[0]/5)
    flag = 0

    # 以防管理者誤闖
    if request.method == 'GET':
        if( current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    # 加入好友名單
    if "addFriend" in request.form :
        friendId = request.values.get('addFriend')
        friend = Friend.find_friend(current_user.id, friendId)
        black = BlackFriend.find_friend(current_user.id, friendId)
        msg = ''
        if (friend is not None and len(friend)!=0):
            msg = '已經存在好友清單'
        elif (black is not None and len(black)!=0):
            msg = '請先刪除黑名單再加好友'
        else:
            Friend.add_friend(
                {
                    'mId' : current_user.id,
                    'friendId' : friendId
                }
            )

        friend_row = Member.ex_get_member(current_user.id)
        friend_data = []

        for i in friend_row:
            friend = {
                '會員編號': i[0],
                '會員名稱': i[1]
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('member.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count, msg=msg)
    
    if "addBlack" in request.form :
        friendId = request.values.get('addBlack')
        friend = BlackFriend.find_friend(current_user.id, friendId)
        black = Friend.find_friend(current_user.id, friendId)
        msg = ''

        if (friend is not None and len(friend)!=0):
            msg = '已經存在黑名單'
        elif (black is not None and len(black)!=0):
            msg = '請先刪除好友再加黑名單'
        else:
            BlackFriend.add_friend(
                {
                    'mId' : current_user.id,
                    'friendId' : friendId
                }
            )

        friend_row = Member.ex_get_member(current_user.id)
        friend_data = []

        for i in friend_row:
            friend = {
                '會員編號': i[0],
                '會員名稱': i[1]
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('member.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count, msg=msg)
    
        
    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        search = request.values.get('keyword')
        keyword = search

        cursor.prepare('SELECT * FROM MEMBER WHERE NAME LIKE :search')
        cursor.execute(None, {'search': '%' + keyword + '%'})
        friend_row = cursor.fetchall()
        friend_data = []
        final_data = []

        for i in friend_row:
            friend = {
                '會員編號': i[0],
                '會員名稱': i[1]
            }
            friend_data.append(friend)
            total = total + 1
        
        if(len(friend_data) < end):
            end = len(friend_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(friend_data[j])
            
        count = math.ceil(total/5)
        
        return render_template('member.html', single=single, keyword=search, friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)    

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        
        friend_row = Member.ex_get_member(current_user.id)
        friend_data = []
        final_data = []

        for i in friend_row:
            friend = {
                '會員編號': i[0],
                '會員名稱': i[1]
            }
            friend_data.append(friend)
            
        if(len(friend_data) < end):
            end = len(friend_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(friend_data[j])
        
        return render_template('member.html', friend_data=final_data, user=current_user.name, page=page, flag=flag, count=count)    
    
    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.prepare('SELECT * FROM MEMBER WHERE NAME LIKE :search')
        cursor.execute(None, {'search': '%' + keyword + '%'})
        friend_row = cursor.fetchall()
        friend_data = []
        total = 0

        for i in friend_row:
            friend = {
                '會員編號': i[0],
                '會員名稱': i[1]
            }

            friend_data.append(friend)
            total = total + 1
            
        if(len(friend_data) < 5):
            flag = 1
        
        count = math.ceil(total/5)    
        
        return render_template('member.html', keyword=search, single=single, friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)    
    
    else:
        friend_row = Member.ex_get_member(current_user.id)
        friend_data = []
        for i in friend_row:
            friend = {
                '會員編號': i[0],
                '會員名稱': i[1]
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('member.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)
    
@game.route('/friend', methods=['GET', 'POST'])
@login_required
def friend():
    result = Friend.count(current_user.id)
    count = math.ceil(result[0]/5)
    flag = 0
    # 以防管理者誤闖
    if request.method == 'GET':
        if( current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    if result[0]==0 :        
        return render_template('empty.html', user=current_user.name, )

    if "delete" in request.form :
        friendId = request.values.get('delete')
        Friend.delete_friend(current_user.id, friendId)

        friend_row = Friend.get_all_friend(current_user.id)
        friend_data = []
        
        for i in friend_row:

            friendName = Member.get_name(i[1])
            friend = {
                '好友編號': i[1],
                '好友名稱': friendName
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('friend.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)
        
    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        search = request.values.get('keyword')
        keyword = search

        cursor.prepare('SELECT * FROM ADDFRIEND WHERE MID=:mId AND FRIENDID IN (SELECT MID FROM MEMBER WHERE NAME LIKE :search )')
        cursor.execute(None, {'mId': current_user.id ,'search': '%' + keyword + '%'})
        friend_row = cursor.fetchall()
        friend_data = []
        final_data = []

        for i in friend_row:

            friendName = Member.get_name(i[1])
            friend = {
                '好友編號': i[1],
                '好友名稱': friendName
            }
            friend_data.append(friend)
            total = total + 1
        
        if(len(friend_data) < end):
            end = len(friend_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(friend_data[j])
            
        count = math.ceil(total/5)
        
        return render_template('friend.html', single=single, keyword=search, friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)    

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        
        friend_row = Friend.get_all_friend(current_user.id)
        friend_data = []
        final_data = []

        for i in friend_row:
            friendName = Member.get_name(i[1])
            friend = {
                '好友編號': i[1],
                '好友名稱': friendName
            }
            friend_data.append(friend)
            
        if(len(friend_data) < end):
            end = len(friend_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(friend_data[j])
        
        return render_template('friend.html', friend_data=final_data, user=current_user.name, page=page, flag=flag, count=count)    
    
    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.prepare('SELECT * FROM ADDFRIEND WHERE MID=:mId AND FRIENDID IN (SELECT MID FROM MEMBER WHERE NAME LIKE :search )')
        cursor.execute(None, {'mId': current_user.id ,'search': '%' + keyword + '%'})
        friend_row = cursor.fetchall()
        friend_data = []
        total = 0

        for i in friend_row:
            friendName = Member.get_name(i[1])
            friend = {
                '好友編號': i[1],
                '好友名稱': friendName
            }

            friend_data.append(friend)
            total = total + 1
            
        if(len(friend_data) < 5):
            flag = 1
        
        count = math.ceil(total/5)    
        
        return render_template('friend.html', keyword=search, single=single, friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)    
    
    else:
        friend_row = Friend.get_all_friend(current_user.id)
        friend_data = []

        for i in friend_row:

            friendName = Member.get_name(i[1])
            friend = {
                '好友編號': i[1],
                '好友名稱': friendName
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('friend.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)

@game.route('/blackfriend', methods=['GET', 'POST'])
@login_required
def blackfriend():
    result = BlackFriend.count(current_user.id)
    count = math.ceil(result[0]/5)
    flag = 0

    # 以防管理者誤闖
    if request.method == 'GET':
        if( current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    if "delete" in request.form :
        friendId = request.values.get('delete')
        BlackFriend.delete_friend(current_user.id, friendId)

        friend_row = BlackFriend.get_all_friend(current_user.id)
        friend_data = []

        for i in friend_row:

            friendName = Member.get_name(i[1])
            friend = {
                '黑名單編號': i[1],
                '黑名單名稱': friendName
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('blackfriend.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)
        
    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        search = request.values.get('keyword')
        keyword = search

        cursor.prepare('SELECT * FROM ADDBLACK WHERE MID=:mId AND BLACKID IN (SELECT MID FROM MEMBER WHERE NAME LIKE :search )')
        cursor.execute(None, {'mId': current_user.id ,'search': '%' + keyword + '%'})
        friend_row = cursor.fetchall()
        friend_data = []
        final_data = []

        for i in friend_row:

            friendName = Member.get_name(i[1])
            friend = {
                '黑名單編號': i[1],
                '黑名單名稱': friendName
            }
            friend_data.append(friend)
            total = total + 1
        
        if(len(friend_data) < end):
            end = len(friend_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(friend_data[j])
            
        count = math.ceil(total/5)
        
        return render_template('blackfriend.html', single=single, keyword=search, friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)    

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        
        friend_row = BlackFriend.get_all_friend(current_user.id)
        friend_data = []
        final_data = []

        for i in friend_row:
            friendName = Member.get_name(i[1])
            friend = {
                '黑名單編號': i[1],
                '黑名單名稱': friendName
            }
            friend_data.append(friend)
            
        if(len(friend_data) < end):
            end = len(friend_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(friend_data[j])
        
        return render_template('blackfriend.html', friend_data=final_data, user=current_user.name, page=page, flag=flag, count=count)    
    
    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.prepare('SELECT * FROM ADDBLACK WHERE MID=:mId AND BLACKID IN (SELECT MID FROM MEMBER WHERE NAME LIKE :search )')
        cursor.execute(None, {'mId': current_user.id ,'search': '%' + keyword + '%'})
        friend_row = cursor.fetchall()
        friend_data = []
        total = 0

        for i in friend_row:
            friendName = Member.get_name(i[1])
            friend = {
                '黑名單編號': i[1],
                '黑名單名稱': friendName
            }

            friend_data.append(friend)
            total = total + 1
            
        if(len(friend_data) < 5):
            flag = 1
        
        count = math.ceil(total/5)    
        
        return render_template('blackfriend.html', keyword=search, single=single, friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)    
    
    else:
        friend_row = BlackFriend.get_all_friend(current_user.id)
        friend_data = []
        for i in friend_row:

            friendName = Member.get_name(i[1])
            friend = {
                '黑名單編號': i[1],
                '黑名單名稱': friendName
            }
            if len(friend_data) < 5:
                friend_data.append(friend)
        
        return render_template('blackfriend.html', friend_data=friend_data, user=current_user.name, page=1, flag=flag, count=count)

@game.route('/record', methods=['GET', 'POST'])
@login_required
def record():
    result = Record.count(current_user.id)
    count = math.ceil(result[0]/5)
    flag = 0

    # 以防管理者誤闖
    if request.method == 'GET':
        if( current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    
    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5

        search = request.values.get('keyword')

        record_row = Record.get_all_record(current_user.id)
        record_data = []
        final_data = []

        for i in record_row:
            gameName = Game.get_name(i[2])
            record = {
                '遊戲編號': i[2],
                '遊戲名稱': gameName,
                '遊戲時間': i[3],
                '遊戲分數': i[4]
            }
            record_data.append(record)
            total = total + 1
        
        if(len(record_data) < end):
            end = len(record_data)
            flag = 1
            
        for j in range(start, end):
            record_data.append(record_data[j])
            
        count = math.ceil(total/5)
        
        return render_template('record.html', single=single, keyword=search, record_data=record_data, user=current_user.name, page=1, flag=flag, count=count)    

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 5
        end = page * 5
        
        record_row = Record.get_all_record(current_user.id)
        record_data = []
        final_data = []

        for i in record_row:
            gameName = Game.get_name(i[2])
            record = {
                '遊戲編號': i[2],
                '遊戲名稱': gameName,
                '遊戲時間': i[3],
                '遊戲分數': i[4]
            }
            record_data.append(record)
            
        if(len(record_data) < end):
            end = len(record_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(record_data[j])
        
        return render_template('record.html', record_data=final_data, user=current_user.name, page=page, flag=flag, count=count)    
    
    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')

        record_row = Record.get_all_record(current_user.id)
        record_data = []
        total = 0

        for i in record_row:
            gameName = Game.get_name(i[2])
            record = {
                '遊戲編號': i[2],
                '遊戲名稱': gameName,
                '遊戲時間': i[3],
                '遊戲分數': i[4]
            }
            record_data.append(record)
            total = total + 1
            
        if(len(record_data) < 5):
            flag = 1
        
        count = math.ceil(total/5)    
        
        return render_template('record.html', keyword=search, single=single, record_data=record_data, user=current_user.name, page=1, flag=flag, count=count)    
    
    else:
        record_row = Record.get_all_record(current_user.id)
        record_data = []
        for i in record_row:
            gameName = Game.get_name(i[2])
            record = {
                '遊戲編號': i[2],
                '遊戲名稱': gameName,
                '遊戲時間': i[3],
                '遊戲分數': i[4]
            }
            if len(record_data) < 5:
                record_data.append(record)
        
        return render_template('record.html', record_data=record_data, user=current_user.name, page=1, flag=flag, count=count)
    

@game.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():

    memberNum = Member.count()[0]
    roomNum = Room.count()[0]
    joinNum = Join.count()[0]

    score_row = Record.member_score_count()
    score_data = []
    for i in score_row:
        data = {
            '會員編號': i[1],
            '會員名稱': i[2],
            '總積分': i[0]
        }
        if len(score_data) < 10:
            score_data.append(data)

    num_row = Record.member_join_count()
    num_data = []
    for i in num_row:
        data = {
            '會員編號': i[1],
            '會員名稱': i[2],
            '總次數': i[0]
        }
        if len(num_data) < 10:
            num_data.append(data)

    return render_template('leaderboard.html', user=current_user.name, memberNum=memberNum, roomNum=roomNum, joinNum=joinNum, score_data=score_data , num_data=num_data )

