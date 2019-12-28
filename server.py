from flask import Flask, render_template, request
import data_manager

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list')
def list_all_questions():
    questions = data_manager.get_all_questions()
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
