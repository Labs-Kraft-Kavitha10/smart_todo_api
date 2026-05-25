.PHONY: help setup train run test-api k6-rampup k6-spike k6-all heal clean clean-all

VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip
PORT := 5001

# Default target — show help when you just type "make"
help:  ## Show this help message
	@echo "Smart Todo API — available commands:"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | \
		awk -F':.*## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Typical demo flow:"
	@echo "  make setup     # one-time"
	@echo "  make train     # one-time (writes model.joblib)"
	@echo "  make run       # leave running in this terminal"
	@echo "  # in another terminal:"
	@echo "  make test-api  # quick curl smoke test"
	@echo "  make k6-all    # run both perf tests"
	@echo "  make heal      # run self-healing test"

setup:  ## Create .venv and install Python dependencies
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

train:  ## Train the classifier (writes model.joblib)
	$(PY) train.py

run:  ## Start the Flask API on :5001 (blocks — Ctrl+C to stop)
	$(PY) app.py

test-api:  ## Quick curl smoke test (API must already be running)
	@echo "GET /health"
	@curl -s -w "  HTTP %{http_code}\n" http://localhost:$(PORT)/health
	@echo ""
	@echo "POST /predict (valid)"
	@curl -s -w "  HTTP %{http_code}\n" \
		-X POST -H "Content-Type: application/json" \
		-d '{"task":"Fix login bug breaking production"}' \
		http://localhost:$(PORT)/predict
	@echo ""
	@echo "POST /predict (missing field)"
	@curl -s -w "  HTTP %{http_code}\n" \
		-X POST -H "Content-Type: application/json" \
		-d '{}' http://localhost:$(PORT)/predict

k6-rampup:  ## Run K6 ramp-up test (~4 min, API must be running)
	@mkdir -p results
	k6 run --out json=results/ramp_up_results.json k6/ramp_up_test.js

k6-spike:  ## Run K6 spike test (~1.5 min, API must be running)
	@mkdir -p results
	k6 run --out json=results/spike_results.json k6/spike_test.js

k6-all: k6-rampup k6-spike  ## Run both K6 tests sequentially (~5.5 min)

heal:  ## Run the self-healing schema test (API must be running)
	$(PY) self_healing_test.py

clean:  ## Remove generated artifacts (keeps the venv)
	rm -f model.joblib k6_report_*.html
	rm -rf results __pycache__

clean-all: clean  ## Also remove the virtual environment
	rm -rf $(VENV)
