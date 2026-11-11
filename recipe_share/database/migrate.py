import argparse
import getpass
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def connect(database=None):
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=database,
    )


def execute_sql_file(connection, path: Path) -> None:
    statements = [statement.strip() for statement in path.read_text(encoding="utf-8").split(";") if statement.strip()]
    with connection.cursor() as cursor:
        for statement in statements:
            if not statement.startswith("--"):
                cursor.execute(statement)
    connection.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up the RecipeShare MySQL database")
    parser.add_argument("--seed", action="store_true", help="Apply seed data")
    args = parser.parse_args()

    database = os.getenv("MYSQL_DATABASE", "recipeshare")
    connection = connect()
    try:
        schema = Path(__file__).with_name("schema.sql")
        schema_text = schema.read_text(encoding="utf-8")
        schema_text = schema_text.replace("recipeshare", database)
        cursor = connection.cursor()
        try:
            for statement in [item.strip() for item in schema_text.split(";") if item.strip()]:
                if not statement.startswith("--"):
                    cursor.execute(statement)
            connection.commit()
        finally:
            cursor.close()
        connection.database = database
        if args.seed:
            seed = Path(__file__).with_name("seeds") / "001_seed.sql"
            seed_text = seed.read_text(encoding="utf-8").replace("recipeshare", database)
            cursor = connection.cursor()
            try:
                for statement in [item.strip() for item in seed_text.split(";") if item.strip()]:
                    if not statement.startswith("--"):
                        cursor.execute(statement)
                connection.commit()
            finally:
                cursor.close()
    finally:
        connection.close()

    print("Database setup complete." + (" Seeds applied." if args.seed else ""))


if __name__ == "__main__":
    main()
