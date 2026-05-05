# columns.py
#
# This file defines the `Column` class used in the ORM framework. Each instance of
# the `Column` class represents a single column in a database table. The `Column` class
# allows us to define the column's data type, constraints (e.g., primary key, nullable, etc.),
# and foreign key relationships.
#
# The `Column` class is used by the ORM framework to map the attributes of Python classes
# (like `User`, `Post`, etc.) to actual database tables. The ORM will automatically generate
# the necessary SQL queries based on these column definitions.
#
# The `Column` class handles attributes such as:
#   - `column_type`: The type of the column (e.g., INTEGER, TEXT).
#   - `primary_key`: Whether the column is part of the primary key.
#   - `nullable`: Whether the column can be null.
#   - `unique`: Whether the column values must be unique.
#   - `foreign_key`: The foreign key constraint that relates to another table.
#
# Students need to implement the following methods to complete the functionality of this class:
#   - `get_sql()`: Generates the SQL representation of the column.
#   - `validate_type()`: Validates that the column's type is supported.
#   - `is_primary_key()`: Checks if the column is part of the primary key.
#   - `to_dict()`: Returns the column's configuration as a dictionary.
#   - `get_constraints()`: Generates a string of the column's constraints (e.g., "NOT NULL").
#   - `is_foreign_key()`: Checks if the column is a foreign key.
#
# Example usage in the ORM base class:
#
#   class User:
#       id = Column(Integer, primary_key=True)  # Primary key column of type Integer
#       name = Column(String(255), nullable=False)  # String column, not nullable
#       email = Column(String(100), unique=True)  # String column, with a unique constraint
#       created_at = Column(Date)  # Date column
#       profile_id = Column(Integer, foreign_key='Profile(id)')  # Foreign key referencing 'Profile' table
#
#   The ORM will use these `Column` instances to define the table schema and generate the
#   corresponding SQL for table creation, validation, and foreign key enforcement.

from api.datatypes import Integer, String, Float, Boolean, Date, Blob

class Column:
    def __init__(
        self, 
        column_type, primary_key=False,
        nullable=True,
        unique=False,
        foreign_key=None,
        default=None,
        on_delete=None,
        on_update=None,
        auto_increment=False
    ): 
        self.type = column_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.foreign_key = foreign_key
        self.on_update = on_update
        self.on_delete = on_delete
        self.default = default
        self.auto_increment = auto_increment

    # TODO: Implement a method to return the SQL representation of the column (e.g., "VARCHAR(255) NOT NULL")
    def to_sql(self):
        """Return the full SQL fragment for this column.
 
        Example: "INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT"
        """
        self.validate_type()
        return f"{self.type.to_sql()} {self.get_constraints()}".strip()
 
    def validate_type(self):
        """Ensure self.type is a supported datatype class or instance.
 
        Converts bare class references (e.g. Integer) into instances
        (Integer()) so that .to_sql() can always be called on self.type.
        """
        allowed_types = (Integer, String, Float, Boolean, Date, Blob)
 
        # Already an instance — nothing to do
        if isinstance(self.type, allowed_types):
            return
 
        # Bare class reference — instantiate it
        if self.type in allowed_types:
            self.type = self.type()
            return
 
        raise TypeError(f"Invalid column type: {self.type}")
 
    def is_primary_key(self):
        """Return True if this column is the primary key."""
        return bool(self.primary_key)
 
    def to_dict(self):
        """Return a dictionary representation of this column's configuration."""
        self.validate_type()
        return {
            "type": self.type.to_sql(),
            "nullable": self.nullable,
            "unique": self.unique,
            "foreign_key": self.foreign_key,
            "on_update": self.on_update,
            "on_delete": self.on_delete,
            "default": self.default,
            "auto_increment": self.auto_increment,
        }
 
    def get_constraints(self):
        """Build the constraint portion of a column definition.
 
        Example output: "NOT NULL PRIMARY KEY AUTO_INCREMENT"
        """
        constraints = []
 
        if not self.nullable:
            constraints.append("NOT NULL")
        if self.primary_key:
            constraints.append("PRIMARY KEY")
        if self.unique:
            constraints.append("UNIQUE")
        if self.auto_increment:
            constraints.append("AUTO_INCREMENT")
        if self.default is not None:
            constraints.append(f"DEFAULT {self.default}")
        if self.foreign_key:
            fk = f"REFERENCES {self.foreign_key}"
            if self.on_update:
                fk += f" ON UPDATE {self.on_update}"
            if self.on_delete:
                fk += f" ON DELETE {self.on_delete}"
            constraints.append(fk)
 
        return " ".join(constraints)
 
    def is_foreign_key(self):
        """Return True if this column has a foreign key constraint."""
        return bool(self.foreign_key)
