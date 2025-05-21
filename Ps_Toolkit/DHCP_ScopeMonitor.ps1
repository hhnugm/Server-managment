#目的是為了確認取得IP的client 是否皆為公司規範定義的hostname，或是否有異質設備嘗試取用IP
#查詢10.20.200.0/24領域下的清單，與IP租約到期日
#因為檢查目標是hostname，所以使用sort-object排序，預設模式為升冪，若要改降冪則需增加 -Descending

$String01 = Get-DhcpServerv4Lease -ComputerName QHTJYDHCP02.unimicron.com -ScopeId 10.20.200.0 | Sort-Object Hostname | Out-String


 ### Smtp setup

$smtp = "smtp.gmail.com"
$from = (hostname) + "_DHCPStatus@gmail.com"
$to = "Dean_zhong@gmail.com"
$CC = "Dean_zhong@gmail.com"
$date = Get-Date -Format yyyMMdd_HH:mm
$subject = "DHCP Scope 10.20.200.0/24  Status@ $date "
$encoding = [System.Text.Encoding]::UTF8
  

#### Send Email

 send-MailMessage -SmtpServer $smtp -From $from -To $to -Cc $cc -Subject $subject  -Encoding $encoding -Body  $String01 #-Attachments $atcm1
