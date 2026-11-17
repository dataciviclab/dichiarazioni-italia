TOOLKIT = toolkit
PYTHON ?= python

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

.PHONY: check run run-all run-batch audit-regioni clean help

check:
	@for f in $(DATASETS); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

run:
	$(TOOLKIT) run

run-all:
	@find datasets -name dataset.yml | sort > /tmp/batch.txt
	$(TOOLKIT) run --batch /tmp/batch.txt
	@rm -f /tmp/batch.txt

# Batch selettivo: usa batch.txt generato dal workflow (solo i dataset toccati
# dalla PR mergiata). Su schedule/dispatch la CI usa run-all.
run-batch:
	@if [ -s batch.txt ]; then \
		$(TOOLKIT) run --batch batch.txt; \
	else \
		echo "Nessun dataset da processare"; \
	fi

.PHONY: registry registry-write
registry:
	$(TOOLKIT) registry build --prefix dichiarazioni-italia

registry-write:
	$(TOOLKIT) registry build --prefix dichiarazioni-italia --write

# Audit: le etichette `regione` devono essere le stesse in tutte le annualità
# della serie. Un conteggio per anno non vede il drift "stessa entità, nome
# diverso tra file"; questo sì. Le eccezioni volute stanno in
# scripts/audit_region_labels_allow.json.
audit-regioni:
	$(PYTHON) scripts/audit_region_labels.py --root out/data/clean

clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
