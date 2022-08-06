#buzzcommunityhelpdesk@gmail.com
#Module Imports
from flask import Flask,render_template,request,redirect,url_for,session,Response,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import sqlite3
import json
import os
from flask_mail import Mail
from werkzeug.utils import secure_filename
from datetime import datetime
from base64 import b64encode
from PIL import Image
import base64
import smtplib
import random
app=Flask(__name__)

app.secret_key=os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///user.db"
app.config['SQLALCHEMY_BINDS']={"buzzPost":"sqlite:///post.db","like":"sqlite:///like.db","comment":"sqlite:///comment.db","follow" :"sqlite:///follows.db" }
#app.config['SQLALCHEMY_BINDS']={}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config.update(
MAIL_SERVER='smtp.gmail.com',
MAIL_PORT='465',
MAIL_USE_SSL=True,
MAIL_USERNAME='buzzcommunityhelpdesk@gmail.com',
MAIL_PASSWORD='knispchvmypkhxnd'
)
mail=Mail(app)
userDb=SQLAlchemy(app)

class buzz_post(userDb.Model):
	__bind_key__ = "buzzPost"
	postId=userDb.Column(userDb.Integer,primary_key=True)
	post_text=userDb.Column(userDb.Text, nullable=False)
	post_img=userDb.Column( userDb.Text,  nullable=False )
	post_date=userDb.Column(userDb.TIMESTAMP,default=datetime.now())
	author=userDb.Column(userDb.Integer,userDb.ForeignKey('bu_zz_user.userId',ondelete='CASCADE'),nullable=False)
	likes=userDb.relationship('Like',backref="post",passive_deletes=True)
	comments=userDb.relationship('Comment',backref="post",passive_deletes=True)
	@property
	def user_b(self):
		return buZz_user.query.filter_by(userId=self.author).first()

class Like(userDb.Model ):
	__bind_key__ = "like"
	id=userDb.Column(userDb.Integer,primary_key=True, autoincrement=True )
	author=userDb.Column(userDb.Integer,userDb.ForeignKey('bu_zz_user.userId',ondelete='CASCADE'),nullable=False)
	postId=userDb.Column(userDb.Integer,userDb.ForeignKey('buzz_post.postId',ondelete='CASCADE'),nullable=False)

class Comment(userDb.Model ):
	__bind_key__ = "comment"
	id=userDb.Column(userDb.Integer,primary_key=True, autoincrement=True )
	post_text=userDb.Column(userDb.String(300), nullable=False)
	date=userDb.Column(userDb.TIMESTAMP,default=datetime.now())
	author=userDb.Column(userDb.Integer,userDb.ForeignKey('bu_zz_user.userId',ondelete='CASCADE'),nullable=False)
	postId=userDb.Column(userDb.Integer,userDb.ForeignKey('buzz_post.postId',ondelete='CASCADE'),nullable=False)	
	@property
	def user_b(self):
		return buZz_user.query.filter_by(userId=self.author).first()
class Follow(userDb.Model):
    __tablename__ = 'follow'
    __bind_key__ = "follow"
    follower_id = userDb.Column(userDb.Integer, userDb.ForeignKey("bu_zz_user.userId", ondelete='CASCADE' ),primary_key=True)
    followed_id = userDb.Column(userDb.Integer, userDb.ForeignKey('bu_zz_user.userId',ondelete='CASCADE'  ),primary_key=True)
    timestamp = userDb.Column(userDb.TIMESTAMP,default=datetime.now())
 
