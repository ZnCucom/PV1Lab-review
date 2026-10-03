import ctypes as c, json, os
from pathlib import Path
r=Path(r'D:\PV1Lab'); d=c.WinDLL(str(r/'tools/Sandboxie-Plus/SbieDll.dll')); u=c.c_ulong
f=d.SbieApi_GetMessage;f.argtypes=[c.POINTER(u),u,c.POINTER(u),c.POINTER(u),c.c_wchar_p,u];f.restype=u
sid=u();c.windll.kernel32.ProcessIdToSessionId(os.getpid(),c.byref(sid));n=u(0);rows=[]
for i in range(100):
 mid=u();pid=u();b=c.create_unicode_buffer(4096);status=f(c.byref(n),sid,c.byref(mid),c.byref(pid),b,c.sizeof(b))
 if status:break
 rows.append({'number':n.value,'id':mid.value,'pid':pid.value,'text':b[:].rstrip('\0').replace('\0',' | ')})
(r/'reports/owned-launch-diagnostics.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows[-15:],indent=2))
