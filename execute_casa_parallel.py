####################################################################################################
# CASA PARALLELISATION
####################################################################################################

# import modules
################

from subprocess import call, Popen, PIPE, STDOUT
from collections import Counter
import time


####################################################################################################

def casa_execute_parallel(processes, max_threads=10, debug=False):

    """
    Run casa split commands in parallel. Up to max_threads processes will be used.
    The chunksize (default: 100 channels) is passed to the splitting function).
    Requires a list of dataset/process status dictionaries.
    """

    # log start of task
    def post_task_start(process):
        print("\n")
        print("=" *80)
        print("Started task:")
        print(process['task'])
        print("=" *80)

    # log end of task
    def post_task_finished(process):
        print("\n")
        print("=" *80)
        print("Finished task:")
        print(process['task'])
        print("Execution took "+str(process['stoptime']-process['starttime'])+"s")
        print("=" *80)
    def post_task_failed(process):
        print("\n")
        print("=" *80)
        print("Task execution failed:")
        print(process['task'])
        print("Execution took "+str(process['stoptime']-process['starttime'])+"s to fail.")
        print("=" *80)

    # log how many task still need Execution
    def post_task_info(processes):
        running_tasks_count, remaining_tasks_count, successful_tasks_count, failed_tasks_count = get_task_execution_infos(processes)
        print("finished task: "+str(failed_tasks_count+successful_tasks_count)+"     running tasks: "+str(running_tasks_count)+"    waiting for execution: "+str(remaining_tasks_count))

    # display statistics when all task are finished
    def post_job_finished(processes, job_starttime, job_stoptime):
        print("\n")
        print("=" *80)
        print("JOB FINISHED ")
        print("=" *80)
        print("Execution took "+str(job_stoptime-job_starttime)+"s")
        print("Excuted "+str(len(processes))+" tasks running "+str(max_threads)+" in parallel.")
        print("\ntask ID\tstatus\texecution time")
        print("~" *40)
        for idx,process in enumerate(processes):
            print(str(idx)+"\t"+process['status']+"\t"+str(process['stoptime']-process['starttime'])+"s")
        print("=" *80)

    # get how many tasks are running, still need to run or were completed already
    def get_task_execution_infos(processes):
        status_list = [process['status'] for process in processes]
        running_tasks_count   = Counter(status_list)['running']
        remaining_tasks_count = Counter(status_list)['not started']
        successful_tasks_count = Counter(status_list)['success']
        failed_tasks_count = Counter(status_list)['failed']
        return running_tasks_count, remaining_tasks_count, successful_tasks_count, failed_tasks_count

    # get the index of an element in a list
    def get_idx(alist, name):
        for idx, itm in enumerate(alist):
            if (name == itm['name']):
                return idx

####################################################################################################

    # log start time of job
    job_starttime = time.time()

    # split all available datasets
    while True:

        # do not spawn more processes than max_threads_split
        # only spawn new process when there is one or more left
        running_tasks_count, remaining_tasks_count, successful_tasks_count, failed_tasks_count = get_task_execution_infos(processes)
        while (running_tasks_count < max_threads) and (remaining_tasks_count > 0):

            # get dataset that is executed next
            remaining_processes = [process for process in processes if (process['status'] == 'not started')]
            this_process = remaining_processes.pop()

            # start process, execute task
            process_idx = get_idx(processes, this_process['name'])
            if (debug == True):
                processes[process_idx]['process'] = Popen(processes[process_idx]['task'])
            else:
                processes[process_idx]['process'] = Popen(processes[process_idx]['task'], stdout=PIPE, stderr=subprocess.STDOUT)
            processes[process_idx]['status'] = 'running'
            processes[process_idx]['starttime'] = time.time()
            post_task_start(processes[process_idx])

            # update stats after spwaning process
            running_tasks_count, remaining_tasks_count, successful_tasks_count, failed_tasks_count = get_task_execution_infos(processes)

        # check if process has finished and update status
        for process in processes:
            # check if process has started already
            if (process['status'] == 'running'):
                # check if finished
                if not (process['process'].poll() == None):
                    process_idx = get_idx(processes, process['name'])
                    processes[process_idx]['stoptime'] = time.time()

                    # check if successful
                    if (process['process'].returncode == 0):
                        processes[process_idx]['status'] = 'success'
                        post_task_finished(processes[process_idx])
                    else:
                        processes[process_idx]['status'] = 'failed'
                        post_task_failed(processes[process_idx])

        # stop when all tasks are executed
        # otherwise wait a second before checking again
        if (running_tasks_count == 0) and (remaining_tasks_count == 0):
            break
        else:
            time.sleep(0.1)

    job_stoptime = time.time()
    post_job_finished(processes, job_starttime, job_stoptime)


####################################################################################################
