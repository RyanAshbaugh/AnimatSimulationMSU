import os

def submit_qsub():
        current_dir = str(os.getcwd())
        qsub_file = open('test.qsub', 'w')
        qsub_file.write('#!/bin/bash -login\n')
        qsub_file.write('#PBS -l walltime=00:05:00,nodes=1:ppn=1\n')
        qsub_file.write('#PBS -l feature=gbe\n')
        qsub_file.write('#PBS -j oe\n\n')
        # qsub_file.write('echo PBS_O_WORKDIR:')
        # qsub_file.write('echo $PBS_O_WORKDIR\n')
        # qsub_file.write('cd /mnt/research/neuro_animat/test_branch\n\n')
        qsub_file.write('echo jobstart\n')
        qsub_file.write('module load Python/2.7.2\n')
        qsub_file.write('module load NumPy\n')
        qsub_file.write('module load SciPy\n\n')
        qsub_file.write('ml\n')
        qsub_file.write('echo jobend\n')
        qsub_file.close
        print 'os.qsubdir', str(os.getcwd())
        # print 'os.getcwd()qsub', str(os.getcwd())
        # qsub_file = 'qsub %s/animat_qsubs_folder/animat_qsub_id_%d.qsub' % (current_dir, animat_id)
        # print qsub_file

        # command = 'qsub animat_qsub_id_%d.qsub' % animat_id
        # process = subprocess.Popen(command, cwd='/mnt/research/neuro_animat/test_branch/animat_qsubs_folder/')
        print 'qsub /mnt/research/neuro_animat/test_branch/test.qsub'
        os.system('qsub test.qsub')
        os.system('echo $SHELL')

main = submit_qsub()

