@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: Pega o diretorio onde este .bat esta localizado (ex: a pasta .continue)
set "CONTINUE_DIR=%~dp0"
:: Remove a barra invertida do final
if "%CONTINUE_DIR:~-1%"=="\" set "CONTINUE_DIR=%CONTINUE_DIR:~0,-1%"

:: Pega o diretorio pai (que eh a raiz do Workspace)
for %%I in ("%CONTINUE_DIR%\..") do set "WORKSPACE_ROOT=%%~fI"

echo ====================================================
echo  Configurador Dinamico da AI Workspace Bridge
echo ====================================================
echo.
echo Identificado que este ambiente portable esta em:
echo %WORKSPACE_ROOT%
echo.
echo Atualizando as tags ^<BRIDGE_WORKSPACE^> nos agentes...
echo.

:: Executa um bloco de PowerShell para fazer o regex-replace em arquivos .yaml e .prompt
set "PS_SCRIPT=$root = '%WORKSPACE_ROOT%'; $rootEscaped = $root -replace '\\', '\\\\'; $files = Get-ChildItem -Path '%CONTINUE_DIR%' -Include *.yaml, *.prompt -Recurse -File; $count = 0; foreach ($f in $files) { $content = Get-Content -LiteralPath $f.FullName -Raw; $pattern = '(?s)(?i)<BRIDGE_WORKSPACE>.*?</BRIDGE_WORKSPACE>'; if ($content -match $pattern) { $newContent = [regex]::Replace($content, $pattern, ('<BRIDGE_WORKSPACE>' + $rootEscaped + '</BRIDGE_WORKSPACE>')); Set-Content -LiteralPath $f.FullName -Value $newContent -NoNewline -Encoding UTF8; Write-Host '  [ OK ] Atualizado:' $f.Name; $count++ } }; if ($count -eq 0) { Write-Host '  Nenhuma tag <BRIDGE_WORKSPACE> encontrada nos arquivos.' }"

powershell -NoProfile -Command "%PS_SCRIPT%"

echo.
echo ====================================================
echo Atualizacao concluida com sucesso!
echo ====================================================
pause