class buZz_user(userDb.Model):
	userId=userDb.Column(userDb.Integer,primary_key=True)
	name=userDb.Column(userDb.String(200),nullable=False)
	username=userDb.Column(userDb.String(200),nullable=False)
	email=userDb.Column(userDb.String(300),nullable=False)
	password=userDb.Column(userDb.String(200),nullable=False)
	bio=userDb.Column(userDb.String(1000))
	avatar=userDb.Column(userDb.Integer, default=100)
	gender=userDb.Column(userDb.String(100),nullable=False)
	posts=userDb.relationship('buzz_post',backref="bu_zz_user",passive_deletes=True)
	
	likes=userDb.relationship('Like',backref="bu_zz_user",passive_deletes=True)
	comments=userDb.relationship('Comment',backref="bu_zz_user",passive_deletes=True)
	#Following Relation Ship 
	followed = userDb.relationship('Follow',foreign_keys=[Follow.follower_id],backref=userDb.backref('follower', lazy='joined'),lazy='dynamic',cascade='all, delete-orphan',passive_deletes=True)
	
	followers = userDb.relationship("Follow",foreign_keys=[Follow.followed_id],backref=userDb.backref('followed', lazy='joined'),lazy='dynamic',cascade='all, delete-orphan',passive_deletes=True  )
	def is_following(self, user):
		if user.userId is None:
			return False
		con=sqlite3.connect('follows.db')
		cursor=con.cursor()
		cursor.execute(f"SELECT * from 'follow' WHERE followed_id='{user.userId}' AND follower_id='{self.userId}' ")
		isfollowing=cursor.fetchall()
		return  (len(isfollowing) > 0)
	def followed_by(self, user):
		if user.userId is None:
			return False
		con=sqlite3.connect('follows.db')
		cursor=con.cursor()
		cursor.execute(f"SELECT * from 'follow' WHERE followed_id='{user.userId}' AND follower_id='{self.userId}' ")
		isfollowing=currsor.fetchall()
		return  (len(isfollowing) == 0)
		
	def follow(self, user):
		#if not self.is_following(user):
		if self.is_following(user):
			return False
		f = Follow(follower=self, followed=user)
		userDb.session.add(f)
		return True		      
	def unfollow(self, user):        
		con=sqlite3.connect('follows.db')
		cursor=con.cursor()
		cursor.execute(f"SELECT * from 'follow' WHERE followed_id='{user.userId}' AND follower_id='{self.userId}' ")
	
		f=cursor.fetchall()
		print(f)
		if len(f)>0:  
			print('hell')      
			user_id=user.userId
			self_id=self.userId			
			cursor.execute("DELETE  From 'follow' WHERE followed_id=%d AND follower_id=%d " %(user_id,self_id) )
			con.commit()
#			print('deleted')
#			userDb.session.commit()


			return True	      
		else:
			print('hi')
			return False 

	def __repr__(self) -> str:
		return f"{self.userId} - {self.email} - {self.username}  "


		
con=sqlite3.connect('user.db')
cursor=con.cursor()
#@app.route("/show/")
#def show():
#    con=sqlite3.connect('post.db')
#    cursor=con.cursor()
#    cursor.execute(f"SELECT * from 'buzz_post' ")
#    posts=cursor.fetchall()
#    post_len=posts.len()
#    i=0
#    while i<post_len:
#    	posts[i][2]=b64encode(posts[i][2]).decode("utf-8")  
#    print(f'Table {posts}')
#    return redirect('/home',posts=posts   )	
    #image = b64encode(obj.image).decode("utf-8")
    #return render_template("show_a.html", obj=obj, image=image)

def login_required(func):
	def wrapper():
		if 'user_id' in session:
			return func()
		else:
			return redirect('/login')
	wrapper.__name__ = func.__name__
  
	return wrapper
			
def send_otp(email):	
	email=email
	email=[email]	
	otp=random.randint(000000,999999)
	print(otp)
	otp=str(otp)
	mail.send_message(subject="Your buZz OTP",sender='buzzcommunityhelpdesk@gmail.com',
	recipients=email,
	body=f'Your buZz Email verification 6 digit otp is {otp}.        Thankyou buzz user for joining us.'
	)
	return otp
def inotp():
	i1=str(request.form.get("i1"))
	i2=str(request.form.get("i2"))
	i3=str(request.form.get("i3"))
	i4=str(request.form.get("i4"))
	i5=str(request.form.get("i5"))
	i6=str(request.form.get("i6"))
	return (i1+i2+i3+i4+i5+i6)
#@app.route('/deleteuser')
#def deleteuser():
#	conn=sqlite3.connect('user.db')
#	cursor=conn.cursor()	
#	query=f"""DELETE from bu_zz_user where userId={id}"""
#	cursor.execute(query)
#	conn.commit()		
#	return 'Deleted'
@app.route('/')
def index(): 
	return render_template('index.html')
