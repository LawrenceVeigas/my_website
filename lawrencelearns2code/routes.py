import secrets
import os
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request
from lawrencelearns2code import app, db, bcrypt
from lawrencelearns2code.models import User, Post
from lawrencelearns2code.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewPostForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc

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
        
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html')

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

        flash('Your account has been created, please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

@app.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
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
    
    image_file = create_image_link(current_user.image_file)
    
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        return redirect(url_for('account', user_id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('account.html', image_file=image_file, form=form, user=current_user)

@app.route('/account/<user_id>/', methods=['GET','POST'])
@login_required
def account(user_id):
    form = UpdateAccountForm()
    
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).all()
    
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
    form = NewPostForm()
    post = Post.query.get_or_404(post_id)

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
        
        return render_template('new_post.html', form=form, content=post.content)

@app.route('/new_post/', methods=['GET','POST'])
@login_required
def new_post():
    form = NewPostForm()

    form.title.render_kw = {'placeholder': 'What do you wanna talk about?'}
    form.subtitle.render_kw = {'placeholder': 'Describe your post in a few words'}

    if form.validate_on_submit():
        post = Post(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data, user_id=current_user.id)
        
        db.session.add(post)
        db.session.commit()
        flash('Done!', 'success')

        return redirect(url_for('blog'))
    
    return render_template('new_post.html', form=form)

@app.route('/read_post/', methods=['GET'])
def read_post():

    pid = request.args.get('_pid', None)
    uid = request.args.get('_uid', None)

    post = Post.query.get_or_404(pid)
    user = User.query.get_or_404(uid)

    image_file = create_image_link(user.image_file)

    return render_template('read_post.html', post=post, user=user, image_file=image_file)