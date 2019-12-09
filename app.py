from flask import Flask, render_template, request, session, redirect, url_for
from dbconnection.connection import *
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = 'steven'# secrete key


# HOME
@app.route('/')
def home():
    return redirect(url_for('login'))

# LOGIN
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        # Query to the database
        cursor.execute('select email from users')
        emails = cursor.fetchall()
        emails = [e[0] for e in emails]  # emails list -> list[0] -> str
        # if the user exist validate
        if email in emails:
            query = 'select password from users where email = "{}"'.format(
                email)
            cursor.execute(query)
            password = cursor.fetchall()
            password = password[0][0]
            # if password is correct is logged successfully
            if pwd == password:
                session['user'] = email  # create new session
                return redirect(url_for('user', usr=email))
            else:
                return render_template('login.html', passworng=True)
        else:
            return render_template('login.html', dontexist=True)

    else:
        if 'user' in session:
            return redirect(url_for('user', usr=session['user']))

    return render_template('login.html')
# SIGN UP
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # Insert data
        email = request.form['email'].lower()  # email get from form
        password = request.form['password'].lower()  # password get from form
        cursor.execute('select email from users')
        users = cursor.fetchall()  # get all accounts
        users = [u[0] for u in users]
        # if email already registered not sign up
        if email in users:
            return render_template('signup.html', email_exist=True)
        else:
            # Query for my database
            query = 'insert into users (email, password) values(%s, %s)'
            values = (email.lower(), password.lower())

            cursor.execute(query, values)
            db.commit()  # to apply the changes
            return render_template('signup.html', succ=True)
    else:
        if 'user' in session:
            return redirect(url_for('user', usr=session['user']))
    return render_template('signup.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# DELETE ACCOUNT
@app.route('/delete')
def delete():
    if 'user' in session:
        cursor.execute(
            'delete from users where email = "{}"'.format(session['user']))
        db.commit()  # update database
        session.pop('user', None)  # Kill the session
        return redirect(url_for('login'))


# USER LOGIN
@app.route('/<usr>')
def user(usr):
    if 'user' in session:
        result = get_comments()#Content posts(text) and date(datetime)
        return render_template('index.html', usr=session['user'], posts=result)
    else:
        return redirect(url_for('login'))

# SEARCH ACCOUNT
@app.route('/<found>', methods=['POST', 'GET'])
def search(found):
    if request.method == 'POST':
        # if any user is registered
        if 'user' in session:
            email_to_search = request.form['search']  # email to search
            cursor.execute('select email from users where email="{}"'.format(email_to_search))
            result = cursor.fetchall()
            if len(result) == 0:
                return render_template('search.html', found=False)
            else:
                result = [r[0] for r in result]
                cursor.execute('select id from users where email = "{}"'.format(email_to_search))
                id = cursor.fetchall()
                id = id[0][0]# id = [(id, )], id[0][0] = id
                data = comments_search(id)
                return render_template('search.html', found=True, email=result[0], data=data)
    
    return redirect(url_for('user', usr=session['user']))

# back function implemented(button) on search template
@app.route('/back')
def back():
    return redirect(url_for('user', usr=session['user']))

# Function for handle comments
@app.route('/comment', methods=['POST', 'GET'])
def comments():
    post = request.form['publication']# Text post user
    #Get user's id that make the post
    cursor.execute('select id from users where email = "{}"'.format(session['user']))
    id = cursor.fetchall()
    id = [i[0] for i in id]# [(id,)] -> [id]
    time = str(datetime.now())#date and datetime current
    query = 'insert into post (id, post, date) values(%s, %s, %s)'
    values = (id[0], post, time)
    cursor.execute(query, values)
    db.commit()# save changes
    return redirect(url_for('user', usr=session['user']))


#Function for get the comment for id user logged and show in the html document 
@app.route('/get_commns', methods=['GET', 'POST'])
def get_comments():
    #Get user's id logged
    cursor.execute('select id from users where email = "{}"'.format(session['user']))
    id = cursor.fetchall()
    id = [i[0] for i in id]# [(id,)] -> [id]

    #get comments(post) and get datetime on posted
    cursor.execute('select id, post, date from post where id = "{}"'.format(id[0]))#get post(comment->text) and date on posted
    result = cursor.fetchall()#data -> [(post, ), (datetime, )]
    result = [list(x) for x in result]
    posts = result#content posts(text) and datetime
    db.commit()#Update database
    return posts


@app.route('/commens_friend')
def comments_search(id):
    cursor.execute('select id, post, date from post where id = "{}"'.format(id))
    result = cursor.fetchall()
    return result


#Function for button delete post
@app.route('/delete-comments', methods=['POST', 'GET'])
def delete_comments():
    post = request.form['post']#text for search in the database and know that comment for delete it.
    d = request.form['date']#date for know that comment for delete it.
    id = request.form['id']#id for to know who's make the comment
    cursor.execute('delete from post where post = "{}"  and date = "{}" and id = "{}"'.format(post, d, id))
    print(post, d, id)
    db.commit()#Update database
    return redirect(url_for('user', usr=session['user']))
if __name__ == "__main__":
    app.run(debug=True)
