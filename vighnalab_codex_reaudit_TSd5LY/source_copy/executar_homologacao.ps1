param(
    [ValidateSet("testes","build")][string]$Modo = "testes"
)
$ErrorActionPreference = "Stop"
$Raiz = $PSScriptRoot
Set-Location -LiteralPath $Raiz
$Inicio = Get-Date
$DataId = $Inicio.ToString("yyyyMMdd_HHmmss")
$Log = Join-Path $Raiz ("DIAGNOSTICO_ULTIMA_EXECUCAO_" + $DataId + ".txt")
$Codigo = 1
$Transcricao = $false

try {
    try {
        Start-Transcript -LiteralPath $Log -Force | Out-Null
        $Transcricao = $true
    } catch {
        ("Falha ao iniciar transcricao PowerShell: " + $_.Exception.Message) |
          Out-File -LiteralPath $Log -Encoding UTF8 -Force
    }

    Write-Host "VighnaStudy Homologador Windows V1.1 / $Modo"
    Write-Host "Pasta de resultados esperada: $Raiz"
    Write-Host "Nenhum arquivo sera instalado no VighnaStudy principal."
    Write-Host "Se o Python falhar, sera criado um ZIP de diagnostico."

    try {
        $Identidade = [Security.Principal.WindowsIdentity]::GetCurrent()
        $Principal = New-Object Security.Principal.WindowsPrincipal($Identidade)
        if ($Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            Write-Warning "CMD aberto como Administrador. O homologador nao precisa de elevacao. Prefira executa-lo sem Administrador."
        }
    } catch { }

    $CaminhoScript = Join-Path $Raiz "homologador_windows.py"
    if (-not (Test-Path -LiteralPath $CaminhoScript)) {
        throw "Pacote incompleto: homologador_windows.py ausente. Extraia o ZIP completo primeiro."
    }

    $Tentativas = @(
        @{ Comando = "py"; Argumentos = @("-3.13") },
        @{ Comando = "py"; Argumentos = @("-3") },
        @{ Comando = "python"; Argumentos = @() }
    )
    $Selecionado = $null
    foreach ($Tentativa in $Tentativas) {
        try {
            $ComandoTeste = $Tentativa.Comando
            $ArgumentosTeste = @($Tentativa.Argumentos)
            & $ComandoTeste @ArgumentosTeste "-c" "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $Selecionado = $Tentativa
                break
            }
        } catch {
            continue
        }
    }
    if ($null -eq $Selecionado) {
        throw "Python 3.11 ou superior nao encontrado. Nao foi instalado nada."
    }

    $ComandoPython = $Selecionado.Comando
    $ParametrosPython = @($Selecionado.Argumentos)
    Write-Host ("Usando Python: " + $ComandoPython + " " + ($ParametrosPython -join " "))

    & $ComandoPython @ParametrosPython "-B" "-X" "utf8" $CaminhoScript "--modo" $Modo
    $Codigo = $LASTEXITCODE
    Write-Host ("Processo Python finalizou com codigo " + $Codigo)
} catch {
    Write-Host ("BLOQUEADO: " + $_.Exception.Message)
    $Codigo = 1
} finally {
    if ($Transcricao) {
        try { Stop-Transcript | Out-Null } catch {}
    }
}

# Uma falha na fase inicial do Python ou mesmo um encerramento abrupto
# deve produzir ao menos um ZIP de diagnostico localizavel.
$ZipsNovos = @(Get-ChildItem -LiteralPath $Raiz -File -Filter "RESULTADOS_HOMOLOGACAO_WINDOWS_*.zip" -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $Inicio.AddSeconds(-2) })
if ($ZipsNovos.Count -eq 0) {
    $ZipEmergencia = Join-Path $Raiz ("RESULTADOS_HOMOLOGACAO_WINDOWS_DIAGNOSTICO_" + $DataId + ".zip")
    Write-Host "Nenhum ZIP de resultados foi encontrado. Criando pacote de diagnostico de emergencia."
    try {
        if (-not (Test-Path -LiteralPath $Log)) {
            ("Nenhum log de transcricao foi gerado. Codigo de saida: " + $Codigo) |
                Out-File -LiteralPath $Log -Encoding UTF8 -Force
        }
        Compress-Archive -LiteralPath $Log -DestinationPath $ZipEmergencia -CompressionLevel Optimal -Force -ErrorAction Stop
        Write-Host "ZIP DE DIAGNOSTICO:" $ZipEmergencia
    } catch {
        Write-Host ("Falha ao empacotar log: " + $_.Exception.Message)
        Write-Host "ARQUIVO DE DIAGNOSTICO TXT:" $Log
    }
    if ($Codigo -eq 0) { $Codigo = 3 }
} else {
    Write-Host "ZIP DE RESULTADOS:"
    foreach ($Arquivo in $ZipsNovos) {
        Write-Host $Arquivo.FullName
    }
}

Write-Host ""
Write-Host "Status do Windows nao autoriza instalacao do M2."
Write-Host "Envie o ZIP de resultados/diagnostico ao ChatGPT."
exit $Codigo
