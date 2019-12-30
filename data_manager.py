import database_common
import psycopg2
import datetime
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
def get_latest_five_questions(cursor):
    cursor.execute(f"""
                        SELECT * FROM questions
                        ORDER BY submission_time DESC
                        LIMIT 5; 
        """)
    questions = cursor.fetchall()
    return questions


@database_common.connection_handler
def get_question(cursor, question_id):
    cursor.execute(f"""
                    UPDATE questions
                    SET view_number = view_number + 1
                    WHERE id = {question_id};
                    SELECT * FROM questions WHERE id = {question_id}; 
    """)
    question = cursor.fetchall()
    return question


@database_common.connection_handler
def get_answers_for_question(cursor, question_id):
    cursor.execute(f"""
                    SELECT * FROM answers WHERE question_id = {question_id} ORDER BY vote_number DESC;
    """)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def post_question(cursor, title, message, image=None):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
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
def question_vote_up(cursor, question_id):
    cursor.execute(f"""
                    UPDATE questions
                    SET vote_number = vote_number + 1
                    WHERE id = {question_id};
""")


@database_common.connection_handler
def question_vote_down(cursor, question_id):
    cursor.execute(f"""
                    UPDATE questions
                    SET vote_number = vote_number - 1
                    WHERE id = {question_id};
""")


@database_common.connection_handler
def answer_vote_up(cursor, answer_id):
    cursor.execute(f"""
                    UPDATE answers
                    SET vote_number = vote_number + 1
                    WHERE id = {answer_id};
""")


@database_common.connection_handler
def answer_vote_down(cursor, answer_id):
    cursor.execute(f"""
                    UPDATE answers
                    SET vote_number = vote_number - 1
                    WHERE id = {answer_id};
""")


@database_common.connection_handler
def delete_question(cursor, question_id):
    # grabs all the answers and then loops through them to delete their comments

    cursor.execute(f"""
                        SELECT * FROM answers WHERE question_id = {question_id} ORDER BY vote_number DESC;
        """)
    answers = cursor.fetchall()
    for answer in answers:
        answer_id = answer['id']
        cursor.execute(f"""
                            DELETE FROM comments 
                            WHERE answer_id = {answer_id};
                """)

    # deletes answers, then question comments, then the question

    cursor.execute(f"""
                    DELETE FROM answers
                    WHERE question_id = {question_id};
                    DELETE FROM comments 
                    WHERE question_id = {question_id};
                    DELETE FROM questions
                    WHERE id = {question_id};
    """)


@database_common.connection_handler
def post_answer(cursor, question_id, message, image=None):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
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


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute(f"""
                    DELETE FROM comments
                    WHERE answer_id = {answer_id};
                    DELETE FROM answers
                    WHERE id = {answer_id};
    """)


@database_common.connection_handler
def get_questions_phrase(cursor, search_phrase):
    cursor.execute(f"""
                        SELECT * FROM questions WHERE title ILIKE '%{search_phrase}%' OR message ILIKE '%{search_phrase}%'; 
        """)
    questions = cursor.fetchall()
    return questions


@database_common.connection_handler
def get_answers_phrase(cursor, search_phrase):
    cursor.execute(f"""
                        SELECT * FROM answers WHERE message ILIKE '%{search_phrase}%'; 
        """)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def post_question_comment(cursor, question_id, message):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
    cursor.execute(f"""
                    INSERT INTO comments (submission_time, question_id, message)
                    VALUES ('{submission_time}', {question_id}, '{message}');
    """)


@database_common.connection_handler
def post_answer_comment(cursor, answer_id, message):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
    cursor.execute(f"""
                    INSERT INTO comments (submission_time, answer_id, message)
                    VALUES ('{submission_time}', {answer_id}, '{message}');
    """)


@database_common.connection_handler
def get_comments_for_question(cursor, question_id):
    comments = []

    # getting comments from the question side

    cursor.execute(f"""
                        SELECT * FROM comments WHERE question_id = {question_id} ORDER BY submission_time DESC;
        """)
    comments.append(cursor.fetchall())

    # getting comments from the answers of the above question

    cursor.execute(f"""
                    SELECT * FROM answers WHERE question_id = {question_id};
    """)
    answers = cursor.fetchall()
    for answer in answers:
        answer_id = answer['id']
        cursor.execute(f"""
                            SELECT * FROM comments WHERE answer_id = {answer_id} ORDER BY submission_time DESC;
            """)
        comments.append(cursor.fetchall())
    return comments


@database_common.connection_handler
def get_comment(cursor, comment_id):
    cursor.execute(f"""
                    SELECT * FROM comments WHERE id = {comment_id}; 
    """)
    answer = cursor.fetchall()
    return answer


@database_common.connection_handler
def update_comment(cursor, comment_id, message):
    cursor.execute(f"""
                    UPDATE comments
                    SET message = '{message}'
                    WHERE id = {comment_id};
    """)
