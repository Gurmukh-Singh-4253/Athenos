DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS student_module_progress;
DROP TABLE IF EXISTS questions;

-- Users table: stores user credentials and type (student or teacher)
CREATE TABLE users (
    username VARCHAR(80) PRIMARY KEY,
    password VARCHAR(120) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('student', 'teacher'))
);

-- Subjects table: lists available subjects
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name VARCHAR(80) UNIQUE NOT NULL
);

-- Chapters table: organizes chapters within subjects
CREATE TABLE chapters (
    chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    chapter_name VARCHAR(80) NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- Modules table: breaks down chapters into modules with optional video lectures
CREATE TABLE modules (
    module_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    module_name VARCHAR(80) NOT NULL,
    video_url TEXT,
    FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id)
);

-- Student_Subjects table: tracks subjects each student is enrolled in and their starting difficulty
CREATE TABLE student_subjects (
    student_username VARCHAR(80),
    subject_id INTEGER,
    starting_difficulty INTEGER,
    PRIMARY KEY (student_username, subject_id),
    FOREIGN KEY (student_username) REFERENCES users(username),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- Student_Teachers table: associates students with their teachers
CREATE TABLE student_teachers (
    student_username VARCHAR(80),
    teacher_username VARCHAR(80),
    PRIMARY KEY (student_username, teacher_username),
    FOREIGN KEY (student_username) REFERENCES users(username),
    FOREIGN KEY (teacher_username) REFERENCES users(username)
);

-- Student_Module_Progress table: tracks each student's progress in modules
CREATE TABLE student_module_progress (
    student_username VARCHAR(80),
    module_id INTEGER,
    current_difficulty INTEGER DEFAULT 1,
    completed BOOLEAN DEFAULT 0,
    mastery BOOLEAN DEFAULT 0,
    PRIMARY KEY (student_username, module_id),
    FOREIGN KEY (student_username) REFERENCES users(username),
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);

-- Questions table: stores questions for module tests at different difficulty levels
CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    difficulty_level INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);

-- Initial_Assessment_Questions table: stores questions for initial subject assessments
CREATE TABLE initial_assessment_questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- Test_Attempts table: logs each test attempt by students, including score and difficulty
CREATE TABLE test_attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_username VARCHAR(80) NOT NULL,
    module_id INTEGER NOT NULL,
    difficulty_level INTEGER NOT NULL,
    score FLOAT NOT NULL,
    date_taken DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_username) REFERENCES users(username),
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);
