test:
	pytest -vv --show-capture=all

ci:
	pytest --show-capture=all --cov=shosai --no-cov-on-fail --cov-report term-missing
	$(MAKE) lint typing

format:
#	pip install -e .[dev]
	black shosai setup.py

lint:
#	pip install -e .[dev]
	flake8 shosai --ignore W503,E203,E501

typing:
#	pip install -e .[dev]
	mypy --strict --strict-equality --ignore-missing-imports shosai
mypy: typing

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/shosai-$(shell cat VERSION)*
	twine upload dist/shosai-$(shell cat VERSION)*

.PHONY: test ci format lint typing mypy build upload
