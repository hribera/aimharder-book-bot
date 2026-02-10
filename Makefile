.PHONY: lint script-headers

PROJECT_PKG ?= aimharder_book_bot

add-headers:
	poetry run licenseheaders -t .headers.tmpl -d ${PROJECT_PKG} -cy
	@echo "Successfully modified headers."

lint:
	poetry run ruff format ${PROJECT_PKG} --check
	poetry run ruff check ${PROJECT_PKG}
