#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Для своего варианта лабораторной работы 2.17 необходимо реализовать хранение
данных в базе данных SQLite3. Информация в базе данных должна храниться
не менее чем в двух таблицах.
"""

import pathlib
import argparse
import sqlite3


# Создание таблицы с информацией и таблицы с оценками
def create_table(database_path):
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    cur.execute(
        """
    CREATE TABLE students_info(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        group_name TEXT,
        subgroup INTEGER,
        estimation REAL,
        birth_year INTEGER
        )
        """
    )
    cur.execute(
        """
    CREATE TABLE students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        group_name TEXT,
        estimation REAL)
        """
    )
    con.commit()
    con.close()


# Добавляет по строке в таблицы
def add_student(name, group_name, subgroup, estimation, birth_year,
                database_path):
    con = sqlite3.connect(database_path)
    cur = con.cursor()

    cur.execute("""
    INSERT INTO students_info(
    name, group_name, subgroup, estimation, birth_year)
    VALUES(?, ?, ?, ?, ?)
    """, (name, group_name, subgroup, estimation, birth_year))

    cur.execute("""
    INSERT INTO students(name, group_name, estimation)
    VALUES(?, ?, ?)""", (name, group_name, estimation))

    con.commit()
    con.close()


# Выбор и затем возврат студентов указанной группы
def select_students(database_path, group_name=None):
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    if group_name:
        cur.execute(f"SELECT name, subgroup, birth_year FROM students_info "
                    f"WHERE group_name LIKE('{group_name}')")
    else:
        cur.execute("SELECT name, group_name, estimation FROM students")

    rows = cur.fetchall()
    con.close()
    return [
        {
            "name": row[0],
            "group_name": row[1],
            "estimation": row[2]
        }
        for row in rows
    ]


# Выводит список студентов
def show_list(staff):
    if staff:
        # Заголовок таблицы.
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 20
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^20} |'.format(
                "No",
                "Ф.И.О.",
                "Группа/Подгруппа",
                "Средняя оценка/Год"
            )
        )
        print(line)
        # Вывести данные о всех студентах.
        for idx, student in enumerate(staff, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:<20} |'.format(
                    idx,
                    student.get('name', ''),
                    student.get('group_name', ''),
                    student.get('estimation', 0)
                )
            )
        print(line)
    else:
        print("Список пуст")


def main(command_line=None):
    # Парсер для определения имени файла
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename",
        action="store",
        help="The data file name"
    )

    # Основной парсер командной строки
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Субпарсер для добавления студента
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new student"
    )
    add.add_argument(
        "-n",
        "--name",
        help="The student`s name"
    )
    add.add_argument(
        "-g",
        "--group_name",
        help="The student`s group name"
    )
    add.add_argument(
        "-s",
        "--subgroup",
        help="The student`s subgroup"
    )
    add.add_argument(
        "-e",
        "--estimation",
        help="The student`s average estimation"
    )
    add.add_argument(
        "-by",
        "--birth_year",
        help="The student`s year of birth"
    )

    # Субпрасер показывающий список студентов
    subparsers.add_parser(
        "list",
        parents=[file_parser],
        help="Show list of student`s"
    )

    # Субпарсер для выбора студентов
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Show list of selected student`s"
    )
    select.add_argument(
        "-gn",
        "--group_number",
        help="The required group"
    )

    # # # # # # # # # # # # # Работа программы # # # # # # # # # # # # # # #
    args = parser.parse_args(command_line)
    dbname = pathlib.Path.cwd() / args.filename
    # Проверка существования файла
    if not pathlib.Path.exists(dbname):
        create_table(dbname)

    if args.command == "add":
        add_student(args.name, args.group_name, args.subgroup,
                    args.estimation, args.birth_year, dbname)
    elif args.command == "list":
        show_list(select_students(dbname))
    elif args.command == "select":
        show_list(select_students(dbname, args.group_number))
    else:
        print("Неизвестная команда!")


if __name__ == '__main__':
    main()
