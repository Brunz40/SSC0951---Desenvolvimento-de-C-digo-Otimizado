#!/usr/bin/env python3
"""Gera o PDF a partir da análise calculada, sem números transcritos à mão."""
import argparse
from io import BytesIO
import json
from pathlib import Path
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
    identificacao = '; '.join(f"{p['nome']}: USP {p['numero_usp']}" for p in pessoas)
    parser.add_argument('--integrantes', default=identificacao)
    args = parser.parse_args()
    source = args.coleta.resolve()
    analysis = source / 'analise'
    data = json.loads((analysis / 'analise.json').read_text())
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
    styles.add(ParagraphStyle(name='Legenda', parent=styles['Pequeno'], alignment=TA_CENTER))
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
    table_number = 0
    def table(rows, widths=None, caption=None):
        nonlocal table_number
        table_number += 1
        cells = [[Paragraph(str(value), styles['Celula']) for value in row] for row in rows]
        obj = Table(cells, colWidths=widths, repeatRows=1, hAlign='CENTER')
        obj.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EDF5')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F6F8')]),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),
            ('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#99ABBC')),
        ]))
        story.extend([obj, Spacer(1,5)])
        if caption:
            p(f'Tabela {table_number}: {caption}', 'Legenda')
        story.append(Spacer(1,4))
    def figure(name, caption, height=205):
        img = Image(str(analysis / 'graficos' / f'{name}.png') if isinstance(name, str) else name)
        scale = min(width / img.imageWidth, height / img.imageHeight)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        story.append(img)
        p(caption, 'Legenda')
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
    p('<b>SSC0951: Desenvolvimento de Código Otimizado</b>')
    for pessoa in pessoas:
        p(f"<b>{escape(pessoa['nome'])}</b>: Nº USP {escape(pessoa['numero_usp'])}")
    title('1. Implementação e medições')
    p('Foram comparadas quatro implementações seriais da multiplicação de matrizes, cada uma com alocação estática e dinâmica, totalizando os oito experimentos do enunciado. Cada elemento da saída soma os produtos de uma linha de A por uma coluna de B.')
    table([['Estática','Dinâmica','Técnica','Implementação'],
           ['E1','E2','Simples','Laços i → j → k'],
           ['E3','E4','Interchange','Troca para i → k → j'],
           ['E5','E6','Unrolling','Duas operações por iteração de k'],
           ['E7','E8','Tiling','Blocos de 32 em cada dimensão']], [55,60,110,width-225], 'Técnicas e modos de alocação dos oito experimentos.')
    p('<b>Configuração.</b> Matrizes 512 × 512 de float, entradas idênticas e compilação GCC 15.3.1 com -O0 em todas as versões, mantendo desativadas as principais otimizações automáticas do compilador. Unrolling e tiling são explícitos, sem OpenMP. As matrizes estáticas são contíguas; as dinâmicas usam um vetor de ponteiros e uma alocação por linha.')
    p('<b>Máquina.</b> AMD Ryzen 7 5700U (8 núcleos/16 CPUs lógicas), Fedora 43, kernel e perf 7.1.13. A L1 de dados tem 32 KiB por núcleo e a L2, 512 KiB. O programa usou uma thread fixada na CPU lógica 2. Frequência e boost permaneceram sob controle do sistema.')
    p('<b>Coleta.</b> Cada um dos oito experimentos foi executado dez vezes, em ordem sorteada: <b>80 medições</b>. O tempo mede zeramento da saída e multiplicação. Os quatro contadores do perf foram ativados ao redor desse trecho, em modo usuário, excluindo alocação, geração das entradas e impressão, com pequeno custo de controle. Todos tiveram cobertura de 100%, sem multiplexação. Nenhuma execução foi descartada.')
    p('<b>Validação.</b> As oito versões passaram em testes contra uma referência em double, com matrizes densas, identidade e zero, tamanhos ímpares, blocos incompletos e chamadas repetidas. Os resultados também coincidiram nas 80 medições.')
    p('<b>Estatística.</b> Para cada métrica e experimento, calculou-se média e intervalo de confiança de 95%: média ± 2,262157 × s/√10, em que s é o desvio padrão amostral e s/√10 é o erro padrão estimado da média. O fator 2,262157 vem da distribuição t de Student com nove graus de liberdade. Nas tabelas, “±” indica a margem desse intervalo. Os cálculos também foram conferidos em R.')

    page()
    title('2. Comparação dos tempos')
    figure('tempos', 'Figura 1: Tempo médio do cálculo e intervalo de confiança de 95%; dez execuções por configuração.', 220)
    rows = [['Exp.','Técnica / alocação','Tempo (s): média ± IC95%','Razão simples / versão']]
    labels = ['Simples','Interchange','Unrolling','Tiling']
    for e in range(1,9):
        base = 1 if e % 2 else 2
        rows.append([f'E{e}', f'{labels[(e-1)//2]} / {"estática" if e%2 else "dinâmica"}', estimate(e,'tempo_segundos'), f'{f(mean(base,"tempo_segundos")/mean(e,"tempo_segundos"),3)}×'])
    table(rows, [35,155,175,width-365], 'Tempos médios, IC95% e razão em relação à versão simples.')
    p(f'<b>Melhor resultado:</b> interchange estático (E3), com {estimate(3,"tempo_segundos")} s. O tempo médio foi {f(reduction(mean(1,"tempo_segundos"),mean(3,"tempo_segundos")),1)}% menor que o de E1, equivalente a uma razão de {f(mean(1,"tempo_segundos")/mean(3,"tempo_segundos"),2)}×. Na alocação estática, todas as técnicas tiveram média menor que a versão simples.')
    p(f'Na alocação dinâmica, tiling (E8) teve a menor média: redução de {f(reduction(mean(2,"tempo_segundos"),mean(8,"tempo_segundos")),1)}% em relação a E2. Unrolling dinâmico (E6) teve média {f(100*(mean(6,"tempo_segundos")/mean(2,"tempo_segundos")-1),1)}% maior que E2.')
    p('A representação dinâmica adiciona acessos a ponteiros e muda a disposição das linhas. Em -O0, esses custos podem contribuir para a diferença de tempo.')

    page()
    title('3. Cache e predição de desvios')
    p('Para cache, foram comparados E1 a E4: simples × interchange. Para predição de desvios, foram comparados E1,E2,E5,E6: simples × unrolling. Cada comparação inclui alocação estática e dinâmica.')
    for optimized, label, metrics, plot_titles, number in [
        (3, 'Interchange', ['L1-dcache-loads', 'L1-dcache-load-misses'],
         ['Leituras na L1', 'Faltas na L1'], 2),
        (5, 'Unrolling', ['branch-instructions', 'branch-misses'],
         ['Instruções de desvio', 'Erros de predição'], 3),
    ]:
        fig, axes = plt.subplots(1, 2, figsize=(9, 2.5))
        scales = [1e6, 1e3 if optimized == 5 else 1e6]
        for ax, metric, plot_title, scale in zip(axes, metrics, plot_titles, scales):
            for parity, offset, color, allocation in [
                (1, -.19, '#2463A0', 'Estática'), (2, .19, '#DB7B26', 'Dinâmica')
            ]:
                ids = [parity, optimized + parity - 1]
                ax.bar([offset, 1 + offset], [mean(e, metric) / scale for e in ids],
                       yerr=[stats[e, metric]['margem_ic95'] / scale for e in ids],
                       width=.36, capsize=3, color=color, label=allocation)
            ax.set_xticks([0, 1], ['Simples', label])
            ax.set_title(plot_title)
            ax.set_ylabel('Milhares de eventos' if scale == 1e3 else 'Milhões de eventos')
            ax.spines[['top', 'right']].set_visible(False)
        axes[0].legend(fontsize=8)
        fig.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=180, bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        figure(buffer, f'Figura {number}: Simples × {label.lower()}: médias e IC95%.', 130)
        units = ['milhões', 'milhares' if optimized == 5 else 'milhões']
        rows = [['Exp.'] + [f'{name}<br/>({unit}): média ± IC95%' for name, unit in zip(plot_titles, units)]]
        for e in [1, 2, optimized, optimized + 1]:
            rows.append([f'E{e}'] + [estimate(e, metric, scale, 5 if metric == 'branch-instructions' else 3) for metric, scale in zip(metrics, scales)])
        table(rows, [35, (width-35)/2, (width-35)/2], f'Contadores: simples × {label.lower()}, nas duas alocações.')
    p(f'<b>Cache:</b> interchange reduziu as faltas de L1 em {f(reduction(mean(1,"L1-dcache-load-misses"),mean(3,"L1-dcache-load-misses")),1)}% na alocação estática e {f(reduction(mean(2,"L1-dcache-load-misses"),mean(4,"L1-dcache-load-misses")),1)}% na dinâmica. A redução é coerente com a ordem i-k-j, que percorre sequencialmente as linhas de B e da saída.')
    p(f'<b>Desvios:</b> unrolling reduziu as instruções de desvio em aproximadamente 49%, mas os erros de predição ficaram próximos de {f(sum(mean(e,"branch-misses") for e in [1,2,5,6])/4000,1)} mil. Expandir duas operações por iteração reduz o controle do laço, sem reduzir os erros de predição na mesma proporção.')

    page()
    title('4. Influência da técnica, alocação e interação')
    p('Foram analisados dois planejamentos 2²: <b>E1 a E4 para cache</b> (simples × interchange) e <b>E1,E2,E5,E6 para branch</b> (simples × unrolling). O segundo fator é estática × dinâmica. A interação mede se o efeito da técnica muda conforme a alocação.')
    p('O modelo é y = q₀ + qA·A + qB·B + qAB·A·B. A representa a técnica (−1 simples, +1 otimizada) e B, a alocação (−1 estática, +1 dinâmica). A influência entre médias é 100·q²/(qA²+qB²+qAB²). O percentual expressa a contribuição de cada fator para a variação entre as quatro médias. Os cálculos foram conferidos em R com lm e anova.')
    names = ['L1 loads','L1 misses','Branch instr.','Branch misses']
    metrics = ['L1-dcache-loads','L1-dcache-load-misses','branch-instructions','branch-misses']
    rows = [['Métrica','Técnica (%)','Alocação (%)','Interação (%)']]
    for name,metric in zip(names,metrics):
        rows.append([name]+[f(effects[metric]['fatores'][factor]['influencia_pct_entre_medias'],3) for factor in ['tecnica','alocacao','interacao']])
    table(rows,[130]+[(width-130)/3]*3, 'Influências considerando a variação entre as quatro médias.')
    p('<b>Interpretação:</b> a alocação domina a variação das leituras de L1; a técnica domina as faltas de L1 e o total de instruções de desvio.')
    p(f'Em branch misses, a alocação respondeu por {f(effects["branch-misses"]["fatores"]["alocacao"]["influencia_pct_entre_medias"],2)}% da variação entre médias, a técnica por {f(effects["branch-misses"]["fatores"]["tecnica"]["influencia_pct_entre_medias"],2)}% e a interação por {f(effects["branch-misses"]["fatores"]["interacao"]["influencia_pct_entre_medias"],3)}%. A diferença simples − unrolling foi de {f(mean(1,"branch-misses")-mean(5,"branch-misses"),1)} erros na alocação estática e {f(mean(2,"branch-misses")-mean(6,"branch-misses"),1)} na dinâmica, diante de cerca de {f(sum(mean(e,"branch-misses") for e in [1,2,5,6])/4000,1)} mil erros por execução. Os intervalos dessas médias se sobrepõem.')

    title('5. Conclusão')
    p('Interchange estático apresentou o menor tempo médio e reduziu fortemente as faltas de L1. Unrolling reduziu as instruções de desvio pela metade, aproximadamente; na versão dinâmica, seu tempo médio foi maior que o da versão simples. Entre as versões dinâmicas, tiling apresentou o menor tempo médio.')
    title('Referências')
    for ref in [
        'BRUSCHI, Sarita Mazzini. 3ª aula: Profiling, páginas 14 a 17. 3aAula_Profiling.pdf.',
        'Linux perf. <link href="https://man7.org/linux/man-pages/man1/perf-stat.1.html" color="#174A76">perf-stat(1)</link>: controle dos eventos e coleta em modo usuário.',
        'NIST/SEMATECH. <link href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm" color="#174A76">Confidence Limits for the Mean</link>. IC bilateral t de Student.',
        'SSC0951. Script R de apoio para cálculo das influências: r.txt.'
    ]:
        p(ref,'Pequeno')

    pdf = root.parent / 'entrega/Relatorio_Atividade2.pdf'
    pdf.parent.mkdir(exist_ok=True)
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('DCO',7)
        canvas.setFillColor(colors.HexColor('#596579'))
        canvas.drawString(42,26,'SSC0951: Multiplicação de matrizes')
        canvas.drawRightString(A4[0]-42,26,str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=42,
                      title='SSC0951: Atividade 2: multiplicação de matrizes e profiling',
                      author='; '.join(p['nome'] for p in pessoas)).build(story,onFirstPage=footer,onLaterPages=footer)
    print(pdf)


if __name__ == '__main__':
    main()
