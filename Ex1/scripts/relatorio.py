#!/usr/bin/env python3
"""Gera o PDF a partir da análise calculada, sem números transcritos à mão."""
import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape
import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('coleta', type=Path)
    parser.add_argument('--integrantes', default='Integrantes e números USP: a preencher pelo grupo.')
    args = parser.parse_args()
    source = args.coleta.resolve()
    analysis = source / 'analise'
    data = json.loads((analysis / 'analise.json').read_text())
    meta = json.loads((source / 'metadados.json').read_text())
    stats = {(r['experimento'], r['metrica']): r for r in data['resumo']}
    effects = data['influencias']
    fontdir = Path(matplotlib.get_data_path()) / 'fonts/ttf'
    pdfmetrics.registerFont(TTFont('DCO', str(fontdir / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DCOBold', str(fontdir / 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('DCO', normal='DCO', bold='DCOBold', italic='DCO', boldItalic='DCOBold')
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = 'DCO'
    styles.add(ParagraphStyle(name='Texto', fontName='DCO', fontSize=9.3, leading=13.5, spaceAfter=7))
    styles.add(ParagraphStyle(name='TituloDCO', fontName='DCOBold', fontSize=19, leading=24, spaceAfter=14, textColor=colors.HexColor('#174A76')))
    styles.add(ParagraphStyle(name='SecaoDCO', fontName='DCOBold', fontSize=13, leading=18, spaceAfter=10, textColor=colors.HexColor('#174A76')))
    styles.add(ParagraphStyle(name='Pequeno', fontName='DCO', fontSize=7.5, leading=10.5, spaceAfter=5))
    styles.add(ParagraphStyle(name='Celula', fontName='DCO', fontSize=7.8, leading=10.5))
    styles.add(ParagraphStyle(name='Formula', fontName='DCO', fontSize=10, leading=15, spaceAfter=9, alignment=TA_CENTER))
    story = []
    width = A4[0] - 84
    def p(text, style='Texto'):
        story.append(Paragraph(text, styles[style]))
    def title(text):
        p(text, 'SecaoDCO')
    def page():
        story.append(PageBreak())
    def table(rows, widths=None):
        cells = [[Paragraph(str(value), styles['Celula']) for value in row] for row in rows]
        obj = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
        obj.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EDF5')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F6F8')]),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),
            ('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#99ABBC')),
        ]))
        story.extend([obj, Spacer(1,9)])
    def figure(name, caption, height=205):
        img = Image(str(analysis / 'graficos' / f'{name}.png'))
        scale = min(width / img.imageWidth, height / img.imageHeight)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        story.append(img)
        p(caption, 'Pequeno')
    def f(value, decimals=3):
        return f'{value:,.{decimals}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    def mean(e, metric):
        return stats[e, metric]['media']
    def reduction(before, after):
        return 100*(1-after/before)
    def estimate(e, metric, divisor=1, decimals=3):
        s = stats[e,metric]
        return f"{f(s['media']/divisor,decimals)} ± {f(s['margem_ic95']/divisor,decimals)}"

    p('Multiplicação de matrizes:<br/>otimizações e perfilamento', 'TituloDCO')
    p('<b>SSC0951 — Desenvolvimento de Código Otimizado</b><br/>Atividade relativa à aula 3 • Coleta: 07/09/2026 • Entrega prevista: 09/09/2026')
    p(escape(args.integrantes))
    title('1. Objetivo e configurações')
    p('Comparar quatro implementações seriais de multiplicação de matrizes com dois modos de alocação, medindo tempo, leituras e faltas em L1 de dados, instruções de desvio e erros de predição. O enunciado define oito experimentos [1]; a operação e as transformações seguem a aula 3, páginas 14–17 [2].')
    table([['Exp.', 'Técnica', 'Alocação', 'Laços / transformação'],
           ['1','Simples','Estática','i → j → k'], ['2','Simples','Dinâmica','i → j → k'],
           ['3','Interchange','Estática','i → k → j'], ['4','Interchange','Dinâmica','i → k → j'],
           ['5','Unrolling','Estática','i → j → k; fator 2 em k'], ['6','Unrolling','Dinâmica','i → j → k; fator 2 em k'],
           ['7','Tiling','Estática','Blocos 32³; i → j → k internos'], ['8','Tiling','Dinâmica','Blocos 32³; i → j → k internos']],
          [35,90,75,width-200])
    p('R[i][j] = Σ<sub>k=0</sub><super>N−1</super> A[i][k] × B[k][j]', 'Formula')
    p(f'Foram realizadas <b>{8*data["n"]} execuções válidas</b>, dez por configuração. Todas utilizaram matrizes {data["tamanho"]} × {data["tamanho"]} de <b>float</b>, entradas idênticas e compilação <b>-O0</b>. A melhor média observada foi a do experimento 3: <b>{estimate(3,"tempo_segundos")} s</b> (média ± margem do IC95%).')
    p('Os resultados descrevem esta implementação, neste computador e protocolo. Contagens menores de uma métrica não implicam, isoladamente, menor tempo de execução.')

    page()
    title('2. Ambiente, implementação e coleta')
    table([['Item','Configuração registrada'],
           ['Processador','AMD Ryzen 7 5700U; 8 núcleos, 16 CPUs lógicas'],
           ['Caches','L1d: 32 KiB por núcleo; L2: 512 KiB por núcleo; L3: 8 MiB no total (lscpu)'],
           ['Sistema','Fedora Linux 43; kernel 7.1.13-100.fc43.x86_64'],
           ['Compilador','GCC 15.3.1; -std=c11 -g -O0 -Wall -Wextra -Werror'],
           ['Perfilador',escape(meta['perf_versao']) + '; pacote oficial Fedora, extraído localmente'],
           ['Execução',f'Uma thread; afinidade na CPU lógica {meta["cpu"]}; CPU irmã 3 não isolada'],
           ['Frequência',f'Governador: {escape(meta.get("scaling_governor","não registrado"))}; boost ativo, sem travar frequência']],
          [95,width-95])
    p('<b>Memória.</b> As matrizes estáticas têm armazenamento <b>static</b> e disposição contígua; as dinâmicas usam <b>float **</b>, vetor de ponteiros e uma alocação por linha. As funções recebem a saída e a zeram a cada chamada. O fator alocação representa também diferenças de disposição e acesso por ponteiros, e não apenas o custo de malloc.')
    p('<b>Transformações.</b> Interchange troca os laços j e k. Unrolling expande duas operações consecutivas do laço k e trata o resto ímpar. Tiling percorre blocos nas três dimensões, preserva i-j-k dentro deles e limita as bordas. Não se utilizam pragmas, OpenMP ou paralelismo.')
    p('<b>Escopo.</b> O cronômetro CLOCK_MONOTONIC mede zeramento da saída e multiplicação. O perf inicia desativado; o programa envia enable, aguarda confirmação, cronometra o cálculo e envia disable. Os contadores incluem um pequeno custo de controle e leitura do relógio ao redor do cálculo, mas excluem geração das entradas, alocação, checksum e impressão [3].')
    p('<b>Eventos.</b> L1-dcache-loads:u, L1-dcache-load-misses:u, branch-instructions:u e branch-misses:u foram agrupados e medidos apenas em modo usuário. Todos tiveram cobertura de 100%, sem multiplexação. Não houve alteração de permissões do kernel (perf_event_paranoid=2).')
    p('<b>Ordem e repetições.</b> Dez rodadas, cada uma contendo E1–E8 em ordem sorteada com semente 9512026. O piloto de oito execuções foi excluído da amostra definitiva. Cada observação usa um processo novo, sem chamada de aquecimento interna. A primeira escrita na saída integra a medição. Nenhuma observação definitiva foi descartada.')

    page()
    title('3. Validação e tratamento estatístico')
    p('<b>Correção.</b> As oito funções foram comparadas elemento a elemento com uma referência em double, usando matrizes densas com sinais e frações, identidade e zero. Os testes cobrem N=1, 2, 3, 10, 32, 33 e 65, blocos 32 e 7 e chamadas repetidas. AddressSanitizer e verificações de comportamento indefinido passaram para os casos registrados. Tamanhos ímpares e blocos incompletos são tratados.')
    p(f'Todas as 80 execuções medidas produziram checksum <b>{data["checksum"]}</b>. O checksum verifica a consistência da campanha; a validação matemática é feita pelos testes independentes. Os arquivos brutos, fontes utilizadas e hashes SHA-256 foram preservados.')
    p('<b>Média e IC95%.</b> Para cada configuração e cada uma das cinco métricas, calculou-se a média, o desvio padrão amostral (denominador n−1) e o intervalo bilateral pela distribuição t de Student [4].')
    p('IC95% = média ± t<sub>0,975; n−1</sub> × s / √n', 'Formula')
    p(f'Com n={data["n"]}, o valor crítico é {f(data["t_critico"],6)}. Nas tabelas, “±” indica a <b>margem do intervalo da média</b>, não o desvio padrão nem a faixa de execuções. Os limites completos e os dados com precisão integral estão em resumo.csv. Os intervalos são individuais, sem ajuste para comparações múltiplas.')
    p('<b>Influências.</b> Foram escolhidos previamente os conjuntos E1,E2,E3,E4 para cache e E1,E2,E5,E6 para branch. Em cada análise 2², A é a técnica (−1 simples, +1 otimizada), B é a alocação (−1 estática, +1 dinâmica), e AB é a interação [5].')
    p('y = q₀ + q<sub>A</sub>A + q<sub>B</sub>B + q<sub>AB</sub>AB + erro', 'Formula')
    p('Os coeficientes são obtidos pelos contrastes das quatro médias divididos por 4. Cada efeito é 2q. Com r=10 réplicas por célula: SQ<sub>A</sub>=4rq<sub>A</sub>², analogamente para B e AB; SQ<sub>erro</sub> é a soma dos quadrados dos desvios dentro de cada célula.')
    p('SQ<sub>total</sub> = SQ<sub>A</sub> + SQ<sub>B</sub> + SQ<sub>AB</sub> + SQ<sub>erro</sub>', 'Formula')
    p('A influência com réplicas é 100 × SQ<sub>fator</sub>/SQ<sub>total</sub>. Também é apresentada a normalização somente entre as quatro médias: 100 × q<sub>fator</sub>²/(q<sub>A</sub>²+q<sub>B</sub>²+q<sub>AB</sub>²). Esta segunda forma soma 100% entre os fatores, mas omite a variação entre repetições. Percentual de influência não é percentual de melhoria de desempenho.')
    p('As contas foram executadas em Python e verificadas por decomposição da soma de quadrados e mínimos quadrados em um exemplo de coeficientes conhecidos. O arquivo de apoio r.txt estava vazio durante a preparação; não se atribui esta implementação a um script da disciplina não lido.', 'Pequeno')

    page()
    title('4. Comparação dos tempos dos oito experimentos')
    figure('tempos','Figura 1 — Médias e intervalos de confiança de 95% para o tempo do cálculo.',220)
    rows = [['Exp.','Técnica / alocação','Tempo (s), média ± IC95%','Razão simples / versão']]
    names = ['Simples','Interchange','Unrolling','Tiling']
    for e in range(1,9):
        base = 1 if e%2 else 2
        rows.append([str(e),f'{names[(e-1)//2]} / {"estática" if e%2 else "dinâmica"}', estimate(e,'tempo_segundos'),f'{f(mean(base,"tempo_segundos")/mean(e,"tempo_segundos"),3)}×'])
    table(rows,[30,160,175,width-365])
    p(f'O interchange estático (E3) reduziu o tempo médio em <b>{f(reduction(mean(1,"tempo_segundos"),mean(3,"tempo_segundos")),1)}%</b> em relação a E1, razão de {f(mean(1,"tempo_segundos")/mean(3,"tempo_segundos"),2)}×. As médias estáticas seguiram a ordem E3 &lt; E7 &lt; E5 &lt; E1.')
    p(f'Na alocação dinâmica, E8 teve a menor média: {estimate(8,"tempo_segundos")} s, redução de {f(reduction(mean(2,"tempo_segundos"),mean(8,"tempo_segundos")),1)}% ante E2. E6 teve média {f(100*(mean(6,"tempo_segundos")/mean(2,"tempo_segundos")-1),1)}% maior que E2. Seus intervalos se sobrepõem; essas razões são descritivas e não constituem testes de significância.')
    p('O custo de carregar ponteiros por linha e a geração de endereços em -O0 podem contribuir para as diferenças entre versões estáticas e dinâmicas. O perfilamento obtido não isola esses mecanismos nem prova uma causa única.')

    page()
    title('5. Leituras e faltas na cache L1 de dados')
    figure('cache','Figura 2 — Contagens de cache para as oito configurações; barras de IC95%.',210)
    table([['Exp.','L1 loads (milhões), média ± IC95%','L1 misses (milhões), média ± IC95%']] +
          [[str(e),estimate(e,'L1-dcache-loads',1e6,3),estimate(e,'L1-dcache-load-misses',1e6,3)] for e in range(1,9)],
          [35,(width-35)/2,(width-35)/2])
    p(f'Interchange diminuiu as faltas de L1 de {f(mean(1,"L1-dcache-load-misses")/1e6,2)} para {f(mean(3,"L1-dcache-load-misses")/1e6,2)} milhões na alocação estática (<b>{f(reduction(mean(1,"L1-dcache-load-misses"),mean(3,"L1-dcache-load-misses")),1)}%</b>) e de {f(mean(2,"L1-dcache-load-misses")/1e6,2)} para {f(mean(4,"L1-dcache-load-misses")/1e6,2)} milhões na dinâmica (<b>{f(reduction(mean(2,"L1-dcache-load-misses"),mean(4,"L1-dcache-load-misses")),1)}%</b>). A ordem i-k-j percorre linhas de B e da saída no laço interno, coerente com maior localidade.')
    p('O total de loads permanece elevado. Esses eventos abrangem as leituras executadas pelo código, inclusive acessos a variáveis e ponteiros em -O0; não equivalem apenas ao número de elementos matemáticos de A e B.')
    p(f'O tiling apresentou forte diferença: E7 teve {f(mean(7,"L1-dcache-load-misses")/1e6,2)} milhões de faltas e E8, {f(mean(8,"L1-dcache-load-misses")/1e6,2)} milhões. Uma hipótese é conflito de conjuntos causado pelo passo de 2.048 bytes entre linhas estáticas e pela ordem interna i-j-k; as linhas dinâmicas têm disposição distinta. Seriam necessários outros tamanhos, blocos ou medidas de endereços para confirmar. Não se conclui que tiling sempre melhora cache.')

    page()
    title('6. Instruções de desvio e erros de predição')
    figure('branch','Figura 3 — Contagens de branch; o número de desvios e o de erros são métricas distintas.',210)
    table([['Exp.','Branch instr. (milhões), média ± IC95%','Branch misses (milhares), média ± IC95%']] +
          [[str(e),estimate(e,'branch-instructions',1e6,5),estimate(e,'branch-misses',1e3,3)] for e in range(1,9)],
          [35,(width-35)/2,(width-35)/2])
    p(f'O unrolling reduziu as instruções de desvio de cerca de {f(mean(1,"branch-instructions")/1e6,3)} para {f(mean(5,"branch-instructions")/1e6,3)} milhões: <b>{f(reduction(mean(1,"branch-instructions"),mean(5,"branch-instructions")),2)}%</b> na alocação estática e {f(reduction(mean(2,"branch-instructions"),mean(6,"branch-instructions")),2)}% na dinâmica. Isso é coerente com metade das iterações de controle do laço k, preservando as multiplicações.')
    p(f'Os erros de predição de E1,E2,E5,E6 ficaram próximos de 265–266 mil. Assim, diminuir quase pela metade o total de desvios não reduziu os erros na mesma proporção. A razão entre as médias de misses e instructions passou de {f(100*mean(1,"branch-misses")/mean(1,"branch-instructions"),3)}% em E1 para {f(100*mean(5,"branch-misses")/mean(5,"branch-instructions"),3)}% em E5; essa taxa é descritiva, sem IC específico.')
    p('Tiling aumentou o total de instruções de desvio devido aos laços de blocagem, mas apresentou menos erros de predição. A mudança no padrão de controle pode explicar parte do comportamento. Como cache, acessos e controle mudam conjuntamente, uma só contagem não explica o tempo final.')

    page()
    title('7. Influência dos fatores e da interação')
    figure('influencias','Figura 4 — Decomposição com réplicas: técnica, alocação, interação e resíduo.',175)
    metric_short = ['L1 loads','L1 misses','Branch instr.','Branch misses']
    metrics = ['L1-dcache-loads','L1-dcache-load-misses','branch-instructions','branch-misses']
    rows = [['Métrica','Técnica (%)','Alocação (%)','Interação (%)','Resíduo (%)']]
    for label,m in zip(metric_short,metrics):
        x=effects[m]
        rows.append([label] + [f(x['fatores'][key]['influencia_pct_total'],3) for key in ['tecnica','alocacao','interacao']] + [f(x['residuo_pct_total'],3)])
    table(rows,[105,100,100,100,width-405])
    p('Tabela 5 — Percentuais da soma de quadrados total das 40 observações de cada subconjunto. Valores exibidos como 0,000% podem ser positivos abaixo da precisão de apresentação.', 'Pequeno')
    rows = [['Métrica','Técnica (%)','Alocação (%)','Interação (%)']]
    for label,m in zip(metric_short,metrics):
        rows.append([label]+[f(effects[m]['fatores'][key]['influencia_pct_entre_medias'],3) for key in ['tecnica','alocacao','interacao']])
    table(rows,[130,(width-130)/3,(width-130)/3,(width-130)/3])
    p('Tabela 6 — Normalização entre as quatro médias, sem componente de erro. O denominador difere do usado na Tabela 5.', 'Pequeno')
    p(f'<b>Cache (E1–E4).</b> A alocação explica {f(effects[metrics[0]]["fatores"]["alocacao"]["influencia_pct_total"],3)}% da variação total em loads; a técnica explica {f(effects[metrics[1]]["fatores"]["tecnica"]["influencia_pct_total"],3)}% em misses. Em média sobre as duas técnicas, mudar de estática para dinâmica acrescentou {f(effects[metrics[0]]["fatores"]["alocacao"]["efeito"]/1e6,2)} milhões de loads. Interchange reduziu, em média sobre as alocações, {f(-effects[metrics[1]]["fatores"]["tecnica"]["efeito"]/1e6,2)} milhões de misses.')
    p(f'<b>Branch (E1,E2,E5,E6).</b> A técnica responde por praticamente 100% da variação nas instruções de desvio. Já em branch misses, <b>{f(effects[metrics[3]]["residuo_pct_total"],2)}% é resíduo entre repetições</b>. O efeito médio do unrolling foi de apenas {f(effects[metrics[3]]["fatores"]["tecnica"]["efeito"],1)} erros por execução. A influência da interação parece maior quando o erro é omitido; não se deve interpretar esse percentual como evidência forte de ganho.')

    page()
    title('8. Variabilidade, limites e conclusões')
    figure('rodadas','Figura 5 — As primeiras observações de alguns experimentos foram mais lentas e foram preservadas.',200)
    p('A afinidade reduz migrações entre núcleos, mas não elimina disputa com processos do sistema, uso da CPU irmã, variação de frequência ou efeitos térmicos. A coleta ocorreu em um computador de uso geral, com boost ativo e sem isolamento do núcleo. A ordem sorteada distribui parte desses efeitos, mas não garante independência perfeita.')
    p('Os ICs t pressupõem observações suficientemente independentes e distribuição das médias adequadamente aproximada; com dez repetições, assimetria e variações de estado da máquina podem afetar essa aproximação. E1, E6 e E7 tiveram intervalos mais largos. Não foram removidos valores extremos, nem feitas repetições seletivas.')
    p('N=512 gera três matrizes de aproximadamente 3 MiB no total, acima da L1d e L2 de um núcleo. BLOCO=32 e fator de unrolling 2 foram fixados, sem busca pelo melhor ajuste. A dimensão é potência de dois e pode acentuar conflitos de cache. Os resultados não descrevem todos os tamanhos e blocos possíveis.')
    p('As medições incluem zeramento e primeira escrita da saída; excluem o tempo de malloc/free e usam apenas eventos de usuário. Portanto, a comparação de alocação avalia principalmente os acessos e a disposição das matrizes, não o custo total de criação de estruturas. Os percentuais de influência dependem dos níveis e subconjuntos escolhidos.')
    p('<b>Conclusões.</b> Interchange estático apresentou o menor tempo médio e reduziu fortemente as faltas de L1. Unrolling diminuiu as instruções de desvio em aproximadamente metade, mas isso não garantiu melhora no caso dinâmico. Tiling dependeu fortemente da disposição em memória. A análise com réplicas mostrou que a variação em branch misses foi dominada pelo resíduo, exigindo cautela para atribuir efeitos aos fatores.')

    page()
    title('9. Reprodutibilidade e referências')
    p('Os dados desta versão estão em <b>Ex1/resultados/coleta_2026-09-07/</b>. O diretório contém medicoes.csv (80 linhas), metadados.json (máquina, versões, ordem e hashes), brutos/ (saída original do perf e do programa) e fontes/ (snapshot dos arquivos usados na coleta).')
    p('Em analise/: resumo.csv contém as 40 combinações experimento/métrica com média, desvio, limites do IC, mínimo, máximo e CV; influencias.csv e influencias.json guardam os efeitos e somas de quadrados; graficos/ contém PNG e PDF vetorial. O piloto está em outro diretório e não entra nos cálculos.')
    p('Os programas de coleta, análise e geração do relatório estão em scripts/. Para reproduzir a análise dos dados existentes, a partir de Ex1:', 'Texto')
    p('../../.ferramentas/venv/bin/python scripts/analisar.py resultados/coleta_2026-09-07<br/>../../.ferramentas/venv/bin/python scripts/relatorio.py resultados/coleta_2026-09-07', 'Pequeno')
    p('Uma nova coleta deve usar um diretório novo, após compilar com TAMANHO=512 e BLOCO=32. O coletor recusa sobrescrever uma coleta existente e exige pelo menos dez rodadas no modo definitivo. Um arquivo de dados incompleto, checksum divergente, contador indisponível ou multiplexado interrompe a validação.')
    p('A instalação do perf no sistema exigiu senha; utilizou-se o pacote Fedora perf-7.1.13-100.fc43.x86_64, com assinatura verificada, extraído em .ferramentas/perf/. Não foram alterados pacotes do sistema ou permissões de contadores. O ambiente Python local usa NumPy 2.2.6 compatível com SciPy 1.14.1.')
    title('Referências')
    refs = [
        '[1] SSC0951. Atividade relativa à aula 3 (Profiling). Arquivo local Atividade_1.pdf. Enunciado, métricas, repetições, IC95% e entrega.',
        '[2] BRUSCHI, Sarita Mazzini. 3ª aula — Técnicas básicas para otimização de código serial / Profiling. Arquivo local 3aAula_Profiling.pdf, páginas 14–17.',
        '[3] Linux perf. perf-stat(1): controle enable/disable, --delay e grupos de eventos. <link href="https://man7.org/linux/man-pages/man1/perf-stat.1.html" color="#174A76">man7.org/linux/man-pages/man1/perf-stat.1.html</link>. Consulta: 07/09/2026.',
        '[4] NIST/SEMATECH. Confidence Limits for the Mean. <link href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm" color="#174A76">NIST e-Handbook, seção 1.3.5.2</link>. Consulta: 07/09/2026.',
        '[5] NIST/SEMATECH. The two-way ANOVA. <link href="https://itl.nist.gov/div898/handbook/prc/section4/prc427.htm" color="#174A76">NIST e-Handbook, seção 7.4.2.7</link>. Consulta: 07/09/2026.'
    ]
    for ref in refs:
        p(ref,'Pequeno')
    p('<b>Identificação:</b> ' + escape(args.integrantes), 'Pequeno')

    pdf = analysis / 'Relatorio_Atividade2.pdf'
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('DCO',7)
        canvas.setFillColor(colors.HexColor('#596579'))
        canvas.drawString(42,26,'SSC0951 • Atividade de profiling • 07/09/2026')
        canvas.drawRightString(A4[0]-42,26,str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=42,
                      title='SSC0951 — Atividade 2: multiplicação de matrizes e profiling',
                      author='Grupo SSC0951').build(story,onFirstPage=footer,onLaterPages=footer)
    print(pdf)


if __name__ == '__main__':
    main()
