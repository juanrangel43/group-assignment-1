# datatypes.py
#
# This file defines the data types used in the ORM framework. Each class represents
# a specific column type that can be used in the database schema. These types
# are then used by the ORM's base class to define columns in database tables.
#
# The `Column` class in the ORM will reference these data types to configure the
# column's behavior, such as validating values, determining the SQL representation,
# and enforcing constraints.
#
# For example,
#   - The `Integer` class represents an INTEGER column type in SQL.
#   - The `String` class represents a TEXT column type with an optional length constraint.
#   - The `Boolean` class represents a BOOLEAN column type.
#
# Students should implement the missing methods for each type (e.g., `get_sql`, `validate`)
# to ensure proper integration with the ORM and the generation of valid SQL queries.
#
# Example usage in the ORM base class:
#
#   class User:
#       id = Column(Integer, primary_key=True)   # An INTEGER primary key column
#       name = Column(String(255), nullable=False)  # A TEXT column with a length of 255, not nullable
#       is_active = Column(Boolean, default=True)  # A BOOLEAN column with a default value of True
#       created_at = Column(Date)  # A DATE column
#
#   This would represent a "User" table with columns: "id", "name", "is_active", and "created_at".
#   The ORM will use the data types (Integer, String, Boolean, Date) to validate values and generate
#   SQL queries when interacting with the database.

class Integer:
    def __init__(self, type="INTEGER", length=None):
        self.type = type
        self.length = length

    # TODO: Implement a method to validate if the integer type is within valid ranges (e.g., for different database systems)
    def validate(self):
        allowed_types = ("TINYINT", "SMALLINT", "MEDIUMINT", "INT", "INTEGER", "BIGINT") # Datatype reference: w3schools MySQL Data Types
        
        if self.type not in allowed_types:
            raise ValueError(f"Invalid integer type: {self.type}")
    # TODO: Implement a method to get the SQL representation of the integer type (e.g., "INTEGER", "TINYINT", ...)
    def to_sql(self):
        return self.type


class String:
    def __init__(self, type='TEXT', length=None):
        self.type = type
        self.length = length

    # TODO: Implement a method to validate if the length is a positive integer and within valid database constraints
    def validate_length(self):
        allowed_types = ("CHAR", "VARCHAR", "TEXT", "TINYTEXT", "MEDIUMTEXT", "LONGTEXT")

        if self.type not in allowed_types:
            raise ValueError(f"Invalid string type: {self.type}")
        if self.length <= 0:
            raise ValueError("Invalid length")
    # TODO: Implement a method to get the SQL representation of the string type, including length if provided (e.g., "TEXT(255), VARCHAR(255), CHAR(2) ...")
    def to_sql(self):
        if self.length is not None:
            return f"{self.type}({self.length})"
        return self.type

class Float:
    def __init__(self, type='FLOAT'):
        self.type = type

    # TODO: Implement a method to validate if the float type fits the allowed precision for the database (e.g., not exceeding maximum limits)
    def validate(self):
        allowed_types = ("FLOAT", "DOUBLE", "DECIMAL")

        if self.type not in allowed_types:
            raise ValueError(f"Invalid float type: {self.type}")
    # TODO: Implement a method to get the SQL representation of the float type (e.g., "REAL")
    def to_sql(self):
        return self.type

class Boolean:
    def __init__(self):
        self.type = "BOOLEAN"

    # TODO: Implement a method to validate if the boolean type is correctly represented (should only allow True, False, or NULL)
    def validate(self):
        allowed_types = ("BOOLEAN", "BOOL")

        if self.type not in allowed_types:
            raise ValueError(f"Invalid boolean type: {self.type}")
    # TODO: Implement a method to get the SQL representation of the boolean type (e.g., "BOOLEAN")
    def to_sql(self):
        return self.type

class Date:
    def __init__(self, type='DATE'):
        self.type = type

    # TODO: Implement a method to validate if the date type is correctly formatted (e.g., for DATE: "YYYY-MM-DD")
    def validate(self):
        allowed_types = ("DATE", "DATETIME", "TIMESTAMP", "TIME", "YEAR")

        if self.type not in allowed_types:
            raise ValueError(f"Invalid date type: {self.type}")

    # TODO: Implement a method to get the SQL representation of the date type (e.g., "DATE", "TIMESTAMP", "DATETIME"...)
    def to_sql(self):
        return self.type

class Blob:
    def __init__(self):
        self.type = "BLOB"

    # TODO: Implement a method to validate if the BLOB type is appropriately used for binary data storage
    def validate(self):
        allowed_types = ("TINYBLOB", "BLOB", "MEDIUMBLOB", "LONGBLOB")

        if self.type not in allowed_types:
            raise ValueError(f"Invalid blob type: {self.type}")

    # TODO: Implement a method to get the SQL representation of the BLOB type (e.g., "BLOB")
    def to_sql(self):
        return self.type

class DateTime:
    def __init__(self, type='DATETIME'):
        self.type = type

    def validate(self):
        allowed_types = ("DATETIME", "TIMESTAMP")
        if self.type not in allowed_types:
            raise ValueError(f"Invalid datetime type: {self.type}")

    def to_sql(self):
        return self.type

class Timestamp:
    def __init__(self, type='TIMESTAMP'):
        self.type = type

    def validate(self):
        allowed_types = ("TIMESTAMP",)
        if self.type not in allowed_types:
            raise ValueError(f"Invalid timestamp type: {self.type}")

    def to_sql(self):
        return self.type

class Decimal:
    def __init__(self, type='DECIMAL', precision=10, scale=2):
        self.type = type
        self.precision = precision
        self.scale = scale

    def validate(self):
        allowed_types = ("DECIMAL", "NUMERIC")
        if self.type not in allowed_types:
            raise ValueError(f"Invalid decimal type: {self.type}")
        if self.precision <= 0 or self.scale < 0 or self.scale > self.precision:
            raise ValueError("Invalid precision/scale for Decimal")

    def to_sql(self):
        return f"{self.type}({self.precision},{self.scale})"