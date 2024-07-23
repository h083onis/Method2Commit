import subprocess
command = "diff -B -w --old-line-format='<%dn\n' --new-line-format='>%dn\n' --unchanged-line-format= test.py test2.py"
print(command.split(' '))
result = subprocess.run(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)