#!/usr/bin/env python3
"""Coleta perf delimitada, preservando dados brutos e a ordem de execução."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import random
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ['L1-dcache-loads', 'L1-dcache-load-misses', 'branch-instructions', 'branch-misses']


def command_output(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.stdout + result.stderr


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ambiente():
    """Registra nomes de processos, sem argumentos ou conteúdo de janelas."""
    power = {}
    for path in Path('/sys/class/power_supply').glob('*/*'):
        if path.name in {'online', 'status', 'capacity'}:
            try:
                power[str(path)] = path.read_text().strip()
            except OSError:
                pass
    return {
        'instante_utc': datetime.now(timezone.utc).isoformat(),
        'processos': command_output(['ps', '-eo', 'pid,comm,pcpu,pmem', '--sort=-pcpu']),
        'nota_ps': '%CPU é a média desde o início do processo; não é uma amostra instantânea.',
        'loadavg': Path('/proc/loadavg').read_text().strip(),
        'alimentacao': power,
    }


def parse_perf(text):
    events = {}
    coverage = {}
    for fields in csv.reader(io.StringIO(text), delimiter=';'):
        if len(fields) < 5:
            continue
        name = fields[2].removesuffix(':u')
        if name not in EVENTS:
            continue
        if name in events:
            raise ValueError(f'Evento duplicado: {name}')
        events[name] = int(fields[0])  # rejeita <not supported>/<not counted>
        coverage[name] = float(fields[4])
        if events[name] <= 0 or coverage[name] < 99.99:
            raise ValueError(f'Contador inválido ou multiplexado: {fields}')
    if set(events) != set(EVENTS):
        raise ValueError(f'Eventos incompletos: {events}')
    return events, coverage


def collect_one(perf, cpu, experiment, prefix, verbose=False):
    ctl_read, ctl_write = os.pipe()
    ack_read, ack_write = os.pipe()
    descriptors = (ctl_read, ctl_write, ack_read, ack_write)
    env = dict(os.environ, LC_ALL='C', DCO_PERF_CTL_FD=str(ctl_write),
               DCO_PERF_ACK_FD=str(ack_read))
    command = [str(perf), 'stat', '--delay=-1', '--control', f'fd:{ctl_read},{ack_write}',
               '-x', ';', '-o', str(prefix.with_suffix('.perf.csv')),
               '-e', '{' + ','.join(e + ':u' for e in EVENTS) + '}', '--',
               'taskset', '-c', str(cpu), str(ROOT / 'build/multiplicacao'), str(experiment)]
    prefix.with_suffix('.comando.json').write_text(json.dumps(command, ensure_ascii=False, indent=2))
    if verbose:
        print('Comando:', shlex.join(command), flush=True)
        print(f'DCO_PERF_CTL_FD={ctl_write}; DCO_PERF_ACK_FD={ack_read}', flush=True)
    try:
        completed = subprocess.run(command, env=env, pass_fds=descriptors,
                                   capture_output=True, text=True, timeout=120)
    finally:
        for descriptor in descriptors:
            os.close(descriptor)
    prefix.with_suffix('.stdout.csv').write_text(completed.stdout)
    prefix.with_suffix('.stderr.txt').write_text(completed.stderr)
    if completed.returncode:
        raise RuntimeError(f'Coleta falhou ({prefix.name}): {completed.stderr}')
    rows = list(csv.DictReader(io.StringIO(completed.stdout)))
    if len(rows) != 1 or int(rows[0]['experimento']) != experiment:
        raise ValueError(f'Saída inesperada: {completed.stdout}')
    row = rows[0]
    if float(row['tempo_segundos']) <= 0:
        raise ValueError('Tempo não positivo')
    events, coverage = parse_perf(prefix.with_suffix('.perf.csv').read_text())
    row.update(events)
    row['cobertura_min_pct'] = min(coverage.values())
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, required=True)
    parser.add_argument('--rodadas', type=int, default=10)
    parser.add_argument('--cpu', type=int, default=2)
    parser.add_argument('--seed', type=int, default=9512026)
    local_perf = ROOT.parents[1] / '.ferramentas/perf/usr/bin/perf'
    parser.add_argument('--perf', type=Path, default=Path(shutil.which('perf') or local_perf))
    parser.add_argument('--piloto', action='store_true')
    parser.add_argument('--experimento', type=int, choices=range(1, 9),
                        help='Mede só este experimento; requer --piloto.')
    parser.add_argument('--mostrar-comando', action='store_true')
    parser.add_argument('--nota-ambiente', default='', help='Condição informada pelo usuário.')
    args = parser.parse_args()
    if args.rodadas < (1 if args.piloto else 10):
        parser.error('Coleta definitiva exige pelo menos dez rodadas.')
    if args.experimento and not args.piloto:
        parser.error('--experimento só pode ser usado com --piloto.')
    if args.cpu not in os.sched_getaffinity(0):
        parser.error('CPU fora da afinidade disponível.')
    perf = args.perf.resolve()
    if not perf.is_file():
        parser.error('perf não encontrado; instale-o ou informe --perf.')
    output = args.saida.resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw = output / 'brutos'
    raw.mkdir()
    sources = ['Main.c', 'Multiplica.h', 'multiplica.c', 'Makefile', 'TestaMultiplica.c', 'scripts/coletar.py']
    snapshot = output / 'fontes'
    snapshot.mkdir()
    for name in sources:
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    rng = random.Random(args.seed)
    schedule = []
    for round_id in range(1, args.rodadas + 1):
        experiments = [args.experimento] if args.experimento else list(range(1, 9))
        rng.shuffle(experiments)
        schedule.extend((round_id, experiment) for experiment in experiments)
    metadata = {
        'inicio_utc': datetime.now(timezone.utc).isoformat(),
        'condicao_informada_pelo_usuario': args.nota_ambiente,
        'ambiente_inicio': ambiente(),
        'piloto': args.piloto, 'rodadas': args.rodadas, 'cpu': args.cpu, 'seed_ordem': args.seed,
        'ordem': schedule, 'perf': str(perf), 'perf_versao': command_output([str(perf), '--version']).strip(),
        'gcc': command_output(['gcc', '--version']), 'kernel': command_output(['uname', '-a']),
        'lscpu': command_output(['lscpu']), 'sistema': Path('/etc/os-release').read_text(),
        'perf_event_paranoid': Path('/proc/sys/kernel/perf_event_paranoid').read_text().strip(),
        'eventos': [e + ':u' for e in EVENTS],
        'escopo': 'zeramento e multiplicacao; contadores de usuario com controle enable/disable e pequeno overhead de controle',
        'aquecimento': 'sem chamada previa no processo; piloto separado nao integra amostra',
        'analise_cache': [1, 2, 3, 4], 'analise_branch': [1, 2, 5, 6],
        'fontes_sha256': {name: digest(ROOT / name) for name in sources},
        'binario_sha256': digest(ROOT / 'build/multiplicacao'),
        'flags': '-std=c11 -g -O0 -Wall -Wextra -Werror (TAMANHO e BLOCO registrados em cada linha)',
    }
    for suffix in ['scaling_governor', 'scaling_driver']:
        path = Path(f'/sys/devices/system/cpu/cpu{args.cpu}/cpufreq/{suffix}')
        if path.exists():
            metadata[suffix] = path.read_text().strip()
    (output / 'metadados.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    expected_checksum = None
    with (output / 'medicoes.csv').open('w', newline='') as file:
        writer = None
        for order, (round_id, experiment) in enumerate(schedule, 1):
            prefix = raw / f'{order:03d}_r{round_id:02d}_e{experiment}'
            row = collect_one(perf, args.cpu, experiment, prefix, args.mostrar_comando)
            if expected_checksum is None:
                expected_checksum = row['checksum']
            if row['checksum'] != expected_checksum:
                raise ValueError(f'Checksum divergente em {prefix}')
            row = {'ordem': order, 'rodada': round_id, **row}
            if writer is None:
                writer = csv.DictWriter(file, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            file.flush()
            print(f"{order:02d}/{len(schedule)} | rodada {round_id:02d} exp. {experiment} | {float(row['tempo_segundos']):.4f} s | contadores 100%", flush=True)
    metadata['fim_utc'] = datetime.now(timezone.utc).isoformat()
    metadata['ambiente_fim'] = ambiente()
    metadata['medicoes_sha256'] = digest(output / 'medicoes.csv')
    metadata['completa'] = True
    (output / 'metadados.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
