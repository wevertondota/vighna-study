# -*- coding: utf-8 -*-
"""Ambiente Python de QA independente, criado apenas mediante comando do usuário.

Nunca importa nem executa código do VighnaStudy. Não altera Python global.
Não copia virtualenvs (eles não são portáteis entre caminhos).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

DEPENDENCIES = ("PySide6==6.11.2", "pyinstaller==6.22.3", "qtawesome==1.4.0")
MARKER = ".vighna_qa_env.json"

class EnvironmentError(ValueError):
    pass


def destination(home: Path | None = None) -> Path:
    """Estável entre atualizações do painel, sempre dentro do perfil Windows."""
    root = (home if home is not None else Path.home())
    return root / "VighnaLab" / "Ambiente_Qt_Homologador"


def interpreter(env: Path) -> Path:
    return env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _check_no_junction(path: Path):
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise EnvironmentError("Caminho contém link simbólico/junction; operação bloqueada.")


def verify_destination(target: Path, home: Path | None = None) -> Path:
    home = Path(home) if home is not None else Path.home()
    expected = destination(home)
    if target != expected:
        raise EnvironmentError("Ambiente deve ficar no diretório VighnaLab predefinido.")
    for p in (home, target.parent, target):
        # Path.exists() é falso para symlink quebrado: verificar mesmo assim.
        _check_no_junction(p)
    for p in (target.parent, target):
        if (p / "VighnaStudy.exe").exists() or (p / "estudos.db").exists():
            raise EnvironmentError("Instalação ou banco real encontrado; operação bloqueada.")
    if target.exists():
        if not target.is_dir():
            raise EnvironmentError("Destino existente não é uma pasta.")
        if not (target / MARKER).is_file():
            raise EnvironmentError("Pasta já existente não pertence ao gerenciador. Nada será sobrescrito.")
        if not (target / "pyvenv.cfg").is_file():
            raise EnvironmentError("Pasta marcada mas virtualenv está incompleto; não alterar automaticamente.")
    return target


def clean_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE",
                 "PIP_TARGET", "PIP_PREFIX", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
        env.pop(name, None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def probe(path: Path, *, timeout=30) -> dict:
    """Verifica Python 3.13 e dependências do Qt/compilação, sem abrir interface."""
    if not path.is_file() or path.name.lower() != ("python.exe" if os.name == "nt" else "python"):
        raise EnvironmentError("python.exe dedicado não encontrado.")
    script = (
        "import json,sys,PySide6,PyInstaller,qtawesome; from importlib import metadata; "
        "from PySide6 import QtWidgets,QtTest; "
        "print(json.dumps({'python':list(sys.version_info[:2]),"
        "'venv':sys.prefix!=sys.base_prefix,"
        "'prefix':sys.prefix,"
        "'pyside6':PySide6.__version__,"
        "'pyinstaller':PyInstaller.__version__,"
        "'qtawesome':metadata.version('QtAwesome')}))"
    )
    try:
        proc = subprocess.run([str(path), "-B", "-c", script], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=timeout, env=clean_env())
    except (OSError, subprocess.TimeoutExpired) as e:
        raise EnvironmentError("Falha ao verificar ambiente Qt.") from e
    if proc.returncode != 0:
        raise EnvironmentError("Dependências não disponíveis: " + (proc.stderr or "erro no Python")[-350:])
    try:
        obj = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError, KeyError) as e:
        raise EnvironmentError("Resultado de verificação inválido.") from e
    if (obj.get("python") != [3, 13] or not obj.get("venv")
            or Path(obj.get("prefix", "")).resolve() != path.parent.parent.resolve()
            or obj.get("pyside6") != "6.11.2"
            or obj.get("pyinstaller") != "6.22.3"
            or obj.get("qtawesome") != "1.4.0"):
        raise EnvironmentError("Versão ou identidade do ambiente não confere.")
    return {"python": "3.13", "pyside6": obj["pyside6"],
            "pyinstaller": obj["pyinstaller"], "qtawesome": obj["qtawesome"]}


def prepare(*, home: Path | None = None, base_python: Path | None = None,
            runner=subprocess.run) -> dict:
    """Cria e valida ambiente exclusivo; jamais instala pacotes no Python-base.

    A instalação pip pode exigir Internet, tempo e espaço livre. Se houver falha,
    a configuração do painel continua apontando para o Python antigo.
    """
    target = destination(home)
    verify_destination(target, home)
    original = Path(base_python) if base_python is not None else Path(sys.executable)
    if not original.is_file():
        raise EnvironmentError("Interpretador Python 3.13 não encontrado.")
    if original.resolve() == interpreter(target).resolve():
        raise EnvironmentError("O Python-base não pode ser o próprio destino.")
    env = clean_env()
    # Inspeção da versão do Python-base antes de criar qualquer diretório.
    try:
        v = runner([str(original), "-B", "-c", "import sys; print('%d.%d'%sys.version_info[:2])"],
                   capture_output=True, text=True, timeout=20, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EnvironmentError("Falha ao verificar o Python de base.") from exc
    if v.returncode or v.stdout.strip() != "3.13":
        raise EnvironmentError("É necessário Python 3.13; nenhuma pasta foi criada.")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        _check_no_junction(target.parent)
        # Criação pelo Python-base. Nada é gravado no ambiente global.
        try:
            cr = runner([str(original), "-B", "-m", "venv", str(target)],
                        capture_output=True, text=True, timeout=150, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EnvironmentError("Falha ao criar ambiente virtual; verifique o diretório de QA.") from exc
        if cr.returncode or not (target / "pyvenv.cfg").is_file():
            raise EnvironmentError("Falha ao criar ambiente virtual. Nenhum pacote global instalado.")
        (target / MARKER).write_text(json.dumps({"component":"vighna-panel-qa",
            "schema":1, "python":"3.13", "packages":list(DEPENDENCIES)}, indent=2), encoding="utf8")
    py = interpreter(target)
    if not py.is_file():
        raise EnvironmentError("O Python virtual não está completo.")
    # Reaproveita ambiente íntegro, sem instalar de novo ou modificar o Python antigo.
    try:
        versions = probe(py)
    except EnvironmentError:
        try:
            install = runner([str(py), "-B", "-m", "pip", "install", "--no-input",
                              "--only-binary=:all:", "--disable-pip-version-check",
                              "--retries", "1", "--timeout", "15", *DEPENDENCIES],
                             capture_output=True, text=True, timeout=900, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EnvironmentError("Instalação das dependências falhou ou excedeu o tempo limite.") from exc
        if install.returncode:
            raise EnvironmentError("Falha ao instalar dependências no ambiente virtual. "
                                   + (install.stderr or install.stdout or "")[-550:])
        versions = probe(py)
    return {"status":"PREPARADO", "interpreter":str(py), "packages":versions,
            "painel_alterado":False, "vighnastudy_alterado":False}


def main(argv=None) -> int:
    args = argparse.ArgumentParser()
    args.add_argument("--prepare", action="store_true")
    ns = args.parse_args(argv)
    if not ns.prepare:
        return 2
    try:
        r = prepare()
        print("AMBIENTE_QT_PREPARADO=" + json.dumps(r, ensure_ascii=False), flush=True)
        return 0
    except EnvironmentError as exc:
        print("AMBIENTE_QT_FALHOU: " + str(exc), file=sys.stderr, flush=True)
        return 1


# G5-B: a execução real ocorre SOMENTE dentro de Windows Sandbox, após clique explícito.
# Todas as fontes provêm dos ZIPs SHA-256 auditados do kit, nunca da instalação pessoal.

G5B_TARGET_BUILD = 'structural-m2-int1-settings-r1d-rc2'
G5B_TIMEOUT_BUILD = 1200
G5B_TIMEOUT_SANDBOX = 540

class G5BSafetyError(ValueError):
    pass


def g5b_folder(root=None, run_id=None):
    from datetime import datetime
    base = Path(root) if root is not None else Path.home() / 'VighnaLab' / 'G5B_Laboratorios'
    stamp = run_id or datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return base / ('G5B_' + stamp)


def g5b_check_root(lab: Path, *, base: Path | None = None):
    if base is None:
        base = Path.home() / 'VighnaLab' / 'G5B_Laboratorios'
    base = Path(base)
    lab = Path(lab)
    if lab.parent != base or not lab.name.startswith('G5B_'):
        raise G5BSafetyError('Destino de laboratório não permitido.')
    for candidate in (base.parent, base, lab):
        if candidate.exists() and (candidate.is_symlink() or
                                   (hasattr(candidate,'is_junction') and candidate.is_junction())):
            raise G5BSafetyError('Junction ou link simbólico detectado no laboratório.')
        if (candidate / 'estudos.db').exists() or (candidate / 'VighnaStudy.exe').exists():
            raise G5BSafetyError('Banco ou EXE externo detectado junto ao laboratório.')
    if lab.exists():
        raise G5BSafetyError('Laboratório já existe. Não sobrescrever.')
    return lab


def g5b_sandbox_configuration(input_folder: Path, output_folder: Path) -> str:
    """ÚNICAS duas pastas do host visíveis: fonte somente-leitura; resultado descartável."""
    from xml.etree import ElementTree as ET
    c = ET.Element('Configuration')
    for name,value in [
        ('vGPU','Disable'),('Networking','Disable'),
        ('ClipboardRedirection','Disable'),('PrinterRedirection','Disable'),
        ('AudioInput','Disable'),('VideoInput','Disable')]:
        ET.SubElement(c,name).text=value
    mappings=ET.SubElement(c,'MappedFolders')
    for folder,guest,readonly in ((input_folder, r'C:\VighnaQA\Entrada', 'true'),
                                  (output_folder, r'C:\VighnaQA\Saida', 'false')):
        m=ET.SubElement(mappings,'MappedFolder')
        ET.SubElement(m,'HostFolder').text=str(folder)
        ET.SubElement(m,'SandboxFolder').text=guest
        ET.SubElement(m,'ReadOnly').text=readonly
    command=ET.SubElement(c,'LogonCommand')
    ET.SubElement(command,'Command').text=(
        r'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass '
        r'-File C:\VighnaQA\Entrada\G5B_EXECUTAR_NO_SANDBOX.ps1')
    ET.indent(c,space='  ')
    return '<?xml version="1.0" encoding="utf-8"?>\n'+ET.tostring(c,encoding='unicode')+'\n'


G5B_SANDBOX_PS = r'''# G5-B / VighnaStudy RC2 — SOMENTE DENTRO DO WINDOWS SANDBOX
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$source = 'C:\VighnaQA\Entrada\VighnaStudy'
$output = 'C:\VighnaQA\Saida'
$folder = 'C:\VighnaQA\Execucao\VighnaStudy'
$exe = Join-Path $folder 'VighnaStudy.exe'
$report = [ordered]@{
  component='vighna-g5b-sandbox'; alvo='structural-m2-int1-settings-r1d-rc2'
  status='BLOQUEADO'; processo_iniciado=$false; janela_detectada=$false
  estabilidade=$false; codigo_saida=$null; titulo_janela=''
  duracao_segundos=0; motivo='Não iniciado'; instalacao_autorizada=$false
}
$p = $null
$started = Get-Date
try {
  if (!(Test-Path -LiteralPath (Join-Path $source 'VighnaStudy.exe') -PathType Leaf)) {throw 'EXE ausente na entrada somente leitura'}
  if (!(Test-Path -LiteralPath $output -PathType Container)) {throw 'Diretório de evidências não está montado'}
  New-Item -ItemType Directory -Path $folder -Force | Out-Null
  # Executável e DLLs rodam no disco DESCARTÁVEL do guest, nunca no diretório mapeado host.
  Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $folder -Recurse -Force -ErrorAction Stop
  $qaProfile = 'C:\VighnaQA\Perfil_Sintetico'
  foreach ($d in @('Home','AppData\Roaming','AppData\Local','Temp')) {
    New-Item -ItemType Directory -Path (Join-Path $qaProfile $d) -Force | Out-Null
  }
  $env:USERPROFILE = Join-Path $qaProfile 'Home'
  $env:APPDATA = Join-Path $qaProfile 'AppData\Roaming'
  $env:LOCALAPPDATA = Join-Path $qaProfile 'AppData\Local'
  $env:TEMP = Join-Path $qaProfile 'Temp'
  $env:TMP = $env:TEMP
  $env:QT_QPA_PLATFORM = 'windows'
  $env:PYTHONPATH = ''
  $env:QT_PLUGIN_PATH = ''
  $p = Start-Process -FilePath $exe -WorkingDirectory $folder -PassThru -ErrorAction Stop
  $report.processo_iniciado = $true
  $window = $false
  $alive = $false
  for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Milliseconds 500
    $check = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
    if (!$check) {break}
    $alive = $true
    if ($check.MainWindowHandle -ne 0) {
      $window = $true
      $report.titulo_janela = [string]$check.MainWindowTitle
      break
    }
  }
  $report.janela_detectada = $window
  if ($window) {
    Start-Sleep -Seconds 8
    $check = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
    $alive = ($null -ne $check)
    $report.estabilidade = $alive
  }
  $report.duracao_segundos = [math]::Round(((Get-Date) - $started).TotalSeconds, 1)
  if ($window -and $alive) {
    $report.status = 'PASSOU_G5B'
    $report.motivo = 'Janela detectada e processo permaneceu ativo 8 segundos.'
  } elseif (!$window) {
    $report.status = 'FALHOU'
    $report.motivo = 'Não foi possível detectar janela principal ativa em até 60 segundos.'
  } else {
    $report.status = 'FALHOU'
    $report.motivo = 'Processo encerrou prematuramente.'
  }
} catch {
  $report.status = 'BLOQUEADO'
  $report.motivo = ('Erro no guest: ' + $_.Exception.GetType().Name)
} finally {
  if ($null -ne $p) {
    try { $c = Get-Process -Id $p.Id -ErrorAction SilentlyContinue; if ($c) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } } catch {}
    try { $report.codigo_saida = $p.ExitCode } catch {}
  }
  try {
    $json = $report | ConvertTo-Json -Depth 3
    [System.IO.File]::WriteAllText((Join-Path $output 'RESULTADO_G5B.json'), $json, [System.Text.Encoding]::UTF8)
  } catch {}
  # Encerramento do guest: todos os dados de execução são descartados.
  Start-Sleep -Seconds 2
  shutdown.exe /s /t 0 | Out-Null
}
'''


def g5b_validate_guest_report(data: bytes) -> dict:
    import json
    if len(data)>30_000:
        raise G5BSafetyError('Relatório guest excede limite.')
    try:
        report=json.loads(data.decode('utf-8-sig'))
    except (UnicodeError,ValueError) as exc:
        raise G5BSafetyError('Relatório guest inválido.') from exc
    if (not isinstance(report,dict) or report.get('component')!='vighna-g5b-sandbox'
            or report.get('alvo')!=G5B_TARGET_BUILD or report.get('instalacao_autorizada') is not False):
        raise G5BSafetyError('Identidade do relatório guest inválida.')
    if report.get('status') not in ('PASSOU_G5B','BLOQUEADO','FALHOU'):
        raise G5BSafetyError('Status guest desconhecido.')
    if report['status']=='PASSOU_G5B' and not (
            report.get('processo_iniciado') is True and report.get('janela_detectada') is True
            and report.get('estabilidade') is True):
        raise G5BSafetyError('Aprovação guest contradiz verificações.')
    return report


def g5b_make_evidence(summary: dict, destination: Path, logs: dict[str,bytes]) -> None:
    import hashlib, json, zipfile
    records={'RESUMO_G5B.json':json.dumps(summary,indent=2,ensure_ascii=False).encode('utf-8')}
    records.update({name:data[:250000] for name,data in logs.items()})
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in records.items()}
    records['MANIFESTO_SHA256.json']=json.dumps(hashes,indent=2).encode('utf-8')
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in records.items():z.writestr(name,data)
    with zipfile.ZipFile(destination) as z:
        if z.testzip(): raise G5BSafetyError('Evidência corrompida.')
        for key,digest in hashes.items():
            if hashlib.sha256(z.read(key)).hexdigest()!=digest:
                raise G5BSafetyError('Hash do relatório divergente.')


def g5b_run():
    """Executa somente mediante confirmação explícita na UI; recusa plataformas não Windows."""
    import hashlib
    from datetime import datetime
    import time
    import zipfile
    import shutil
    import tempfile
    import sys
    import os
    import subprocess
    import json
    if sys.platform != 'win32':
        raise G5BSafetyError('G5-B exige Windows Sandbox; não pode executar EXE neste sistema.')
    import homologador_windows as h
    from painel_g5_preflight import run_g5_a
    g5a=run_g5_a()
    if g5a.get('status')!='DIAGNOSTICO_APROVADO':
        raise G5BSafetyError('G5-A falhou. G5-B bloqueado.')
    # Arquivos do kit protegidos pelo manifesto original, NÃO da instalação principal.
    pre=h.preflight_selftest()
    base=h.checked_archive(h.KIT/'insumos'/h.BASE)
    rc2=h.checked_archive(h.KIT/'insumos'/h.RC2,prefix='codigo/')
    if rc2.get('VighnaStudy.spec') is None or base.get('VighnaStudy.spec') is None:
        raise G5BSafetyError('Spec original ausente.')
    if not h.inspect_static(base,h.checked_archive(h.KIT/'insumos'/h.PATCH),rc2):
        raise G5BSafetyError('Contrato RC2 inválido.')
    rc2['VighnaStudy.spec']=base['VighnaStudy.spec']
    if Path.home().is_symlink():
        raise G5BSafetyError('Perfil com link simbólico; teste bloqueado.')
    lab=g5b_folder()
    g5b_check_root(lab)
    sandbox_exe=Path(os.environ.get('WINDIR',r'C:\Windows'))/'System32'/'WindowsSandbox.exe'
    if not sandbox_exe.is_file():
        raise G5BSafetyError('WindowsSandbox.exe ausente. Ative Área Restrita do Windows.')
    lab.mkdir(parents=True)
    code=lab/'CODIGO_QA'
    inp=lab/'ENTRADA_SOMENTE_LEITURA'
    out=lab/'SAIDA_SINTETICA'
    dist=lab/'DIST'
    inp.mkdir();out.mkdir()
    h.write_sources(rc2,code)
    rfile=lab/'log_pyinstaller.txt'
    result={'component':'vighna-g5b-host','alvo':G5B_TARGET_BUILD,
            'status':'BLOQUEADO','g5_aprovado':False,'instalacao_autorizada':False,
            'g5c_pendente':True,'sandbox_rede':'Disable','sandbox_clipboard':'Disable',
            'g5a_status':g5a['status'],'spec_r1d_sha256':h.digest(base['VighnaStudy.spec']),
            'preflight':pre['status'],'versao_painel':'3.1.3'}
    # Nome do ZIP deve ser composto como string antes da união com Path.
    # Em Windows, Path + str gera TypeError antes de iniciar o Sandbox.
    zipfile_output = lab / ('G5_B_DIAGNOSTICO_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.zip')
    safe_log={}
    try:
        print('ETAPA_G5B: Preparando compilação isolada; isso pode levar alguns minutos.',flush=True)
        env=h.environment_qa(lab)
        for n in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
            env.pop(n,None)
        args=[sys.executable,'-B','-m','PyInstaller','--noconfirm','--distpath',str(dist),
              '--workpath',str(lab/'BUILD'),'VighnaStudy.spec']
        with rfile.open('wb') as stream:
            process=subprocess.Popen(args,cwd=code,env=env,stdout=stream,stderr=subprocess.STDOUT)
            started=time.monotonic()
            while process.poll() is None and time.monotonic()-started < G5B_TIMEOUT_BUILD:
                time.sleep(2)
                elapsed=int(time.monotonic()-started)
                if elapsed>0 and elapsed%20<2:
                    print(f'ETAPA_G5B: Compilação ainda em andamento ({elapsed}s).',flush=True)
            if process.poll() is None:
                process.kill();process.wait(timeout=15)
                raise G5BSafetyError('PyInstaller excedeu tempo máximo de 20 minutos.')
            if process.returncode != 0:
                raise G5BSafetyError('Compilação QA falhou; verificar log sem iniciar Sandbox.')
        built=dist/'VighnaStudy'/'VighnaStudy.exe'
        if not built.is_file():
            raise G5BSafetyError('Executável ausente no build concluído.')
        exe_hash=h.digest_file(built)
        result['exe_sha256']=exe_hash
        result['exe_bytes']=built.stat().st_size
        folder=dist/'VighnaStudy'
        if sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())>750_000_000:
            raise G5BSafetyError('Build excede limite de 750MB.')
        # Copiar apenas o resultado do PyInstaller, sem dados locais ou do usuário.
        shutil.copytree(folder,inp/'VighnaStudy',symlinks=False)
        (inp/'G5B_EXECUTAR_NO_SANDBOX.ps1').write_text(G5B_SANDBOX_PS,encoding='utf-8')
        config=lab/'G5B_LABORATORIO.wsb'
        config.write_text(g5b_sandbox_configuration(inp,out),encoding='utf-8')
        print('ETAPA_G5B: Iniciando Sandbox com rede e clipboard desativados.',flush=True)
        proc=subprocess.Popen([str(sandbox_exe),str(config)],cwd=lab)
        start=time.monotonic();guest_file=out/'RESULTADO_G5B.json'
        while time.monotonic()-start<G5B_TIMEOUT_SANDBOX:
            if guest_file.is_file():
                report=g5b_validate_guest_report(guest_file.read_bytes())
                result['guest']=report
                result['status']=report['status']
                print('ETAPA_G5B: Resultado recebido do Windows Sandbox: '+result['status'],flush=True)
                break
            if proc.poll() is not None:
                raise G5BSafetyError('Windows Sandbox encerrou sem gerar relatório guest.')
            time.sleep(2)
            if int(time.monotonic()-start)%30<2:
                print('ETAPA_G5B: Aguardando relatório do Sandbox.',flush=True)
        else:
            raise G5BSafetyError('Sandbox não respondeu dentro de 9 minutos; feche-o manualmente.')
        # Guest inicia fechamento. Não interromper guest antes de transferir relatório.
    except Exception as exc:
        result['status']='BLOQUEADO'
        result['motivo']=str(exc)[:350]
        print('ETAPA_G5B: BLOQUEADO — '+result['motivo'],flush=True)
    finally:
        # Não arquiva código, EXE nem perfis: apenas logs curtos e indicadores QA.
        if rfile.is_file(): safe_log['PYINSTALLER_LOG_FINAL.txt']=rfile.read_bytes()[-180000:]
        if (out/'RESULTADO_G5B.json').is_file():
            safe_log['RESULTADO_GUEST.json']=(out/'RESULTADO_G5B.json').read_bytes()[:30000]
        g5b_make_evidence(result,zipfile_output,safe_log)
        print('ZIP DE DIAGNOSTICO CRIADO: '+str(zipfile_output),flush=True)
        print('STATUS: G5-B '+result['status']+'; G5-C PENDENTE; INSTALACAO NAO AUTORIZADA.',flush=True)
        # Apaga as fontes/compilação host somente se o guest terminou; caso contrário
        # preserva a pasta para não remover arquivos ainda mapeados no Sandbox.
    return 0 if result['status']=='PASSOU_G5B' else 1

# G5-C: verificações do executável REAL em Windows Sandbox descartável.
# Nunca acessar instalação/banco pessoal nem considerar G5 automaticamente liberado.
G5C_TIMEOUT_SANDBOX = 780

G5C_SANDBOX_PS = r'''# G5-C V3.1.9: janela por PID, foco comprovado, diagnóstico de sessão e UIA conservadora.
# Executar EXCLUSIVAMENTE como LogonCommand do Windows Sandbox offline.
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$source='C:\VighnaQA\Entrada\VighnaStudy'
$output='C:\VighnaQA\Saida'
$folder='C:\VighnaQA\Execucao\VighnaStudy'
$exe=Join-Path $folder 'VighnaStudy.exe'
$database=Join-Path $folder 'estudos.db'
$report=[ordered]@{
  component='vighna-g5c-sandbox'; alvo='structural-m2-int1-settings-r1d-rc2';
  status='BLOQUEADO'; instalacao_autorizada=$false; banco_sintetico=$true;
  rede='Disable'; clipboard='Disable'; execucoes=@();
  dashboard_verificado=$false; dashboard_evidencia='PENDENTE';
  navegacao_configuracoes='PENDENTE'; config_janela_titulo='';
  captura_inicio=$false; captura_dashboard=$false; captura_configuracoes=$false;
  retorno_dashboard='PENDENTE'; captura_retorno_dashboard=$false;
  transicao_tela_detectada=$false; navegacao_automatica='INCONCLUSIVA';
  encerramento_controlado=$false; reinicializacao=$false;
  banco_criado=$false; banco_cabecalho_ok=$false; banco_sha256='';
  captura_criada=$false; captura_metodos=@{}; captura_erros=@{}; motivo='Ainda não iniciado';
  sandbox_desligamento_automatico=$false; janela_qa_verificada=$false;
  sessao_grafica=@{}; janela_qa_eventos=@(); foco_eventos=@(); uia_eventos=@()
}
$jobs=@()
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class VighnaQAWin {
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int cmd);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rectangle);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
 [DllImport("user32.dll")] public static extern void mouse_event(int flags,int dx,int dy,int data,int info);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr param);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd,StringBuilder text,int count);
 [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr hWnd,out int pid);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
 [DllImport("user32.dll", SetLastError=true)] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
 public delegate bool EnumProc(IntPtr hWnd,IntPtr p);
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int Left,Top,Right,Bottom;}
 public static IntPtr WindowFor(int pid, bool settings) {
   IntPtr result=IntPtr.Zero;
   EnumProc fn=(hw,p)=> {
     int found=0;GetWindowThreadProcessId(hw,out found);
     if(found==pid && IsWindowVisible(hw)) {
       var t=new StringBuilder(300); GetWindowText(hw,t,300);
       if(t.Length>0) {
         bool isSettings=t.ToString().StartsWith("Configurações",StringComparison.OrdinalIgnoreCase) || t.ToString().StartsWith("Configuracoes",StringComparison.OrdinalIgnoreCase);
         if((settings && isSettings) || (!settings && !isSettings)) {result=hw;return false;}
       }
     }
     return true;
   };
   EnumWindows(fn,IntPtr.Zero);return result;
 }
 public static string[] TitlesFor(int pid) {
   var result=new System.Collections.Generic.List<string>();
   EnumProc fn=(hw,p)=> { int found=0;GetWindowThreadProcessId(hw,out found);
     if(found==pid && IsWindowVisible(hw)) {var t=new StringBuilder(300);GetWindowText(hw,t,300);
       if(t.Length>0) result.Add(t.ToString());}return true;};
   EnumWindows(fn,IntPtr.Zero); return result.ToArray();
 }
}
'@
function Start-QAProcess {
  $proc=Start-Process -FilePath $exe -WorkingDirectory $folder -PassThru -ErrorAction Stop
  $script:jobs += $proc
  $hasWindow=$false;$title=''
  for($i=0;$i -lt 150;$i++) {
    Start-Sleep -Milliseconds 500
    $current=Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if($null -eq $current) {break}
    if($current.MainWindowHandle -ne 0) {$hasWindow=$true;$title=[string]$current.MainWindowTitle;break}
  }
  return @{proc=$proc;hasWindow=$hasWindow;title=$title}
}
function Stop-QAProcess ($proc) {
  if($null -eq $proc) {return $false}
  $current=Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
  if($null -eq $current) {return $false}
  $closed=$false
  try {$null=$current.CloseMainWindow()} catch {}
  for($i=0;$i -lt 24;$i++) {
    Start-Sleep -Milliseconds 500
    if($null -eq (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue)) {$closed=$true;break}
  }
  if(!$closed) {try {Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue} catch {}}
  return $closed
}
function QAGetVerifiedWindow($processId,[bool]$settings=$false) {
  $hw=[VighnaQAWin]::WindowFor([int]$processId,[bool]$settings)
  if($hw -eq [IntPtr]::Zero) {return [IntPtr]::Zero}
  $owner=0
  $null=[VighnaQAWin]::GetWindowThreadProcessId($hw,[ref]$owner)
  if($owner -ne [int]$processId -or ![VighnaQAWin]::IsWindowVisible($hw)) {return [IntPtr]::Zero}
  return $hw
}
function QAGetForegroundPid {
  $hw=[VighnaQAWin]::GetForegroundWindow()
  if($hw -eq [IntPtr]::Zero) {return -1}
  $owner=0
  $null=[VighnaQAWin]::GetWindowThreadProcessId($hw,[ref]$owner)
  return [int]$owner
}
function QARecordSession($processId) {
  $screens=0;$interactive=$false;$hostSession=-1;$qaSession=-1
  try {$screens=[System.Windows.Forms.Screen]::AllScreens.Count} catch {}
  try {$interactive=[Environment]::UserInteractive} catch {}
  try {$hostSession=[System.Diagnostics.Process]::GetCurrentProcess().SessionId} catch {}
  try {$qaSession=[System.Diagnostics.Process]::GetProcessById([int]$processId).SessionId} catch {}
  $foreground=QAGetForegroundPid
  $report.sessao_grafica=@{ host_session=$hostSession; qa_session=$qaSession;
    sessao_igual=($hostSession -ge 0 -and $hostSession -eq $qaSession);
    user_interactive=$interactive; monitores=$screens; foreground_pid=$foreground;
    foreground_qa=($foreground -eq [int]$processId) }
  $report.janela_qa_verificada=((QAGetVerifiedWindow $processId) -ne [IntPtr]::Zero)
  $report.janela_qa_eventos += @{etapa='identificacao'; janela_qa=$report.janela_qa_verificada;
    titulos=@([VighnaQAWin]::TitlesFor([int]$processId)) }
  return $report.janela_qa_verificada
}
function QAEnsureFocus($processId,$step) {
  $preferSettings=($step -eq 'fechar_configuracoes')
  $hw=QAGetVerifiedWindow $processId $preferSettings
  if($hw -eq [IntPtr]::Zero) {
    $report.foco_eventos += @{etapa=$step;resultado='SEM_JANELA_DO_PID';foreground_pid=(QAGetForegroundPid)}
    return $false
  }
  for($attempt=1;$attempt -le 3;$attempt++) {
    $null=[VighnaQAWin]::ShowWindow($hw,9) # SW_RESTORE, não altera instalação.
    $requested=[VighnaQAWin]::SetForegroundWindow($hw)
    Start-Sleep -Milliseconds (250*$attempt)
    $observed=QAGetForegroundPid
    $report.foco_eventos += @{etapa=$step;tentativa=$attempt;ativacao_retorno=[bool]$requested;
      foreground_pid=$observed;resultado=$(if($observed -eq [int]$processId){'CONFIRMADO'}else{'NEGADO'})}
    if($observed -eq [int]$processId) {return $true}
  }
  return $false
}
function QAInvokeOwnedButton($processId,$pattern,$step) {
  # UIA InvokePattern no HWND verificado pelo PID; não envia teclas globais.
  $hw=QAGetVerifiedWindow $processId
  if($hw -eq [IntPtr]::Zero) {return $false}
  try {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    $root=[System.Windows.Automation.AutomationElement]::FromHandle($hw)
    $all=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
    for($i=0;$i -lt [Math]::Min($all.Count,1200);$i++) {
      $el=$all.Item($i)
      if($el.Current.ProcessId -ne [int]$processId) {continue}
      if($el.Current.ControlType.ProgrammaticName -ne 'ControlType.Button') {continue}
      if($el.Current.Name -notmatch $pattern) {continue}
      $invoke=$null
      if($el.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern,[ref]$invoke)) {
        $invoke.Invoke()
        $report.uia_eventos += @{etapa=$step;acao='InvokePattern';nome=$el.Current.Name;resultado='ENVIADO_AO_PID'}
        return $true
      }
    }
    $report.uia_eventos += @{etapa=$step;resultado='SEM_CONTROLE_INVOCAVEL'}
  } catch {$report.uia_eventos += @{etapa=$step;resultado='ERRO_UIA';erro=([string]$_.Exception.Message).Substring(0,[Math]::Min(180,([string]$_.Exception.Message).Length))}}
  return $false
}
function Save-QACapture($filename) {
  # Falha na API grafica do Sandbox nao deve interromper reinicializacao nem SQLite.
  # SOMENTE dentro do guest; PrintWindow como alternativa, nunca imagem do host.
  $lastError=''
  for($attempt=1;$attempt -le 3;$attempt++) {
    $bmp=$null;$graphics=$null
    try {
      if((QAGetForegroundPid) -ne [int]$script:qaProcessId) {
        throw 'CopyFromScreen bloqueado: o foco não pertence ao EXE QA.'
      }
      $bounds=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
      if($bounds.Width -lt 320 -or $bounds.Height -lt 240 -or
         $bounds.Width -gt 7680 -or $bounds.Height -gt 4320) {
        throw 'Resolução do Sandbox não utilizável para captura.'
      }
      $bmp=New-Object System.Drawing.Bitmap($bounds.Width,$bounds.Height)
      $graphics=[System.Drawing.Graphics]::FromImage($bmp)
      $graphics.CopyFromScreen($bounds.Location,[System.Drawing.Point]::Empty,$bounds.Size)
      $bmp.Save((Join-Path $output $filename),[System.Drawing.Imaging.ImageFormat]::Png)
      $report.captura_metodos[$filename]='CopyFromScreen tentativa '+$attempt
      return $true
    } catch {
      $lastError=[string]$_.Exception.Message
      Start-Sleep -Milliseconds (350 * $attempt)
    } finally {
      if($null -ne $graphics) {$graphics.Dispose()}
      if($null -ne $bmp) {$bmp.Dispose()}
    }
  }
  # Alternativa restrita: copiar pixels APENAS da janela do processo QA no guest.
  # PrintWindow pode falhar em Qt; sem evidência, sempre manter status PARCIAL.
  $bmp=$null;$graphics=$null;$hdc=[IntPtr]::Zero
  try {
    $preferSettings=($filename -like '*CONFIGURACOES*')
    $hw=QAGetVerifiedWindow $script:qaProcessId $preferSettings
    if($hw -eq [IntPtr]::Zero) {throw 'Janela visível do EXE QA não identificada pelo PID.'}
    $pidOwned=0
    $null=[VighnaQAWin]::GetWindowThreadProcessId($hw,[ref]$pidOwned)
    if($pidOwned -ne [int]$script:qaProcessId) {throw 'PrintWindow bloqueado: HWND não pertence ao EXE QA.'}
    $rect=New-Object VighnaQAWin+RECT
    if(![VighnaQAWin]::GetWindowRect($hw,[ref]$rect)) {
      throw 'Não foi possível obter o retângulo da janela.'
    }
    $w=$rect.Right-$rect.Left;$h=$rect.Bottom-$rect.Top
    if($w -lt 200 -or $h -lt 120 -or $w -gt 7680 -or $h -gt 4320) {
      throw 'Dimensões da janela QA inválidas.'
    }
    $bmp=New-Object System.Drawing.Bitmap($w,$h)
    $graphics=[System.Drawing.Graphics]::FromImage($bmp)
    $hdc=$graphics.GetHdc()
    $ok=[VighnaQAWin]::PrintWindow($hw,$hdc,[uint32]2)
    $graphics.ReleaseHdc($hdc);$hdc=[IntPtr]::Zero
    if(!$ok) {throw 'PrintWindow retornou false.'}
    # Recusa tela quase uniforme ou sem informação visual.
    $samples=0;$distinct=[System.Collections.Generic.HashSet[int]]::new()
    for($y=5;$y -lt $h-5;$y += [Math]::Max(1,[int]($h/9))) {
      for($x=5;$x -lt $w-5;$x += [Math]::Max(1,[int]($w/9))) {
        $null=$distinct.Add($bmp.GetPixel($x,$y).ToArgb());$samples++
      }
    }
    if($samples -lt 40 -or $distinct.Count -lt 6) {throw 'PrintWindow sem conteúdo visual confiável.'}
    $bmp.Save((Join-Path $output $filename),[System.Drawing.Imaging.ImageFormat]::Png)
    $report.captura_metodos[$filename]='PrintWindow janela QA'
    return $true
  } catch {
    $report.captura_erros[$filename]=($lastError+' | '+[string]$_.Exception.Message).Substring(0,[Math]::Min(450,($lastError+' | '+[string]$_.Exception.Message).Length))
    return $false
  } finally {
    if($null -ne $graphics) {
      if($hdc -ne [IntPtr]::Zero) {$graphics.ReleaseHdc($hdc)}
      $graphics.Dispose()
    }
    if($null -ne $bmp) {$bmp.Dispose()}
  }
}
function QACaptureDifference($one,$two) {
  # Evidência auxiliar; nunca aprova a identidade da tela sozinha.
  if(!(Test-Path $one) -or !(Test-Path $two)) {return $false}
  $a=$null;$b=$null
  try {
    $a=[System.Drawing.Bitmap]::FromFile($one)
    $b=[System.Drawing.Bitmap]::FromFile($two)
    if($a.Width -ne $b.Width -or $a.Height -ne $b.Height) {return $false}
    $count=0;$diff=0
    for($y=45;$y -lt $a.Height-30;$y+=24) {
      for($x=24;$x -lt $a.Width-24;$x+=24) {
        $c=$a.GetPixel($x,$y);$d=$b.GetPixel($x,$y);$count++
        if([math]::Abs([int]$c.R-[int]$d.R)+[math]::Abs([int]$c.G-[int]$d.G)+[math]::Abs([int]$c.B-[int]$d.B) -gt 80) {$diff++}
      }
    }
    return ($count -gt 100 -and ($diff/$count) -ge 0.10)
  } catch {
    $report.captura_erros['comparacao']=[string]$_.Exception.Message
    return $false
  } finally {
    if($null -ne $a) {$a.Dispose()}
    if($null -ne $b) {$b.Dispose()}
  }
}
function QAAssertGuestForeground($processId) {
  $hw=[VighnaQAWin]::GetForegroundWindow()
  if($hw -eq [IntPtr]::Zero) {throw 'Não há janela de QA em primeiro plano.'}
  $foregroundPid=0
  $null=[VighnaQAWin]::GetWindowThreadProcessId($hw,[ref]$foregroundPid)
  if($foregroundPid -ne [int]$processId) {throw 'O foco não pertence ao executável QA: teclas bloqueadas.'}
}
function QAGetConfigTitle($processId) {
  foreach($title in [VighnaQAWin]::TitlesFor([int]$processId)) {
    if($title -match '(?i)^Configurações\s*[—-]\s*VighnaStudy') {return $title}
  }
  return ''
}
try {
  if(!(Test-Path -LiteralPath (Join-Path $source 'VighnaStudy.exe') -PathType Leaf)) {throw 'EXE QA ausente.'}
  if(!(Test-Path -LiteralPath $output -PathType Container)) {throw 'Montagem de evidências ausente.'}
  New-Item -ItemType Directory -Path $folder -Force | Out-Null
  Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $folder -Recurse -Force -ErrorAction Stop
  if(!(Test-Path -LiteralPath $exe -PathType Leaf)) {throw 'Cópia local de EXE ausente.'}
  $qaProfile='C:\VighnaQA\Perfil_Sintetico'
  foreach($d in @('Home','AppData\Roaming','AppData\Local','Temp')) {
    New-Item -ItemType Directory -Path (Join-Path $qaProfile $d) -Force | Out-Null
  }
  $env:USERPROFILE=Join-Path $qaProfile 'Home'
  $env:APPDATA=Join-Path $qaProfile 'AppData\Roaming'
  $env:LOCALAPPDATA=Join-Path $qaProfile 'AppData\Local'
  $env:TEMP=Join-Path $qaProfile 'Temp';$env:TMP=$env:TEMP
  $env:QT_QPA_PLATFORM='windows';$env:PYTHONPATH='';$env:QT_PLUGIN_PATH=''
  $first=Start-QAProcess
  $report.execucoes += @{fase='primeira';processo_iniciado=$true;janela_detectada=$first.hasWindow;titulo=$first.title}
  if(!$first.hasWindow) {throw 'Primeira inicialização sem janela.'}
  Start-Sleep -Seconds 4
  $current=Get-Process -Id $first.proc.Id -ErrorAction Stop
  $script:qaProcessId=[int]$first.proc.Id
  $null=QARecordSession $first.proc.Id
  $null=QAEnsureFocus $first.proc.Id 'captura_inicio'
  Start-Sleep -Milliseconds 600
  $report.captura_inicio=[bool](Save-QACapture 'CAPTURA_G5C_INICIO.png')
  # Uma captura indisponível não impede o atalho nem os testes independentes.
  # Falha de foco NÃO pode provocar envio de teclas para outro processo.
  try {
    if(!(QAEnsureFocus $first.proc.Id 'atalho_dashboard')) {
      $report.navegacao_automatica='FOCO_INDISPONIVEL_DASHBOARD'
      if(!(QAInvokeOwnedButton $first.proc.Id '(?i)dashboard de estudos' 'dashboard_uia')) {
        throw 'Foco indisponível e UIAutomation sem botão Dashboard do processo QA.'
      }
      $report.navegacao_automatica='DASHBOARD_VIA_UIA'
    } else {
      QAAssertGuestForeground $first.proc.Id
      [System.Windows.Forms.SendKeys]::SendWait('^h')
      $report.navegacao_automatica='DASHBOARD_VIA_ATALHO_COM_FOCO'
    }
    Start-Sleep -Seconds 5
    $report.captura_dashboard=[bool](Save-QACapture 'CAPTURA_G5C_DASHBOARD.png')
    $report.transicao_tela_detectada=[bool](QACaptureDifference (Join-Path $output 'CAPTURA_G5C_INICIO.png') (Join-Path $output 'CAPTURA_G5C_DASHBOARD.png'))
    if($report.transicao_tela_detectada) {$report.dashboard_evidencia='CAPTURA_TRANSICAO_AUDITORIA'}
  } catch {
    $report.navegacao_automatica='DASHBOARD_NAO_ACESSIVEL_SEM_FOCO'
    $report.captura_erros['navegacao_dashboard']=[string]$_.Exception.Message
  }
  # Não confundir texto "Dashboard de Estudos" no portal com a tela do Dashboard.
  # Somente elementos específicos da tela de destino podem confirmar automaticamente.
  try {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    $rootUI=[System.Windows.Automation.AutomationElement]::FromHandle($current.MainWindowHandle)
    $all=$rootUI.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
    $labels=@()
    for($i=0;$i -lt [Math]::Min($all.Count,1800);$i++) {$labels += [string]$all.Item($i).Current.Name}
    $joined=($labels -join ' | ')
    if(($joined -match '(?i)tempo efetivo|ritmo de estudo') -and
       ($joined -match '(?i)recomendações|meta semanal|disciplinas') -and
       ($joined -notmatch 'Escolha para onde deseja ir')) {
      $report.dashboard_verificado=$true
      $report.dashboard_evidencia='COMPROVADO_POR_IDENTIFICADORES'
    }
  } catch {} # Se UIA Qt não apresentar labels, permanece pendente.
  # A busca global só recebe teclas com foco no PID de QA efetivamente comprovado.
  # UIAutomation é alternativa independente do foco, com InvokePattern no controle do mesmo PID.
  try {
    $hw=QAGetVerifiedWindow $first.proc.Id
    if($hw -eq [IntPtr]::Zero) {throw 'Janela QA não encontrada por PID.'}
    $title=''
    if(QAEnsureFocus $first.proc.Id 'busca_configuracoes') {
      QAAssertGuestForeground $first.proc.Id
      [System.Windows.Forms.SendKeys]::SendWait('^k')
      Start-Sleep -Milliseconds 1000
      $titles=[VighnaQAWin]::TitlesFor([int]$first.proc.Id)
      if($titles -contains 'Buscar no Vighna') {
        $report.navegacao_automatica='BUSCA_GLOBAL_ABERTA'
        QAAssertGuestForeground $first.proc.Id
        [System.Windows.Forms.SendKeys]::SendWait('configuracoes')
        Start-Sleep -Milliseconds 900
        QAAssertGuestForeground $first.proc.Id
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
        $report.navegacao_automatica='BUSCA_GLOBAL_COMANDO_ENVIADO'
      } else {$report.navegacao_automatica='BUSCA_GLOBAL_NAO_CONFIRMADA'}
      Start-Sleep -Seconds 2
      $title=QAGetConfigTitle $first.proc.Id
    } else {$report.navegacao_automatica='FOCO_INDISPONIVEL_BUSCA_BLOQUEADA'}
    if(!$title) {
      if(QAInvokeOwnedButton $first.proc.Id '(?i)^configura(c|ç)(o|õ)es$' 'configuracoes_uia') {
        $report.navegacao_automatica='UIA_INVOKE_CONFIGURACOES'
        Start-Sleep -Seconds 2
        $title=QAGetConfigTitle $first.proc.Id
      } else { $report.uia_eventos += @{etapa='configuracoes_uia';resultado='NAO_CONFIRMADO'} }
    }
    if($title) {
      $report.config_janela_titulo=$title
      $report.navegacao_configuracoes='CONFIRMADA'
      $report.captura_configuracoes=[bool](Save-QACapture 'CAPTURA_G5C_CONFIGURACOES.png')
      if(QAEnsureFocus $first.proc.Id 'fechar_configuracoes') {
        QAAssertGuestForeground $first.proc.Id
        [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
        Start-Sleep -Seconds 2
        if(!(QAGetConfigTitle $first.proc.Id)) {
          $report.captura_retorno_dashboard=[bool](Save-QACapture 'CAPTURA_G5C_RETORNO_DASHBOARD.png')
          if($report.captura_retorno_dashboard -and $report.captura_dashboard -and
             !(QACaptureDifference (Join-Path $output 'CAPTURA_G5C_DASHBOARD.png') (Join-Path $output 'CAPTURA_G5C_RETORNO_DASHBOARD.png'))) {
            $report.retorno_dashboard='CONFIRMADO_POR_IMAGEM_E_FECHAMENTO'
          } else {$report.retorno_dashboard='CAPTURA_PARA_AUDITORIA'}
        }
      } else {$report.retorno_dashboard='FOCO_INDISPONIVEL_FECHAMENTO_BLOQUEADO'}
    }
  } catch {
    $report.navegacao_automatica='NAVEGACAO_NAO_CONFIRMADA'
    $report.captura_erros['navegacao_configuracoes']=([string]$_.Exception.Message).Substring(0,[Math]::Min(220,([string]$_.Exception.Message).Length))
  }
  $report.captura_criada=$report.captura_inicio -and $report.captura_dashboard
  $report.encerramento_controlado=[bool](Stop-QAProcess $first.proc)
  if(!$report.encerramento_controlado) {throw 'Primeira execução não encerrou via CloseMainWindow.'}
  $second=Start-QAProcess
  $report.execucoes += @{fase='segunda';processo_iniciado=$true;janela_detectada=$second.hasWindow;titulo=$second.title}
  $report.reinicializacao=$second.hasWindow
  if(!$second.hasWindow) {throw 'Segunda inicialização sem janela.'}
  Start-Sleep -Seconds 3
  if(!(Stop-QAProcess $second.proc)) {throw 'Segunda execução não encerrou controladamente.'}
  if(Test-Path -LiteralPath $database -PathType Leaf) {
    $report.banco_criado=$true
    $dbBytes=[System.IO.File]::ReadAllBytes($database)
    if($dbBytes.Length -ge 100) {
      $signature=[System.Text.Encoding]::ASCII.GetString($dbBytes,0,16)
      $report.banco_cabecalho_ok=($signature -eq "SQLite format 3`0")
    }
    $report.banco_sha256=(Get-FileHash -LiteralPath $database -Algorithm SHA256).Hash.ToLowerInvariant()
    if($report.banco_cabecalho_ok) {Copy-Item -LiteralPath $database -Destination (Join-Path $output 'BANCO_G5C_SINTETICO.db') -Force}
  }
  if($report.reinicializacao -and $report.encerramento_controlado -and $report.banco_cabecalho_ok) {
    if($report.janela_qa_verificada -and $report.sessao_grafica.sessao_igual -and
       $report.captura_inicio -and $report.captura_dashboard -and
       $report.dashboard_verificado -and $report.navegacao_configuracoes -eq 'CONFIRMADA' -and $report.captura_configuracoes -and
       $report.retorno_dashboard -eq 'CONFIRMADO_POR_IMAGEM_E_FECHAMENTO' -and $report.captura_retorno_dashboard) {
      $report.status='PASSOU_G5C'
      $report.motivo='Duas inicializações, SQLite e navegação identificada por dados independentes.'
    } else {
      $report.status='PARCIAL'
      if($report.captura_erros.Count -gt 0) {
        $report.motivo='EXE e banco verificados; falhas de captura registradas. Navegação visual pendente.'
      } else {
        $report.motivo='EXE e banco verificados; telas registradas para auditoria. Navegação não comprovada automaticamente.'
      }
    }
  } else {
    $report.status='PARCIAL'
    $report.motivo='Alguma evidência de banco ou reinicialização não foi confirmada.'
  }
} catch {
  $report.status='FALHOU'
  $report.motivo=[string]$_.Exception.Message
} finally {
  foreach($proc in $jobs) {
    try {$current=Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
      if($null -ne $current) {Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue}} catch {}
  }
  try {$json=$report | ConvertTo-Json -Depth 7
       [System.IO.File]::WriteAllText((Join-Path $output 'RESULTADO_G5C.json'),$json,[System.Text.Encoding]::UTF8)} catch {}
  # Sem shutdown do Sandbox: fechar manualmente, somente após receber o ZIP.
}
'''


def g5c_validate_report(data: bytes) -> dict:
    if len(data)>40000:
        raise G5BSafetyError('Relatório G5-C excede limite.')
    try:
        obj=json.loads(data.decode('utf-8-sig'))
    except (ValueError,UnicodeError) as exc:
        raise G5BSafetyError('Relatório guest G5-C ilegível.') from exc
    if not isinstance(obj,dict) or obj.get('component')!='vighna-g5c-sandbox' or \
            obj.get('alvo')!=G5B_TARGET_BUILD or obj.get('instalacao_autorizada') is not False or \
            obj.get('banco_sintetico') is not True or obj.get('rede')!='Disable' or obj.get('clipboard')!='Disable':
        raise G5BSafetyError('Identidade ou proteção do diagnóstico G5-C inválida.')
    if obj.get('status') not in ('PASSOU_G5C','PARCIAL','FALHOU','BLOQUEADO'):
        raise G5BSafetyError('Status G5-C não reconhecido.')
    runs=obj.get('execucoes')
    if not isinstance(runs,list) or len(runs)>2 or not all(isinstance(i,dict) for i in runs):
        raise G5BSafetyError('Execuções G5-C inválidas.')
    if obj['status']=='PASSOU_G5C' and not (len(runs)==2 and
            all(x.get('janela_detectada') is True for x in runs) and
            obj.get('dashboard_verificado') is True and
            obj.get('dashboard_evidencia')=='COMPROVADO_POR_IDENTIFICADORES' and
            obj.get('navegacao_configuracoes')=='CONFIRMADA' and
            obj.get('config_janela_titulo','').startswith('Configurações') and
            obj.get('janela_qa_verificada') is True and
            isinstance(obj.get('sessao_grafica'),dict) and obj['sessao_grafica'].get('sessao_igual') is True and
            obj.get('captura_inicio') is True and
            obj.get('captura_dashboard') is True and
            obj.get('captura_configuracoes') is True and
            obj.get('retorno_dashboard')=='CONFIRMADO_POR_IMAGEM_E_FECHAMENTO' and
            obj.get('captura_retorno_dashboard') is True and
            obj.get('encerramento_controlado') is True and
            obj.get('reinicializacao') is True and
            obj.get('banco_cabecalho_ok') is True):
        raise G5BSafetyError('Aprovação G5-C contradiz as evidências.')
    return obj


def g5c_sqlite_check(db_path:Path, reported_digest:str) -> dict:
    import hashlib, sqlite3
    if not db_path.is_file() or db_path.stat().st_size>80_000_000:
        return {'status':'BLOQUEADO','motivo':'Banco sintético ausente ou muito grande.'}
    with db_path.open('rb') as f:
        if f.read(16)!=b'SQLite format 3\x00':
            return {'status':'FALHOU','motivo':'Cabeçalho SQLite inválido.'}
    digest=hashlib.sha256(db_path.read_bytes()).hexdigest()
    if digest!=reported_digest:
        return {'status':'FALHOU','motivo':'Hash do banco sintético não confere.'}
    try:
        # Somente leitura, sem executar SQL do banco ou extensões.
        uri='file:'+db_path.resolve().as_posix()+'?mode=ro&immutable=1'
        con=sqlite3.connect(uri,uri=True,timeout=5)
        try:
            con.enable_load_extension(False)
            check=con.execute('PRAGMA integrity_check').fetchone()
            tables=con.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()
        finally:con.close()
        if check!=('ok',) or not tables or tables[0]<1:
            return {'status':'FALHOU','motivo':'Integridade ou tabelas do SQLite inválidas.'}
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as exc:
        return {'status':'FALHOU','motivo':type(exc).__name__}
    return {'status':'PASSOU','sha256':digest,'tabelas':tables[0],'integridade':'ok'}


def g5c_make_evidence(summary:dict, dest:Path, reports:dict[str,bytes]) -> None:
    import hashlib,zipfile
    files={'RESUMO_G5C.json':json.dumps(summary,ensure_ascii=False,indent=2).encode('utf8')}
    files.update({k:v[:250000] for k,v in reports.items() if k in ('RESULTADO_GUEST_G5C.json','LOG_PYINSTALLER_G5C.txt')})
    for screenshot in ('CAPTURA_G5C_INICIO.png','CAPTURA_G5C_DASHBOARD.png','CAPTURA_G5C_CONFIGURACOES.png','CAPTURA_G5C_RETORNO_DASHBOARD.png'):
        data=reports.get(screenshot)
        if data and data.startswith(b'\x89PNG\r\n\x1a\n') and len(data)<2_500_000:
            files[screenshot]=data
    hashes={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
    files['MANIFESTO_SHA256.json']=json.dumps(hashes,indent=2).encode()
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None or any(hashlib.sha256(z.read(k)).hexdigest()!=v for k,v in hashes.items()):
            raise G5BSafetyError('ZIP G5-C inválido.')


def g5c_run() -> int:
    """Compila somente o candidato QA e executa o ensaio G5-C dentro do Sandbox.

    O EXE nunca é executado no host. O banco resultante permanece temporário e
    não é empacotado no ZIP do diagnóstico. A saída da UI não libera o gate.
    """
    import hashlib, shutil,subprocess,sys,time
    import homologador_windows as h
    from painel_g5_preflight import run_g5_a
    from datetime import datetime
    if sys.platform!='win32':
        raise G5BSafetyError('G5-C só pode ser executado em Windows com Sandbox.')
    if run_g5_a().get('status')!='DIAGNOSTICO_APROVADO':
        raise G5BSafetyError('G5-A não aprovado; execução bloqueada.')
    h.preflight_selftest()
    base=h.checked_archive(h.KIT/'insumos'/h.BASE)
    rc2=h.checked_archive(h.KIT/'insumos'/h.RC2,prefix='codigo/')
    if not h.inspect_static(base,h.checked_archive(h.KIT/'insumos'/h.PATCH),rc2):
        raise G5BSafetyError('Contrato de fontes RC2 não aprovado.')
    rc2['VighnaStudy.spec']=base['VighnaStudy.spec']
    home=Path.home()
    if home.is_symlink():raise G5BSafetyError('Perfil redirecionado por link.')
    lab=g5b_folder(root=home/'VighnaLab'/'G5B_Laboratorios',run_id='G5B_G5C_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    g5b_check_root(lab)
    sandbox=Path(os.environ.get('WINDIR',r'C:\Windows'))/'System32'/'WindowsSandbox.exe'
    if not sandbox.is_file():raise G5BSafetyError('Windows Sandbox ausente.')
    lab.mkdir(parents=True)
    code=lab/'CODIGO_QA';inp=lab/'ENTRADA_SOMENTE_LEITURA';out=lab/'SAIDA_SINTETICA';dist=lab/'DIST'
    inp.mkdir();out.mkdir();h.write_sources(rc2,code)
    logfile=lab/'log_pyinstaller.txt'
    zipresult=lab/('G5_C_DIAGNOSTICO_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip')
    result={'component':'vighna-g5c-host','alvo':G5B_TARGET_BUILD,'versao_painel':__import__('painel_atualizador').panel_version(h.KIT),
            'status':'BLOQUEADO','g5_aprovado':False,'instalacao_autorizada':False,
            'sandbox_rede':'Disable','sandbox_clipboard':'Disable',
            'validacao_interface':'PENDENTE','validacao_sqlite':'PENDENTE'}
    safe={}
    try:
        print('ETAPA_G5C: Compilando RC2 com spec original em fontes QA.',flush=True)
        env=h.environment_qa(lab)
        for name in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):env.pop(name,None)
        with logfile.open('wb') as stream:
            proc=subprocess.Popen([sys.executable,'-B','-m','PyInstaller','--noconfirm',
                '--distpath',str(dist),'--workpath',str(lab/'BUILD'),'VighnaStudy.spec'],
                cwd=code,env=env,stdout=stream,stderr=subprocess.STDOUT)
            try:proc.wait(timeout=G5B_TIMEOUT_BUILD)
            except subprocess.TimeoutExpired:
                proc.kill();proc.wait(timeout=15);raise G5BSafetyError('Compilação excedeu limite.')
        if proc.returncode!=0:raise G5BSafetyError('PyInstaller falhou.')
        folder=dist/'VighnaStudy';built=folder/'VighnaStudy.exe'
        if not built.is_file():raise G5BSafetyError('Build incompleto.')
        if sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())>750_000_000:
            raise G5BSafetyError('Build excede 750 MB.')
        result['exe_sha256']=h.digest_file(built)
        shutil.copytree(folder,inp/'VighnaStudy',symlinks=False)
        (inp/'G5C_EXECUTAR_NO_SANDBOX.ps1').write_text(G5C_SANDBOX_PS,encoding='utf-8-sig')
        config=g5b_sandbox_configuration(inp,out).replace('G5B_EXECUTAR_NO_SANDBOX.ps1','G5C_EXECUTAR_NO_SANDBOX.ps1')
        (lab/'G5C_LABORATORIO.wsb').write_text(config,encoding='utf8')
        print('ETAPA_G5C: Abrindo Sandbox sem rede/clipboard; aguarde duas inicializações.',flush=True)
        sandbox_process=subprocess.Popen([str(sandbox),str(lab/'G5C_LABORATORIO.wsb')],cwd=lab)
        guest=out/'RESULTADO_G5C.json'; start=time.monotonic()
        while time.monotonic()-start<G5C_TIMEOUT_SANDBOX:
            if guest.is_file():
                data=guest.read_bytes();rep=g5c_validate_report(data)
                safe['RESULTADO_GUEST_G5C.json']=data
                result['guest']=rep
                db=out/'BANCO_G5C_SINTETICO.db'
                sqlitecheck=g5c_sqlite_check(db,rep.get('banco_sha256',''))
                result['sqlite']=sqlitecheck
                result['validacao_sqlite']=sqlitecheck['status']
                result['validacao_interface']=rep.get('navegacao_configuracoes','PENDENTE')
                result['capturas_pendentes']=[name for name in ('captura_inicio','captura_dashboard','captura_configuracoes','captura_retorno_dashboard') if rep.get(name) is not True]
                result['erros_captura']=rep.get('captura_erros',{})
                if rep['status']=='PASSOU_G5C' and sqlitecheck['status']=='PASSOU':
                    result['status']='EVIDENCIA_G5C_COMPLETA'
                elif rep['status'] in ('PASSOU_G5C','PARCIAL'):
                    result['status']='PARCIAL'
                else:
                    result['status']=rep['status']
                print('ETAPA_G5C: Relatório recebido. Status: '+result['status'],flush=True)
                break
            if sandbox_process.poll() is not None:
                raise G5BSafetyError('Sandbox encerrou antes de gerar relatório.')
            time.sleep(2)
        else:raise G5BSafetyError('O Sandbox não respondeu dentro do limite de 13 minutos.')
    except Exception as exc:
        result['status']='BLOQUEADO';result['motivo']=str(exc)[:350]
        print('ETAPA_G5C: BLOQUEADO — '+result['motivo'],flush=True)
    finally:
        if logfile.is_file():safe['LOG_PYINSTALLER_G5C.txt']=logfile.read_bytes()[-180000:]
        for filename in ('CAPTURA_G5C_INICIO.png','CAPTURA_G5C_DASHBOARD.png','CAPTURA_G5C_CONFIGURACOES.png','CAPTURA_G5C_RETORNO_DASHBOARD.png'):
            screenshot=out/filename
            if screenshot.is_file() and screenshot.stat().st_size<2_500_000:
                safe[filename]=screenshot.read_bytes()
        # Nunca inclui o banco SQLite nem arquivos pessoais no diagnóstico.
        g5c_make_evidence(result,zipresult,safe)
        print('ZIP DE DIAGNOSTICO CRIADO: '+str(zipresult),flush=True)
        print('STATUS G5-C: '+result['status']+'. Instalação M2 não autorizada.',flush=True)
        print('O Sandbox poderá ser fechado pela janela X, após receber o ZIP.',flush=True)
    return 0 if result['status']=='EVIDENCIA_G5C_COMPLETA' else 1





def g5c_verify_evidence(file:Path)->dict:
    """Verifica evidência G5-C como documentação local; NÃO confere autoria nem conteúdo visual."""
    import hashlib,json,zipfile,struct
    file=Path(file)
    screenshots={
        'CAPTURA_G5C_INICIO.png','CAPTURA_G5C_DASHBOARD.png',
        'CAPTURA_G5C_CONFIGURACOES.png','CAPTURA_G5C_RETORNO_DASHBOARD.png'}
    expected=screenshots|{'RESUMO_G5C.json','RESULTADO_GUEST_G5C.json',
                          'LOG_PYINSTALLER_G5C.txt','MANIFESTO_SHA256.json'}
    if not file.is_file() or file.stat().st_size>12_000_000:
        raise G5BSafetyError('Evidência inexistente ou maior que 12 MB.')
    with zipfile.ZipFile(file) as z:
        infos=z.infolist()
        if len(infos)!=len(expected) or {i.filename for i in infos}!=expected:
            raise G5BSafetyError('Evidência G5-C com arquivos inesperados ou duplicados.')
        if sum(i.file_size for i in infos)>16_000_000 or any(i.file_size>4_000_000 for i in infos):
            raise G5BSafetyError('Limite de arquivos de evidência ultrapassado.')
        if z.testzip() is not None:
            raise G5BSafetyError('CRC inválido.')
        hashes=json.loads(z.read('MANIFESTO_SHA256.json'))
        if not isinstance(hashes,dict) or set(hashes)!=(expected-{'MANIFESTO_SHA256.json'}):
            raise G5BSafetyError('Manifesto G5-C inválido.')
        for name,sha in hashes.items():
            if not isinstance(sha,str) or hashlib.sha256(z.read(name)).hexdigest()!=sha:
                raise G5BSafetyError('SHA-256 inválido para '+name)
        for name in screenshots:
            head=z.read(name)[:24]
            if len(head)<24 or head[:8]!=b'\x89PNG\r\n\x1a\n' or head[12:16]!=b'IHDR':
                raise G5BSafetyError('Captura inválida: '+name)
            width,height=struct.unpack('>II',head[16:24])
            if not (350<=width<=8192 and 200<=height<=8192):
                raise G5BSafetyError('Dimensões de captura inválidas.')
        host=json.loads(z.read('RESUMO_G5C.json'))
        guest=json.loads(z.read('RESULTADO_GUEST_G5C.json'))
    if not isinstance(host,dict) or not isinstance(guest,dict):
        raise G5BSafetyError('Resumo e guest inválidos.')
    requirements=(host.get('component')=='vighna-g5c-host'
                  and host.get('alvo')==G5B_TARGET_BUILD
                  and host.get('status')=='EVIDENCIA_G5C_COMPLETA'
                  and host.get('validacao_interface')=='CONFIRMADA'
                  and host.get('validacao_sqlite')=='PASSOU'
                  and host.get('g5_aprovado') is False
                  and host.get('instalacao_autorizada') is False
                  and guest.get('component')=='vighna-g5c-sandbox'
                  and guest.get('alvo')==G5B_TARGET_BUILD
                  and guest.get('status')=='PASSOU_G5C'
                  and guest.get('instalacao_autorizada') is False
                  and guest.get('dashboard_verificado') is True
                  and guest.get('navegacao_configuracoes')=='CONFIRMADA'
                  and guest.get('captura_configuracoes') is True
                  and guest.get('captura_dashboard') is True
                  and guest.get('captura_inicio') is True
                  and guest.get('captura_retorno_dashboard') is True
                  and guest.get('reinicializacao') is True
                  and guest.get('encerramento_controlado') is True
                  and guest.get('banco_criado') is True
                  and guest.get('banco_cabecalho_ok') is True
                  and guest.get('rede')=='Disable'
                  and guest.get('clipboard')=='Disable')
    if not requirements:
        raise G5BSafetyError('G5-C não comprovou os requisitos previstos.')
    return {'component':'g5-evidence-checkpoint', 'status':'EVIDENCIADO_DOCUMENTALMENTE',
            'alvo':G5B_TARGET_BUILD,
            'arquivo_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
            'arquivo_nome':file.name, 'imagens_verificadas':4,
            'instalacao_autorizada':False,
            'observacao':'Hashes não autenticam origem; análise humana das capturas exigida no G7.'}


def g5c_register_evidence(path:Path, *,home:Path|None=None)->dict:
    import json,os
    obj=g5c_verify_evidence(path)
    base=(Path(home) if home is not None else Path.home())/'VighnaLab'/'Gates_QA'
    for parent in (base.parent,base):
        if parent.exists() and (parent.is_symlink() or (hasattr(parent,'is_junction') and parent.is_junction())):
            raise G5BSafetyError('Registro G5-C em diretório com link/junction: bloqueado.')
        if (parent/'estudos.db').exists() or (parent/'VighnaStudy.exe').exists():
            raise G5BSafetyError('Diretório contém dados de instalação real: bloqueado.')
    base.mkdir(parents=True,exist_ok=True)
    target=base/'G5_C_EVIDENCIA.json';tmp=base/'G5_C_EVIDENCIA.tmp'
    if target.is_symlink() or tmp.is_symlink():
        raise G5BSafetyError('Registro local inseguro.')
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf8')
    os.replace(tmp,target)
    return obj


def g5c_load_registry(*,home:Path|None=None)->dict|None:
    import json
    base=(Path(home) if home is not None else Path.home())/'VighnaLab'/'Gates_QA'
    file=base/'G5_C_EVIDENCIA.json'
    if base.is_symlink() or file.is_symlink() or not file.is_file() or file.stat().st_size>4096:
        return None
    try:
        data=json.loads(file.read_text(encoding='utf8'))
    except (OSError,ValueError):return None
    if (not isinstance(data,dict) or data.get('component')!='g5-evidence-checkpoint'
            or data.get('status')!='EVIDENCIADO_DOCUMENTALMENTE'
            or data.get('alvo')!=G5B_TARGET_BUILD
            or data.get('imagens_verificadas')!=4
            or data.get('instalacao_autorizada') is not False):
        return None
    digest=data.get('arquivo_sha256','')
    if not isinstance(digest,str) or len(digest)!=64:return None
    return data

# G6-A: laboratório descartável para exercitar o ATUALIZADOR ORIGINAL R1D.
# Não compila nem executa VighnaStudy.exe. Não homologa atualização real Windows.
G6A_TARGET = 'structural-m2-int1-settings-r1d-rc2'


def g6a_safety_root(root: Path) -> Path:
    root=Path(root)
    required=Path.home()/'VighnaLab'/'G6A_Laboratorios'
    if root != required:
        raise G5BSafetyError('G6-A somente no diretório QA definido.')
    for item in (root.parent,root):
        if item.exists() and (item.is_symlink() or (hasattr(item,'is_junction') and item.is_junction())):
            raise G5BSafetyError('Diretório QA aponta para junction/symlink.')
        if (item/'estudos.db').exists() or (item/'VighnaStudy.exe').exists():
            raise G5BSafetyError('Arquivos de uma instalação encontrados; operação bloqueada.')
    return root


def g6a_exercise(root:Path, *, sabotage:str|None=None) -> dict:
    """Executa a transação do atualizador ORIGINAL sobre fontes e dados artificiais."""
    import hashlib, importlib.util, json, sqlite3, zipfile
    from contextlib import closing
    import homologador_windows as h
    if root.exists():
        raise G5BSafetyError('Cópia de QA já existe: não sobrescrever.')
    base = h.checked_archive(h.KIT/'insumos'/h.BASE)
    patch = h.KIT/'insumos'/h.PATCH
    root.mkdir(parents=True,exist_ok=False)
    for name,data in base.items():
        target=root.joinpath(*name.split('/'))
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    import importlib.util
    spec=importlib.util.spec_from_file_location('vighna_qa_engine_g6a',root/'vighna_update_engine.py')
    if spec is None or spec.loader is None:
        raise G5BSafetyError('Engine QA não pôde ser carregado.')
    engine=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    before=engine.version_from_file(root/'versao.py')
    if before != ('0.29.59','structural-m1c-readpilot-restore-offline-r1d-v1',25):
        raise G5BSafetyError('Versão de origem inesperada.')
    old_main=hashlib.sha256((root/'main.py').read_bytes()).hexdigest()
    old_versao=(root/'versao.py').read_bytes()
    db=root/'estudos.db'
    # sqlite3.Connection.__exit__ gerencia transações, mas NÃO fecha o handle.
    # No Windows, um handle aberto impede shutil.rmtree no fim do laboratório.
    with closing(sqlite3.connect(db)) as conn:
        with conn:
            conn.execute('CREATE TABLE qa_marcador (id INTEGER PRIMARY KEY, texto TEXT NOT NULL)')
            conn.execute('INSERT INTO qa_marcador VALUES (7, \'QA_SYNTHETIC_ONLY\')')
    old_db=hashlib.sha256(db.read_bytes()).hexdigest()
    active=root/'dist'/'SistemaEstudos';active.mkdir(parents=True)
    old_exe=b'QA_PLACEHOLDER_R1D_NOT_EXECUTABLE'
    (active/'VighnaStudy.exe').write_bytes(old_exe)
    inspected=engine.inspect_package(patch,root)
    if inspected['target_build']!=G6A_TARGET:raise G5BSafetyError('RC2 inesperado.')
    trigger=[]
    def fake_builder(work,output,report):
        if sabotage=='build':
            raise RuntimeError('FALHA_QA_SIMULADA_BUILD')
        output.mkdir(parents=True,exist_ok=True)
        (output/'VighnaStudy.exe').write_bytes(b'QA_PLACEHOLDER_RC2_NOT_EXECUTABLE')
    if sabotage=='after_commit':
        real_check=engine.check_database
        def injected(path):
            if Path(path)==db and engine.version_from_file(root/'versao.py')[1]==G6A_TARGET:
                raise engine.UpdateError('FALHA_QA_SIMULADA_APOS_COMMIT')
            return real_check(path)
        engine.check_database=injected
    try:
        try:
            installed=engine.install_package(patch,root,python_exe='QA',runner=fake_builder,
                report=lambda pct,msg: trigger.append(int(pct)))
            if sabotage is not None: raise G5BSafetyError('Falha simulada não ocorreu.')
        except engine.UpdateError as exc:
            if sabotage not in ('build','after_commit'):
                raise
            if 'FALHA_QA_SIMULADA' not in str(exc):
                raise G5BSafetyError('Motivo da falha divergente.') from exc
            installed=None
    finally:
        if sabotage=='after_commit':engine.check_database=real_check
    current=engine.version_from_file(root/'versao.py')
    with closing(sqlite3.connect(db)) as conn:
        rows=conn.execute('SELECT id,texto FROM qa_marcador').fetchall()
        ok_integrity=conn.execute('PRAGMA integrity_check').fetchone()==('ok',)
    if rows != [(7,'QA_SYNTHETIC_ONLY')] or not ok_integrity:
        raise G5BSafetyError('Marcador de banco sintético alterado.')
    if hashlib.sha256(db.read_bytes()).hexdigest()!=old_db:
        raise G5BSafetyError('Bytes do SQLite sintético divergiram.')
    entries=list((root/'backups'/'atualizacoes').glob('*/state.json'))
    history=list((root/'backups'/'atualizacoes').glob('historico.jsonl'))
    if len(history)!=1:
        raise G5BSafetyError('Histórico da transação não encontrado.')
    events=[json.loads(line) for line in history[0].read_text(encoding='utf8').splitlines()]
    if sabotage is None:
        if current[1]!=G6A_TARGET or (active/'VighnaStudy.exe').read_bytes()!=b'QA_PLACEHOLDER_RC2_NOT_EXECUTABLE':
            raise G5BSafetyError('RC2 sintético não foi aplicado.')
        if hashlib.sha256((root/'main.py').read_bytes()).hexdigest()==old_main:
            raise G5BSafetyError('Main não foi atualizado.')
        if len(entries)!=1:
            raise G5BSafetyError('Checkpoint de atualização ausente.')
        state=json.loads(entries[0].read_text(encoding='utf8'))
        back=entries[0].parent
        if state['phase']!='installed' or not (back/'estudos.db').is_file():
            raise G5BSafetyError('Snapshot não está íntegro.')
        if (back/'anterior_executavel'/'VighnaStudy.exe').read_bytes()!=old_exe:
            raise G5BSafetyError('EXE QA antigo não foi preservado.')
        engine.check_database(back/'estudos.db')
        if events[-1]['status']!='installed':
            raise G5BSafetyError('Histórico não registrou sucesso.')
        status='ATUALIZACAO_SINTETICA_APLICADA'
    else:
        if current != before or (root/'versao.py').read_bytes()!=old_versao:
            raise G5BSafetyError('Rollback falhou na versão de origem.')
        if hashlib.sha256((root/'main.py').read_bytes()).hexdigest()!=old_main:
            raise G5BSafetyError('Rollback falhou no main.')
        if (active/'VighnaStudy.exe').read_bytes()!=old_exe:
            raise G5BSafetyError('Rollback falhou no EXE sintético.')
        if events[-1]['status']!='failed' or events[-1].get('rollback_errors'):
            raise G5BSafetyError('Falha não foi registrada ou rollback teve erros.')
        if sabotage=='after_commit' and (len(entries)!=1 or json.loads(entries[0].read_text())['phase']!='recovered'):
            raise G5BSafetyError('Recuperação pós-commit não foi documentada.')
        status='FALHA_SIMULADA_REVERTIDA'
    return {'status':status,'cenario':sabotage or 'sucesso','schema':current[2],
            'banco_qa_integridade':'ok','banco_qa_marcador':'preservado',
            'build_usou_exe_ficticio':True,'historico_final':events[-1]['status'],
            'engine_sha256':hashlib.sha256((root/'vighna_update_engine.py').read_bytes()).hexdigest(),
            'pacote_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),
            'backup_criado':bool(entries),'etapas':trigger}


def g6a_run(labroot:Path|None=None,*,persist:bool=True)->dict:
    """Sem acesso ao banco pessoal. Relatório verificável, não execução Sandbox."""
    import datetime, hashlib, json, os, shutil, tempfile, zipfile
    import homologador_windows as h
    root=g6a_safety_root(labroot or Path.home()/'VighnaLab'/'G6A_Laboratorios')
    h.preflight_selftest()
    root.mkdir(parents=True,exist_ok=True)
    results=[]
    for scenario in (None,'build','after_commit'):
        temp=Path(tempfile.mkdtemp(prefix='G6A_',dir=str(root)))
        qa=temp/'instalacao_qa'
        try:
            results.append(g6a_exercise(qa,sabotage=scenario))
        finally:
            # Não encobrir o erro original caso a limpeza também falhe.
            try:
                shutil.rmtree(temp)
            except OSError as cleanup_error:
                if sys.exc_info()[0] is not None:
                    print('G6-A: aviso: falha adicional na limpeza do laboratório: '
                          +str(cleanup_error), file=sys.stderr, flush=True)
                else:
                    raise G5BSafetyError('G6-A concluiu o cenário, mas o laboratório '
                                         'não pôde ser removido: '+str(cleanup_error)) from cleanup_error
    obj={'component':'vighna-g6a-synthetic','version': '3.1.11',
         'alvo':G6A_TARGET,'resultado':'PASSOU_G6A_SINTETICO',
         'ambiente':'laboratorio QA descartavel','execucao_exe_real':False,
         'build_pyi_real':False,'windows_sandbox_executado':False,
         'gate_g6_aprovado':False,'instalacao_autorizada':False,
         'cenarios':results}
    if persist:
        stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        target=root/('G6_A_DIAGNOSTICO_'+stamp+'.zip')
        content=json.dumps(obj,indent=2,ensure_ascii=False).encode('utf8')
        entries={'RESUMO_G6A.json':content}
        entries['MANIFESTO_SHA256.json']=json.dumps({k:hashlib.sha256(v).hexdigest() for k,v in entries.items()},indent=2).encode()
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in entries.items():z.writestr(name,data)
        with zipfile.ZipFile(target) as z:
            if z.testzip() is not None:raise G5BSafetyError('Diagnóstico G6-A inválido.')
        print('ZIP DE DIAGNOSTICO CRIADO: '+str(target),flush=True)
        print('STATUS G6-A: PASSOU EM AMBIENTE SINTETICO. G6 e instalação seguem pendentes.',flush=True)
    return obj

if __name__ == "__main__":
    if sys.argv[1:] == ['--g6a']:
        try:
            g6a_run()
            sys.exit(0)
        except Exception as error:
            print('ETAPA_G6A: FALHOU: '+str(error),file=sys.stderr,flush=True)
            sys.exit(1)
    if sys.argv[1:] == ['--g5c']:
        try:
            sys.exit(g5c_run())
        except Exception as error:
            print('ETAPA_G5C: BLOQUEADO ANTES DO LABORATORIO: '+str(error),file=sys.stderr,flush=True)
            sys.exit(1)
    if sys.argv[1:] == ['--g5b']:
        try:
            sys.exit(g5b_run())
        except Exception as error:
            print('ETAPA_G5B: BLOQUEADO ANTES DO LABORATORIO: '+str(error),file=sys.stderr,flush=True)
            sys.exit(1)
    sys.exit(main())

