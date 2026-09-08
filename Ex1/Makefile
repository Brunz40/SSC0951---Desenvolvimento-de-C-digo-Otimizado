CC = gcc
TAMANHO ?= 512
BLOCO ?= 32
EXPERIMENTO ?= 1
PERF ?= $(if $(wildcard ../../.ferramentas/perf/usr/bin/perf),../../.ferramentas/perf/usr/bin/perf,perf)
PYTHON ?= $(if $(wildcard ../../.ferramentas/venv/bin/python),../../.ferramentas/venv/bin/python,python3)
COLETA ?= resultados/coleta_2026-09-07
SAIDA ?= resultados/coleta_$(shell date +%Y%m%d_%H%M%S)
RODADAS ?= 10
CPU ?= 2
# Todas as técnicas usam -O0; unrolling e tiling são explícitos no código.
FLAGS = -std=c11 -g -O0 -Wall -Wextra -Werror
DEFINES = -DTAMANHO=$(TAMANHO) -DBLOCO=$(BLOCO)

.PHONY: all executar teste verificar perfil coletar analisar relatorio clean FORCE
all: build/multiplicacao

# Recompila para respeitar mudanças em TAMANHO/BLOCO sem usar os .o antigos.
build/multiplicacao: Main.c multiplica.c Multiplica.h FORCE | build
	$(CC) $(FLAGS) $(DEFINES) Main.c multiplica.c -o $@

build:
	mkdir -p $@

executar: build/multiplicacao
	./build/multiplicacao $(EXPERIMENTO)

teste: | build
	@set -eu; for n in 1 2 3 10 32 33 65; do \
		$(CC) $(FLAGS) -DTAMANHO=$$n -DBLOCO=$(BLOCO) TestaMultiplica.c multiplica.c -lm -o build/teste-$$n; \
		./build/teste-$$n; \
	done

verificar: | build
	@set -eu; for n in 1 2 3 10 32 33 65; do \
		$(CC) $(FLAGS) -fsanitize=address,undefined -fsanitize-undefined-trap-on-error -fno-omit-frame-pointer -DTAMANHO=$$n -DBLOCO=$(BLOCO) TestaMultiplica.c multiplica.c -lm -o build/sanitizado-$$n; \
		./build/sanitizado-$$n; \
	done

# Piloto: uma rodada das oito configurações, com contadores delimitados.
perfil: build/multiplicacao
	$(PYTHON) scripts/coletar.py --perf "$(PERF)" --saida "$(SAIDA)" --cpu $(CPU) --rodadas 1 --piloto

coletar: build/multiplicacao
	$(PYTHON) scripts/coletar.py --perf "$(PERF)" --saida "$(SAIDA)" --cpu $(CPU) --rodadas $(RODADAS)

analisar:
	$(PYTHON) scripts/analisar.py "$(COLETA)"

relatorio:
	$(PYTHON) scripts/relatorio.py "$(COLETA)"

clean:
	rm -rf build
