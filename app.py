from flask import Flask
from flask import request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_login import current_user
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:A20190499n@localhost/flasksocial'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SKHqSOPP'
db = SQLAlchemy(app)


@app.route('/')
@login_required
def home():
    userId = User.query.filter_by(id=current_user.id).first()
    user = UserDetails.query.filter_by(user_id=userId.id).first()
    return render_template('welcome.html', user=user)

@app.route('/user_list')
@login_required
def get_user_list():
    users = User.query.all()
    userD = UserDetails.query.all()
    return render_template('user_list.html', users=users, userD=userD)

@app.route('/editprofile')
@login_required
def edit_profile():
    now_user = User.query.filter_by(email=current_user.email).first()
    return render_template('user_detail.html', now_user=now_user)

@app.route('/add_user_details', methods=['POST'])
def add_user_details():
    user_details = UserDetails(request.form['pid'], request.form['username'], request.form['profile_pic'], request.form['location'])
    db.session.add(user_details)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/feed')
def get_post():
    singlePost = Post.query.all()
    return render_template('post_feed.html', singlePost=singlePost)


@app.route('/profile/<id>')
def user_profile(id):
    oneUser = UserDetails.query.filter_by(id=id).first()
    sUser = User.query.filter_by(id=oneUser.user_id).first()
    user_posts = Post.query.filter_by(posted_by=sUser.email)
    return render_template('user_profile.html', oneUser = oneUser, sUser=sUser, user_posts=user_posts)


@app.route('/posting')
@login_required
def posting():
    now_user = User.query.filter_by(email=current_user.email).first()
    dt = datetime.now()
    userId = User.query.filter_by(id=current_user.id).first()
    user = UserDetails.query.filter_by(user_id=userId.id).first()
    #oneUser = UserDetails.query.filter_by(id=user.id).first()
    return render_template('add_post.html', now_user=now_user, timestamp=dt, oneUser=user)


@app.route('/add_post', methods =['POST'])
def add_post():
    post = Post(request.form['pcontent'], request.form['pemail'], request.form['datetime'])
    userId = User.query.filter_by(id=current_user.id).first()
    user = UserDetails.query.filter_by(user_id=userId.id).first()
    id = user.id
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('user_profile', id=id))

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(100))
    profile_pic = db.Column(db.String(300))
    location = db.Column(db.String(100))

    def __init__(self, user_id, username, profile_pic, location):
        self.user_id = user_id
        self.username = username
        self.profile_pic = profile_pic
        self.location = location

    def __repr__(self):
        return '<UserDetails %r>' % self.username

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(timezone=True))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

class Post(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    post_content = db.Column(db.String(200))
    posted_by = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime(timezone=True))


    def __init__(self, post_content, posted_by, timestamp):
        self.post_content = post_content
        self.posted_by = posted_by
        self.timestamp = timestamp

        def __respr__(self):
            return '<Post %r>' % self.post_content

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
# @app.before_first_request
# def create_user():
#     db.create_all()
#     user_datastore.create_user(email='def@xyz.com', password='test456')
#     db.session.commit()



if __name__ == "__main__":
    app.run(debug = True)