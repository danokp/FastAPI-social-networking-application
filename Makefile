POETRY := poetry run

runserver:
	@$(POETRY) uvicorn src.main:app --reload

migrations:
	@$(POETRY) alembic init migrations

automigrate:
	@$(POETRY) alembic revision --autogenerate -m 'Initial'

migrate:
	@$(POETRY) alembic upgrade head
