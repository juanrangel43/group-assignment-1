# EXTRA CREDIT AND OPTIONAL (3 points)
# migrations.py
#
# This file is responsible for managing database migrations. Migrations allow you to manage changes
# to the database schema over time, including creating tables, adding columns, and modifying the schema.
#
# Students are required to implement the following methods to perform migration tasks on the database.
#
# Example migration tasks include:
#   - Creating a new table.
#   - Adding new columns to an existing table.
#   - Removing columns from an existing table.
#   - Renaming columns in a table.
#   - Altering column types or constraints.
#
# Each method should:
#   - Open a connection and cursor to the database.
#   - Ensure the connection and cursor are properly closed after the operation, even in case of errors.
#   - Handle exceptions with appropriate error messages.
#   - Commit the transaction if the operation is successful, and rollback if there is an error.

# migrations.py

from api.db_connectors import MySQL


class Migrations:

    @classmethod
    def create_table(cls, table_name, schema):
        """Create a new table in the database.

        Args:
            table_name (str): Name of the table to create.
            schema (str): Column definitions, e.g.
                          "id INTEGER PRIMARY KEY AUTO_INCREMENT, name TEXT NOT NULL"

        Example:
            Migrations.create_table(
                "Station",
                "station_id INTEGER PRIMARY KEY AUTO_INCREMENT, name TEXT NOT NULL"
            )
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Table '{table_name}' created.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def add_column(cls, table_name, column_name, column_type):
        """Add a new column to an existing table.

        Args:
            table_name (str):  Table to alter, e.g. "Album"
            column_name (str): New column name, e.g. "genre"
            column_type (str): SQL type string, e.g. "VARCHAR(100)"

        Example:
            Migrations.add_column("Album", "genre", "VARCHAR(100)")
        """
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Column '{column_name}' added to '{table_name}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def remove_column(cls, table_name, column_name):
        """Remove a column from an existing table.

        Args:
            table_name (str):  Table to alter.
            column_name (str): Column to drop.

        Example:
            Migrations.remove_column("Album", "genre")
        """
        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Column '{column_name}' removed from '{table_name}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def rename_column(cls, table_name, old_column_name, new_column_name):
        """Rename a column in an existing table.

        Args:
            table_name (str):      Table to alter.
            old_column_name (str): Current column name.
            new_column_name (str): Desired new column name.

        Example:
            Migrations.rename_column("Album", "yr_released", "year_released")
        """
        query = (
            f"ALTER TABLE {table_name} "
            f"RENAME COLUMN {old_column_name} TO {new_column_name}"
        )

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Column '{old_column_name}' renamed to '{new_column_name}' in '{table_name}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def change_column_type(cls, table_name, column_name, new_column_type):
        """Change the data type of an existing column.

        Args:
            table_name (str):      Table to alter.
            column_name (str):     Column whose type will change.
            new_column_type (str): New SQL type, e.g. "BIGINT" or "VARCHAR(255)".

        Example:
            Migrations.change_column_type("Album", "year_released", "SMALLINT")
        """
        query = (
            f"ALTER TABLE {table_name} "
            f"MODIFY COLUMN {column_name} {new_column_type}"
        )

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Column '{column_name}' in '{table_name}' changed to '{new_column_type}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def add_constraint(cls, table_name, constraint_type, column_name, constraint_name):
        """Add a constraint to a column (e.g. UNIQUE, NOT NULL via MODIFY).

        Args:
            table_name (str):      Table to alter.
            constraint_type (str): Constraint keyword, e.g. "UNIQUE".
            column_name (str):     Column the constraint applies to.
            constraint_name (str): Symbolic name for the constraint.

        Example:
            Migrations.add_constraint("Artist", "UNIQUE", "name", "uq_artist_name")
        """
        query = (
            f"ALTER TABLE {table_name} "
            f"ADD CONSTRAINT {constraint_name} {constraint_type} ({column_name})"
        )

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Constraint '{constraint_name}' added to '{table_name}.{column_name}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def remove_constraint(cls, table_name, constraint_name):
        """Remove a named constraint from a table.

        Args:
            table_name (str):      Table to alter.
            constraint_name (str): Name of the constraint to drop.

        Example:
            Migrations.remove_constraint("Artist", "uq_artist_name")
        """
        query = f"ALTER TABLE {table_name} DROP INDEX {constraint_name}"

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Constraint '{constraint_name}' removed from '{table_name}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def rename_table(cls, old_table_name, new_table_name):
        """Rename an existing table.

        Args:
            old_table_name (str): Current table name.
            new_table_name (str): Desired new table name.

        Example:
            Migrations.rename_table("Album", "MusicAlbum")
        """
        query = f"RENAME TABLE {old_table_name} TO {new_table_name}"

        connection, cursor = MySQL.instance()
        try:
            cursor.execute(query)
            connection.commit()
            print(f"Table '{old_table_name}' renamed to '{new_table_name}'.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def apply_migration(cls, migration_file):
        """Execute all SQL statements found in a migration file.

        The file may contain multiple statements separated by semicolons.
        Blank lines and comment lines (starting with '--') are ignored.

        Args:
            migration_file (str): Path to the .sql migration file.

        Example:
            Migrations.apply_migration("migrations/001_add_genre_column.sql")
        """
        with open(migration_file, "r") as f:
            raw = f.read()

        # Split on semicolons, strip whitespace, drop empty/comment-only lines
        statements = [
            stmt.strip()
            for stmt in raw.split(";")
            if stmt.strip() and not stmt.strip().startswith("--")
        ]

        connection, cursor = MySQL.instance()
        try:
            for statement in statements:
                cursor.execute(statement)
            connection.commit()
            print(f"Migration '{migration_file}' applied successfully.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def rollback_migration(cls, migration_file):
        """Execute all SQL statements in a rollback / down migration file.

        Follows the same convention as apply_migration — the file should
        contain the inverse operations (DROP, ALTER, etc.) that undo a
        previously applied migration.

        Args:
            migration_file (str): Path to the rollback .sql file.

        Example:
            Migrations.rollback_migration("migrations/001_add_genre_column_down.sql")
        """
        with open(migration_file, "r") as f:
            raw = f.read()

        statements = [
            stmt.strip()
            for stmt in raw.split(";")
            if stmt.strip() and not stmt.strip().startswith("--")
        ]

        connection, cursor = MySQL.instance()
        try:
            for statement in statements:
                cursor.execute(statement)
            connection.commit()
            print(f"Migration '{migration_file}' rolled back successfully.")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

