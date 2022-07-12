from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user, login_required, UserMixin
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class Clothes(db.Model):
  __tablename__ = 'clothes'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  userId = db.Column(db.Integer)
  name = db.Column(db.String(32))
  category = db.Column(db.String(32))
  color = db.Column(db.String(32))

class Cloth_set(db.Model):
  userId = db.Column(db.Integer,primary_key=True)
  setName = db.Column(db.String(32),primary_key=True)
  top = db.Column(db.String(32))
  outer = db.Column(db.String(32))
  buttom = db.Column(db.String(32))
  shoes = db.Column(db.String(32))
  accessory = db.Column(db.String(32))

class Friend(db.Model):
  loginuserId = db.Column(db.Integer, primary_key=True)
  frienduserId = db.Column(db.Integer, primary_key=True)

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100))
  name = db.Column(db.String(1000))

class ClothesLog(db.Model):
  loginuserId = db.Column(db.Integer, primary_key=True)
  friendId = db.Column(db.Integer, primary_key=True)
  clothesId = db.Column(db.Integer,primary_key=True)
  
   

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

@app.route("/")
def index():
  return render_template('title.html')
    
@app.route('/home')
def home():
  name = session["name"]
  return render_template('home.html', name=name)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method =='POST':
    session.permanent = True
    email = request.form['email']
    password = request.form['password']

    found_user = User.query.filter_by(email=email, password=password).first()
    if found_user:
      session["email"] = email
      session["name"]  = User.query.filter_by(email=email).first().name
      session["id"]  = User.query.filter_by(email=email).first().id
      return redirect(url_for('home'))
    else:
      flash("入力された内容では登録がありません。ご確認ください。")
      return redirect(url_for('login'))
    
  else:
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'GET':
    return render_template('signup.html')
  else:
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
  
    found_user = User.query.filter_by(email=email).first()

    if found_user:
      flash('アカウントが既に存在しています。')
      return redirect(url_for('signup'))

    else:
      new_user = User(email=email, name=name, password=password)
    
      #add new user
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('login'))

@app.route('/deleteAccount', methods=['GET', 'POST'])
def signout():
  if request.method == 'GET':
    flash('ユーザーネーム：'+session["name"])
    flash('メールアドレス：'+session["email"])
    flash('アカウントを削除しますか？')
    return render_template('deleteAccount.html')
  else:
    password = request.form['password']
    
    check_user = User.query.filter_by(id=session["id"] ,password=password).first()
    flash(check_user)
    if check_user:
      User.query.filter_by(id=session["id"]).delete()
      db.session.commit()
      return redirect(url_for('signout'))

    else:
      flash('パスワードが違います。')
      return redirect(url_for('signout'))

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/clothes',methods=['GET','POST'])
def clothesfunc():
  if request.method == 'GET':
    clothes = db.session.query(Clothes).filter_by(userId=session["id"])
    return render_template('clothes.html',clothes=clothes)
  else:
    userId = session["id"]
    name = request.form.get('name')
    category = request.form.get('category')
    color = request.form.get('color')

    newClothes = Clothes(userId=userId,name=name,category=category,color=color)

    db.session.add(newClothes)
    db.session.commit()

    return redirect('/clothes')

@app.route('/clothes/register')
def clothesRegister():
  return render_template('clothesRegister.html')


@app.route('/clothesSet',methods=['GET','POST'])
def clothesSetfunc():
  if request.method == 'GET':
    clothesSet = Cloth_set.query.filter_by(userId=session["id"])
    return render_template('clothesSet.html',clothesSet=clothesSet)
  else:
    setName = request.form.get('setName')
    top = request.form.get('top')
    outer = request.form.get('outer')
    buttom = request.form.get('buttom')
    shoes = request.form.get('shoes')
    accessory = request.form.get('accessory')

    newClothesSet = Cloth_set(userId=session["id"],setName=setName,top=top,outer=outer,buttom=buttom,shoes=shoes,accessory=accessory)

    db.session.add(newClothesSet)
    db.session.commit()

    return redirect('/clothesSet')

@app.route('/clothesSet/register',methods=['GET'])
def clothesSet():
  if request.method == 'GET':
    top = db.session.query(Clothes).filter_by(userId=session["id"],category='トップス')
    outer = db.session.query(Clothes).filter_by(userId=session["id"],category='アウター')
    buttom = db.session.query(Clothes).filter_by(userId=session["id"],category='ボトムズ')
    shoes = db.session.query(Clothes).filter_by(userId=session["id"],category='シューズ')
    accessory = db.session.query(Clothes).filter_by(userId=session["id"],category='アクセサリー')

    return render_template('clothesSetRegister.html',top=top,outer=outer,buttom=buttom,shoes=shoes,accessory=accessory)

@app.route('/suggestion',methods=['GET','POST'])
def suggestion():
  if request.method == 'GET':
    friends = Friend.query.filter_by(loginuserId=session["id"]).all()
    friends_id = [friend.frienduserId for friend in friends]

    friend = [User.query.filter_by(id=friend_id) for friend_id in friends_id]
    # print(friend[0])
    return render_template('suggestion.html',friend=friend)
  else:
    friend = request.form.get('friend')
    LastClothes = ClothesLog.query.filter_by(friendId=friend)

    db.session.add()
    db.session.commit()

    return redirect('/clothesSet')
  return render_template('suggestion.html')

@app.route('/friend')
def friend():
  return render_template('friend.html')
  
@app.route('/setting')
def setting():
  return render_template('setting.html')

@app.route('/friendlist')
def friendlist():
  """fdlistid = db.session.query(Friend).filter_by(loginuserId=session["id"]).all().frienduserId
  fdnames = db.session.query(User).filter_by(id=fdlistid).all().name"""
  
  fdlistid = Friend.query.filter_by(loginuserId=session["id"]).with_entities(Friend.frienduserId)
  
  #fdlistid = Friend.query(Friend.frienduserId).filter_by(loginuserId=session["id"]).all()
  #fdnames = User.query(User.name).filter_by(id=fdlistid).all()
  '''
  fdlists = Friend.query.filter_by(loginuserId=session["id"]).all()
  fdlistids = []
  for fdlist in fdlists:
    fdlistids.append(fdlist.frienduserId)
  fdnames = [User.query.filter_by(id=fdlistid) for fdlistid in fdlistids]
  '''
  fdnames = User.query.filter_by(id=fdlistid).with_entities(User.name).all()
  
  return render_template('friendlist.html', fdnames=fdnames)

@app.route('/friendadd', methods=['GET', 'POST'])
def friendadd():
  if request.method == 'GET':
    return render_template('friendadd.html')
  else:
    friendemail = request.form['friendemail']
  
    found_friend = User.query.filter_by(email=friendemail).first()
    
    if found_friend:
      friendid = User.query.filter_by(email=friendemail).first().id
      new_friend = Friend()
      new_friend.loginuserId=session["id"]
      new_friend.frienduserId=friendid
    
      #add new user
      db.session.add(new_friend)
      db.session.commit()
      return redirect(url_for('friendlist'))

    else:
      flash('アカウントが存在していません。')
      return redirect(url_for('friendadd'))


if __name__ == '__main__':
  #db.create_all()
  app.run(debug=True, host='0.0.0.0', port=8080)
  