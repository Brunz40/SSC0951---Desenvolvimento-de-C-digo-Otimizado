.DEFAULT_GOAL := all
COLETA ?= dados/coleta_2026-09-07
SAIDA ?= dados/coleta_$(shell date +%Y%m%d_%H%M%S)
.PHONY: all executar teste verificar perfil coletar analisar validar-r relatorio clean
all executar teste verificar perfil coletar analisar validar-r relatorio clean:
	$(MAKE) -C Ex1 $@ COLETA="$(abspath $(COLETA))" SAIDA="$(abspath $(SAIDA))"
