# -*- coding: utf-8 -*-
"""G6-B1: transaction of original update engine with real EXEs in Windows Sandbox.

Builds R1D, RC2 and a frozen guest agent from pinned QA inputs in a *new* lab.
The guest uses the real engine with a precompiled-binary runner; G6-B2 must
cover production's builder=None PyInstaller path, so this cannot approve G6.
"""
from __future__ import annotations
from datetime import datetime
import ast
import csv
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from xml.etree import ElementTree as ET
import zipfile

RC2_BUILD='structural-m2-int1-settings-r1d-rc2'
MAX_BUILD_SECONDS=1200
MAX_SANDBOX_SECONDS=1000

class G6BSafetyError(ValueError):pass


def engine_hidden_imports(source:bytes)->tuple[str,...]:
    """Capture import roots from the independently SHA-checked R1D QA engine.

    importlib.exec_module() loads an engine dynamically at runtime; PyInstaller's
    dependency scanner cannot see those imports. Fail closed if engine adds a
    non-stdlib dependency or a relative import, rather than assuming it exists.
    """
    tree=ast.parse(source.decode('utf-8-sig'),filename='vighna_update_engine.py')
    roots=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            roots.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                raise G6BSafetyError('Import relativo inesperado no motor QA')
            if node.module:
                roots.add(node.module.split('.')[0])
    roots.discard('__future__')
    unknown=roots-set(sys.stdlib_module_names)
    if unknown:
        raise G6BSafetyError('Dependencias externas no motor QA nao homologadas: '+', '.join(sorted(unknown)))
    if not {'uuid','tempfile','ast'}<=roots:
        raise G6BSafetyError('Motor QA de base mudou: faltam dependencias esperadas')
    return tuple(sorted(roots))


