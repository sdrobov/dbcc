#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace

from sqlalchemy import MetaData, create_engine, Table, Column
from sqlalchemy.engine import Engine


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

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

    old_table: Table
    for old_table in old_meta.sorted_tables:
        table_found = False
        old_table_schema = f'{old_table.schema}.' if old_table.schema else ''
        old_table_name = old_table_schema + old_table.name

        new_table: Table
        for new_table in new_meta.sorted_tables:
            new_table_schema = f'{new_table.schema}.' if new_table.schema else ''
            new_table_name = new_table_schema + new_table.name
            if old_table_name == new_table_name:
                table_found = True

                old_column: Column
                for old_column in old_table.columns:
                    column_found = False

                    new_column: Column
                    for new_column in new_table.columns:
                        if old_column.name == new_column.name:
                            column_found = True

                            if str(old_column.type) != str(new_column.type):
                                warnings.append(
                                    f'in old DB column {old_table_name}.{old_column.name} '
                                    f'has type {old_column.type}, while in new DB '
                                    f'type changed to {new_column.type}')

                            break

                    if not column_found:
                        errors.append(
                            f'column {old_table_name}.{old_column.name} '
                            'not found in new DB')

                break

        if not table_found:
            errors.append(f'table {old_table_name} not found in new DB')

    if len(warnings) > 0:
        for warning in warnings:
            print('WARNING: ' + warning)

    if len(errors) > 0:
        for error in errors:
            print('ERROR: ' + error)

        exit(1)


if __name__ == '__main__':
    main()
