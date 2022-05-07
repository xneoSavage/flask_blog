from app import app, db
from flask import render_template, flash, redirect, url_for, request
from forms import LoginForm, RegistrationForm, CreatePostForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():  # put application's code here
	posts = Post.query.all()
	return render_template('index.html', title='Title', posts=posts)

@app.route('/main')
def main():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	else:
		return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		user.check_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congrats! You are registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main'))


@login_required
@app.route('/post', methods=['GET', 'POST'])
def create_post():
	u = current_user
	form = CreatePostForm()
	if current_user.is_authenticated:
		if form.validate_on_submit():
			post = Post(header=form.header.data, body=form.body.data, user_id=u.get_id())
			db.session.add(post)
			db.session.commit()
			flash('You are created post!')
			return redirect(url_for('index'))
		return render_template('create_post.html', form=form, title='Create Post')
	return redirect(url_for('login'))

@login_required
@app.route('/delete_post', methods=['GET', 'POST'])
def delete_post():
	post_id = Post.query.all()
	post = Post.query.filter_by(id=post_id)


@login_required
@app.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'},
	]
	return render_template('user.html', user=user, posts=posts)


@app.before_request
def before_request():
	"""
	Return last_seen time
	:return:
	"""
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data 	# Тут вилізає помилка, якщо такий юзер вже є, отримуємо 500
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user', username=current_user.username))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)