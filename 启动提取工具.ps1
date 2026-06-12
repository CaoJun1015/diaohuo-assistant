# 联想配置提取工具启动器
# 这个脚本会自动检测环境并启动提取工具

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   联想配置提取工具" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
Write-Host "[1/4] 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "  [错误] Python未安装或未配置PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "  解决方法：" -ForegroundColor Yellow
    Write-Host "  1. 下载Python: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. 安装时勾选 'Add Python to PATH'" -ForegroundColor White
    Write-Host ""
    Read-Host "按Enter键退出"
    exit 1
}

# 检查python-docx
Write-Host ""
Write-Host "[2/4] 检查python-docx模块..." -ForegroundColor Yellow
python -c "import docx" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  未安装，正在安装..." -ForegroundColor Yellow
    pip install python-docx
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  安装成功!" -ForegroundColor Green
    } else {
        Write-Host "  [错误] 安装失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
} else {
    Write-Host "  已安装" -ForegroundColor Green
}

# 检查脚本
Write-Host ""
Write-Host "[3/4] 检查提取脚本..." -ForegroundColor Yellow
$scriptPath = Join-Path $PSScriptRoot "extract_lenovo_config.py"
if (Test-Path $scriptPath) {
    Write-Host "  脚本存在" -ForegroundColor Green
} else {
    Write-Host "  [错误] extract_lenovo_config.py 不存在" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 询问输入文件
Write-Host ""
Write-Host "[4/4] 选择文件..." -ForegroundColor Yellow
Add-Type -AssemblyName System.Windows.Forms
$openFile = New-Object System.Windows.Forms.OpenFileDialog
$openFile.Filter = "Word文档 (*.docx)|*.docx"
$openFile.Title = "选择Word文档"

if ($openFile.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    $inputFile = $openFile.FileName
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($inputFile)
    $outputFile = Join-Path ([System.IO.Path]::GetDirectoryName($inputFile)) "${fileName}_联想配置.docx"
    
    Write-Host ""
    Write-Host "输入文件: $inputFile" -ForegroundColor Cyan
    Write-Host "输出文件: $outputFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "开始提取..." -ForegroundColor Green
    Write-Host ""
    
    # 执行Python脚本
    Set-Location $PSScriptRoot
    python extract_lenovo_config.py "`"$inputFile`"" "`"$outputFile`""
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "提取完成！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "输出文件: $outputFile" -ForegroundColor Cyan
        Write-Host ""
        
        # 打开输出文件
        Start-Process $outputFile
    } else {
        Write-Host ""
        Write-Host "[错误] 提取失败" -ForegroundColor Red
    }
} else {
    Write-Host "已取消" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "按Enter键退出"