def probe_frozen_guest(guestexe:Path, engine_bytes:bytes, lab:Path)->Path:
    """Execute the actual frozen agent and import the real QA engine before Sandbox.

    This is an import-only preflight, not proof of update/rollback, which must
    still be demonstrated by Windows Sandbox and separate evidence.
    """
    import homologador_windows as h
    probe=lab/'PROBE_ENGINE_QA'
    probe.mkdir(exist_ok=False)
    module=probe/'vighna_update_engine.py'
    module.write_bytes(engine_bytes)
    log=lab/'PROBE_GUEST.log'
    env=h.environment_qa(lab)
    for key in ('PYTHONPATH','PYTHONHOME','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
        env.pop(key,None)
    try:
        completed=subprocess.run([str(guestexe),'--probe-engine',str(module)],
                                  cwd=str(probe),env=env,capture_output=True,
                                  timeout=45,check=False)
        log.write_bytes(b'G6B1 frozen-engine probe, exit='+str(completed.returncode).encode()+b'\n'+
                        completed.stdout[-20000:]+b'\n'+completed.stderr[-20000:])
        if completed.returncode!=0 or b'G6B1_ENGINE_IMPORT_OK' not in completed.stdout:
            raise G6BSafetyError('Agente congelado nao consegue importar o motor QA; consultar PROBE_GUEST.log')
    except subprocess.TimeoutExpired as err:
        log.write_text('Frozen QA engine import timed out',encoding='utf8')
        raise G6BSafetyError('Timeout na importacao congelada do motor QA') from err
    return log


def root_qa(home:Path|None=None)->Path:
    return (home or Path.home())/'VighnaLab'/'G6B_Laboratorios'


def ensure_safe(base:Path,home:Path|None=None):
    h=home or Path.home()
    if base!=root_qa(h):raise G6BSafetyError('Somente pasta oficial G6-B1 autorizada')
    for item in (h,base.parent,base):
        if item.exists():
            if item.is_symlink() or (hasattr(item,'is_junction') and item.is_junction()):
                raise G6BSafetyError('Symlink/junction em pasta de laboratório')
            if ((item/'estudos.db').exists() or (item/'VighnaStudy.exe').exists()
                or (item/'dist'/'VighnaStudy'/'VighnaStudy.exe').exists()):
                raise G6BSafetyError('Instalação pessoal perto do laboratório: bloqueado')
    return base


def sandbox_xml(source:Path,output:Path)->str:
    r=ET.Element('Configuration')
    for tag in ('vGPU','Networking','ClipboardRedirection','PrinterRedirection','AudioInput','VideoInput'):
        ET.SubElement(r,tag).text='Disable'
    maps=ET.SubElement(r,'MappedFolders')
    for host,guest,ro in ((source,r'C:\VighnaQA\Entrada','true'),(output,r'C:\VighnaQA\Saida','false')):
        item=ET.SubElement(maps,'MappedFolder')
        ET.SubElement(item,'HostFolder').text=str(host)
        ET.SubElement(item,'SandboxFolder').text=guest
        ET.SubElement(item,'ReadOnly').text=ro
    command=ET.SubElement(r,'LogonCommand')
    ET.SubElement(command,'Command').text=(
        r'C:\VighnaQA\Entrada\G6B1_GUEST.exe --input C:\VighnaQA\Entrada --output C:\VighnaQA\Saida')
    ET.indent(r,space='  ')
    return '<?xml version="1.0" encoding="utf-8"?>\n'+ET.tostring(r,encoding='unicode')+'\n'


def _request_close_owned_sandbox_window(pid: int) -> int:
    """Ask windows belonging to the *launched PID* to close via WM_CLOSE.

    Do not infer PID from window title, kill process trees, broadcast WM_CLOSE,
    or touch an unrelated Windows Sandbox instance. A client hosted by a
    different PID is deliberately left for manual closing.
    """
    if sys.platform != 'win32' or not isinstance(pid, int) or pid <= 0:
        return 0
    user32 = ctypes.windll.user32
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    posted = []

    def visit(hwnd, unused):
        owner = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            # WM_CLOSE asks the application to shut down through its UI.
            if user32.PostMessageW(hwnd, 0x0010, 0, 0):
                posted.append(True)
        return 1

    callback = callback_type(visit)
    if not user32.EnumWindows(callback, 0):
        raise G6BSafetyError('Não foi possível enumerar janelas do Sandbox QA')
    return len(posted)


def sandbox_processes_qa() -> dict[int, str]:
    """Read-only PID inventory. No taskkill and no access to unrelated apps."""
    if sys.platform != 'win32':
        return {}
    result = subprocess.run(['tasklist', '/NH', '/FO', 'CSV'], capture_output=True,
                            text=True, errors='replace', timeout=30)
    if result.returncode:
        raise G6BSafetyError('Não foi possível verificar processos Sandbox existentes')
    found = {}
    names = {'windowssandbox.exe': 'WindowsSandbox.exe',
             'windowssandboxclient.exe': 'WindowsSandboxClient.exe'}
    for row in csv.reader(result.stdout.splitlines()):
        if len(row) < 2 or row[0].casefold() not in names:
            continue
        try:
            pid = int(row[1].replace(',', '').replace('.', ''))
        except ValueError:
            raise G6BSafetyError('PID de Sandbox ilegível')
        if pid <= 0 or pid in found:
            raise G6BSafetyError('PID de Sandbox inválido ou duplicado')
        found[pid] = names[row[0].casefold()]
    return found


def visible_client_windows(pids: dict[int, str]) -> list[dict]:
    """Enumerate only visible top-level windows owned by known client PIDs."""
    if sys.platform != 'win32':
        return []
    from ctypes import wintypes
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows.argtypes = (callback_type, ctypes.c_void_p)
    user32.EnumWindows.restype = ctypes.c_int
    user32.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD))
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.IsWindowVisible.argtypes = (ctypes.c_void_p,)
    user32.IsWindowVisible.restype = ctypes.c_int
    result = []
    def visit(hwnd, unused):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if pids.get(owner.value) == 'WindowsSandboxClient.exe' and user32.IsWindowVisible(hwnd):
            result.append({'hwnd': int(hwnd), 'pid': owner.value})
        return 1
    callback = callback_type(visit)
    if not user32.EnumWindows(callback, None):
        raise G6BSafetyError('Não foi possível enumerar janelas cliente do Sandbox')
    return result


def verified_qa_client_candidate(before: dict[int, str], after: dict[int, str],
                                 windows: list[dict], launcher_pid: int):
    """Require sole newly created launcher+client and exactly one client window."""
    if before or not isinstance(launcher_pid, int) or launcher_pid <= 0:
        return None
    clients = [pid for pid, name in after.items() if name == 'WindowsSandboxClient.exe']
    if (len(after) != 2 or after.get(launcher_pid) != 'WindowsSandbox.exe'
            or len(clients) != 1):
        return None
    matching = [w for w in windows if w.get('pid') == clients[0]
                and isinstance(w.get('hwnd'), int) and w['hwnd'] > 0]
    return matching[0] if len(matching) == 1 and len(windows) == 1 else None


