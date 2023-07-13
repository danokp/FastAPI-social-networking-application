POETRY := poetry run

runserver:
	@$(POETRY) uvicorn src.main:app --reload