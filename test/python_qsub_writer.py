import os

def submit_qsub():
    os.system('qsub test.qsub')

main = submit_qsub()