def post_close_verified_client(hwnd: int, expected_pid: int) -> bool:
    """Recheck HWND and owner immediately before posting one WM_CLOSE."""
    if sys.platform != 'win32':
        return False
    from ctypes import wintypes
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD))
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.IsWindow.argtypes = (ctypes.c_void_p,)
    user32.IsWindow.restype = ctypes.c_int
    user32.IsWindowVisible.argtypes = (ctypes.c_void_p,)
    user32.IsWindowVisible.restype = ctypes.c_int
    user32.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)
    user32.PostMessageW.restype = ctypes.c_int
    owner = wintypes.DWORD()
    if not user32.IsWindow(hwnd) or not user32.IsWindowVisible(hwnd):
        return False
    if not user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner)) or owner.value != expected_pid:
        return False
    return bool(user32.PostMessageW(hwnd, 0x0010, 0, 0))



def _normalized_sandbox_ui_text(text: str) -> str:
    """Compare native UI labels without relying on Windows locale accents."""
    import unicodedata
    cleaned = unicodedata.normalize('NFKD', text.casefold())
    return ' '.join(''.join(ch for ch in cleaned if not unicodedata.combining(ch)).split())


def _is_expected_sandbox_discard_message(title: str, body: str, ok: str,
                                         cancel: str) -> bool:
    """Only the standard Windows Sandbox destructive-close prompt is approved.

    Never match a dialog merely from a caption, or from an OK button alone.
    The wording is intentionally strict and supports the known pt-BR / en-US
    native message text. Unfamiliar Windows builds remain manual.
    """
    title = _normalized_sandbox_ui_text(title)
    body = _normalized_sandbox_ui_text(body)
    ok = _normalized_sandbox_ui_text(ok).replace('&', '')
    cancel = _normalized_sandbox_ui_text(cancel).replace('&', '')
    if ok != 'ok' or cancel not in ('cancelar', 'cancel'):
        return False
    if title == 'area restrita do windows':
        return (all(x in body for x in (
            'que deseja fechar',
            'area restrita do windows',
            'todo o seu conteudo',
            'descartado e perdido permanentemente')))
    if title == 'windows sandbox':
        return (all(x in body for x in (
            'are you sure you want to close',
            'windows sandbox',
            'all of its content',
            'discarded and permanently lost')))
    return False


def _select_verified_sandbox_modal(windows: list[dict], main_hwnd: int) -> int | None:
    """Select the *other* uniquely identified top-level #32770 window.

    Windows Sandbox may create its confirmation as an independent top-level
    window with GW_OWNER=0. This is safe to accept only when BOTH the already
    verified main window and a single distinct dialog are present. The caller
    also validates PID, exact text, IDOK/IDCANCEL and UI identity twice.
    """
    if not isinstance(main_hwnd, int) or main_hwnd <= 0 or len(windows) != 2:
        return None
    main = [w for w in windows if w.get('hwnd') == main_hwnd]
    others = [w for w in windows if w.get('hwnd') != main_hwnd]
    if len(main) != 1 or len(others) != 1:
        return None
    if main[0].get('parent_hwnd') != 0 or main[0].get('owner_hwnd') != 0:
        return None
    dialog = others[0]
    if (not isinstance(dialog.get('hwnd'), int) or dialog['hwnd'] <= 0
            or dialog.get('parent_hwnd') != 0
            or dialog.get('owner_hwnd') not in (0, main_hwnd)):
        return None
    return dialog['hwnd']


