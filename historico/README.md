# Histórico preservado

- `piloto.zip`: todas as medições e fontes do piloto, excluídas da análise final.
- `arquivos_anteriores.zip`: teste.c original, executáveis/objetos antigos,
  README anterior, gerador anterior do relatório e o PDF anterior à identificação.
- `manifesto_arquivos.json`: origem, membro do ZIP e SHA-256 de cada arquivo
  compactado, incluindo os dados e fontes da coleta definitiva.

Todos os arquivos foram comparados byte a byte por SHA-256 antes de remover
as cópias soltas. Para consultar, abra o ZIP; para recuperar, extraia em uma
pasta separada. Os caminhos internos representam a organização da época.

Os originais da coleta definitiva ficam em `../dados/coleta_2026-09-07/brutos.zip`
e `fontes.zip`. Os CSVs usados na análise permanecem soltos em `dados/`.