@app.route('/home') 
def home():
	if 'user_id' in session:
		userId=session['user_id']
		posts=buzz_post.query.order_by(desc(buzz_post.post_date)).all()
		user=buZz_user.query.filter_by(userId=userId).first()				
		post_len=len(posts)
		i=0
		img_list=[]
		dates=[]
		todayDate=datetime.now().date()
		print(type(todayDate))
		todayDate=str(todayDate)		
	
		while i<post_len:
			
			d=str(posts[i].post_date).split(' ')
			
			date=d[0]
			dates.append(date)		
			img=posts[i].post_img.split(',')
			if len(img)>1:
				img_list.append(img[1])
			else:
				img_list.append(img)
			
			i=i+1  
    	#print(f'Table {posts}')
		
#		print(img_list), images=img_list
		return render_template('home.html',posts=posts,dates=dates,imgs=img_list,todayDate=todayDate,user=user)
	else:
		return redirect('/login')
@app.route('/signup',methods=['POST','GET'])
def signup_form():
	msg=""
	if 'user_id' in session:
		return redirect('/home')
	else:	
		if request.method=='POST':
			con=sqlite3.connect('user.db')
			cursor=con.cursor()
			name=request.form.get('name')
			email=request.form.get('email')			
			password=request.form.get('userpass')
			
			cursor.execute(f"SELECT * from 'bu_zz_user' WHERE email='{email}' ")
			users=cursor.fetchall()
			if len(users)>0:
			
				msg=f"This user already exists!Try using another email"
				return render_template('signup.html',message=msg)
			else:				
				session['email']=email
				session['name']=name				
				session['password']=password
			
				otp=send_otp(email)	
				session['otp']=otp
				session["username"]=False
				return redirect(url_for('verifyemail'))		
		else:
			return render_template('signup.html')
@app.route('/verifyemail',methods=['POST','GET']) 
def verifyemail():
	email=session['email']
	if request.method=='POST': 
		otp=session['otp']		
		inpotp=inotp()	
		print(inpotp)
		if inpotp==otp:
			if session["username"]:
				return redirect('/newpassword')				
			print('Correct Otp')
			return render_template('userInfo.html')			
		else:
			if session["username"]:
				render_template("emailverify.html ",msg="In correct Otp")				
			print('Otp Incorrect')
			return redirect('/signup')	
	else:	
		return render_template('emailverify.html',email=email)
@app.route('/userinfo',methods=["POST"])
def userinfo():
	if request.method=='POST':
		uname=request.form.get("user_name")
		ugender=request.form.get("user_gender")
		email=session['email']
		name=session['name']		
		password=session['password']
		con=sqlite3.connect('user.db')
		cursor=con.cursor()
		cursor.execute(f"SELECT * from 'bu_zz_user' WHERE username='{uname}' ")
		isuser=cursor.fetchall()
		if len(isuser)>0:
			msg=f"This username already exists!"
			return render_template('userInfo.html',msg=msg)
						
		else:		
			data=buZz_user(name=name,username=uname,email=email,password=password,gender=ugender)
			userDb.session.add(data)
			userDb.session.commit()
			
			cursor.execute(f"SELECT * from 'bu_zz_user' WHERE email='{email}' ")
			users=cursor.fetchall()
			session['user_id']=users[0][0]
			session.pop('email')
			session.pop('name')		
			session.pop('password')			
			session.pop('otp')
			return redirect('/home')																					
@app.route('/login',methods=['POST','GET'])
def login_form():
	msg=""
	if 'user_id' in session:
		return redirect('/home')
	else:
		if request.method=='POST':
			con=sqlite3.connect('user.db')
			cursor=con.cursor() 
			username=request.form.get('user_name')
			#email=request.form.get('ug_id')
			password=request.form.get('upass')
			if '@' in username:
				email=username
				cursor.execute(f"SELECT * from 'bu_zz_user' WHERE email='{email}' AND password='{password}' ")
			else:
				cursor.execute(f"SELECT * from 'bu_zz_user' WHERE  username='{username}' AND password='{password}' ")
			users=cursor.fetchall()
			if len(users)>0:
				session['user_id']=users[0][0]
				msg=""
				return redirect('/home')
			else:
				msg="**Incorrect Username or Password"
				return render_template('login.html',message=msg)
		
		else:	
			return render_template('login.html',message=msg)
