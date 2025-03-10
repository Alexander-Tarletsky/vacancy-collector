alembic init -t async alembic

alembic revision --autogenerate -m "Init migration"
alembic upgrade head

ruff check app/crud/vacancy.py --select I --fix
