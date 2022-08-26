#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Для своего варианта лабораторной работы 2.17 необходимо реализовать хранение
данных в базе данных SQLite3. Информация в базе данных должна храниться
не менее чем в двух таблицах.
"""

import pathlib
import argparse
import psycopg2


# Создание таблицы с информацией и таблицы с оценками
def create_table(con):
    cur = con.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS students_info(
        id SERIAL PRIMARY KEY,
        name TEXT,
        group_name TEXT,
        subgroup INTEGER,
        estimation REAL,
        birth_year INTEGER);
        """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS students(
        id SERIAL PRIMARY KEY,
        name TEXT,
        group_name TEXT,
        estimation REAL);
        """
    )
    con.commit()


# Добавляет по строке в таблицы
def add_student(name, group_name, subgroup, estimation, birth_year,
                con):
    cur = con.cursor()

    cur.execute(f"""
    INSERT INTO students_info(
    name, group_name, subgroup, estimation, birth_year)
    VALUES('{name}', '{group_name}', {subgroup}, {estimation}, {birth_year});
    """)

    cur.execute(f"""
    INSERT INTO students(name, group_name, estimation)
    VALUES('{name}', '{group_name}', {estimation});""")

    con.commit()
    con.close()


# Выбор и затем возврат студентов указанной группы
def select_students(con, group_name=None):
    cur = con.cursor()
    if group_name:
        cur.execute(f"SELECT name, subgroup, birth_year FROM students_info "
                    f"WHERE group_name LIKE('{group_name}');")
    else:
        cur.execute("SELECT name, group_name, estimation FROM students;")

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
    # Парсер для определения имени базы данных
    db_parser = argparse.ArgumentParser(add_help=False)
    db_parser.add_argument(
        "db_name",
        action="store",
        help="The database name"
    )

    # Основной парсер командной строки
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Субпарсер для добавления студента
    add = subparsers.add_parser(
        "add",
        parents=[db_parser],
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
        parents=[db_parser],
        help="Show list of student`s"
    )

    # Субпарсер для выбора студентов
    select = subparsers.add_parser(
        "select",
        parents=[db_parser],
        help="Show list of selected student`s"
    )
    select.add_argument(
        "-gn",
        "--group_number",
        help="The required group"
    )

    # # # # # # # # # # # # # Работа программы # # # # # # # # # # # # # # #
    args = parser.parse_args(command_line)

    con = psycopg2.connect(database=args.db_name,
                           user="postgres",
                           password="postgres",
                           host="localhost",
                           port="5432")
    create_table(con)

    if args.command == "add":
        add_student(args.name, args.group_name, args.subgroup,
                    args.estimation, args.birth_year, con)
    elif args.command == "list":
        show_list(select_students(con))
    elif args.command == "select":
        show_list(select_students(con, args.group_number))
    else:
        print("Неизвестная команда!")


if __name__ == '__main__':
    main()