@app.route('/enteremail') 
def enteremail():
	return render_template('enteremail.html')
@app.route('/otpenter', methods=["POST"])
def otpenter(): 
	if request.method=='POST':
		email=request.form.get('email')
		if email:
			user=buZz_user.query.filter_by(email=email).first()
			
			if user:
				session["username"]=user.username				
				session ["email"]=email											
				session["otp"]=send_otp(email)
				return render_template("emailverify.html") 
			else:
				msg=f"No acount found with {email} Id!"
				return render_template('enteremail.html',msg=msg)
			
				
									
@app.route('/newpassword',methods=["POST","GET"])
def newpassword():
	if request.method=='POST':
		password=request.form.get('password')
		print(password)
		username=session["username"]
		con=sqlite3.connect('user.db')
		cursor=con.cursor()
		print(username)
		cursor.execute(f"UPDATE 'bu_zz_user' SET password='{password}' WHERE username='{username}' ")
		con.commit()
		return redirect('/login')
	else:
		return render_template('newpassword.html')
		
@app.route('/logout')
def logout():
	if 'user_id' in session:
		session.pop('user_id')
		return redirect('/login')
	else:
		return redirect('/login')
@app.route('/upload',methods=['POST'])
def upload(): 
	userId=session['user_id']

	output = request.get_json(force=True)
		
	listOut=list(output.values())
	lenList=len(listOut)
	dateTime=datetime.now()
	
	if lenList > 1:
		post_text=listOut[0]
		post_img=listOut[1]
	else:
		post_text=listOut[0]
		post_img=' '	
	post=buzz_post(post_text=post_text,post_img=post_img,post_date=dateTime, author=userId )
	
	userDb.session.add(post)
	userDb.session.commit()
	return redirect('/home')
@app.route('/likePost/<int:post_id>' , methods=["POST"])
def likePost(post_id):
	userId=session['user_id']
	post=buzz_post.query.filter_by(postId=post_id).first()
	like=Like.query.filter_by(author=userId,postId=post_id).first()
	if like:
		userDb.session.delete(like)
		userDb.session.commit()
		jsonified=jsonify({"likes":len(post.likes),"liked":userId in map(lambda x:x.author,post.likes)})
								
		return jsonified
	else:
		postLike=Like(author=userId,postId=post_id)
		userDb.session.add(postLike)
		userDb.session.commit()
		jsonified=jsonify({"likes":len(post.likes),"liked":userId in map(lambda x:x.author,post.likes)})
		print('Json Data',jsonified)
		return jsonified
		
@app.route('/addComment/<int:post_id>/<comment>' , methods=["POST"])
def addComment(post_id,comment):		
	comText=comment
	print('Hello here is comment',comText)
	if comText:
		userId=session['user_id']
	#	post=buzz_post.query.filter_by(postId=post_id).first()
		comment=Comment(post_text=comText,author=userId,postId=post_id)
		userDb.session.add(comment)
		userDb.session.commit()
		comments=Comment.query.filter_by(postId=post_id).all()
		text=comment.post_text
		user=comment.author
		userobj=buZz_user.query.filter_by(userId=user). first()
		name=userobj.name
		username=userobj.username
		date=comment.date.strftime("%I:%M %p • %d %b %Y ") 
		
		#for c in comments:
#			text.append(c.post_text)
#			user.append(c.author)
#			date.append(c.date)
		jsonified=jsonify({"comments":text,"user":name,"username":username,"date":date})
		return jsonified
		

@app.route('/contact')
@login_required
def contact():
	return render_template('contactform.html')


