#!/usr/bin/env python3
import pathlib,subprocess,os
p=pathlib.Path('/home/alokgarg/market_lab/tools/iverilog-13.0')
def run(cmd,cwd=p,env=None):
 print('RUN',cmd,flush=True);subprocess.run(cmd,cwd=cwd,env=env,check=True)
src=p/'source'
if not src.exists():run(['git','clone','--depth','1','--branch','v13_0','https://github.com/steveicarus/iverilog.git',str(src)])
deps=p/'build-dependencies';deps.mkdir(exist_ok=True)
run(['apt-get','download','bison','flex','gperf','m4','libfl2','libfl-dev'],cwd=deps)
for deb in deps.glob('*.deb'):run(['dpkg-deb','-x',str(deb),str(deps/'root')])
env=dict(os.environ);env['PATH']=str(deps/'root/usr/bin')+':'+env['PATH'];env['BISON_PKGDATADIR']=str(deps/'root/usr/share/bison');env['M4']=str(deps/'root/usr/bin/m4')
run(['sh','autoconf.sh'],cwd=src,env=env)
run(['./configure','--prefix='+str(p/'installed')],cwd=src,env=env)
run(['make','-j2'],cwd=src,env=env)
run(['make','install'],cwd=src,env=env)
print('INSTALL COMPLETE',flush=True)
