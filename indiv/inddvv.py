#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import sqlite3
import typing as t
from pathlib import Path


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Создать таблицу с информацией о рейсах.
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_destination TEXT NOT NULL,
        flight_tp TEXT NOT NULL
        )
        """
    )
    # Создать таблицу с информацией о номерах рейсов.
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS numbers (
        flight_id INTEGER NOT NULL,
        number_flight_numer INTEGER NOT NULL,
        FOREIGN KEY(flight_id) REFERENCES flights(flight_id)
        )
        """
    )
    conn.close()


def add_flight(
        database_path: Path,
        destination: str,
        number_flight: int,
        type_plane: str
) -> None:
    """
    Добавить рейс в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT flight_id FROM flights WHERE flight_destination = ?
        """,
        (destination,)
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO flights (flight_destination, flight_tp) VALUES (?, ?)
            """,
            (destination, type_plane)
        )
        flight_id = cursor.lastrowid

    else:
        flight_id = row[0]

    cursor.execute(
        """
        INSERT INTO numbers (flight_id, number_flight_numer)
        VALUES (?, ?)
        """,
        (flight_id, number_flight)
    )
    conn.commit()
    conn.close()


def display_flights(flights):
    """
    Вывод информации о рейсах.
    """
    if flights:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 18
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^18} |'.format(
                "№",
                "Destination",
                "NumberOfTheFlight",
                "TypeOfThePlane"
            )
        )
        print(line)

        for idx, flight in enumerate(flights, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>18} |'.format(
                    idx,
                    flight.get('destination', ''),
                    flight.get('number_flight', ''),
                    flight.get('type_plane', 0)
                )
            )
        print(line)
    else:
        print('list is empty')


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT flights.flight_destination, flights.flight_tp, numbers.number_flight_numer
        FROM numbers
        INNER JOIN flights ON numbers.flight_id = flights.flight_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "destination": row[0],
            "number_flight": row[1],
            "type_plane": row[2],
        }
        for row in rows
    ]


def select_flights(
        database_path: Path, tp: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Вывод на экран информации по типу рейса.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT flights.flight_destination, flights.flight_tp, numbers.number_flight_numer
        FROM numbers
        INNER JOIN flights ON numbers.flight_id = flights.flight_id
        WHERE flights.flight_tp = ?
        """,
        (tp,)
    )
    rows = cursor.fetchall()
    conn.close()
    if len(rows) == 0:
        return []

    return [
        {
            "destination": row[0],
            "type_plane": row[1],
            "number_flight": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        required=False,
        default=str(Path.cwd() / "data_ph.db"),
        help="The database file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("flights")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления рейса.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new flight"
    )
    add.add_argument(
        "-d",
        "--destination",
        action="store",
        required=True,
        help="Destination of the flight"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="Number of the flight"
    )
    add.add_argument(
        "-t",
        "--type",
        action="store",
        required=True,
        help="Type of the plane"
    )

    # Создать субпарсер для отображения всех рейсов.
    display = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all flights"
    )

    # Создать субпарсер для выбора рейсов.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select flights by type"
    )
    select.add_argument(
        "-t",
        "--type",
        action="store",
        required=True,
        help="The required flight type"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)

    if args.command == "add":
        add_flight(db_path, args.destination, args.number, args.type)
    elif args.command == "display":
        display_flights(select_all(db_path))
    elif args.command == "select":
        display_flights(select_flights(db_path, args.type))


if __name__ == '__main__':
    main()

