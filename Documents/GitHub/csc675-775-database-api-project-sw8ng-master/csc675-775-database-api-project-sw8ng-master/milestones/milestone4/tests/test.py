# This file is to perform tests to models such as getting a record, inserting, updating ...

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Then import your models
from models.models import User
from models.models import User

def print_user(user):
    print(f"User ID: {user.user_id}, Username: {user.username}, Email: {user.email}")

def main():
    # Create the User table if it doesn't exist
    User.create_schema()

    print("\n--- CREATE ---")
    user = User.create(
        username="sfsu",
        password="student",
        email="student@sfsu.edu",
        first_name="San",
        last_name="Francisco"
    )
    print_user(user)

    print("\n--- GET ---")
    fetched = User.get(user.user_id)
    print_user(fetched)

    print("\n--- UPDATE ---")
    fetched.first_name = "Updated"
    fetched.save()
    updated = User.get(user.user_id)
    print_user(updated)

    print("\n--- QUERY ---")
    results = User.query(username="sfsu")
    print(f"Query found {len(results)} user(s).")

    print("\n--- DELETE ---")
    User.delete(user.user_id)
    deleted = User.get(user.user_id)
    print(f"User after deletion: {deleted is None} (should be True)")

    print("\nDone.")

if __name__ == "__main__":
    main()