def _native_sandbox_discard_dialog(client_pid: int, owner_hwnd: int) -> dict | None:
    """Read-only enumeration of the single native QA Sandbox discard dialog.

    Standard Sandbox on pt-BR Windows creates TWO top-level #32770 windows:
    the main UI and its unowned confirmation (GW_OWNER=0). Require that exact
    structure in the verified client's PID; never choose by caption alone.
    """
    if sys.platform != 'win32' or client_pid <= 0 or owner_hwnd <= 0:
        return None
    from ctypes import wintypes
    u = ctypes.WinDLL('user32', use_last_error=True)
    HWND = ctypes.c_void_p
    ENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, HWND, ctypes.c_void_p)
    u.EnumWindows.argtypes = (ENUMPROC, ctypes.c_void_p)
    u.EnumWindows.restype = ctypes.c_int
    u.EnumChildWindows.argtypes = (HWND, ENUMPROC, ctypes.c_void_p)
    u.EnumChildWindows.restype = ctypes.c_int
    u.GetWindowThreadProcessId.argtypes = (HWND, ctypes.POINTER(wintypes.DWORD))
    u.GetWindowThreadProcessId.restype = wintypes.DWORD
    u.IsWindow.argtypes = (HWND,);u.IsWindow.restype = ctypes.c_int
    u.IsWindowVisible.argtypes = (HWND,);u.IsWindowVisible.restype = ctypes.c_int
    u.IsWindowEnabled.argtypes = (HWND,);u.IsWindowEnabled.restype = ctypes.c_int
    u.GetWindow.argtypes = (HWND, ctypes.c_uint);u.GetWindow.restype = HWND
    u.GetParent.argtypes = (HWND,);u.GetParent.restype = HWND
    u.GetDlgItem.argtypes = (HWND, ctypes.c_int);u.GetDlgItem.restype = HWND
    u.GetClassNameW.argtypes = (HWND, ctypes.c_void_p, ctypes.c_int)
    u.GetClassNameW.restype = ctypes.c_int
    u.SendMessageTimeoutW.argtypes = (HWND, ctypes.c_uint, ctypes.c_size_t,
                                     ctypes.c_ssize_t, ctypes.c_uint,
                                     ctypes.c_uint, ctypes.POINTER(ctypes.c_size_t))
    u.SendMessageTimeoutW.restype = ctypes.c_void_p

    def class_name(hwnd):
        buf = ctypes.create_unicode_buffer(128)
        if not u.GetClassNameW(hwnd, ctypes.cast(buf, ctypes.c_void_p), 128):
            return ''
        return buf.value

    def text_of(hwnd):
        if not hwnd:return ''
        buf = ctypes.create_unicode_buffer(1024)
        written = ctypes.c_size_t()
        # WM_GETTEXT = 0x000D, SMTO_ABORTIFHUNG = 0x0002.
        ok = u.SendMessageTimeoutW(hwnd, 0x000D, 1024, ctypes.addressof(buf),
                                   0x0002, 700, ctypes.byref(written))
        return buf.value if ok else ''

    # Main window must still be visible and belong to the same QA client.
    main_pid = wintypes.DWORD()
    if (not u.IsWindow(owner_hwnd) or not u.IsWindowVisible(owner_hwnd)
            or not u.GetWindowThreadProcessId(owner_hwnd, ctypes.byref(main_pid))
            or main_pid.value != client_pid or class_name(owner_hwnd) != '#32770'):
        return None
    found=[]
    def visit(hwnd, _):
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if (pid.value == client_pid and u.IsWindowVisible(hwnd)
                and class_name(hwnd) == '#32770'):
            found.append({'hwnd':int(hwnd),
                          'owner_hwnd':int(u.GetWindow(hwnd, 4) or 0),
                          'parent_hwnd':int(u.GetParent(hwnd) or 0)})
        return 1
    cb = ENUMPROC(visit)
    if not u.EnumWindows(cb, None):
        return None
    # A third dialog, unknown owner or absent main window means manual OK.
    dialog = _select_verified_sandbox_modal(found, owner_hwnd)
    if dialog is None or not u.IsWindow(dialog) or not u.IsWindowVisible(dialog):
        return None
    ok_hwnd = u.GetDlgItem(dialog, 1)  # IDOK
    cancel_hwnd = u.GetDlgItem(dialog, 2)  # IDCANCEL
    if (not ok_hwnd or not cancel_hwnd
            or class_name(ok_hwnd) != 'Button' or class_name(cancel_hwnd) != 'Button'
            or not u.IsWindowEnabled(ok_hwnd)):
        return None
    for btn in (ok_hwnd, cancel_hwnd):
        button_pid = wintypes.DWORD()
        if (int(u.GetParent(btn) or 0) != dialog
                or not u.GetWindowThreadProcessId(btn, ctypes.byref(button_pid))
                or button_pid.value != client_pid):
            return None
    pieces=[]
    def visit_child(hwnd, _):
        if class_name(hwnd) == 'Static':
            t=text_of(hwnd)
            if t:pieces.append(t)
        return 1
    child_callback = ENUMPROC(visit_child)
    u.EnumChildWindows(dialog, child_callback, None)
    title=text_of(dialog)
    body=' '.join(pieces)
    if not _is_expected_sandbox_discard_message(title, body,
                                                text_of(ok_hwnd), text_of(cancel_hwnd)):
        return None
    return {'dialog_hwnd':dialog,'button_hwnd':int(ok_hwnd),
            'client_pid':client_pid,'owner_hwnd':owner_hwnd,
            'confirmation_type':'sandbox_discard_native_ptbr_enus'}


