import subprocess,sys,time
from pathlib import Path
p=Path(sys.argv[1])
if len(sys.argv)==2:
    subprocess.Popen([sys.executable,'-B',__file__,str(p),'child'],creationflags=subprocess.CREATE_NO_WINDOW)
else:
    (p/'output'/'child_started.txt').write_text('owned child, no credentials')
    until=time.monotonic()+10
    while time.monotonic()<until and not (p/'temp'/'stop.request').exists(): time.sleep(.1)
    (p/'output'/'child_stopped.txt').write_text('cooperative exit')
