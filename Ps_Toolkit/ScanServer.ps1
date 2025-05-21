#The Start-Job command uses the Test-Connection cmdlet to ping many computers in an enterprise. The value of the TargetName parameter is a Get-Content command that reads a list of computer names from the Servers.txt file. The command uses the Start-Job cmdlet to run the command as a background job and it saves the job in the $job variable.
#The Receive-Job command is instructed to -Wait until the job is completed, and then gets the results and stores them in the $Results variable.#

$job = Start-Job -ScriptBlock { Test-Connection -TargetName (Get-Content -Path "Servers.txt") }
$Results = Receive-Job $job -Wait
