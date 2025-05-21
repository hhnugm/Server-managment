@echo -off
  
#set Startup delay time for 0 sec
#=======================
set StartupDelay 0
#=======================
 
# if Counter not set 
#======================= 
if "%Counter%" == "" then
  set Counter 1
endif
#=======================
 
# set Counter+1
#=======================
for %a run (%Counter% 1%Counter%)
  set Counter+1 %a
  if "%Counter%" ne "%a" then
    goto Leave_For
  endif
endfor
#=======================
  
#Wait for 3 sec then system warm reboot
#=======================
:Leave_For
 echo Loop Cycle = %Counter%
 set Counter %Counter+1%
 set -d Counter+1
 stall 3000000
 reset -w
#=======================
