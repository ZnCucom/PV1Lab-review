import ctypes as C,subprocess,sys,time
from pathlib import Path
import lab
from native_snapshot_test import preflight,drain,R,SB,BOX,P
run=Path(sys.argv[1]);preflight();drain()
U=C.WinDLL('user32');metadata={'unicode_available':bool(U.IsClipboardFormatAvailable(13)),'sequence':U.GetClipboardSequenceNumber()}
name='peripheral-'+run.name+'.json'
p=subprocess.Popen([str(SB/'Start.exe'),'/box:'+BOX,'/silent','/hide_window','/wait','/env:TEMP='+str(P),'/env:TMP='+str(P),str(P/'peripheral_probe.exe'),str(P/name)],cwd=P)
assert p.wait(timeout=40)==0;drain()
got=lab.read(R/'boxes'/BOX/'drive/D/PV1Lab/staging/owned-standard-payload'/name)
post={'unicode_available':bool(U.IsClipboardFormatAvailable(13)),'sequence':U.GetClipboardSequenceNumber()}
report={'probe':got,'host_before':metadata,'host_after':post,'scope':'API handle presence and format metadata only; never read or change clipboard content, disk bytes, real input or screen','run_id':run.name,'box_active_processes':0}
report['status']='PASS' if got.get('clipboard_open') and got.get('unicode_format_available') and not got.get('clipboard_data_handle_available') and metadata==post and metadata['unicode_available'] and got['physical_drive_0_open_error']==got['physical_drive_1_open_error']==5 else 'INCONCLUSIVE_OR_FAIL'
lab.save(R/'reports/peripheral_results.json',report)
assert report['status']=='PASS',report
