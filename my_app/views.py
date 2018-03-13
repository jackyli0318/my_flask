from my_app import app
from functools import wraps
from db import engine
from flask import render_template, session, redirect, request, jsonify
from .models import add_user, check_user, login_check, Post


# check whether the user has logged in or not      By Zhi
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if g.user is None:
        if 'username' not in session:
            print ('No user now.')
            # return redirect(url_for('/login', next=request.url))
            return render_template('login.html')
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html', session=session)


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if 'username' in session:
        return redirect('/list')
    if request.method == "GET":
        info = "Tips: Username and password can not accept special characters."
        return render_template('sign_up.html', info=info)
    else:
        error = None
        username = request.form['username']
        password = request.form['password']
        con_psw = request.form['confirm_psw']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        flag = username and password and email and first_name and last_name
        psw_equal = password == con_psw

        if not username.isalnum():
            error = "Username should not contain special characters."
            return render_template('sign_up.html', error=error)

        if not password.isalnum():
            error = "Password should not contain special characters."
            return render_template('sign_up.html', error=error)

        if flag:
            if psw_equal:
                if not check_user(username):
                    # user = User(username, password, email, first_name, last_name)
                    add_user(username, password, email, first_name, last_name)
                else:
                    error = "Username existed."
                    return render_template('sign_up.html', error=error)
            else:
                error = "Please input the same password."
                return render_template('sign_up.html', error=error)
        else:
            error = 'Please fill all the field.'
            return render_template('sign_up.html', error=error)
        info = "You have created an account already, please login now!"
        return render_template('login.html', info=info)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return redirect('/list')
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username.isalnum():
            error = "Username should not contain special characters."
            return render_template('login.html', error=error)

        if not password.isalnum():
            error = "Password should not contain special characters."
            return render_template('login.html', error=error)

        if login_check(username, password):
            session['username'] = username
        else:
            error = 'Please input the correct username and password!'
            return render_template('login.html', error=error)
        print("Login successfully.")
        return redirect('/list')

    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == "GET":
        return redirect('/')
    status = ""
    msg = None
    if request.method == "POST":
        if session.get('username', None):
            del session['username']
            status = "ok"
    if msg:
        return jsonify({"status": status, "msg": msg})
    return jsonify({"status": status})


#posts part
@app.route('/list', methods=['GET', 'POST'])
@login_required
def show_list():
    page = int(request.args.get('page_no', 0))
    keyword = request.args.get('keyword', "")

    # result from mongo for pagination
    posts, page_sum = Post.find_pagination(page=page, keyword=keyword)
    # posts, page_sum = es.search(page=page, keyword=keyword)

    has_prev = False
    has_next = False
    prev_page = 1
    next_page = page_sum

    page_list = list()
    end = page + 5
    start = page - 5
    if end >= page_sum:
        end = page_sum
    if start < 1:
        start = 1

    for i in range(start, end+1):
        page_list.append(i)

    if page < 1:
        page = 1

    if page > page_sum:
        page = page_sum

    if page > 1:
        has_prev = True
        prev_page = page-1

    if page < page_sum:
        has_next = True
        next_page = page+1

    pagination_data = {
        "has_prev": has_prev,
        "has_next": has_next,
        "page_list": page_list,
        "last_page": page_sum,
        "cur_page": page,
        "prev_page": prev_page,
        "next_page": next_page,
        "keyword": keyword,
    }
    return render_template('list.html', session=session, posts=posts, pagination_data=pagination_data)


@app.route('/post', methods=['GET','POST'])
@login_required
def show_detail():
    id = request.args.get('id', None)
    post = Post.find_one(id)
    if post:
        return render_template('post_detail.html', post=post)
    return redirect('/')


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    # mongo
    for i in range(1,100):
        post = Post("Energy News!"+str(i), "First news!!!"+str(i), "Goo"+str(i))
        post.insert_post()
        print("Insert one post in mondoDB.")
    return redirect('/list')


@app.route('/sync_posts', methods=['GET','POST'])
@login_required
def sync_posts():
    post_list = Post.get_all()
    # es.postlst_es(postlst=post_list)

    return redirect('/list')

# clear elasticsearch

# for i in range(1, 10):
#     lst = es.search()
#     lst = lst.get('hits').get('hits')
#     a = list()
#     for item in lst:
#         a.append(item.get('_id'))
#     for item in a:
#         es.delete(index='po', doc_type='post', id=item)
#
