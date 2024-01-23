# pgxfer

This container is a wrapper around `pg_dump` and `pg_restore`. It is meant to simplify the process of moving postgres databases.

## Usage

The program emits the following help text when invoked with `-h` or `--help` flags.

```
usage: pgxfer [-h] [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]
              [--log-dir LOG_DIR] [--source-host SOURCE_HOST]
              [--source-port SOURCE_PORT] [--source-username SOURCE_USERNAME]
              [--source-password SOURCE_PASSWORD] [--source-name SOURCE_NAME]
              [--dest-host DEST_HOST] [--dest-port DEST_PORT]
              [--dest-username DEST_USERNAME] [--dest-password DEST_PASSWORD]
              [--dest-name DEST_NAME]

util for running pgdump between postgres instances

options:
  -h, --help            show this help message and exit
  --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                        log level to use when writing to the console (default:
                        'INFO')
  --log-dir LOG_DIR     directory in which to write log files (default: None)
  --source-host SOURCE_HOST
                        network address of source database server (default:
                        'localhost')
  --source-port SOURCE_PORT
                        network port number of source database server
                        (default: 5432)
  --source-username SOURCE_USERNAME
                        username to use when authenticating with source
                        database server (default: 'postgres')
  --source-password SOURCE_PASSWORD
                        password to use when authenticating with source
                        database server (default: 'postgres')
  --source-name SOURCE_NAME
                        name of database to connect to on the source database
                        server (default: 'postgres')
  --dest-host DEST_HOST
                        network address of dest database server (default:
                        'dest')
  --dest-port DEST_PORT
                        network port number of dest database server (default:
                        5432)
  --dest-username DEST_USERNAME
                        username to use when authenticating with dest database
                        server (default: 'postgres')
  --dest-password DEST_PASSWORD
                        password to use when authenticating with dest database
                        server (default: 'postgres')
  --dest-name DEST_NAME
                        name of database to connect to on the dest database
                        server (default: 'postgres')

```

## Environment Variables

| Env. Var          | Info                                                             |
|-------------------|------------------------------------------------------------------|
| `DEST_HOST`       |  network address of dest database server                         |
| `DEST_PORT`       |  network port number of dest database server                     |
| `DEST_USERNAME`   |  username to use when authenticating with dest database server   |
| `DEST_PASSWORD`   |  password to use when authenticating with dest database server   |
| `DEST_NAME`       |  name of database to connect to on the dest database server      |
| `SOURCE_HOST`     |  network address of source database server                       |
| `SOURCE_PORT`     |  network port number of source databaseserver                    |
| `SOURCE_USERNAME` |  username to use when authenticating with source database server |
| `SOURCE_PASSWORD` |  password to use when authenticating with source database server |
| `SOURCE_NAME`     |  name of database to connect to on the source database server    |
| `LOG_DIR`         |  directory in which to write log files                           |
| `LOG_LEVEL`       |  log level to use when writing to the console                    |


## compose example

This container is intended to be deployed with Docker Compose or something like Kubernetes:

```yaml
services:
  pgxfer:
    image: backplane/pgxfer:1
    environment:
      DEST_HOST: "sourcehost"
      DEST_PORT: "5432"
      DEST_USERNAME: "postgres"
      DEST_PASSWORD: "hunter2"
      DEST_NAME: "postgres"
      SOURCE_HOST: "desthost"
      SOURCE_PORT: "5432"
      SOURCE_USERNAME: "dbadmin"
      SOURCE_PASSWORD: "egg$.ample.Passw0r7"
      SOURCE_NAME: "newpostgres"
      LOG_DIR: "/log"
      LOG_LEVEL: "DEBUG"
    restart: no
    volumes:
      - "./log:/log"
```
