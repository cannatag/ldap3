$Strategies = @('SYNC', 'ASYNC')
$Servers = @('EDIR')
$Decoders = @('INTERNAL', 'EXTERNAL')
$Booleans = @('TRUE', 'FALSE')

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
    $env:PYTHONIOENCODING="utf-8"

    if ($Python -eq "2.7") {
        py -2.7 -m unittest discover -s test -c
    }
    elseif ($Python -eq "3.8") {
        .\venv\Scripts\python -m unittest discover -s test -c
    }
    else {
        Write-Host "Unknown Python version " + $Python
    }
}

function RunAllTestWithPythonVersion
{
    param(
        [string]$Python
    )

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
                            Write-Host "Running -Python $Python -Strategy $Strategy -Server $Server -Lazy $Lazy -Logging $Logging -CheckNames $CheckName -Decoder $Decoder"
                            RunTestSuite -Python $Python -Strategy $Strategy -Server $Server -Lazy $Lazy -Logging $Logging -CheckNames $CheckName -Decoder $Decoder
                            Write-Host "Done. ***********"
                        }
                    }
                }
            }
        }
    }
}
#
#RunTestSuite -Python 4.2 -Strategy SYNC -Server EDIR -Lazy FALSE -Logging FALSE -CheckNames TRUE -Decoder INTERNAL
#RunTestSuite -Python 3.8 -Strategy SYNC -Server EDIR -Lazy FALSE -Logging FALSE -CheckNames TRUE -Decoder INTERNAL
#RunTestSuite -Python 2.7 -Strategy SYNC -Server EDIR -Lazy FALSE -Logging FALSE -CheckNames TRUE -Decoder INTERNAL
#RunTestSuite -Python 2.6 -Strategy SYNC -Server EDIR -Lazy FALSE -Logging FALSE -CheckNames TRUE -Decoder INTERNAL
#
RunAllTestWithPythonVersion('3.8')