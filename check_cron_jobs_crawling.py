import commands
import re
import sys
import os

PROCESS_NAME = '4sq'

def discover_processes():
    output_processes = commands.getoutput('ps -A | grep 4sq_').strip()
    if output_processes:
        list_processes = map(lambda x: x.split(' ')[-1], output_processes.split('\n'))
        return list_processes
    else:
        return []

def trigger_not_running(running_processes, machine_name, base_dir, output_dir):
    if (PROCESS_NAME + '_' + machine_name) not in running_processes:
        CREDENTIALS_FILENAME = base_dir + '/_4sq_crawler/credentials/' + machine_name + '_credentials'
        os.system('python ' + base_dir + '/_4sq_crawler/threaded_4sq_crawler.py ' + PROCESS_NAME + '_' + machine_name + ' ' + base_dir + '/_4sq_crawler/data/split_' + machine_name + ' ' + output_dir + ' ' + CREDENTIALS_FILENAME + ' &')

def main(machine_name, base_dir, output_dir):
    running_processes = discover_processes()
    trigger_not_running(running_processes, machine_name, base_dir, output_dir)

if __name__ == '__main__':
    machine_name = sys.argv[1]
    base_dir = sys.argv[2]
    output_dir = sys.argv[3]
    main(machine_name, base_dir, output_dir)
