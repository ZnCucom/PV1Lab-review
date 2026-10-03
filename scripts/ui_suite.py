"""Exercise only a newly-created hidden synthetic host window; never user windows."""
import json,subprocess,sys,time
from pathlib import Path
import lab
R=lab.ROOT;run=Path(sys.argv[1]);payload=R/'staging'/'owned-standard-payload';ready=run/'output'/'ui-host-ready.txt';stop=run/'temp'/'ui-host-stop.request';box='PV1Lab_StandardTest'
host=subprocess.Popen([str(payload/'ui_canary.exe'),'host',str(ready),str(stop)],cwd=run)
deadline=time.monotonic()+10
try:
    while not ready.exists():
        assert time.monotonic()<deadline and host.poll() is None,'host window initialization failed'
        time.sleep(.1)
    hostpid,hwnd=ready.read_text().split();assert int(hostpid)==host.pid
    args=[str(R/'tools'/'Sandboxie-Plus'/'Start.exe'),'/box:'+box,'/silent','/hide_window','/wait',str(payload/'ui_canary.exe'),'probe',hostpid,hwnd,str(payload/'ui-results.json')]
    probe=subprocess.Popen(args,cwd=payload);code=probe.wait(timeout=20);assert code==0
finally:
    stop.write_text('owned-window cooperative exit')
    host.wait(timeout=10)
data=lab.read(R/'boxes'/box/'drive'/'D'/'PV1Lab'/'staging'/payload.name/'ui-results.json');data['host']=lab.read(Path(str(ready)+'.json'))
data['scope']='Own synthetic window only; no real keyboard events, desktop pixels, clipboard contents or other user windows read'
lab.save(R/'reports'/'standard_ui_results.json',data)
assert data['sbie_loaded']
assert data['host_process_open_error']==5 or (data['handle_query_status']==0 and not data['host_process_granted_access']&0x30),'host memory access rights not blocked'
assert not data['send_message_succeeded'] and data['host']['host_messages_received']==0
assert not data['own_window_print_succeeded']
