"""Read only driver metadata for the known owned hold probe; no process memory/token reads."""
import ctypes as C,json
from pathlib import Path
R=Path(r'D:\PV1Lab');p=R/'boxes'/'PV1Lab_StandardTest'/'drive'/'D'/'PV1Lab'/'staging'/'owned-standard-payload'/'hold-results.json'
h=json.loads(p.read_text());assert not h['complete']
d=C.WinDLL(str(R/'tools'/'Sandboxie-Plus'/'SbieDll.dll'))
f=d.SbieApi_QueryProcessInfo;f.argtypes=[C.c_void_p,C.c_uint32];f.restype=C.c_uint64
flags=f(h['pid'],0)
data={'pid':h['pid'],'flags':hex(flags),'valid_process':bool(flags&1),'app_compartment':bool(flags&0x01000000),'privacy_mode':bool(flags&0x02000000),'rule_specificity':bool(flags&0x04000000),'drop_rights_configured':bool(flags&0x80),'rights_dropped':bool(flags&0x100)}
(R/'reports'/'standard_driver_flags.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
assert data['valid_process'] and not data['app_compartment'] and not data['rule_specificity']
