from flask import Flask, render_template, request, redirect, url_for
from flask import session
import data_manager

app = Flask(__name__)


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/4545bec'


@app.route('/')
def index():
    questions = data_manager.get_latest_five_questions()
    return render_template('index.html',
                           questions=questions)


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/list')
def list_all_questions():
    order_by = 'submission_time'
    order_direction = 'DESC'
    if request.args.get(key='order_by'):
        order_by = request.args.get(key='order_by')
    if request.args.get(key='order_direction'):
        order_direction = request.args.get(key='order_direction')
    questions = data_manager.get_all_questions(order_by, order_direction)
    return render_template('list.html',
                           questions=questions)


@app.route('/question/<question_id>')
def display_question(question_id):
    question_id = int(question_id)
    question = data_manager.get_question(question_id)
    answers = data_manager.get_answers_for_question(question_id)
    comments = data_manager.get_comments_for_question(question_id)
    tags = data_manager.get_question_tags(question_id)
    return render_template('question.html',
                           question_id=question_id,
                           question=question,
                           answers=answers,
                           comments=comments,
                           tags=tags)


@app.route('/question/<question_id>/vote-up')
def question_vote_up(question_id):
    points_user_id = data_manager.get_user_id_by_question_id(question_id)
    data_manager.question_vote_up(question_id, points_user_id)
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/question/<question_id>/vote-down')
def question_vote_down(question_id):
    points_user_id = data_manager.get_user_id_by_question_id(question_id)
    data_manager.question_vote_down(question_id, points_user_id)
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'GET':
        question = data_manager.get_question(question_id)
        return render_template('edit-question.html',
                               question_id=question_id,
                               question=question)
    elif request.method == 'POST':
        edited_question_title = request.form['title'].replace("'", "''")
        edited_question_message = request.form['message'].replace("'", "''")
        data_manager.update_question(question_id, edited_question_title, edited_question_message)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/add-question', methods=['GET', 'POST'])
def new_question():
    if request.method == 'GET':
        return render_template('new-question.html')
    elif request.method == 'POST':
        new_question_title = request.form['title'].replace("'", "''")
        new_question_message = request.form['message'].replace("'", "''")
        user_id = data_manager.get_user_id_by_username(session['username'])
        question_id = data_manager.post_question(new_question_title, new_question_message, user_id)
        question = data_manager.get_question(question_id)
        answers = data_manager.get_answers_for_question(question_id)
        return render_template('question.html',
                               question_id=question_id,
                               question=question,
                               answers=answers)


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect(url_for('list_all_questions'))


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def question_new_answer(question_id):
    if request.method == 'GET':
        return render_template('new-answer.html',
                               question_id=question_id)
    elif request.method == 'POST':
        new_answer_message = request.form['message'].replace("'", "''")
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.post_answer(question_id, new_answer_message, user_id)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    if request.method == 'GET':
        answer = data_manager.get_answer(answer_id)
        return render_template('edit-answer.html',
                               answer_id=answer_id,
                               answer=answer)
    elif request.method == 'POST':
        answer = data_manager.get_answer(answer_id)
        question_id = answer['question_id']
        edited_answer_message = request.form['message'].replace("'", "''")
        data_manager.update_answer(answer_id, edited_answer_message)
        return redirect(url_for('display_question',
                                question_id=question_id))


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    answer = data_manager.get_answer(answer_id)
    question_id = answer['question_id']
    data_manager.delete_answer(answer_id)
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/answer/<answer_id>/vote-up')
def answer_vote_up(answer_id):
    points_user_id = data_manager.get_user_id_by_answer_id(answer_id)
    data_manager.answer_vote_up(answer_id, points_user_id)
    answer = data_manager.get_answer(answer_id)
    question_id = answer['question_id']
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/answer/<answer_id>/vote-down')
def answer_vote_down(answer_id):
    points_user_id = data_manager.get_user_id_by_answer_id(answer_id)
    data_manager.answer_vote_down(answer_id, points_user_id)
    answer = data_manager.get_answer(answer_id)
    question_id = answer['question_id']
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/search')
def search():
    search_phrase = request.args.get('search-phrase')
    questions = data_manager.get_questions_phrase(search_phrase)
    answers = data_manager.get_answers_phrase(search_phrase)
    return render_template('search.html',
                           search_phrase=search_phrase,
                           questions=questions,
                           answers=answers)


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def question_new_comment(question_id):
    if request.method == 'GET':
        return render_template('new-comment.html',
                               question_id=question_id)
    elif request.method == 'POST':
        message = request.form['message'].replace("'", "''")
        question_id = question_id
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.post_question_comment(question_id=question_id,
                                           message=message,
                                           user_id=user_id)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def answer_new_comment(answer_id):
    if request.method == 'GET':
        return render_template('new-comment.html',
                               answer_id=answer_id)
    elif request.method == 'POST':
        message = request.form['message'].replace("'", "''")
        answer_id = answer_id
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.post_answer_comment(answer_id=answer_id,
                                         message=message,
                                         user_id=user_id)
        answer = data_manager.get_answer(answer_id)
        question_id = answer['question_id']
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == 'GET':
        comment = data_manager.get_comment(comment_id)
        return render_template('edit-comment.html',
                               comment_id=comment_id,
                               comment=comment)
    elif request.method == 'POST':
        comment = data_manager.get_comment(comment_id)
        if comment[0]['question_id']:
            question_id = comment[0]['question_id']
            edited_comment_message = request.form['message'].replace("'", "''")
            data_manager.update_comment(comment_id, edited_comment_message)
            return redirect(url_for('display_question',
                                    question_id=question_id))
        elif comment[0]['answer_id']:
            answer_id = comment[0]['answer_id']
            edited_comment_message = request.form['message'].replace("'", "''")
            data_manager.update_comment(comment_id, edited_comment_message)
            answer = data_manager.get_answer(answer_id)
            question_id = answer['question_id']
            return redirect(url_for('display_question',
                                    question_id=question_id))


