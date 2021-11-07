import sys, os, math

if len(sys.argv) < 2:
    print("usage: PerfMon.py <data.csv>")
    exit(0)
target = sys.argv[1]
if not os.path.exists(target):
    print(f'target file \'{target}\' could not be found!')
    exit(0)
raw = open(target, 'r')
row = raw.readline()

cols = {}
for i, name in enumerate(row.strip().split(",")):
    cols[name.strip()] = i

print(cols)

data = {}

while row := raw.readline():
    split = row.strip().split(",")
    date = split[cols['date_time']].strip()
    uptime = int(split[cols['uptime_seconds']].strip())
    tps = float(split[cols['ticks_per_second']].strip())
    ticklen = float(split[cols['tick_length_ms']].strip())
    pcount = round(float(split[cols['player_count']].strip()))
    totalmem = int(split[cols['total_memory']].strip())
    usedmem = int(split[cols['used_memory']].strip())
    freemem = int(split[cols['free_memory']].strip())
    cpu = float(split[cols['cpu_usage']].strip())
    
    if not pcount in data:
        data[pcount] = {'count':0,'tps':0,'ticklen':0,'totalmem':0,'usedmem':0,'freemem':0,'cpu':0}
    data[pcount]['tps'] = ((data[pcount]['tps']*data[pcount]['count'])+tps)/(data[pcount]['count']+1)
    data[pcount]['ticklen'] = ((data[pcount]['ticklen']*data[pcount]['count'])+ticklen)/(data[pcount]['count']+1)
    data[pcount]['totalmem'] = ((data[pcount]['totalmem']*data[pcount]['count'])+totalmem)/(data[pcount]['count']+1)
    data[pcount]['usedmem'] = ((data[pcount]['usedmem']*data[pcount]['count'])+usedmem)/(data[pcount]['count']+1)
    data[pcount]['freemem'] = ((data[pcount]['freemem']*data[pcount]['count'])+freemem)/(data[pcount]['count']+1)
    data[pcount]['cpu'] = ((data[pcount]['cpu']*data[pcount]['count'])+cpu)/(data[pcount]['count']+1)
    data[pcount]['count'] += 1

processed = {}

for key in sorted(data):
    set = data[key]
    processed[key] = {'tps':set['tps'],'ticklen':set['ticklen'],'usedmem':set['usedmem'],'usedmemp':set['usedmem']/set['totalmem']*100,'cpu':set['cpu']*100,'core':set['cpu']*100*8}
    print(f'========[ Players: {key} ]========')
    print(f'TPS:            {set["tps"]:6.2f}')
    print(f'Tick Length:    {set["ticklen"]:6.2f}ms')
    print(f'Used Memory:    {set["usedmem"]/set["totalmem"]*100:6.2f}% ({set["usedmem"]/(1024**2):6.2f}MB)')
    print(f'CPU Usage:      {set["cpu"]*100:6.2f}%')
    print(f'CPU Core Usage: {set["cpu"]*100*8:6.2f}%')

print('\n\n========[ Delta From Idle ]========')

for key in sorted(processed):
    if key == 0:
        continue
    set = processed[key]
    print(f'========[ Players: {key} ]========')
    print(f'TPS:            {set["tps"]-processed[0]["tps"]:6.2f}')
    print(f'Tick Length:    {set["ticklen"]-processed[0]["ticklen"]:6.2f}ms')
    print(f'Used Memory:    {set["usedmemp"]-processed[0]["usedmemp"]:6.2f}% ({(set["usedmem"]-processed[0]["usedmem"])/(1024**2):6.2f}MB)')
    print(f'CPU Usage:      {set["cpu"]-processed[0]["cpu"]:6.2f}%')
    print(f'CPU Core Usage: {set["core"]-processed[0]["core"]:6.2f}%')

print('\n\n========[ Delta From Idle Per Player ]========')

avgdeltapp = {'count':0,'tps':0,'ticklen':0,'usedmem':0,'usedmemp':0,'cpu':0,'core':0}

for key in sorted(processed):
    if key == 0:
        continue
    set = processed[key]
    avgdeltapp['tps'] = ((avgdeltapp['tps']*avgdeltapp['count'])+(set["tps"]-processed[0]["tps"])/key)/(avgdeltapp['count']+1)
    avgdeltapp['ticklen'] = ((avgdeltapp['ticklen']*avgdeltapp['count'])+(set["ticklen"]-processed[0]["ticklen"])/key)/(avgdeltapp['count']+1)
    avgdeltapp['usedmem'] = ((avgdeltapp['usedmem']*avgdeltapp['count'])+(set["usedmem"]-processed[0]["usedmem"])/key)/(avgdeltapp['count']+1)
    avgdeltapp['usedmemp'] = ((avgdeltapp['usedmemp']*avgdeltapp['count'])+(set["usedmemp"]-processed[0]["usedmemp"])/key)/(avgdeltapp['count']+1)
    avgdeltapp['cpu'] = ((avgdeltapp['cpu']*avgdeltapp['count'])+(set["cpu"]-processed[0]["cpu"])/key)/(avgdeltapp['count']+1)
    avgdeltapp['core'] = ((avgdeltapp['core']*avgdeltapp['count'])+(set["core"]-processed[0]["core"])/key)/(avgdeltapp['count']+1)
    avgdeltapp['count'] += 1
    
    print(f'========[ Players: {key} ]========')
    print(f'TPS:            {(set["tps"]-processed[0]["tps"])/key:6.2f}')
    print(f'Tick Length:    {(set["ticklen"]-processed[0]["ticklen"])/key:6.2f}ms')
    print(f'Used Memory:    {(set["usedmemp"]-processed[0]["usedmemp"])/key:6.2f}% ({(set["usedmem"]-processed[0]["usedmem"])/(1024**2)/key:6.2f}MB)')
    print(f'CPU Usage:      {(set["cpu"]-processed[0]["cpu"])/key:6.2f}%')
    print(f'CPU Core Usage: {(set["core"]-processed[0]["core"])/key:6.2f}%')

print('\n\n========[ Avg Delta From Idle Per Player ]========')
print(f'TPS:            {avgdeltapp["tps"]:6.2f}')
print(f'Tick Length:    {avgdeltapp["ticklen"]:6.2f}ms')
print(f'Used Memory:    {avgdeltapp["usedmemp"]:6.2f}% ({avgdeltapp["usedmem"]/(1024**2):6.2f}MB)')
print(f'CPU Usage:      {avgdeltapp["cpu"]:6.2f}%')
print(f'CPU Core Usage: {avgdeltapp["core"]:6.2f}%')

raw.close()