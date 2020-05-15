import subprocess

args = ['git', 'diff', '--raw', '-z', '--line-prefix=',  'd6d6bd4931f45c910042da6a8458546a79c919ee']

completed_process: subprocess.CompletedProcess = \
    subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

stdout: str = completed_process.stdout
stderr: str = completed_process.stderr

print(stdout)
print(stderr)