# Atividade 2 — Multiplicação de matrizes e profiling

**Fernando Alee Suaiden — USP 12680836**  
**Bruno Dalcantoni Cozac — USP 13686323**

## O que abrir

- **[Relatório para entrega](entrega/Relatorio_Atividade2.pdf)** — resultados dos oito experimentos.
- [Anexo técnico](entrega/Anexo_tecnico.pdf) — explicações completas, efeitos principais, interações e reprodução.

## Organização

| Pasta | Conteúdo |
| --- | --- |
| `entrega/` | Relatório principal e anexo técnico |
| `Ex1/` | Código C, teste das oito versões e scripts atuais |
| `dados/coleta_2026-09-07/` | 80 medições, metadados e análises |
| `historico/` | Piloto, teste antigo, binários antigos e versões anteriores, compactados |

Dentro da coleta, `medicoes.csv` contém as medições; `analise/` contém as
estatísticas e gráficos. Os arquivos originais do perf estão em `brutos.zip`
e as fontes usadas na coleta, em `fontes.zip`. Não é necessário extrair os
ZIPs para recalcular a análise ou gerar o relatório.

## Comandos

```sh
make teste                 # verifica as oito implementações
make executar EXPERIMENTO=3
make relatorio             # recalcula a análise, confere em R e gera os dois PDFs
```

O número do experimento vai de 1 a 8, na ordem do enunciado. Os PDFs usam os dados salvos; `make relatorio` não refaz a coleta.
Os nomes e números USP ficam em `Ex1/integrantes.json`.

Para mais detalhes: [instruções do código e da coleta](Ex1/README.md).
As medições e conclusões se referem à máquina e ao protocolo descritos no PDF.

[Como medir e conferir os resultados com perf](Ex1/PERF.md).
