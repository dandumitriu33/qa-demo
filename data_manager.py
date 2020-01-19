import database_common
import psycopg2
import datetime
import time
import bcrypt


@database_common.connection_handler
def get_all_questions(cursor, order_by='submission_time', order_direction='DESC'):
    order_dict = {
                'submission_time': "SELECT questions.*, users.username FROM questions LEFT JOIN users ON questions.user_id = users.id ORDER BY submission_time ",
                'title': "SELECT questions.*, users.username FROM questions LEFT JOIN users ON questions.user_id = users.id ORDER BY title ",
                'message': "SELECT questions.*, users.username FROM questions LEFT JOIN users ON questions.user_id = users.id ORDER BY message ",
                'view_number': "SELECT questions.*, users.username FROM questions LEFT JOIN users ON questions.user_id = users.id ORDER BY view_number ",
                'vote_number': "SELECT questions.*, users.username FROM questions LEFT JOIN users ON questions.user_id = users.id ORDER BY vote_number "
    }
    cursor.execute(order_dict[order_by] + order_direction + ";")
    questions = cursor.fetchall()
    return questions


@database_common.connection_handler
def get_latest_five_questions(cursor):
    cursor.execute(f"""
                        SELECT questions.*, users.username FROM questions LEFT JOIN users ON questions.user_id = users.id
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
                    SELECT questions.*, users.username FROM questions 
                    LEFT JOIN users on questions.user_id = users.id
                    WHERE questions.id = {question_id}; 
    """)
    question = cursor.fetchall()
    return question


