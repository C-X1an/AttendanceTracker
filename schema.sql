-- Schema only. No user records, password hashes or activity data.

CREATE TABLE attendance (
    username TEXT NOT NULL,
    employee_type TEXT NOT NULL,
    department TEXT NOT NULL,
    morning_status TEXT NOT NULL,
    afternoon_status TEXT NOT NULL, 
    remarks TEXT NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE users (
    username TEXT NOT NULL,
    employee_type TEXT NOT NULL,
    department TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    PRIMARY KEY(username)
);
