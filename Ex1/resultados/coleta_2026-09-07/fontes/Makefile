CC = gcc
TAMANHO ?= 512
BLOCO ?= 32
EXPERIMENTO ?= 1
# Todas as técnicas usam -O0; unrolling e tiling são explícitos no código.
FLAGS = -std=c11 -g -O0 -Wall -Wextra -Werror
DEFINES = -DTAMANHO=$(TAMANHO) -DBLOCO=$(BLOCO)
EVENTOS = L1-dcache-loads,L1-dcache-load-misses,branch-instructions,branch-misses

.PHONY: all executar teste verificar perfil clean FORCE
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

# Uma execução exploratória; os contadores abrangem o processo inteiro.
perfil: build/multiplicacao
	@command -v perf >/dev/null 2>&1 || { echo "perf não encontrado; é necessário instalá-lo para coletar os eventos." >&2; exit 1; }
	perf stat -e $(EVENTOS) -- ./build/multiplicacao $(EXPERIMENTO)

clean:
	rm -rf build
