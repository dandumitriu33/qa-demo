import database_common
import psycopg2


@database_common.connection_handler
def get_all_questions(cursor):
    cursor.execute("""
                    SELECT * FROM questions ORDER BY submission_time ASC;
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
