import subprocess

f = open('data.txt', 'w')
i = 2

p = subprocess.Popen(["python RiotApi.py matches1.json"],
                 stdout=subprocess.PIPE)

for ln in p.stdout:
    f.write(ln)

f.close()