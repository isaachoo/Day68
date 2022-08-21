from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

# app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = b'_5#y2L"F4Q8zmmmxec]/'
login_manager = LoginManager()
login_manager.init_app(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            email=request.form.get("email"),
            password=generate_password_hash(request.form.get("password"),'pbkdf2:sha256',16),
            name=request.form.get("name")
        )
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash("already exist")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        get_row = db.session.query(User).filter(User.email == request.form.get("email")).first()
        if get_row:
            if check_password_hash(get_row.password, request.form.get('password')):
                print("bingo")
                login_user(get_row)
                if get_row.is_authenticated:
                    return redirect(url_for("secrets"))
            else:
                flash('Password wrong')
        else:
            flash('login wrong')
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', "files/cheat_sheet.pdf")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


if __name__ == "__main__":
    app.run(debug=True)
