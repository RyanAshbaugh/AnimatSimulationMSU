import subprocess

x = subprocess.check_output('ls')
y = x.split()
z = ' '.join(y)
#z = []
#for file in y:
 #   file = file+' '
  #  z.append(file)
print z 