@app.route('/comment/<comment_id>/delete')
def delete_comment(comment_id):
    comment = data_manager.get_comment(comment_id)
    if comment[0]['question_id']:
        question_id = comment[0]['question_id']
        data_manager.delete_comment(comment_id)
        return redirect(url_for('display_question',
                                question_id=question_id))
    elif comment[0]['answer_id']:
        answer_id = comment[0]['answer_id']
        answer = data_manager.get_answer(answer_id)
        question_id = answer['question_id']
        data_manager.delete_comment(comment_id)
        return redirect(url_for('display_question',
                                question_id=question_id))


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def question_new_tag(question_id):
    if request.method == 'POST':
        new_tag_name = request.form['tag-name']
        data_manager.add_new_tag_to_db(new_tag_name)
        tag_id = data_manager.get_tag_id_by_name(new_tag_name)
        data_manager.add_new_tag_to_question(tag_id, question_id)
        return redirect(url_for('display_question',
                                question_id=question_id))
    all_tags = data_manager.get_all_tags()
    question_tags = data_manager.get_question_tags(question_id)
    return render_template('new-tag.html',
                           question_id=question_id,
                           all_tags=all_tags,
                           question_tags=question_tags)


@app.route('/question/<question_id>/add-tag/<tag_id>')
def add_tag_to_question(tag_id, question_id):
    data_manager.add_new_tag_to_question(tag_id, question_id)
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_tag_from_question(tag_id, question_id):
    data_manager.delete_tag_from_question(tag_id=tag_id, question_id=question_id)
    return redirect(url_for('display_question',
                            question_id=question_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = data_manager.hash_password(request.form['password'])
        data_manager.register_user(name, username, password)
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db_password = data_manager.get_db_password_for_user(request.form['username'])
        if data_manager.verify_password(request.form['password'], db_password):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return 'Username or password invalid.'
    return render_template('login.html')


@app.route('/logout')
def logout():
    # removes the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/users')
def display_users():
    users = data_manager.get_all_users()
    return render_template('users.html',
                           users=users)


@app.route('/user/<user_id>')
def display_user_activity(user_id):
    target_user_username = data_manager.get_username_by_user_id(user_id)
    target_user_questions = data_manager.get_all_user_questions(user_id)
    target_user_answers = data_manager.get_all_user_answers(user_id)
    target_user_comments = data_manager.get_all_user_comments(user_id)
    return render_template('user.html',
                           target_user_username=target_user_username,
                           target_user_questions=target_user_questions,
                           target_user_answers=target_user_answers,
                           target_user_comments=target_user_comments)


@app.route('/answer/<answer_id>/accept')
def accept_answer(answer_id):
    answer = data_manager.get_answer(answer_id)
    question_id = answer['question_id']
    points_user_id = data_manager.get_user_id_by_answer_id(answer_id)
    if answer['accepted']:
        data_manager.update_answer_not_accepted(answer_id, points_user_id)
        return redirect(url_for('display_question', question_id=question_id))
    elif not answer['accepted']:
        data_manager.update_answer_accepted(answer_id, points_user_id)
        return redirect(url_for('display_question', question_id=question_id))


if __name__ == '__main__':
    app.run(debug=True)
