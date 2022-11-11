from werkzeug.security import generate_password_hash,check_password_hash
import requests
from flask_sqlalchemy import SQLAlchemy
import flask_sqlalchemy
from flask import Flask,render_template,request

db=SQLAlchemy()

app = Flask(__name__)
userName = False
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///final.db'
db.init_app(app)

class Film(db.Model):
    userName=db.Column(db.String,primary_key=True)
    imDBId=db.Column(db.String,primary_key=True)
    title=db.Column(db.String,nullable=False)
    rate=db.Column(db.Float)

class User(db.Model):
    userName=db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    global userName
    if(userName==False):
        return render_template('index.html')
    return render_template('Search.html')

@app.route('/logout')
def Logout():
    global userName
    userName=False
    return render_template('Login.html')

@app.route('/register', methods = ['GET', 'POST'])
def Registration():
    if(request.method=="POST"):
        check = User.query.filter_by(email=request.values['email']).first()
        if check is None:
            if request.form["password"] == request.form["confirmPassword"] and "@" in request.values['email']:
                hash=generate_password_hash(request.form["password"])
                userName =request.form['userName']
                email = request.form['email']
                status="player"
                newUser = User(userName=userName, password=hash, email=email, status=status)
                db.session.add(newUser)
                db.session.commit()
                return (Login())
            else:
                return ("Your confirm password or email is incorrect")
        else:
            return ("This user is already exist")
    return render_template("Registration.html",title=Registration)

@app.route('/login',methods = ['GET', 'POST'])
def Login():
    global userName
    if request.method=='POST':
        check = User.query.filter_by(userName=(request.form['userName'])).first()
        if check_password_hash(check.password, request.form['password']):
            userName=request.form['userName']
            return render_template('Search.html',dic={},n=0,userName=userName,status=check.status)
        else:
            return ("Error")
    return render_template('Login.html')

@app.route('/search',methods = ['GET', 'POST'])
def Search():
    global userName
    check = User.query.filter_by(userName=userName).first()
    if request.method=='POST':
        user_input = request.form['search']
        SearchAPI = 'https://imdb-api.com/en/API/Search/k_198rwh5t/' + user_input
        r = requests.get(SearchAPI)
        searchFilms = r.json()['results']
        imDBId = [i['id'] for i in searchFilms]
        title = [i['title'] for i in searchFilms]
        image = [i['image'] for i in searchFilms]
        n = len(imDBId)
        dic = {'id': imDBId, 'title': title, 'image': image}
        return render_template('Search.html', dic=dic, n=n, userName=userName,status=check.status)
    return render_template('Search.html',dic={},n=0,userName=userName,status=check.status)

@app.route('/Top',methods = ['GET', 'POST'])
def Top():
    TopAPI='https://imdb-api.com/en/API/Top250Movies/k_198rwh5t'
    r = requests.get(TopAPI)
    TopFilms = r.json()['items']
    rank=[i['rank'] for i in TopFilms]
    title = [i['title'] for i in TopFilms]
    image=[i['image'] for i in TopFilms]
    imDbRating=[i['imDbRating'] for i in TopFilms]
    n = len(rank)
    dic = {'rank': rank, 'title': title, 'image': image,'rating':imDbRating}
    return render_template('Top.html',n=n,dic=dic)

@app.route('/mylist',methods=['GET', 'POST'])
def MyList():
    return render_template('MyList.html',film=Film.query.all())

@app.route('/add-list',methods=['GET', 'POST'])
def AddList():
    global userName
    id=request.form['id']
    RatingsAPI='https://imdb-api.com/en/API/Ratings/k_198rwh5t/'+id
    r = requests.get(RatingsAPI)
    title = r.json()['title']
    myfilm=Film(userName=userName,imDBId=id,title=title)
    db.session.add(myfilm)
    db.session.commit()
    return render_template('MyList.html', film=Film.query.all())

@app.route('/delete-list',methods=['GET', 'POST'])
def DeleteList():
    global userName
    imdbid=request.form['imdbid']
    select= Film.query.filter_by(userName=userName,imDBId=imdbid).first()
    if select is None:
        return('Error')
    db.session.delete(select)
    db.session.commit()
    return render_template('MyList.html', film=Film.query.all())

@app.route('/update-list',methods=['GET', 'POST'])
def UpdateList():
    global userName
    imdbid = request.form['imdbid1']
    select = Film.query.filter_by(userName=userName, imDBId=imdbid).first()
    if select is None:
        return ('Error')
    select.title=request.form['title']
    db.session.commit()
    return render_template('MyList.html', film=Film.query.all())

if __name__ == '__main__':
    app.run(debug=True)