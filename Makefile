SHELL := bash

.PHONY: check clean reformat dist install test docs wheel bump-version

all: dist

check:
	scripts/check-code.sh

reformat:
	scripts/format-code.sh

install:
	scripts/create-venv.sh

dist:
	python3 setup.py sdist
	scripts/zip-models.sh

test:
	scripts/run-tests.sh
	scripts/test-lang-dirs.sh

docs:
	sphinx-apidoc -f -o docs/source gruut
	sphinx-build -b html docs/source/ docs/

wheel:
	rm -f dist/*.whl
	python -m build --wheel

bump-version:
	@VERSION=$$(cat gruut/VERSION); \
	if echo "$$VERSION" | grep -qP '\.post(\d+)$$'; then \
		NUM=$$(echo "$$VERSION" | grep -oP '(?<=\.post)\d+$$'); \
		NEXT=$$((NUM + 1)); \
		NEW=$$(echo "$$VERSION" | sed "s/\.post$$NUM$$/.post$$NEXT/"); \
	else \
		NEW="$$VERSION.post1"; \
	fi; \
	echo "$$NEW" > gruut/VERSION; \
	echo "Bumped version: $$VERSION -> $$NEW"; \
	git add gruut/VERSION; \
	git commit -m "bump version: $$NEW"; \
	git push
