#取值轉字串放入變數
$DHCP_Service = get-service DHCPServer | Out-String
$DHCP_Status = Get-DhcpServerv4ScopeStatistics -ComputerName dhcp02.unimicron.com | Out-String

#合併兩變數內的string
$StringMerge01 = $DHCP_Service + $DHCP_Status

#取Service運行值，備於填入郵件主旨
$SubjectService = get-service DHCPServer |select Status 


#backup conifg
Backup-DhcpServer -ComputerName "dhcp02.unimicron.com" -Path "C:\JOBS\DHCP_backup"

 ### Smtp setup

$smtp = "smtp.gmail.com"
$from = (hostname) + "_DHCPStatus@gmail.com"
$to = "hhnugm@gmail.com"
$CC = "hhnugm@gmail.com"
$date = Get-Date -Format yyyMMdd_HH:mm
$subject = "DHCP  $SubjectService "
$encoding = [System.Text.Encoding]::UTF8

 ### dhcp設定檔備份附件
 #$atcm1= "C:\JOBS\DHCP_backup\DhcpCfg"
  

#### Send Email

 send-MailMessage -SmtpServer $smtp -From $from -To $to -Cc $cc -Subject $subject  -Encoding $encoding -Body  $StringMerge01 #-Attachments $atcm1
