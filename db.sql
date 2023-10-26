CREATE TABLE IF NOT EXISTS v_school.user (
    user_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(55) NOT NULL,
    middlename VARCHAR(55),
    lastname VARCHAR(55) NOT NULL,
    email VARCHAR(55) UNIQUE,
    phonenumber BIGINT(20) UNIQUE,
    gender VARCHAR(20) NOT NULL,
    relationship VARCHAR(55) NOT NULL,
    dateofbirth DATE,
    password VARCHAR(250),
    parent_id INTEGER,
    is_active INTEGER
);


create table if not exists v_school.enroll(
    id integer auto_increment primary key,
    subject_name varchar(55),
    description varchar(250),
    levels varchar(55),
    cls_start date,
    status varchar(55)
);