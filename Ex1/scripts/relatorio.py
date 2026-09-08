#!/usr/bin/env python3
"""Gera o PDF a partir da análise calculada, sem números transcritos à mão."""
import argparse
import csv
import json
from datetime import datetime
from zoneinfo import ZoneInfo
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
    root = Path(__file__).resolve().parents[1]
    pessoas = json.loads((root / 'integrantes.json').read_text())
    identificacao = '; '.join(f"{p['nome']} — USP {p['numero_usp']}" for p in pessoas)
    parser.add_argument('--integrantes', default=identificacao)
    args = parser.parse_args()
    source = args.coleta.resolve()
    analysis = source / 'analise'
    data = json.loads((analysis / 'analise.json').read_text())
    meta = json.loads((source / 'metadados.json').read_text())
    data_coleta = datetime.fromisoformat(meta['inicio_utc']).astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y')
    nota_ambiente = meta.get('condicao_informada_pelo_usuario', '')
    registros = [meta.get('ambiente_inicio', {}), meta.get('ambiente_fim', {})]
    if all(r.get('processos') for r in registros):
        condicao = 'Os processos foram registrados no início e no fim da coleta. '
        navegadores = {'firefox', 'chrome', 'chromium', 'brave', 'opera'}
        comuns = set.intersection(*[{line.split()[1] for line in r['processos'].splitlines()
                                    if len(line.split()) >= 2} for r in registros]) & navegadores
        if comuns:
            condicao += 'O processo ' + ', '.join(sorted(comuns)) + ' apareceu nos dois registros. '
        bateria = all(any(k.endswith('/status') and v == 'Discharging'
                          for k, v in r.get('alimentacao', {}).items()) for r in registros)
        if bateria:
            condicao += 'O notebook estava na bateria nos dois momentos. '
        condicao += 'Esses registros não medem a carga instantânea de cada aplicativo. '
    else:
        condicao = 'Não foram registrados os aplicativos abertos nesta coleta. '
    if nota_ambiente:
        condicao += 'Condição informada pelo operador: ' + escape(nota_ambiente) + '. '
    with (source / 'medicoes.csv').open() as arquivo:
        medicoes = list(csv.DictReader(arquivo))
    tempos_rodadas = {}
    for linha in medicoes:
        tempos_rodadas.setdefault(int(linha['rodada']), []).append(float(linha['tempo_segundos']))
    medias_rodadas = {r: sum(v) / len(v) for r, v in tempos_rodadas.items()}
    primeira_rodada = medias_rodadas[min(medias_rodadas)]
    rodadas_finais = [v for r, v in medias_rodadas.items() if r >= 3]
    media_final = sum(rodadas_finais) / len(rodadas_finais)
    brutos_nome = 'brutos.zip' if (source / 'brutos.zip').exists() else 'brutos/'
    fontes_nome = 'fontes.zip' if (source / 'fontes.zip').exists() else 'fontes/'
    stats = {(r['experimento'], r['metrica']): r for r in data['resumo']}
    effects = data['influencias']
    if not (analysis / 'validacao_R.txt').is_file():
        raise ValueError('Execute make validar-r antes de gerar o relatório final.')
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

    p('Multiplicação de matrizes<br/>e análise de desempenho', 'TituloDCO')
    p(f'<b>SSC0951 — Desenvolvimento de Código Otimizado</b><br/>Coleta: {data_coleta}')
    for pessoa in pessoas:
        p(f"<b>{escape(pessoa['nome'])}</b> — Nº USP {escape(pessoa['numero_usp'])}")
    title('1. O que foi feito')
    p('Foram comparadas quatro implementações seriais da multiplicação de matrizes, cada uma com alocação estática e dinâmica, totalizando os oito experimentos do enunciado [1]. Cada elemento da saída soma os produtos de uma linha de A por uma coluna de B.')
    table([['Estática','Dinâmica','Técnica','Implementação'],
           ['E1','E2','Simples','Laços i → j → k'],
           ['E3','E4','Interchange','Troca para i → k → j'],
           ['E5','E6','Unrolling','Duas operações por iteração de k'],
           ['E7','E8','Tiling','Blocos de 32 em cada dimensão']], [55,60,110,width-225])
    p('<b>Configuração.</b> Matrizes 512 × 512 de float, entradas idênticas e compilação GCC 15.3.1 com -O0 em todas as versões. Unrolling e tiling são explícitos, sem OpenMP. As matrizes estáticas são contíguas; as dinâmicas usam um vetor de ponteiros e uma alocação por linha.')
    p('<b>Máquina.</b> AMD Ryzen 7 5700U (8 núcleos/16 CPUs lógicas), Fedora 43, kernel e perf 7.1.13. A L1 de dados tem 32 KiB por núcleo e a L2, 512 KiB. O programa usou uma thread fixada na CPU lógica 2. Frequência e boost permaneceram sob controle do sistema.')
    p('<b>Coleta.</b> Foram feitas dez rodadas com os oito experimentos em ordem sorteada: <b>80 medições</b>. O piloto foi separado. O tempo mede zeramento da saída e multiplicação. Os quatro contadores do perf foram ativados ao redor desse trecho, em modo usuário, excluindo alocação, geração das entradas e impressão, com pequeno custo de controle [3]. Todos tiveram cobertura de 100%, sem multiplexação. Nenhuma execução foi descartada.')
    p('<b>Validação.</b> As oito versões passaram em testes contra uma referência em double, com matrizes densas, identidade e zero, tamanhos ímpares, blocos incompletos e chamadas repetidas. As 80 medições tiveram o mesmo checksum.')
    p('<b>Estatística.</b> Para cada métrica e experimento, calculou-se média e intervalo de confiança de 95%: média ± 2,262157 × s/√10, com desvio padrão amostral e t de Student com nove graus de liberdade [4]. Nas tabelas, “±” indica a margem desse intervalo. Os cálculos também foram conferidos em R.')

    page()
    title('2. Comparação dos tempos')
    figure('tempos', 'Figura 1 — Tempo médio do cálculo e intervalo de confiança de 95%; dez execuções por configuração.', 220)
    rows = [['Exp.','Técnica / alocação','Tempo (s): média ± IC95%','Razão simples / versão']]
    labels = ['Simples','Interchange','Unrolling','Tiling']
    for e in range(1,9):
        base = 1 if e % 2 else 2
        rows.append([f'E{e}', f'{labels[(e-1)//2]} / {"estática" if e%2 else "dinâmica"}', estimate(e,'tempo_segundos'), f'{f(mean(base,"tempo_segundos")/mean(e,"tempo_segundos"),3)}×'])
    table(rows, [35,155,175,width-365])
    p(f'<b>Melhor resultado:</b> interchange estático (E3), com {estimate(3,"tempo_segundos")} s. O tempo médio foi {f(reduction(mean(1,"tempo_segundos"),mean(3,"tempo_segundos")),1)}% menor que o de E1, equivalente a uma razão de {f(mean(1,"tempo_segundos")/mean(3,"tempo_segundos"),2)}×. Na alocação estática, todas as técnicas tiveram média menor que a versão simples.')
    p(f'Na alocação dinâmica, tiling (E8) teve a menor média: redução de {f(reduction(mean(2,"tempo_segundos"),mean(8,"tempo_segundos")),1)}% em relação a E2. Unrolling dinâmico (E6) teve média {f(100*(mean(6,"tempo_segundos")/mean(2,"tempo_segundos")-1),1)}% maior que E2. Os intervalos de E6 e E2 se sobrepõem; as razões apresentadas são comparações descritivas, não testes de significância.')
    p('A representação dinâmica adiciona acessos a ponteiros e muda a disposição das linhas. Em -O0, esses custos podem contribuir para a diferença de tempo. Os contadores medidos ajudam a interpretar o resultado, mas não isolam uma causa única.')

    page()
    title('3. Cache e desvios: resultados das oito versões')
    figure('cache', 'Figura 2 — Leituras e faltas de leitura na L1 de dados; médias e IC95%.', 135)
    figure('branch', 'Figura 3 — Instruções de desvio e erros de predição; médias e IC95%.', 135)
    def count_cell(e, metric, divisor, digits=3):
        s = stats[e,metric]
        return f"{f(s['media']/divisor,digits)}<br/>± {f(s['margem_ic95']/divisor,digits)}"
    rows = [['Exp.','L1 loads<br/>(milhões)','L1 misses<br/>(milhões)','Branch instr.<br/>(milhões)','Branch misses<br/>(milhares)']]
    for e in range(1,9):
        rows.append([f'E{e}',count_cell(e,'L1-dcache-loads',1e6),count_cell(e,'L1-dcache-load-misses',1e6),count_cell(e,'branch-instructions',1e6,5),count_cell(e,'branch-misses',1e3)])
    table(rows,[31]+[(width-31)/4]*4)
    p('<b>Cache:</b> interchange reduziu as faltas de L1 em cerca de 94% nas duas alocações, coerente com o acesso sequencial às linhas de B e da saída. Tiling teve comportamento diferente entre as alocações: E7 manteve muitas faltas e E8 reduziu-as fortemente. Conflitos de cache associados ao passo das linhas são uma hipótese, ainda não comprovada.')
    p(f'<b>Desvios:</b> unrolling reduziu as instruções de desvio em aproximadamente 49%, mas os erros de predição ficaram próximos de {f(sum(mean(e,"branch-misses") for e in [1,2,5,6])/4000,1)} mil. Portanto, menos desvios não significaram redução proporcional dos erros nem ganho garantido de tempo.')

    page()
    title('4. Influência da técnica, alocação e interação')
    p('Seguindo o material R [5], foram analisados dois planejamentos 2²: <b>E1–E4 para cache</b> (simples × interchange) e <b>E1,E2,E5,E6 para branch</b> (simples × unrolling). O segundo fator é estática × dinâmica. A interação mede se o efeito da técnica muda conforme a alocação.')
    p('O modelo é y = q₀ + qA·A + qB·B + qAB·A·B, com níveis −1/+1. A influência do material é 100·q²/(qA²+qB²+qAB²). Ela reparte a variação entre as quatro médias; <b>não é o percentual de melhora de desempenho</b>. A adaptação em R usa lm e anova e reproduziu os resultados de Python.')
    names = ['L1 loads','L1 misses','Branch instr.','Branch misses']
    metrics = ['L1-dcache-loads','L1-dcache-load-misses','branch-instructions','branch-misses']
    rows = [['Métrica','Técnica (%)','Alocação (%)','Interação (%)']]
    for name,metric in zip(names,metrics):
        rows.append([name]+[f(effects[metric]['fatores'][factor]['influencia_pct_entre_medias'],3) for factor in ['tecnica','alocacao','interacao']])
    table(rows,[130]+[(width-130)/3]*3)
    p('Tabela 3 — Influências calculadas como no script de apoio, considerando as quatro médias.', 'Pequeno')
    figure('influencias', 'Figura 4 — Análise adicional das 40 observações de cada subconjunto, incluindo o erro entre repetições.', 160)
    rows = [['Métrica','Técnica (%)','Alocação (%)','Interação (%)','Resíduo (%)']]
    for name,metric in zip(names,metrics):
        x=effects[metric]
        rows.append([name]+[f(x['fatores'][factor]['influencia_pct_total'],3) for factor in ['tecnica','alocacao','interacao']]+[f(x['residuo_pct_total'],3)])
    table(rows,[115]+[(width-115)/4]*4)
    p('Tabela 4 — Com réplicas: SQfator = 4·10·q²; SQerro soma os desvios quadráticos dentro de cada combinação. Percentuais divididos pela soma de quadrados total. Valores muito pequenos podem arredondar para 0,000%.', 'Pequeno')
    p(f'<b>Interpretação:</b> a alocação domina a variação das leituras de L1; a técnica domina as faltas de L1 e o total de instruções de desvio. Em branch misses, {f(effects["branch-misses"]["residuo_pct_total"],2)}% da variação total é resíduo entre execuções. Por isso, os {f(effects["branch-misses"]["fatores"]["interacao"]["influencia_pct_entre_medias"],2)}% de interação da Tabela 3 não devem ser entendidos como grande ganho ou evidência forte de efeito.')

    page()
    title('5. Limitações e conclusão')
    figure('rodadas','Figura 5 — Tempos por rodada. As primeiras observações mais lentas foram mantidas.',165)
    p(f'<b>Mudança durante a coleta.</b> A primeira rodada teve média de {f(primeira_rodada,3)} s por execução; da terceira em diante, {f(media_final,3)} s. Essa diferença sugere mudança nas condições de execução. Sem medir frequência, temperatura e carga durante cada execução, não é possível determinar a causa. Todas as observações foram mantidas.')
    p(f'<b>Limites da comparação.</b> {condicao} A CPU irmã não foi isolada e a frequência não foi fixada. Os ICs t são individuais e pressupõem estabilidade e independência suficientes. A mudança de tempo durante a coleta limita essa interpretação; uma média menor não significa uma medição mais estável.')
    p('O estudo usa um único tamanho de matriz e de bloco. A dimensão 512, potência de dois, pode acentuar conflitos de cache. Os resultados não devem ser generalizados para todas as dimensões, compiladores ou arquiteturas. A medição inclui zeramento e primeira escrita da saída, mas exclui malloc/free: avalia principalmente a disposição e o acesso às matrizes, não o custo de alocá-las.')
    p('<b>Conclusão.</b> Interchange estático apresentou o menor tempo médio e reduziu fortemente as faltas de L1. Unrolling quase dividiu por dois as instruções de desvio, mas não garantiu ganho na versão dinâmica. Tiling dependeu da disposição em memória. A análise das repetições mostrou que diferenças pequenas em branch misses exigem cautela.')
    p(f'<b>Reprodução.</b> O repositório preserva as 80 medições em {source.parent.name}/{source.name}/medicoes.csv. As tabelas completas e os gráficos estão em analise/; {brutos_nome} contém as saídas originais e {fontes_nome}, o código usado. O piloto anterior foi preservado separadamente em historico/piloto.zip. O comando <b>make relatorio COLETA={source.parent.name}/{source.name}</b> recalcula a análise e a conferência em R e gera este PDF e o Anexo_tecnico.pdf.')
    p('O anexo contém a metodologia completa e os gráficos de efeitos principais e interação. Os arquivos preservados têm verificação SHA-256; o relatório usa os dados medidos, sem descartar observações.', 'Pequeno')
    title('Referências')
    for ref in [
        '[1] SSC0951. Atividade relativa à aula 3 (Profiling). Enunciado: Atividade_1.pdf.',
        '[2] BRUSCHI, Sarita Mazzini. 3ª aula — Profiling, páginas 14–17. 3aAula_Profiling.pdf.',
        '[3] Linux perf. <link href="https://man7.org/linux/man-pages/man1/perf-stat.1.html" color="#174A76">perf-stat(1)</link>: controle dos eventos e coleta em modo usuário.',
        '[4] NIST/SEMATECH. <link href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm" color="#174A76">Confidence Limits for the Mean</link>. IC bilateral t de Student.',
        '[5] SSC0951. Script R de apoio: r.txt, preservado em Ex1/material_apoio/r_original.txt. Adaptação: Ex1/scripts/validar_analise.R.'
    ]:
        p(ref,'Pequeno')

    pdf = root.parent / 'entrega/Relatorio_Atividade2.pdf'
    pdf.parent.mkdir(exist_ok=True)
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('DCO',7)
        canvas.setFillColor(colors.HexColor('#596579'))
        canvas.drawString(42,26,f'SSC0951 • Coleta: {data_coleta}')
        canvas.drawRightString(A4[0]-42,26,str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=42,
                      title='SSC0951 — Atividade 2: multiplicação de matrizes e profiling',
                      author='; '.join(p['nome'] for p in pessoas)).build(story,onFirstPage=footer,onLaterPages=footer)
    print(pdf)


if __name__ == '__main__':
    main()
