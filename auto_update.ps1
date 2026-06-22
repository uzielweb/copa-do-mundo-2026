$ErrorActionPreference = "Continue"
$repoPath = "d:\laragon\www\github\copa-do-mundo-2026"

try {
    Set-Location $repoPath

    # Exibir notificação do Windows de início
    Add-Type -AssemblyName System.Windows.Forms
    $balloon = New-Object System.Windows.Forms.NotifyIcon
    $balloon.Icon = [System.Drawing.SystemIcons]::Information
    $balloon.BalloonTipIcon = "Info"
    $balloon.BalloonTipTitle = "Copa do Mundo 2026"
    $balloon.BalloonTipText = "A rotina automática de atualização de vídeos foi iniciada em segundo plano."
    $balloon.Visible = $true
    $balloon.ShowBalloonTip(5000)

    Write-Output "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Iniciando rotina de atualização automática..."

    # Executa a busca de novos vídeos do YouTube e download se aplicável
    Write-Output "Rodando update_cup_videos.py..."
    python update_cup_videos.py --download

    # Prepara os arquivos para commit
    git add .

    # Verifica se houve alguma alteração real nos arquivos
    $status = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Output "Nenhuma atualização encontrada. Encerrando."
        $balloon.Dispose()
        exit 0
    }

    # Se houver alterações, realiza o commit
    Write-Output "Alterações detectadas. Realizando commit..."
    $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Auto-update videos: $dateStr"

    # Envia para a branch principal (main)
    Write-Output "Enviando dados para a branch 'main'..."
    git push origin main

    # Realiza o merge na branch gh-pages e faz o push
    Write-Output "Atualizando a branch 'gh-pages' via merge..."
    git checkout gh-pages
    git merge main
    git push origin gh-pages

    # Retorna para a branch principal
    Write-Output "Retornando para a branch 'main'..."
    git checkout main

    # Exibir notificação de sucesso
    $balloon.BalloonTipText = "Novos vídeos encontrados e enviados para o GitHub com sucesso!"
    $balloon.ShowBalloonTip(5000)

    Write-Output "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Processo concluído com sucesso!"
    Start-Sleep -Seconds 5
    $balloon.Dispose()
} catch {
    Write-Error "Ocorreu um erro durante a execução: $_"
    if ($balloon) { $balloon.Dispose() }
}
