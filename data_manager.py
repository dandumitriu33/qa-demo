import database_common
import psycopg2
import time


@database_common.connection_handler
def get_all_questions(cursor):
    cursor.execute("""
                    SELECT * FROM questions ORDER BY submission_time DESC;
    """)
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
def post_question(cursor, title, message):
    submission_time = int(round(time.time() * 1000))
    cursor.execute(f"""
                    INSERT INTO questions (submission_time, view_number, vote_number, title, message, image)
                    VALUES ('{submission_time}', 0, 0, '{title}', '{message}', null);
""")
    cursor.execute(f"""
                    SELECT id FROM questions WHERE submission_time = '{submission_time}';
""")
    question_id = cursor.fetchall()[0]['id']
    return question_id
