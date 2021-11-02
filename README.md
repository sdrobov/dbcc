# Database Breaking Changes Checker (dbcc)

## Description

This small utility allows you to check the two versions of the database for backward compatibility.
It simply checks all tables and columns of the old database for availability in the new database,
as well as checks the correspondence of data types for columns.

## Usage

```
usage: dbcc.py [-h] -o OLD -n NEW

Checks for breaking changes between DB versions

optional arguments:
  -h, --help         show this help message and exit
  -o OLD, --old OLD  Old DB dsn
  -n NEW, --new NEW  New DB dsn
```

OR via docker: `docker run --rm -it sdrobov/dbcc`