@database_common.connection_handler
def get_answers_for_question(cursor, question_id):
    cursor.execute(f"""
                    SELECT answers.*, users.username FROM answers 
                    LEFT JOIN users ON answers.user_id = users.id
                    WHERE question_id = {question_id} ORDER BY vote_number DESC;
    """)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def post_question(cursor, title, message, user_id):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
    cursor.execute(f"""
                    INSERT INTO questions (submission_time, view_number, vote_number, title, message, user_id)
                    VALUES ('{submission_time}', 0, 0, '{title}', '{message}', {user_id});
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
def get_user_id_by_question_id(cursor, question_id):
    cursor.execute(f"""
                    SELECT user_id FROM questions
                    WHERE id={question_id};
    """)
    result = cursor.fetchone()
    user_id = result['user_id']
    return user_id


@database_common.connection_handler
def question_vote_up(cursor, question_id, points_user_id):
    cursor.execute(f"""
                    UPDATE questions
                    SET vote_number = vote_number + 1
                    WHERE id = {question_id};
                    UPDATE users
                    SET reputation = reputation + 5
                    WHERE id={points_user_id};
""")


@database_common.connection_handler
def question_vote_down(cursor, question_id, points_user_id):
    cursor.execute(f"""
                    UPDATE questions
                    SET vote_number = vote_number - 1
                    WHERE id = {question_id};
                    UPDATE users
                    SET reputation = reputation - 2
                    WHERE id={points_user_id};
""")


@database_common.connection_handler
def get_user_id_by_answer_id(cursor, answer_id):
    cursor.execute(f"""
                    SELECT user_id FROM answers
                    WHERE id={answer_id};
    """)
    result = cursor.fetchone()
    user_id = result['user_id']
    return user_id


@database_common.connection_handler
def answer_vote_up(cursor, answer_id, points_user_id):
    cursor.execute(f"""
                    UPDATE answers
                    SET vote_number = vote_number + 1
                    WHERE id = {answer_id};
                    UPDATE users
                    SET reputation = reputation + 10
                    WHERE id={points_user_id};
""")


@database_common.connection_handler
def answer_vote_down(cursor, answer_id, points_user_id):
    cursor.execute(f"""
                    UPDATE answers
                    SET vote_number = vote_number - 1
                    WHERE id = {answer_id};
                    UPDATE users
                    SET reputation = reputation - 2
                    WHERE id={points_user_id};
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
                    DELETE FROM question_tag
                    WHERE question_id = {question_id};
                    DELETE FROM comments 
                    WHERE question_id = {question_id};
                    DELETE FROM questions
                    WHERE id = {question_id};
    """)


@database_common.connection_handler
def post_answer(cursor, question_id, message, user_id):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
    cursor.execute(f"""
                    INSERT INTO answers (submission_time, vote_number, question_id, message, user_id)
                    VALUES ('{submission_time}', 0, {question_id}, '{message}', {user_id})
    """)


@database_common.connection_handler
def get_answer(cursor, answer_id):
    cursor.execute(f"""
                    SELECT * FROM answers WHERE id = {answer_id}; 
    """)
    answer = cursor.fetchone()
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
def post_question_comment(cursor, question_id, message, user_id):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
    cursor.execute(f"""
                    INSERT INTO comments (submission_time, question_id, message, user_id)
                    VALUES ('{submission_time}', {question_id}, '{message}', {user_id});
    """)


@database_common.connection_handler
def post_answer_comment(cursor, answer_id, message, user_id):
    submission_time = datetime.datetime.utcnow().isoformat(' ', 'seconds')
    cursor.execute(f"""
                    INSERT INTO comments (submission_time, answer_id, message, user_id)
                    VALUES ('{submission_time}', {answer_id}, '{message}', {user_id});
    """)


@database_common.connection_handler
def get_comments_for_question(cursor, question_id, answer_id_list):
    if not answer_id_list:
        answer_id_list.append('0')
    answer_id_str = ', '.join(answer_id_list)
    cursor.execute(f"""
                        SELECT * FROM comments WHERE question_id = {question_id} OR answer_id IN ({answer_id_str});
    """)
    comments = cursor.fetchall()
    return comments
    # comments = []
    #
    # # getting comments from the question side
    #
    # cursor.execute(f"""
    #                     SELECT * FROM comments WHERE question_id = {question_id} ORDER BY submission_time DESC;
    #     """)
    # comments.append(cursor.fetchall())
    #
    # # getting comments from the answers of the above question
    #
    # cursor.execute(f"""
    #                 SELECT * FROM answers WHERE question_id = {question_id};
    # """)
    # answers = cursor.fetchall()
    # for answer in answers:
    #     answer_id = answer['id']
    #     cursor.execute(f"""
    #                         SELECT * FROM comments WHERE answer_id = {answer_id} ORDER BY submission_time DESC;
    #         """)
    #     comments.append(cursor.fetchall())
    # return comments


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


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    cursor.execute(f"""
                    DELETE FROM comments
                    WHERE id = {comment_id};
    """)


@database_common.connection_handler
def get_all_tags(cursor):
    cursor.execute(f"""
                    SELECT * FROM tag ORDER BY name ASC; 
    """)
    all_tags = cursor.fetchall()
    return all_tags


@database_common.connection_handler
def get_all_tags_with_stats(cursor):
    cursor.execute(f"""
                    SELECT tag.name, COUNT(question_tag.question_id) AS times FROM tag 
                    LEFT JOIN question_tag ON tag.id = question_tag.tag_id
                    GROUP BY tag.name 
                    ORDER BY tag.name ASC; 
    """)
    all_tags_with_stats = cursor.fetchall()
    return all_tags_with_stats


@database_common.connection_handler
def get_question_tags(cursor, question_id):
    cursor.execute(f"""
                    SELECT question_tag.*, tag.name FROM question_tag 
                    JOIN tag ON question_tag.tag_id = tag.id
                    WHERE question_id={question_id} 
                    ORDER BY name ASC; 
    """)
    question_tags = cursor.fetchall()
    return question_tags


@database_common.connection_handler
def add_new_tag_to_db(cursor, new_tag_name):
    cursor.execute(f"""
                        INSERT INTO tag (name) VALUES ('{new_tag_name}');
        """)


@database_common.connection_handler
def get_tag_id_by_name(cursor, new_tag_name):
    cursor.execute(f"""
                    SELECT id FROM tag WHERE name = '{new_tag_name}';
""")
    result = cursor.fetchone()
    tag_id = result['id']
    return tag_id


@database_common.connection_handler
def add_new_tag_to_question(cursor, tag_id, question_id):
    cursor.execute(f"""
                        INSERT INTO question_tag (tag_id, question_id) VALUES ({tag_id}, {question_id});
        """)


@database_common.connection_handler
def delete_tag_from_question(cursor, tag_id, question_id):
    cursor.execute(f"""
                    DELETE FROM question_tag WHERE tag_id={tag_id} AND question_id={question_id};
""")


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


@database_common.connection_handler
def register_user(cursor, name, username, password):
    cursor.execute(f"""
                        INSERT INTO users (name, username, password)
                        VALUES ('{name}', '{username}', '{password}');
""")


@database_common.connection_handler
def get_db_password_for_user(cursor, username):
    cursor.execute(f"""
                       SELECT password FROM users
                       WHERE username='{username}';
    """)
    result = cursor.fetchone()
    hashed_password = result['password']
    return hashed_password


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


@database_common.connection_handler
def get_all_users(cursor):
    cursor.execute(f"""
                    SELECT * FROM users; 
    """)
    users = cursor.fetchall()
    return users


@database_common.connection_handler
def get_user_id_by_username(cursor, username):
    cursor.execute(f"""
                           SELECT id FROM users
                           WHERE username='{username}';
        """)
    result = cursor.fetchone()
    user_id = result['id']
    return user_id


@database_common.connection_handler
def get_username_by_user_id(cursor, user_id):
    cursor.execute(f"""
                   SELECT username FROM users
                   WHERE id='{user_id}';
""")
    result = cursor.fetchone()
    target_user_username = result['username']
    return target_user_username


@database_common.connection_handler
def get_all_user_questions(cursor, user_id):
    cursor.execute(f"""
            SELECT users.username, questions.title, questions.id FROM users
            JOIN questions ON users.id = questions.user_id
            WHERE users.id={user_id}
            ;
""")
    user_questions = cursor.fetchall()
    return user_questions


@database_common.connection_handler
def get_all_user_answers(cursor, user_id):
    cursor.execute(f"""
            SELECT users.username, answers.message, answers.question_id FROM users
            JOIN answers ON users.id = answers.user_id
            WHERE users.id={user_id}
            ;
""")
    user_answers = cursor.fetchall()
    return user_answers


@database_common.connection_handler
def get_all_user_comments(cursor, user_id):
    cursor.execute(f"""
            SELECT users.username, 
                    comments.message, 
                    comments.question_id, 
                    comments.answer_id, 
                    ( SELECT answers.question_id FROM answers
                        WHERE id=comments.answer_id) AS answers_linked_question_id
            FROM users
            JOIN comments ON users.id = comments.user_id
            WHERE users.id={user_id}
            ;
""")
    user_comments = cursor.fetchall()
    return user_comments


@database_common.connection_handler
def update_answer_not_accepted(cursor, answer_id, points_user_id):
    cursor.execute(f"""
                    UPDATE answers
                    SET accepted=false
                    WHERE id={answer_id};
                    UPDATE users
                    SET reputation = reputation - 15
                    WHERE id={points_user_id};
    """)


@database_common.connection_handler
def update_answer_accepted(cursor, answer_id, points_user_id):
    cursor.execute(f"""
                    UPDATE answers
                    SET accepted=true
                    WHERE id={answer_id};
                    UPDATE users
                    SET reputation = reputation + 15
                    WHERE id={points_user_id};
    """)
