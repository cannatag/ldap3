$PythonVersions = @('3.9', '2.7')
$Strategies = @('SYNC', 'ASYNC', 'SAFE_SYNC', 'RESTARTABLE', 'SAFE_RESTARTABLE')
$Servers = @('EDIR')
$Decoders = @('INTERNAL', 'EXTERNAL')
$Booleans = @('TRUE', 'FALSE')
$OnlyTrue = @('TRUE')
$OnlyFalse = @('FALSE')

$env:VERBOSE="FALSE"
$env:PYTHONIOENCODING="utf-8"
#$env:PYTHONTRACEMALLOC=2

function RunTestSuite
{
    param(
        [string]$Python,
        [string]$Strategy,
        [string]$Server,
        [string]$Lazy,
        [string]$Logging,
        [string]$CheckNames,
        [string]$Decoder
    )

    $env:STRATEGY=$Strategy
    $env:SERVER=$Server
    $env:LAZY=$Lazy
    $env:LOGGING=$Logging
    $env:CHECK_NAMES=$CheckNames
    $env:DECODER=$Decoder
    
    if ($Python -eq "2.7") {
        py -2.7 -m unittest discover -s test -c
    }
    elseif ($Python -eq "3.9") {
        .\venv\Scripts\python -m unittest discover -s test -c
    }
        elseif ($Python -eq "2.6") {
            $env:PYTHONIOENCODING="UTF8"
            .\venv\Scripts\python -m unittest discover -s test -c
    }
    else {
        Write-Host "Unknown Python version " + $Python
    }
}

function RunAllSuites
{
    param(
        [bool]$DryRun
    )
    $counter=0
    foreach ($Python in $PythonVersions)
    {
        foreach ($Strategy in $Strategies)
        {
            foreach ($Server in $Servers)
            {
                foreach ($Lazy in $Booleans)
                {
                    foreach ($Logging in $Booleans)
                    {
                        foreach ($CheckName in $Booleans)
                        {
                            foreach ($Decoder in $Decoders)
                            {
                                $counter++
                                if (-not $DryRun)
                                {
                                    Write-Host "RUNNING $counter  -Python $Python -Strategy $Strategy -Server $Server -Lazy $Lazy -Logging $Logging -CheckNames $CheckName -Decoder $Decoder"
                                    RunTestSuite -Python $Python -Strategy $Strategy -Server $Server -Lazy $Lazy -Logging $Logging -CheckNames $CheckName -Decoder $Decoder
                                    Write-Host "Done."
                                }
                                else {
                                    Write-Host "DRYRUN $counter  -Python $Python -Strategy $Strategy -Server $Server -Lazy $Lazy -Logging $Logging -CheckNames $CheckName -Decoder $Decoder"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

RunAllSuites -Dryrun $true
RunAllSuites -Dryrun $false