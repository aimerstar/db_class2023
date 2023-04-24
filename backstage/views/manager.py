from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        gid = request.values.get('delete')
        data = Game_List.delete_recordcheck(gid)
        
        if(data != None):
            flash('failed')
        else:
            data = Game_List.get_gname(gid)
            Game_List.delete_gamelist(gid)
    
    elif 'edit' in request.values:
        gid = request.values.get('edit')
        return redirect(url_for('manager.edit', gid=gid))
    
    gamelist_data = gamelist()
    return render_template('productManager.html', gamelist_data = gamelist_data, user=current_user.name)

def gamelist():
    gamelist_row = Game_List.get_all_gamelist()
    gamelist_data = []
    for i in gamelist_row:
        gamelist = {
            '遊戲編號': i[0],
            '遊戲名稱': i[1],
            '遊戲說明': i[2]
        }
        gamelist_data.append(gamelist)
    return gamelist_data

# 新增商品
@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            number = str(random.randrange( 10000, 99999))
            en = random.choice(string.ascii_letters)
            gid = en + number
            data = Game_List.get_gameid(gid)

        name = request.values.get('name')
        description = request.values.get('description')

        if (len(name) < 1 or len(description) < 1):
            return redirect(url_for('manager.productManager'))
        
        Game_List.add_gamelist(
            {'gid' : gid,
             'name' : name,
             'description':description
            }
        )

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

#編輯商品
@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('gamePlatform'))

    if request.method == 'POST':
        Game_List.update_gamelist(
            {
            'name' : request.values.get('name'),
            'description' : request.values.get('description'),
            'gid' : request.values.get('gid')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        gamelist = show_info()
        return render_template('edit.html', data=gamelist)


def show_info():
    gid = request.args['gid']
    data = Game_List.get_gameid(gid)
    gname = data[1]
    description = data[2]

    gamelist = {
        '遊戲編號':gid,
        '遊戲名稱': gname,
        '遊戲說明': description
    }
    return gamelist

#後台:會員管理
@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Member_List.get_member()
        order_data = []
        for i in order_row:
            order = {
                '會員編號': i[0],
                '會員名稱': i[1],
                '會員帳號': i[2],
                
            }
            order_data.append(order)
            
            
        orderdetail_row = Member_List.get_memberdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '會員編號': j[0],
                '好友編號': j[1],
                '好友名稱': j[2],
                '好友帳號': j[3]
            }
            order_detail.append(orderdetail)

        blackdetail_row = Member_List.get_blackdetail()
        black_detail = []

        for b in blackdetail_row:
            blackdetail = {
                '會員編號': b[0],
                '黑名單編號': b[1],
                '黑名單名稱': b[2],
                '黑名單帳號': b[3]
            }
            black_detail.append(blackdetail)
        
    return render_template('orderManager.html', orderData = order_data, orderdetail = order_detail, blackdetail = black_detail, user=current_user.name)


