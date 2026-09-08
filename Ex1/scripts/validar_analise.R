#!/usr/bin/env Rscript
# Adaptação de material_apoio/r_original.txt para as medições desta atividade.
# O planejamento completo de quatro células é explícito; lm e anova são os
# mesmos usados no apoio. R base basta, sem dependência de FrF2.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop('Uso: Rscript scripts/validar_analise.R DIRETORIO_COLETA')
coleta <- normalizePath(args[1], mustWork = TRUE)
saida <- file.path(coleta, 'analise')
dados <- read.csv(file.path(coleta, 'medicoes.csv'), check.names = FALSE)
python <- read.csv(file.path(saida, 'resumo.csv'), check.names = FALSE)
influencias.python <- read.csv(file.path(saida, 'influencias.csv'), check.names = FALSE)
stopifnot(nrow(dados) >= 80, all(table(dados$experimento) >= 10))
options(digits = 16)
metricas <- c('tempo_segundos', 'L1-dcache-loads', 'L1-dcache-load-misses',
              'branch-instructions', 'branch-misses')
resumo <- data.frame()
for (experimento in 1:8) {
  for (metrica in metricas) {
    x <- dados[dados$experimento == experimento, metrica]
    stopifnot(all(is.finite(x)))
    n <- length(x)
    margem <- qt(0.975, df = n - 1) * sd(x) / sqrt(n)
    resumo <- rbind(resumo, data.frame(experimento, metrica, n,
                     media = mean(x), desvio_padrao = sd(x), margem_ic95 = margem,
                     ic95_inferior = mean(x) - margem, ic95_superior = mean(x) + margem))
  }
}
comparado <- merge(resumo, python, by = c('experimento', 'metrica'), suffixes = c('.R', '.Python'))
stopifnot(nrow(comparado) == 40)
for (campo in c('media', 'desvio_padrao', 'margem_ic95', 'ic95_inferior', 'ic95_superior')) {
  a <- comparado[[paste0(campo, '.R')]]
  b <- comparado[[paste0(campo, '.Python')]]
  stopifnot(all(abs(a - b) <= 1e-7 * pmax(1, abs(b))))
}
write.csv(resumo, file.path(saida, 'resumo_R.csv'), row.names = FALSE)

influencias <- data.frame()
coeficientes <- data.frame()
anovas <- list()
pdf(file.path(saida, 'efeitos_interacoes_R.pdf'), width = 12, height = 4.5)
for (metrica in metricas[-1]) {
  otimizada <- if (startsWith(metrica, 'L1')) 3 else 5
  nome <- if (otimizada == 3) 'Interchange' else 'Unrolling'
  # Mesmo fatorial 2^2 do apoio: -1 é simples/estática; +1 é otimizada/dinâmica.
  plano <- expand.grid(Tecnica = c(-1, 1), Alocacao = c(-1, 1))
  plano$experimento <- ifelse(plano$Tecnica == -1, 1, otimizada) + ifelse(plano$Alocacao == 1, 1, 0)
  plano$resultado <- vapply(plano$experimento, function(e) mean(dados[dados$experimento == e, metrica]), numeric(1))
  modelo <- lm(resultado ~ Tecnica * Alocacao, data = plano)
  # Quatro médias e quatro parâmetros: zero graus de liberdade residuais.
  # O apoio usa as três Mean Sq; aqui não se interpretam testes F desse ajuste.
  tab <- suppressWarnings(anova(modelo))
  stopifnot(all(tab$Df[1:3] == 1))
  SST <- sum(tab$'Mean Sq'[1:3])
  parcelas <- 100 * tab$'Mean Sq'[1:3] / SST
  # Comparação adicional com réplicas: inclui soma de quadrados do erro.
  replicado <- merge(dados[dados$experimento %in% plano$experimento, ],
                     plano[c('experimento', 'Tecnica', 'Alocacao')], by = 'experimento')
  replicado$resultado <- replicado[[metrica]]
  tab.rep <- anova(lm(resultado ~ Tecnica * Alocacao, data = replicado))
  pct.total <- 100 * tab.rep$'Sum Sq'[1:3] / sum(tab.rep$'Sum Sq')
  fatores <- c('tecnica', 'alocacao', 'interacao')
  for (i in 1:3) {
    py <- influencias.python[influencias.python$metrica == metrica & influencias.python$fator == fatores[i], ]
    stopifnot(nrow(py) == 1,
              abs(parcelas[i] - py$influencia_pct_entre_medias) < 1e-6,
              abs(pct.total[i] - py$influencia_pct_total) < 1e-6)
    influencias <- rbind(influencias, data.frame(metrica, fator = fatores[i],
                          influencia_pct_entre_medias = parcelas[i], influencia_pct_total = pct.total[i]))
  }
  coeficientes <- rbind(coeficientes, data.frame(metrica, termo = names(coef(modelo)), q = unname(coef(modelo))))
  anovas[[metrica]] <- list(plano = plano, anova_medias = tab, anova_replicas = tab.rep)
  unidade <- if (metrica == 'branch-misses') 1e3 else 1e6
  y <- plano$resultado / unidade
  par(mfrow = c(1, 3), mar = c(4, 4, 4, 1), oma = c(0, 0, 2, 0))
  plot(c(-1, 1), tapply(y, plano$Tecnica, mean), type = 'b', xaxt = 'n',
       xlab = 'Tecnica', ylab = paste('Media em', if (unidade == 1e3) 'milhares' else 'milhoes'), main = 'Efeito principal: tecnica')
  axis(1, at = c(-1, 1), labels = c('Simples', nome))
  plot(c(-1, 1), tapply(y, plano$Alocacao, mean), type = 'b', xaxt = 'n',
       xlab = 'Alocacao', ylab = 'Media marginal', main = 'Efeito principal: alocacao')
  axis(1, at = c(-1, 1), labels = c('Estatica', 'Dinamica'))
  interaction.plot(factor(plano$Tecnica, levels = c(-1, 1), labels = c('Simples', nome)),
                   factor(plano$Alocacao, levels = c(-1, 1), labels = c('Estatica', 'Dinamica')),
                   y, type = 'b', xlab = 'Tecnica', ylab = 'Media por combinacao',
                   trace.label = 'Alocacao', main = 'Interacao', col = c('#2463A0', '#DB7B26'))
  mtext(metrica, outer = TRUE, font = 2)
}
dev.off()
write.csv(influencias, file.path(saida, 'influencias_R.csv'), row.names = FALSE)
write.csv(coeficientes, file.path(saida, 'coeficientes_R.csv'), row.names = FALSE)
capture.output(anovas, file = file.path(saida, 'anova_R.txt'))
capture.output(sessionInfo(), file = file.path(saida, 'sessao_R.txt'))
writeLines(c('OK: 40 medias, desvios e IC95% coincidem com Python (tolerancia relativa 1e-7).',
             'OK: 12 influencias entre medias e 12 com replicas coincidem (tolerancia absoluta 1e-6 ponto percentual).',
             'Modelo do r.txt: lm(resultado ~ Tecnica * Alocacao), anova e normalizacao pelas tres Mean Sq.',
             'Graficos de efeitos principais e interacao: efeitos_interacoes_R.pdf.'),
           file.path(saida, 'validacao_R.txt'))
cat(readLines(file.path(saida, 'validacao_R.txt')), sep = '\n')
