from flask import Flask, render_template
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


@app.route('/add-question')
def new_question():
    return 'new q'


if __name__ == '__main__':
    app.run(debug=True)
