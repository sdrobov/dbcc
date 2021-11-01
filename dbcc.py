#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace

from sqlalchemy import MetaData, create_engine, Table, Column
from sqlalchemy.engine import Engine

ERRORS: list[str] = []
WARNINGS: list[str] = []


def check_tables(old_meta: MetaData, new_meta: MetaData) -> None:
    old_table: Table
    for old_table in old_meta.sorted_tables:
        found = False
        old_table_schema = f'{old_table.schema}.' if old_table.schema else ''
        old_table_name = old_table_schema + old_table.name

        new_table: Table
        for new_table in new_meta.sorted_tables:
            new_table_schema = f'{new_table.schema}.' if new_table.schema else ''
            new_table_name = new_table_schema + new_table.name
            if old_table_name == new_table_name:
                found = True
                break

        if not found:
            ERRORS.append(f'table {old_table_name} not found in new DB')


def check_fields(old_meta: MetaData, new_meta: MetaData) -> None:
    old_table: Table
    for old_table in old_meta.sorted_tables:
        old_table_schema = f'{old_table.schema}.' if old_table.schema else ''
        old_table_name = old_table_schema + old_table.name

        new_table: Table
        for new_table in new_meta.sorted_tables:
            new_table_schema = f'{new_table.schema}.' if new_table.schema else ''
            new_table_name = new_table_schema + new_table.name

            if old_table_name != new_table_name:
                continue

            old_column: Column
            for old_column in old_table.columns:
                found = False

                new_column: Column
                for new_column in new_table.columns:
                    if old_column.name == new_column.name:
                        found = True

                        if str(old_column.type) != str(new_column.type):
                            WARNINGS.append(
                                f'column {old_table_name}.{old_column.name} '
                                f'has type {old_column.type}, while column '
                                f'{new_table_name}.{new_column.name} '
                                f'has type {new_column.type}')

                if not found:
                    ERRORS.append(
                        f'column {old_table_name}.{old_column.name} '
                        'not found in new DB')


def main() -> None:
    parser: ArgumentParser = ArgumentParser(
        description='Checks for breaking changes between DB versions')
    parser.add_argument('-o', '--old', type=str,
                        help='Old DB dsn', required=True, action='store')
    parser.add_argument('-n', '--new', type=str,
                        help='New DB dsn', required=True, action='store')

    args: Namespace = parser.parse_args()
    old_dsn: str = args.old
    new_dsn: str = args.new

    old_engine: Engine = create_engine(old_dsn, future=True)
    new_engine: Engine = create_engine(new_dsn, future=True)

    old_meta: MetaData = MetaData()
    old_meta.reflect(bind=old_engine)
    new_meta: MetaData = MetaData()
    new_meta.reflect(bind=new_engine)

    check_tables(old_meta, new_meta)
    check_fields(old_meta, new_meta)

    if len(WARNINGS) > 0:
        for warning in WARNINGS:
            print('WARNING: ' + warning)

    if len(ERRORS) > 0:
        for error in ERRORS:
            print('ERROR: ' + error)

        exit(1)


if __name__ == '__main__':
    main()
