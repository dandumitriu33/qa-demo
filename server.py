from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
    question = data_manager.get_question(question_id)
    answers = data_manager.get_answers_for_question(question_id)
    return render_template('question.html',
                           question_id=question_id,
                           question=question,
                           answers=answers)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'GET':
        question = data_manager.get_question(question_id)
        return render_template('edit-question.html',
                               question_id=question_id,
                               question=question)
    elif request.method == 'POST':
        edited_question_title = request.form['title']
        edited_question_message = request.form['message']
        data_manager.update_question(question_id, edited_question_title, edited_question_message)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/add-question', methods=['GET', 'POST'])
def new_question():
    if request.method == 'GET':
        return render_template('new-question.html')
    elif request.method == 'POST':
        new_question_title = request.form['title']
        new_question_message = request.form['message']
        question_id = data_manager.post_question(new_question_title, new_question_message)
        question = data_manager.get_question(question_id)
        answers = data_manager.get_answers_for_question(question_id)
        return render_template('question.html',
                               question_id=question_id,
                               question=question,
                               answers=answers)


if __name__ == '__main__':
    app.run(debug=True)
