.PHONY: install install-dev run test verify evaluate smoke generate-demo

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements-dev.txt

run:
	./start.sh

test:
	PYTHONPATH=packages/faultline_core:apps/api pytest -q packages/faultline_core/tests apps/api/tests

verify:
	./scripts/verify_submission.sh

evaluate:
	PYTHONPATH=packages/faultline_core:apps/api python scripts/evaluate.py

smoke:
	./scripts/smoke_test.sh

generate-demo:
	PYTHONPATH=packages/faultline_core:apps/api python scripts/generate_demo_asset.py