def _confirm_owned_sandbox_discard(client_pid: int, owner_hwnd: int,
                                   expected_processes: dict[int,str],
                                   timeout: float=5.0) -> dict:
    """Accept ONLY the exact native confirmation owned by the QA client.

    If identity or UI wording changes, do not send the click. This helper is
    never called without the earlier guest-evidence and ownership gates.
    """
    result={'acao':'confirmacao_manual','clicou_ok':False}
    if sys.platform != 'win32':return result
    if not expected_processes or not client_pid or not owner_hwnd:return result
    end=time.monotonic()+max(0.0,min(float(timeout),7.0))
    while time.monotonic() < end:
        if sandbox_processes_qa()!=expected_processes:
            result['motivo']='inventario_pid_alterado';return result
        item=_native_sandbox_discard_dialog(client_pid,owner_hwnd)
        if item is not None:
            # Repeat process/window/content verification directly before click.
            if sandbox_processes_qa()!=expected_processes:
                result['motivo']='inventario_pid_alterado';return result
            if _native_sandbox_discard_dialog(client_pid,owner_hwnd)!=item:
                result['motivo']='dialogo_alterado';return result
            from ctypes import wintypes
            u=ctypes.WinDLL('user32',use_last_error=True)
            u.SendMessageTimeoutW.argtypes=(ctypes.c_void_p,ctypes.c_uint,ctypes.c_size_t,
                                           ctypes.c_ssize_t,ctypes.c_uint,ctypes.c_uint,
                                           ctypes.POINTER(ctypes.c_size_t))
            u.SendMessageTimeoutW.restype=ctypes.c_void_p
            returned=ctypes.c_size_t()
            # BM_CLICK = 0x00F5, SMTO_ABORTIFHUNG = 2, timeout 2 s.
            # Only IDOK control of this exact verified modal window.
            delivered=u.SendMessageTimeoutW(item['button_hwnd'],0x00F5,0,0,2,2000,
                                            ctypes.byref(returned))
            if delivered:
                return {'acao':'confirmacao_automatica_enviada','clicou_ok':True,
                        'dialogo_nativo_validado':True,'metodo':'BM_CLICK_IDOK'}
            result['motivo']='mensagem_botao_nao_entregue';return result
        time.sleep(0.15)
    result['motivo']='confirmacao_nativa_nao_identificada'
    return result


def close_verified_qa_client(process, *, before: dict[int, str], timeout: float = 15.0) -> dict:
    """Close the sole evidence-backed QA Sandbox, including its native dialog.

    A dialog mismatch leaves the confirmation manual. No process is killed,
    and failure to close never changes the result of G6 or authorizes RC2.
    """
    pid = getattr(process, 'pid', None)
    manual = {'estado': 'cliente_nao_identificado_fechamento_manual',
              'pid_qa': pid, 'solicitacoes_wm_close': 0, 'fechamento_forcado': False,
              'confirmacao_automatica':False, 'metodo': 'qa_cliente_revalidado'}
    if not isinstance(before, dict) or before or not isinstance(pid, int) or pid <= 0:
        return manual
    try:
        after = sandbox_processes_qa()
        candidate = verified_qa_client_candidate(before, after, visible_client_windows(after), pid)
        if candidate is None:
            return manual
        if sandbox_processes_qa() != after:
            return manual
        confirmed = verified_qa_client_candidate(before, after, visible_client_windows(after), pid)
        if confirmed != candidate:
            return manual
        if not post_close_verified_client(candidate['hwnd'], candidate['pid']):
            return manual
        result = {'estado': 'fechamento_pendente_manual', 'pid_qa': pid,
                  'pid_cliente': candidate['pid'], 'solicitacoes_wm_close': 1,
                  'fechamento_forcado': False, 'confirmacao_automatica':False,
                  'metodo': 'qa_cliente_revalidado'}
        started=time.monotonic()
        # A short first wait: a native confirmation blocks process termination.
        try:
            process.wait(timeout=min(max(0.1, timeout), 0.7))
        except subprocess.TimeoutExpired:
            remaining=max(0.0, timeout-(time.monotonic()-started))
            if remaining >= 0.5:
                confirmation=_confirm_owned_sandbox_discard(
                    candidate['pid'],candidate['hwnd'],after,timeout=min(5.0,remaining))
                result['dialogo_de_descarte']=confirmation
                result['confirmacao_automatica']=confirmation['clicou_ok']
            remaining=max(0.0,timeout-(time.monotonic()-started))
            if remaining > 0:
                try: process.wait(timeout=remaining)
                except subprocess.TimeoutExpired: return result
            else:return result
        # Process termination alone does not prove the UI/client closed.
        end=time.monotonic()+max(0.0,timeout)
        while time.monotonic()<end:
            remaining=sandbox_processes_qa()
            if pid not in remaining and candidate['pid'] not in remaining:
                result['estado']='encerrado_graciosamente'
                result['ambos_processos_encerrados']=True
                return result
            time.sleep(0.2)
        return result
    except (OSError, subprocess.SubprocessError, G6BSafetyError, ValueError):
        return manual


