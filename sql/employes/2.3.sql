CREATE TYPE grage_type AS ENUM ('junior', 'middle', 'senior');
CREATE TYPE score_type AS ENUM ('A', 'B', 'C', 'D', 'E');
CREATE TYPE job_title AS ENUM ('Data_Analist', 'Data_Engineer', 'Data_Analist_Team_Lead', 'Data_Engeneer_Team_Lead', 'General_Manager');


CREATE TABLE IF NOT EXISTS department (
    department_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Name VARCHAR (255) NOT NULL,
    director_firstname VARCHAR (255),
    director_lastname VARCHAR (255),
    director_surname VARCHAR (255),
    employee_count SMALLINT)

INSERT INTO department (
    name,
    director_firstname,
    director_lastname,
    director_surname,
    employee_count)

VALUES 
    ('Development', 'Oleg', 'Ivanov', 'Vasilievich', 3),
    ('Analitics', 'Igor', 'Petrov', 'Genadievich', 2),
    ('Support', 'Ivan', 'Sidorov', 'Petrovich', 2),
    ('Administration', 'Yuri', 'Lushkov', 'Afanasievich', 1);


   CREATE TABLE IF NOT EXISTS employees (
    employee_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    firstname VARCHAR (255) NOT NULL,
    lastname VARCHAR (255) NOT NULL,
    surname VARCHAR (255) NOT NULL,
    birthday DATE NOT NULL,
    working_start_date DATE NOT NULL,
    job_title VARCHAR (255) NOT NULL,
    salary INT,
    department_id INT,
    grade VARCHAR (255) NOT NULL,
    driver_license BOOLEAN,
    CONSTRAINT department_fk
        FOREIGN KEY (department_id)
        REFERENCES department(department_id)
        ON DELETE CASCADE);


CREATE TABLE IF NOT EXISTS scores (
    employee_id INT PRIMARY KEY,
    q1 score_type,
    q2 score_type,
    q3 score_type,
    q4 score_type,
    CONSTRAINT employee_fk
        FOREIGN KEY(employee_id)
        REFERENCES employees(employee_id)
        ON DELETE CASCADE);



INSERT INTO employees (
    firstname,
    lastname,
    surname,
    birthday,
    working_start_date,
    job_title,
    grade,
    salary,
    department_id,
    driver_license
)
VALUES
    ('Ivan', 'Ivanov', 'Ivanovich', '1995-02-20', '2018-03-04', 'Data_Engineer_Team_Lead', 'senior', 350000, 1, True),
    ('Petr', 'Petrov', 'Afanasivich', '1985-03-24', '2019-04-04', 'Data_Analist_Team_Lead', 'senior', 350000, 2, True),
    ('Ivan', 'Sidorov','Petrovich', '1975-06-04', '2020-06-06', 'Data_Engeneer_Team_Lead', 'senior', 350000, 3, True),
    ('Aleksey', 'Lushkov', 'Yurievich', '1989-04-01', '2001-05-05', 'General_Manager', 'senior', 450000, 4, True),
    ('Dmitry', 'Poliaykov', 'Genadievich', '2001-01-01', '2005-07-07', 'Data_Engineer', 'middle', 120000, 1, False),
    ('Yulia', 'Smirnova', 'Anreevna', '1999-07-29', '2006-08-08', 'Data_Engineer', 'senior', 150000, 1, True),
    ('Ravil', 'Gilmanov', 'Amirovich', '1995-08-27', '2007-09-09', 'Data_Engineer', 'junior', 80000, 1, False),
    ('Galina', 'Vorobieva', 'Sergeevna', '2002-02-11', '2008-10-10', 'Data_Analist', 'middle', 150000, 2, True),
    ('Irina', 'Sinitsina', 'Dmitrienvna', '1997-09-21', '2009-11-11', 'Data_Analist', 'junior', 90000, 2, False),
    ('Svetlana', 'Galkina', 'Anvarovna', '1987-07-14', '2010-12-12', 'Data_Engineer', 'middle', 100000, 3, True),
    ('Oleg', 'Voronov', 'Vladimirovich', '2003-01-17', '2011-01-01', 'Data_Engineer', 'middle', 90000, 3, False),
    ('Andrey', 'Yastrebov', 'Georgievich', '1977-07-23', '2012-02-02', 'Data_Engineer', 'junior', 80000, 3, False);


INSERT INTO department (Name, director_firstname, director_lastname, director_surname, employee_count)
VALUES ('Data Intellectual analitics', 'Крючков', 'Андрей', 'Алексеевич', 3);   

INSERT INTO employees (
    firstname,
    lastname,
    surname,
    birthday,
    working_start_date,
    job_title,
    grade,
    salary,
    department_id,
    driver_license
)
VALUES
    ('Aram', 'Akopian', 'Ilshatovich', '1975-02-01', '2022-03-04', 'Data_Analist_Team_Lead', 'senior', 350000, 5, True),
    ('Vera', 'Breus', 'Nikolayevna', '1985-04-20', '2020-04-04', 'Data_Analist_Team_Lead', 'middle', 350000, 5, True),
    ('Ivan', 'Sidorov','Petrovich', '1975-06-04', '2020-06-06', 'Data_Engeneer_Team_Lead', 'middle', 350000, 5, True);

SELECT employee_id, firstname, lastname, DATE(NOW()) - DATE(working_start_day) AS days_experience FROM employees;

SELECT employee_id, firstname, lastname, DATE(NOW()) - DATE(startday) AS days_experience FROM employees ORDER BY days_experience DESC LIMIT 3;

SELECT employee_id, firstname, lastname, FROM employees WHERE driver_license = 'True';

INSERT INTO scores (
    employee_id, 
    q1, 
    q2, 
    q3, 
    q4 
)
VALUES 
    (1, 'A', 'B', 'C', 'D'),
    (2, 'A', 'B', 'C', 'C'),
    (3, 'A', 'B', 'D', 'D'),
    (4, 'A', 'A', 'C', 'D'),
    (5, 'B', 'B', 'C', 'D'),
    (6, 'A', 'B', 'B', 'D'),
    (7, 'A', 'A', 'A', 'A'),
    (8, 'B', 'B', 'B', 'B'),
    (9, 'C', 'C', 'C', 'C'),
    (10, 'D', 'D', 'D', 'D'),
    (11, 'A', 'B', 'A', 'E'),
    (12, 'A', 'B', 'C', 'D'),
    (13, 'A', 'E', 'C', 'D'),
    (14, 'A', 'B', 'C', 'A'),
    (15, 'A', 'B', 'C', 'B');

SELECT employee_id FROM scores 
WHERE 'D' IN (q1, q2, q3, q4) 
OR 'E' IN (q1, q2, q3, q4);

SELECT 	employee_id, firstname, lastname, job_title FROM employees ORDER BY salary DESC LIMIT 1;