import os


# Force automated tests to use the dedicated test database.
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://workhub:"
    "workhub_dev_password@localhost:5434/workhub_test"
)