def close_own_sandbox(process, *, timeout: float = 15.0,
                      ownership_snapshot=None, evidence_confirmed: bool = False) -> dict:
    """Request graceful closure, without terminate()/kill() fallback.

    If the Sandbox UI has a distinct process or does not respond, leave it
    running for manual closure. An inability to close must never erase QA
    evidence or turn a completed test into an installation authorization.
    """
    if process is None:
        return {'estado': 'nao_iniciado', 'fechamento_forcado': False}
    if process.poll() is not None:
        return {'estado': 'ja_encerrado', 'fechamento_forcado': False}
    pid = getattr(process, 'pid', None)
    if not isinstance(pid, int) or pid <= 0:
        return {'estado': 'pid_indisponivel_fechamento_manual', 'fechamento_forcado': False}
    if ownership_snapshot is not None:
        if not evidence_confirmed:
            return {'estado':'evidencia_nao_confirmada_fechamento_manual', 'pid_qa':pid,
                    'solicitacoes_wm_close':0, 'fechamento_forcado':False}
        return close_verified_qa_client(process, before=ownership_snapshot, timeout=timeout)
    sent = _request_close_owned_sandbox_window(pid)
    if sent == 0:
        return {'estado': 'janela_nao_identificada_fechamento_manual',
                'pid_qa': pid, 'solicitacoes_wm_close': 0, 'fechamento_forcado': False}
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'estado': 'fechamento_pendente_manual', 'pid_qa': pid,
                'solicitacoes_wm_close': sent, 'fechamento_forcado': False}
    return {'estado': 'encerrado_graciosamente', 'pid_qa': pid,
            'solicitacoes_wm_close': sent, 'fechamento_forcado': False}


def build(py:Path,code:Path,lab:Path,label:str,*,is_guest:bool=False, hidden_imports:tuple[str,...]=()):
    import homologador_windows as h
    dist=lab/('DIST_'+label)
    work=lab/('BUILD_'+label)
    log=lab/('BUILD_'+label+'.log')
    env=h.environment_qa(lab)
    for k in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
        env.pop(k,None)
    if is_guest:
        cmd=[str(py),'-B','-m','PyInstaller','--noconfirm','--clean','--onefile',
             '--console','--name','G6B1_GUEST',
             *(f'--hidden-import={module}' for module in hidden_imports),
             '--distpath',str(dist),
             '--workpath',str(work),'--specpath',str(lab/'SPEC_GUEST'),str(code)]
        (lab/'SPEC_GUEST').mkdir(exist_ok=True)
        cwd=lab
    else:
        cmd=[str(py),'-B','-m','PyInstaller','--noconfirm','--clean',
             '--distpath',str(dist),'--workpath',str(work),'VighnaStudy.spec']
        cwd=code
    print(f'ETAPA_G6B1: compilando {label} em laboratório isolado...',flush=True)
    with log.open('wb') as stream:
        proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        try:rc=proc.wait(timeout=MAX_BUILD_SECONDS)
        except subprocess.TimeoutExpired:
            proc.kill();proc.wait()
            raise G6BSafetyError('Timeout PyInstaller: '+label)
    if rc!=0:raise G6BSafetyError('PyInstaller falhou em '+label)
    exe=dist/('G6B1_GUEST.exe' if is_guest else 'VighnaStudy/VighnaStudy.exe')
    if not exe.is_file():raise G6BSafetyError('EXE ausente: '+label)
    return exe


