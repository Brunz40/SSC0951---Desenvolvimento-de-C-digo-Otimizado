#!/usr/bin/env python3
"""Executa a validação com Rscript instalado ou com o R local do projeto."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
script = root / 'scripts/validar_analise.R'
installed = shutil.which('Rscript')
env = dict(os.environ)
if installed:
    command = [installed, '--vanilla', str(script), *sys.argv[1:]]
else:
    local = root.parents[1] / '.ferramentas/r'
    executable = local / 'usr/lib64/R/bin/exec/R'
    if not executable.is_file():
        sys.exit('R não encontrado. Instale R e execute Rscript scripts/validar_analise.R DIRETORIO_COLETA.')
    env.update(R_HOME=str(local / 'usr/lib64/R'), R_SHARE_DIR=str(local / 'usr/share/R'),
               R_INCLUDE_DIR=str(local / 'usr/include/R'), R_DOC_DIR=str(local / 'usr/share/doc/R'))
    paths = [str(local / 'usr/lib64/R/lib'), str(local / 'usr/lib64')]
    if env.get('LD_LIBRARY_PATH'):
        paths.append(env['LD_LIBRARY_PATH'])
    env['LD_LIBRARY_PATH'] = ':'.join(paths)
    command = [str(executable), '--vanilla', '--slave', '-f', str(script), '--args', *sys.argv[1:]]
sys.exit(subprocess.run(command, env=env).returncode)
