import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, make_response
from lawrencelearns2code import app, db, bcrypt, mail
from lawrencelearns2code.models import User, Post
from lawrencelearns2code.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewPostForm
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from sqlalchemy import desc
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# functions
def create_image_link(fn, blog=0):
    
    if blog==1:
        return url_for('static',filename='images/blog-pictures/' + fn)
    elif blog==0:
        return url_for('static',filename='images/profile-pictures/' + fn)

def save_picture(form_picture, blog=0):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    if blog==0:
        picture_path = os.path.join(app.root_path, 'static/images/profile-pictures', picture_fn)
    elif blog==1:
        picture_path = os.path.join(app.root_path, 'static/images/blog-pictures', picture_fn)
        
    output_size = (150,150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def send_activation_link(user):
    s = Serializer(app.config['SECRET_KEY'], 1800)
    token = s.dumps({'user_id': user.id}).decode('utf-8')
    link = request.host_url + url_for('activate_account', token=token)
    return link

def verify_activation_link(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except Exception as e:
        print(str(e))
        return None
    return user_id

@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/contact/')
def contact():
    return render_template('contact.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/register/', methods=['GET','POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        user = User.query.filter_by(email=form.email.data).first()
        link = send_activation_link(user)

        with app.app_context():
            msg = Message("Hi, you've registered as a user on LawrenceLearns2Code.com!")
            msg.recipients = [form.email.data]
            msg.body = f"Dear {form.username.data},\nI are extremely happy to have you onboard with us. Hope you enjoy this website.\nDo use the platform to create and share posts with fellow users. :)\nHere is your activation link:\n{link}\nDo note: The link is valid only for 30 minutes\n\nRegards,\nLawrence"
            
            mail.send(msg)

        flash('Please check your email and click on the link to activate account.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

@app.route('/activate_account/<token>')
def activate_account(token):
    user_id = verify_activation_link(token)

    if user_id is not None:
        user = User.query.get(user_id)
        user.activated = True

        db.session.add(user)
        db.session.commit()

        flash('Account activated! Please go ahead and login.', 'success')
        return redirect(url_for('login'))
    else:
        flash('The link has expired or is invalid', 'info')
        return redirect(url_for('login'))

@app.route('/login/', methods=['GET','POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('account', user_id=current_user.id))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.activated:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Account has not been activated, we\'ve resent the activation link to your email account. Kindly activate your account', 'info')
                
                user = User.query.filter_by(email=form.email.data).first()
                link = send_activation_link(user)

                with app.app_context():
                    msg = Message("Hi, you've registered as a user on LawrenceLearns2Code.com!")
                    msg.recipients = [form.email.data]
                    msg.body = f"Dear {user.username},\nI are extremely happy to have you onboard with us. Hope you enjoy this website.\nDo use the platform to create and share posts with fellow users. :)\nHere is your activation link:\n{link}\nDo note: The link is valid only for 30 minutes\n\nRegards,\nLawrence"
                    
                    mail.send(msg)
                
                return redirect(url_for('login'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/update_account/', methods=['GET','POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    form.picture.render_kw = {'hidden':'true'}
    image_file = create_image_link(current_user.image_file)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        return redirect(url_for('account', user_id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('account.html', image_file=image_file, form=form, user=current_user)

@app.route('/account/<user_id>/', methods=['GET','POST'])
def account(user_id):
    form = UpdateAccountForm()
    
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(desc('date_posted')).all()
    
    image_file = create_image_link(user.image_file)
    form.username.render_kw = {'readonly':'true'}
    form.email.render_kw = {'readonly':'true'}
    form.picture.render_kw = {'hidden':'true'}
    form.submit.render_kw = {'hidden':'true'}

    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email

    return render_template('account.html', image_file=image_file, form=form, user=user, posts=posts)

@app.route('/blog/', methods=['GET'])
def blog():
    posts = Post.query.order_by(desc('date_posted')).all()

    return render_template('blog.html', posts=posts)

@app.route('/edit_post/<post_id>/', methods=['GET','POST'])
@login_required 
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user.id != post.author.id:
        return "You cannot edit this post"

    form = NewPostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.content = form.content.data

        db.session.commit()
        flash('Post updated!','success')

        return redirect(url_for('blog'))

    elif request.method == 'GET':
        form.title.data = post.title
        form.subtitle.data = post.subtitle
        
        return render_template('new_post.html', form=form, post=post)

@app.route('/new_post/', methods=['GET','POST'])
@login_required
def new_post():
    form = NewPostForm()

    form.title.render_kw = {'placeholder': 'What do you wanna talk about?'}
    form.subtitle.render_kw = {'placeholder': 'Describe your post in a few words'}

    if form.validate_on_submit():
        post = Post(title=form.title.data, 
                    subtitle=form.subtitle.data, 
                    content=form.content.data, 
                    user_id=current_user.id)
        
        db.session.add(post)
        db.session.commit()
        flash('Done!', 'success')

        return redirect(url_for('blog'))
    
    return render_template('new_post.html', form=form)

@app.route('/read_post/', methods=['GET'])
def read_post():

    pid = request.args.get('pid', None)
    uid = request.args.get('uid', None)
    title = request.args.get('title')

    post = Post.query.get_or_404(pid)
    user = User.query.get_or_404(uid)

    image_file = create_image_link(user.image_file)

    return render_template('read_post.html', post=post, user=user, image_file=image_file)

@app.route('/delete_post/<post_id>/')
@login_required 
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user.id != post.author.id:
        return "You are not authorized to do this"

    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted', 'success')

    return redirect(url_for('blog'))

@app.route('/update-profile-pic', methods=['POST'])
def update_profile_pic():

    if request.method == 'POST':
        file = request.files['avatar']
        filename = file.filename
    
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/images/profile-pictures', picture_fn)
            
        output_size = (500,500)
        i = Image.open(file)
        i.thumbnail(output_size)
        i = i.convert("RGB")
        i.save(picture_path)

        current_user.image_file = picture_fn

        db.session.commit()
        
        return make_response('Sucess', 200)