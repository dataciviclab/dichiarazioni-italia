TOOLKIT = toolkit

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

.PHONY: check run run-all clean help

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

.PHONY: registry registry-write
registry:
	$(TOOLKIT) registry build --prefix dichiarazioni-italia

registry-write:
	$(TOOLKIT) registry build --prefix dichiarazioni-italia --write

clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
