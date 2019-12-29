import database_common
import psycopg2
import time


@database_common.connection_handler
def get_all_questions(cursor, order_by='submission_time', order_direction='DESC'):
    order_dict = {
                'submission_time': "SELECT * FROM questions ORDER BY submission_time ",
                'title': "SELECT * FROM questions ORDER BY title ",
                'message': "SELECT * FROM questions ORDER BY message ",
                'view_number': "SELECT * FROM questions ORDER BY view_number ",
                'vote_number': "SELECT * FROM questions ORDER BY vote_number "
    }
    cursor.execute(order_dict[order_by] + order_direction + ";")
    questions = cursor.fetchall()
    return questions



@database_common.connection_handler
def get_question(cursor, question_id):
    cursor.execute(f"""
                    SELECT * FROM questions WHERE id = {question_id}; 
    """)
    question = cursor.fetchall()
    return question


@database_common.connection_handler
def get_answers_for_question(cursor, question_id):
    cursor.execute(f"""
                    SELECT * FROM answers WHERE question_id = {question_id};
    """)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def post_question(cursor, title, message, image=None):
    submission_time = int(round(time.time() * 1000))
    cursor.execute(f"""
                    INSERT INTO questions (submission_time, view_number, vote_number, title, message, image)
                    VALUES ('{submission_time}', 0, 0, '{title}', '{message}', '{image}');
""")
    cursor.execute(f"""
                    SELECT id FROM questions WHERE submission_time = '{submission_time}';
""")
    question_id = cursor.fetchall()[0]['id']
    return question_id


@database_common.connection_handler
def update_question(cursor, question_id, title, message):
    cursor.execute(f"""
                    UPDATE questions
                    SET title = '{title}', message = '{message}'
                    WHERE id = {question_id};
    """)


@database_common.connection_handler
def delete_question(cursor, question_id):
    cursor.execute(f"""
                    DELETE FROM questions
                    WHERE id = {question_id};
    """)
    cursor.execute(f"""
                    DELETE FROM answers
                    WHERE question_id = {question_id};
    """)


@database_common.connection_handler
def post_answer(cursor, question_id, message, image=None):
    submission_time = int(round(time.time() * 1000))
    cursor.execute(f"""
                    INSERT INTO answers (submission_time, vote_number, question_id, message, image)
                    VALUES ('{submission_time}', 0, {question_id}, '{message}', '{image}')
    """)


@database_common.connection_handler
def get_answer(cursor, answer_id):
    cursor.execute(f"""
                    SELECT * FROM answers WHERE id = {answer_id}; 
    """)
    answer = cursor.fetchall()
    return answer


@database_common.connection_handler
def update_answer(cursor, answer_id, message):
    cursor.execute(f"""
                    UPDATE answers
                    SET message = '{message}'
                    WHERE id = {answer_id};
    """)
