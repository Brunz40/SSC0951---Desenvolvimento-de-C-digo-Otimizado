#!/usr/bin/env python3
"""Estatísticas, decomposição fatorial 2² com réplicas e gráficos exportáveis."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import scipy
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

METRICS = ['tempo_segundos', 'L1-dcache-loads', 'L1-dcache-load-misses',
           'branch-instructions', 'branch-misses']
NAMES = ['Simples', 'Interchange', 'Unrolling', 'Tiling']
COLORS = ['#2463A0', '#DB7B26']


def factorial(cells):
    """Ordem: simples/estática, simples/dinâmica, técnica/estática, técnica/dinâmica."""
    values = np.asarray(cells, dtype=float)
    if values.ndim != 2 or values.shape[0] != 4 or values.shape[1] < 2:
        raise ValueError('O fatorial exige quatro células com réplicas balanceadas.')
    r = values.shape[1]
    means = values.mean(axis=1)
    design = np.array([[1, -1, -1, 1], [1, -1, 1, -1],
                       [1, 1, -1, -1], [1, 1, 1, 1]], dtype=float)
    q = design.T @ means / 4
    ss = 4 * r * q[1:] ** 2
    residual = float(np.sum((values - means[:, None]) ** 2))
    total = float(np.sum((values - values.mean()) ** 2))
    np.testing.assert_allclose(ss.sum() + residual, total, rtol=1e-10, atol=1e-5)
    result = {'q0': float(q[0]), 'n_por_celula': r, 'sse': residual, 'sst': total,
              'residuo_pct_total': 100 * residual / total if total else 0,
              'fatores': {}}
    for i, name in enumerate(['tecnica', 'alocacao', 'interacao']):
        result['fatores'][name] = {
            'q': float(q[i + 1]), 'efeito': float(2 * q[i + 1]), 'ss': float(ss[i]),
            'influencia_pct_total': float(100 * ss[i] / total) if total else 0,
            'influencia_pct_entre_medias': float(100 * ss[i] / ss.sum()) if ss.sum() else 0,
        }
    return result


def self_test():
    # Modelo conhecido: intercepto=100; qA=10; qB=-3; qAB=2;
    # três réplicas simétricas por célula, erro total=8.
    cells = [[96, 95, 94], [86, 85, 84], [112, 111, 110], [110, 109, 108]]
    result = factorial(cells)
    assert result['q0'] == 100
    # Verificação independente por mínimos quadrados sobre todas as observações.
    design = np.array([[1, -1, -1, 1], [1, -1, 1, -1],
                       [1, 1, -1, -1], [1, 1, 1, 1]])
    expected, *_ = np.linalg.lstsq(np.repeat(design, 3, axis=0), np.array(cells).ravel(), rcond=None)
    np.testing.assert_allclose([result['q0']] + [v['q'] for v in result['fatores'].values()], expected)
    assert result['sse'] == 8


def write_csv(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('coleta', type=Path)
    args = parser.parse_args()
    self_test()
    source = args.coleta.resolve()
    metadata = json.loads((source / 'metadados.json').read_text())
    if not metadata.get('completa') or metadata['piloto']:
        raise ValueError('É necessária uma coleta definitiva completa.')
    raw = source / 'medicoes.csv'
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == metadata['medicoes_sha256']
    with raw.open() as file:
        rows = list(csv.DictReader(file))
    repetitions = metadata['rodadas']
    assert repetitions >= 10 and len(rows) == 8 * repetitions
    for round_id in range(1, repetitions + 1):
        assert sorted(int(row['experimento']) for row in rows if int(row['rodada']) == round_id) == list(range(1, 9))
    assert len({r['checksum'] for r in rows}) == 1
    assert len({(r['tamanho'], r['bloco']) for r in rows}) == 1
    assert all(float(r['cobertura_min_pct']) >= 99.99 for r in rows)
    output = source / 'analise'
    output.mkdir(exist_ok=True)
    plots = output / 'graficos'
    plots.mkdir(exist_ok=True)
    samples = {e: {m: np.array([float(row[m]) for row in rows if int(row['experimento']) == e])
                   for m in METRICS} for e in range(1, 9)}
    summary = []
    lookup = {}
    for experiment in range(1, 9):
        for metric in METRICS:
            values = samples[experiment][metric]
            assert len(values) == repetitions and np.isfinite(values).all()
            mean = float(values.mean())
            sd = float(values.std(ddof=1))
            halfwidth = float(t.ppf(.975, repetitions - 1) * sd / np.sqrt(repetitions))
            stat = {'experimento': experiment, 'metrica': metric, 'n': repetitions,
                    'media': mean, 'desvio_padrao': sd, 'margem_ic95': halfwidth,
                    'ic95_inferior': mean - halfwidth, 'ic95_superior': mean + halfwidth,
                    'minimo': float(values.min()), 'maximo': float(values.max()),
                    'cv_pct': 100 * sd / mean if mean else 0}
            summary.append(stat)
            lookup[experiment, metric] = stat
    write_csv(output / 'resumo.csv', summary)
    effects = {}
    effect_rows = []
    for metric in METRICS[1:]:
        pair = [1, 2, 3, 4] if metric.startswith('L1') else [1, 2, 5, 6]
        effects[metric] = factorial([samples[e][metric] for e in pair])
        effects[metric]['experimentos'] = pair
        for factor, stat in effects[metric]['fatores'].items():
            effect_rows.append({'metrica': metric, 'fator': factor, **stat})
    write_csv(output / 'influencias.csv', effect_rows)
    (output / 'influencias.json').write_text(json.dumps(effects, ensure_ascii=False, indent=2))

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.dpi': 140, 'savefig.dpi': 200})
    def save(fig, name):
        fig.tight_layout()
        for ext in ['png', 'pdf']:
            fig.savefig(plots / f'{name}.{ext}', bbox_inches='tight')
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.1))
    for offset, color, label in [(-.19, COLORS[0], 'Estática'), (.19, COLORS[1], 'Dinâmica')]:
        parity = 1 if offset < 0 else 2
        ids = [parity + 2 * i for i in range(4)]
        means = [lookup[e, 'tempo_segundos']['media'] for e in ids]
        errors = [lookup[e, 'tempo_segundos']['margem_ic95'] for e in ids]
        bars = ax.bar(np.arange(4) + offset, means, width=.36, color=color, yerr=errors,
                      capsize=4, label=label)
        for bar, experiment, mean, error in zip(bars, ids, means, errors):
            ax.text(bar.get_x() + bar.get_width()/2, mean + error + .025,
                    f'E{experiment}\n{mean:.3f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(range(4), NAMES)
    ax.set_ylabel('Tempo do cálculo (s)')
    ax.set_title(f'Oito configurações — média e IC de 95% (n={repetitions})')
    ax.set_ylim(0, max(lookup[e,'tempo_segundos']['ic95_superior'] for e in range(1,9)) * 1.2)
    ax.legend(loc='upper left')
    save(fig, 'tempos')

    for group, metrics, labels in [
        ('cache', METRICS[1:3], ['Leituras L1 de dados', 'Faltas de leitura L1 de dados']),
        ('branch', METRICS[3:], ['Instruções de desvio', 'Erros de predição'])]:
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
        for ax, metric, label in zip(axes, metrics, labels):
            for parity, offset, color, allocation in [(1, -.19, COLORS[0], 'Estática'), (2, .19, COLORS[1], 'Dinâmica')]:
                ids = [parity + 2*i for i in range(4)]
                ax.bar(np.arange(4)+offset, [lookup[e,metric]['media']/1e6 for e in ids],
                       yerr=[lookup[e,metric]['margem_ic95']/1e6 for e in ids], capsize=3,
                       width=.36, color=color, label=allocation)
            ax.set_xticks(range(4), NAMES, rotation=18)
            ax.set_title(label)
            ax.set_ylabel('Milhões de eventos; média ± IC95%')
        axes[0].legend()
        save(fig, group)

    fig, ax = plt.subplots(figsize=(9, 3.8))
    positions = np.arange(4)
    left = np.zeros(4)
    for name, color, label in [('tecnica','#2463A0','Técnica'), ('alocacao','#DB7B26','Alocação'),
                               ('interacao','#41866B','Interação'), ('residuo','#9A9A9A','Resíduo')]:
        values = np.array([effects[m]['residuo_pct_total'] if name == 'residuo' else
                           effects[m]['fatores'][name]['influencia_pct_total'] for m in METRICS[1:]])
        ax.barh(positions, values, left=left, color=color, label=label)
        for y, base, value in zip(positions, left, values):
            if value >= 5:
                ax.text(base+value/2, y, f'{value:.1f}%', ha='center', va='center', color='white')
        left += values
    ax.set_yticks(positions, ['L1 loads (E1–E4)', 'L1 misses (E1–E4)',
                            'Branch instr. (E1,E2,E5,E6)', 'Branch misses (E1,E2,E5,E6)'])
    ax.set_xlim(0,100)
    ax.set_xlabel('Parcela da soma de quadrados total (%)')
    ax.legend(ncol=4, loc='upper center', bbox_to_anchor=(.5,1.2))
    save(fig, 'influencias')

    fig, ax = plt.subplots(figsize=(9,3.8))
    for e in range(1,9):
        selected = [row for row in rows if int(row['experimento']) == e]
        ax.plot([int(row['rodada']) for row in selected], [float(row['tempo_segundos']) for row in selected],
                marker='o', markersize=3, label=f'E{e}')
    ax.set_xlabel('Rodada (ordem interna sorteada)')
    ax.set_ylabel('Tempo do cálculo (s)')
    ax.set_title('Dispersão e evolução temporal das execuções')
    ax.legend(ncol=4, fontsize=8)
    save(fig, 'rodadas')

    report_data = {'n': repetitions, 't_critico': float(t.ppf(.975, repetitions-1)),
                   'tamanho': int(rows[0]['tamanho']), 'bloco': int(rows[0]['bloco']),
                   'checksum': rows[0]['checksum'], 'resumo': summary, 'influencias': effects,
                   'versoes': {'numpy': np.__version__, 'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__}}
    (output / 'analise.json').write_text(json.dumps(report_data, ensure_ascii=False, indent=2))
    print(f'Análise concluída: {output}')
    for e in range(1,9):
        stat = lookup[e,'tempo_segundos']
        print(f"E{e}: {stat['media']:.6f} ± {stat['margem_ic95']:.6f} s")


if __name__ == '__main__':
    main()