def export_evidence(summary:dict,output:Path,logfiles:list[Path])->Path:
    import homologador_windows as h
    output.mkdir(parents=True,exist_ok=True)
    zipname=output/('G6_B1_DIAGNOSTICO_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
    records={'RESUMO_G6B1.json':json.dumps(summary,indent=2,ensure_ascii=False).encode()}
    for f in logfiles:
        if f.is_file():
            # Only tails of PyInstaller logs, no executables, sources, database or personal files.
            records[f.name+'.txt']=f.read_bytes()[-110_000:]
    for n in ('RESULTADO_G6B1.json','DIAGNOSTICO_SQLITE_G6B1.json',
              'MANIFESTO_G6B1_SHA256.json'):
        f=output/n
        if f.is_file():
            data=f.read_bytes()
            if len(data)>5_000_000:
                raise G6BSafetyError('Diagnostico G6-B1 excedeu o limite seguro: '+n)
            records[n]=data
    records['MANIFESTO_SHA256.json']=json.dumps(
        {k:hashlib.sha256(v).hexdigest() for k,v in records.items()},indent=2).encode()
    with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in records.items():z.writestr(name,data)
    with zipfile.ZipFile(zipname) as z:
        if z.testzip() is not None:raise G6BSafetyError('ZIP de evidências corrompido')
        for name,d in json.loads(z.read('MANIFESTO_SHA256.json')).items():
            if hashlib.sha256(z.read(name)).hexdigest()!=d:
                raise G6BSafetyError('Hash diagnóstico divergente')
    return zipname


def run(py:Path|None=None, *,launch:bool=True)->dict:
    import homologador_windows as h
    if sys.platform!='win32':
        raise G6BSafetyError('Execução real requer Windows com Windows Sandbox instalado')
    h.preflight_selftest()
    ensure_safe(root_qa())
    win=Path(os.environ.get('WINDIR',r'C:\Windows'))/'System32'/'WindowsSandbox.exe'
    if not win.is_file():raise G6BSafetyError('WindowsSandbox.exe não encontrado')
    py=Path(py or sys.executable)
    # Use only the selected interpreter from the QA environment, never copy packages into global Python.
    if not py.is_file():raise G6BSafetyError('Python QA não encontrado')
    base=h.checked_archive(h.KIT/'insumos'/h.BASE)
    patch=h.checked_archive(h.KIT/'insumos'/h.PATCH)
    rc2=h.checked_archive(h.KIT/'insumos'/h.RC2,prefix='codigo/')
    h.inspect_static(base,patch,rc2)
    if 'vighnastudy.ico' not in rc2:raise G6BSafetyError('Ícone para build QA ausente')
    # Inputs from reviewed bundles only. EXE is never copied from user's existing installation.
    lab=root_qa()/('G6B1_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    if lab.exists():raise G6BSafetyError('Execução QA já existe; sobrescrita proibida')
    lab.parent.mkdir(parents=True,exist_ok=True)
    lab.mkdir(exist_ok=False)
    inp=lab/'ENTRADA_SOMENTE_LEITURA'; inp.mkdir()
    out=lab/'SAIDA';out.mkdir()
    logs=[]
    result={'component':'vighna-g6b1-host','version':'3.1.16',
            'target_build':RC2_BUILD,'status':'BLOQUEADO',
            'instalacao_autorizada':False,'gate_g6_aprovado':False,
            'original_engine_exercised_in_guest':False,
            'original_builder_in_guest':False,
            'host_build_R1D':False,'host_build_RC2':False,
            'guest_build_executed':False,'guest_probe_passed':False,
            'windows_sandbox_executado':False,
            'user_db_or_installation_used':False}
    try:
        base=dict(base)
        base['vighnastudy.ico']=rc2['vighnastudy.ico']
        rc2_sources=dict(base)
        rc2_sources.update(patch)
        rc2_sources.pop('manifest.json',None)
        rc2_sources['VighnaStudy.spec']=base['VighnaStudy.spec']
        for label,sources in [('R1D',base),('RC2',rc2_sources)]:
            # create code under disposable QA path, not actual product folder
            sources_dir=lab/('FONTES_'+label)
            h.write_sources(sources,sources_dir)
            built=build(py,sources_dir,lab,label)
            logs.append(lab/('BUILD_'+label+'.log'))
            dist=built.parent
            if sum(p.stat().st_size for p in dist.rglob('*') if p.is_file())>750_000_000:
                raise G6BSafetyError('EXE real QA excedeu 750 MB')
            shutil.copytree(dist,inp/label,symlinks=False)
            result['host_build_'+label]=True
            result['sha256_exe_'+label]=h.digest_file(built)
            print('ETAPA_G6B1: EXE real '+label+' compilado, SHA-256 registrado',flush=True)
        hidden_imports=engine_hidden_imports(base['vighna_update_engine.py'])
        guestexe=build(py,h.KIT/'painel_g6b_guest.py',lab,'GUEST',
                       is_guest=True,hidden_imports=hidden_imports)
        logs.append(lab/'BUILD_GUEST.log')
        logs.append(lab/'PROBE_GUEST.log')
        probe_frozen_guest(guestexe,base['vighna_update_engine.py'],lab)
        result['guest_probe_passed']=True
        print('ETAPA_G6B1: motor original importado no GUEST congelado',flush=True)
        shutil.copy2(guestexe,inp/'G6B1_GUEST.exe')
        for rel in (h.BASE,h.PATCH):
            shutil.copy2(h.KIT/'insumos'/rel,inp/rel)
        files={p.relative_to(inp).as_posix():h.digest_file(p)
               for p in sorted(inp.rglob('*')) if p.is_file()}
        (inp/'MANIFESTO_G6B1.json').write_text(json.dumps({
            'component':'vighna-g6b1-input','version':'3.1.16',
            'target_build':RC2_BUILD,'sha256_files':files,
            'instalacao_autorizada':False,'compiled_engine_bundled':False},indent=2),encoding='utf-8')
        config=lab/'G6B1_SOMENTE_SANDBOX.wsb'
        config.write_text(sandbox_xml(inp,out),encoding='utf-8')
        result['guest_build_executed']=True
        result['status']='PREPARADO_NAO_EXECUTADO'
        if launch:
            print('ETAPA_G6B1: iniciando Windows Sandbox isolado, sem rede e clipboard',flush=True)
            try: sandbox_before = sandbox_processes_qa()
            except (OSError, subprocess.SubprocessError, G6BSafetyError): sandbox_before = None
            proc=subprocess.Popen([str(win),str(config)],cwd=lab)
            try:
                start=time.monotonic()
                while time.monotonic()-start<MAX_SANDBOX_SECONDS:
                    report=out/'RESULTADO_G6B1.json'
                    manifest=out/'MANIFESTO_G6B1_SHA256.json'
                    if report.is_file() and manifest.is_file():
                        blob=report.read_bytes()
                        checks=json.loads(manifest.read_text(encoding='utf-8-sig'))
                        if checks.get('RESULTADO_G6B1.json')!=hashlib.sha256(blob).hexdigest():
                            raise G6BSafetyError('SHA-256 guest inválido')
                        sqlite_diagnostic=out/'DIAGNOSTICO_SQLITE_G6B1.json'
                        if (not sqlite_diagnostic.is_file() or
                            checks.get('DIAGNOSTICO_SQLITE_G6B1.json')!=
                                hashlib.sha256(sqlite_diagnostic.read_bytes()).hexdigest()):
                            raise G6BSafetyError('Diagnostico SQLite guest ausente ou invalido')
                        guest=json.loads(blob.decode('utf-8-sig'))
                        if (guest.get('component')!='vighna-g6b1-guest'
                            or guest.get('target_build')!=RC2_BUILD
                            or guest.get('instalacao_autorizada') is not False
                            or guest.get('gate_g6_aprovado') is not False):
                            raise G6BSafetyError('Relatório guest incoerente')
                        result['guest']=guest
                        result['windows_sandbox_executado']=guest.get('windows_sandbox_executado') is True
                        result['original_engine_exercised_in_guest']=(
                            guest.get('engine_original_qa') is True and bool(guest.get('cenarios')))
                        result['status']=guest.get('status','BLOQUEADO')
                        break
                    if proc.poll() is not None:
                        raise G6BSafetyError('Windows Sandbox encerrou antes do diagnóstico')
                    time.sleep(3)
                else:raise G6BSafetyError('Timeout de resposta Windows Sandbox')
            finally:
                try:
                    result['encerramento_sandbox'] = close_own_sandbox(
                        proc, ownership_snapshot=sandbox_before if sandbox_before is not None else {},
                        evidence_confirmed=(sandbox_before is not None
                            and result.get('windows_sandbox_executado') is True
                            and result.get('original_engine_exercised_in_guest') is True))
                    if 'manual' in result['encerramento_sandbox']['estado']:
                        print('ETAPA_G6B1: Sandbox permanece aberto; feche pela janela X quando conveniente.',flush=True)
                except Exception as exc:
                    result['erro_encerramento_sandbox'] = str(exc)[:300]
    except Exception as error:
        result['status']='FALHOU_OU_BLOQUEADO';result['motivo']=str(error)[:600]
    finally:
        # Keep the lab; deleting while Sandbox has mapped it would invalidate the report.
        zipname=export_evidence(result,out,logs)
        print('ZIP DE DIAGNOSTICO CRIADO: '+str(zipname),flush=True)
        print('STATUS G6-B1: '+result['status']+'; G6-B2 E G7 PENDENTES.',flush=True)
    return result


if __name__=='__main__':
    try:
        x=run()
        sys.exit(0 if x['status']=='PASSOU_B1_EXECUTAVEIS_REAIS' else 1)
    except Exception as exc:
        print('ETAPA_G6B1: BLOQUEADO: '+str(exc),file=sys.stderr,flush=True)
        sys.exit(1)
