DROP TABLE IF EXISTS comments;
create table comments (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	submission_time VARCHAR(20) NOT NULL,
	question_id NUMERIC,
	answer_id NUMERIC,
	message VARCHAR(1000) NOT NULL
);
INSERT INTO comments (id, submission_time, question_id, answer_id, message) VALUES (1, '1576167982', 16, NULL, 'Not clear ... aaaa!!!!');