@app.route('/profile/<int:id>',methods=['GET']) 
def profile_user(id):
	con=sqlite3.connect('follows.db')
	cursor=con.cursor()
	currentid=session["user_id"] 
	current_user=buZz_user.query.filter_by(userId=currentid).first()
	cursor.execute(f"SELECT * from 'follow' WHERE follower_id='{currentid}' ")
	cufollowed=cursor.fetchall()
	cursor.execute(f"SELECT * from 'follow' WHERE followed_id='{id}' ")
	follows=cursor.fetchall()
	cursor.execute(f"SELECT * from 'follow' WHERE follower_id='{id}' ")
	followers=cursor.fetchall()
	
	#follows=Follow.query.filter_by(followed_id=id).all()
	followerusers=[]
	followedusers=[]
	cufollowedusers=[]
	for  i in follows:
		follower_user=buZz_user.query.filter_by(userId=i[0]).first()
		followerusers.append(follower_user)		
	print(followerusers)
	for i in followers:
		followed_user=buZz_user.query.filter_by(userId=i[1]).first()
		followedusers.append(followed_user)
	for i in cufollowed:
		followed_user=buZz_user.query.filter_by(userId=i[1]).first()
		cufollowedusers.append(followed_user)
		print(cufollowedusers)
	user = buZz_user.query.filter_by(userId=id).first()
	return render_template('profile.html',user=user,follows=followerusers,followed=followedusers,cuser=current_user,cfollowed=cufollowedusers)
@app.route('/updateprof',methods=["POST"])
def updateprof():
	currentid=session["user_id"] 
	jsn = request.get_json(force=True)
		
	listjsn=list(jsn.values())
	print(listjsn)
	name=listjsn[0]
	bio=listjsn[1]
	avatar=listjsn[2]
	username=listjsn[3]
	user = buZz_user.query.filter_by(username=username).first()
	id=user.userId
	if id==currentid:	
		con=sqlite3.connect('user.db')
		cursor=con.cursor()
		tar_li=avatar.split('/')
		tar_nm=tar_li[len(tar_li)-1]
		tar_li=tar_nm.split(".")
		avatar=int(tar_li[0])		
		cursor.execute(f"UPDATE 'bu_zz_user' SET name='{name}',bio='{bio}',avatar='{avatar}' WHERE userId='{currentid}' ")
		con.commit()

	return redirect(f'/profile/{id}')
	
@app.route('/follow/<int:id>')
def follow(id):
	
	user = buZz_user.query.filter_by(userId=id).first()
	currentid=session["user_id"]
	current_user=buZz_user.query.filter_by(userId=currentid).first()
	#
	if user is None:
		return redirect('/home')
	
	current_user.follow(user)
	userDb.session.commit()
	flash(f"You started to follow {user.username}")
	return redirect(f'/profile/{id}')
@app.route('/unfollow/<int:id>')
def unfollow(id):
    user = buZz_user.query.filter_by(userId=id).first()
    currentid=session ["user_id"]
    current_user=buZz_user.query.filter_by(userId=currentid).first()
    if user is None:
    	return redirect('/home')    
    current_user.unfollow(user)
    flash(f"You unfollowed {user.username}") 	
    return redirect(f'/profile/{id}')	

@app.route('/search' ,methods=["POST","GET"])
@login_required   
def search():
	currentid=session ["user_id"]
	current_user=buZz_user.query.filter_by(userId=currentid).first() 
	if request.method=='POST':
		searched=request.form.get("search")
		if searched != "":
			user=buZz_user.query
			if " " in searched:
				_search=searched.replace(" ","_")				
				_user=user.filter(buZz_user.username.like('%' +_search + '%')).all()
				print(_search)
				searchedli=searched.split(" ")	
				searched=(searchedli[0]+searchedli[1])			
				users=user.filter(buZz_user.username.like('%' + searched + '%')).all()
				return render_template("search.html",matchedusers=users,user=current_user,_users=_user)									
			users=user.filter(buZz_user.username.like('%' + searched + '%')).all()
			return render_template("search.html",matchedusers=users,user=current_user) 
		else:
			return render_template("search.html",msg="Search Something!",user=current_user ) 
			
	else:
		return render_template("search.html",user=current_user)
	
@app.before_first_request
def create_tables():
    userDb.create_all()		
if __name__=='__main__':
	app.run(debug=True)