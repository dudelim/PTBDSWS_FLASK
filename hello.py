import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserForm()
    form.populate_choices()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data, role_id=form.role.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        session['role'] = form.role.data
        return redirect(url_for('index'))
    users = User.query.all()
    roles = Role.query.all()
    users_count = User.query.count()
    roles_count = Role.query.count()
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False), users=users, users_count=users_count, roles=roles, roles_count=roles_count)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

class UserForm(FlaskForm):
    name = StringField('What is your name?:', validators=[DataRequired()])
    role = SelectField('Role:', choices=[])
    submit = SubmitField('Submit')

    def populate_choices(self):
        from hello import Role
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

if __name__ == '__main__':
    app.run(debug=True)