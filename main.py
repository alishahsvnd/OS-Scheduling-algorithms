import threading
import time

class Process(object):

    def __init__(self, p_id: str , burst_time: int, arrival_time: int) -> None:
        self.id = p_id
        self.burst_time = burst_time
        self.p_time = ProcessTime(arrival_time)
        self.start = False
        self.first_burst_time = burst_time

    def __bool__(self) -> bool:
        return bool(self.burst_time)

    def __str__(self) -> str:
        return str(self.id)

    def __lt__(self, other: 'Process') -> bool:
        return self.burst_time < other.burst_time

    def run_ms(self) -> None:
        time.sleep(1 / 1000)
        self.burst_time -= 1


class ProcessTime(object):
  
    def __init__(self, arrival_time: int) -> None:
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.start_time = 0
        self.end_time = 0

    @property
    def response_time(self) -> int:
        return self.start_time - self.arrival_time

    @property
    def turnaround_time(self) -> int:
        return self.end_time - self.arrival_time


class OS(object):

    def __init__(self) -> None:
        self._burst_times = {}
        self._burst_times2 = {}
        self._io_times = {}
        self._io_times_temp = {}
        self._arrival_times = {}
        self._timer = 0
        self._ready_queue = []
        self._io_works = []
        self._last_arrive = 0
        self._gantt_chart = []
        self.real_tat = 0
        self.idle = 0

    def clear(self) -> None:
        
        self._burst_times.clear()
        self._burst_times2.clear()
        self._io_times.clear()
        self._io_times_temp.clear()
        self._arrival_times.clear()
        self._timer = 0
        self._ready_queue.clear()
        self._io_works.clear()
        self._last_arrive = 0
        self._gantt_chart.clear()
        self.real_tat = 0
        self.idle = 0

    @property
    def process_count(self) -> int:
        return len(self._burst_times)

    @property
    def cpu_util(self) -> float:
        if self._timer:
            return (self._timer - self.idle) / self._timer
        return 1.0

    @property
    def throughput(self) -> float:
        if self._timer:
            return len(self._ready_queue) * 1000 / self._timer
        return 1.0

    @property
    def avg_tt(self) -> float:
        if self._ready_queue:
            return sum([prs.p_time.turnaround_time for prs in self._ready_queue]) / len(self._ready_queue)
        return 0.0

    @property
    def avg_rt(self) -> float:
        if self._ready_queue:
            return sum([prs.p_time.response_time for prs in self._ready_queue]) / len(self._ready_queue)
        return 0.0

    @property
    def avg_wt(self) -> float:
        if self._ready_queue:
            return sum([prs.p_time.waiting_time for prs in self._ready_queue]) / len(self._ready_queue)
        return 0.0
        

    def __str__(self) -> str:
        newlist = sorted(self._ready_queue, key=lambda x: x.id)
        print()
        print('============================================================================')
        print()
        print('       response time      turnaround time       waiting time')#      start time      end time')
        for prs in newlist :
            print('p',prs.id , '         ' , prs.p_time.response_time , '                  '  , prs.p_time.turnaround_time , '              '  , prs.p_time.waiting_time )#, '               ',prs.p_time.start_time , '               ' ,prs.p_time.end_time  )

        print('------------------------------------------------------------------')
        print('AVG          ' ,self.avg_rt,'                ', self.avg_tt,'           ' ,self.avg_wt)
        print()
        print('Throughput:   ',       self.throughput)
        print('CPU Utilization:  ',   self.cpu_util*100)
        print('Total time:',     self._timer)
        print('Idle time: ',    self.idle)
        print()
        print()
        return ' '
          

    def set_data(self, file_path: str) -> None:
     
        prs_data = csv_parser("inputs.csv")
        self.clear()
        for p_id, arrival_time, burst_time1, io_time, burst_time2 in prs_data:
            self._burst_times[p_id] = int(burst_time1)
            self._burst_times2[p_id] = int(burst_time2)
            self._io_times[p_id] = int(io_time)
            self._io_times_temp[p_id] = int(io_time)
            self._arrival_times[p_id] = int(arrival_time)
        self._last_arrive = max(self._arrival_times.values())
        self.reset_timer()

    def process_generator(self, p_id: str , burst_time: int) -> None:
      
        for prs in self._ready_queue:
            if prs.id == p_id:
                # prs.burst_time = burst_time
                break
        else:
            self._ready_queue.append(Process(p_id, burst_time, self._arrival_times[p_id]))

    def reset_timer(self) -> None:
        self._timer = 0

    @property
    def timer(self) -> int:
        return self._timer

    def new_to_ready(self) -> None:

        for prs in self._io_works:
            if self._arrival_times[prs.id] == self._timer:
                self._ready_queue.append(prs)
                self._io_works.remove(prs)
        for p_id in self._arrival_times:
            if self._arrival_times[p_id] == self._timer:
                self.process_generator(p_id, self._burst_times[p_id])

    def cpu_to_io(self, prs: Process) -> None:
       
        at2 = self._io_times[prs.id] + self._timer
        self._io_times[prs.id] = 0
        self._arrival_times[prs.id] = at2
        prs.burst_time = self._burst_times2[prs.id]
        self._io_works.append(prs)
        self._ready_queue.remove(prs)
        self._last_arrive = max(self._last_arrive, self._arrival_times[prs.id])

    def wait(self) -> None:
        
        time.sleep(1 / 1000)
        self._timer += 1
        # self.add_to_chart()
        self.idle += 1

    def fcfs(self) -> None:
        
        start_time = time.time()
        while any(self._ready_queue) or self._timer <= self._last_arrive:
            self.new_to_ready()
            for prs in self._ready_queue:
                if prs:
                    while prs:
                        if not prs.start:
                            prs.start = True
                            prs.p_time.start_time = self._timer
                        prs.run_ms()
                        self._timer += 1
                        # self.add_to_chart(prs)
                        self.new_to_ready()
                    else:
                        if self._io_times[prs.id]:
                           self.cpu_to_io(prs)

                        else:
                            prs.p_time.end_time = self._timer
                            prs.p_time.waiting_time =  prs.p_time.turnaround_time - prs.first_burst_time - self._burst_times2[prs.id] - self._io_times_temp[prs.id]
                    break
            else:
                self.wait()
        self.real_tat = time.time() - start_time

    def sjf(self) -> None:  # sjf
        
        start_time = time.time()
        while any(self._ready_queue) or self._timer <= self._last_arrive:
            self.new_to_ready()
            temp_rq = [prs for prs in self._ready_queue if prs]  # remove executed processes (have no burst time)
            if temp_rq:
                min_prs = min(temp_rq)  # choose shortest process
                while min_prs:
                    if not min_prs.start:
                        min_prs.start = True
                        min_prs.p_time.start_time = self._timer
                    min_prs.run_ms()
                    self._timer += 1
                    # self.add_to_chart(min_prs)
                    self.new_to_ready()
                else:
                    if self._io_times[min_prs.id]:
                        self.cpu_to_io(min_prs)
                    else:
                        min_prs.p_time.end_time = self._timer
                        min_prs.p_time.waiting_time = min_prs.p_time.response_time  # for sjf
            else:
                self.wait()
        self.real_tat = time.time() - start_time

    def rr(self) -> None:
       
        start_time = time.time()
        while any(self._ready_queue) or self._timer <= self._last_arrive:
            self.new_to_ready()
            nothing = True
            for prs in self._ready_queue:
                counter = 0
                for _ in range(5):
                    if prs:
                        nothing = False
                        if not prs.start:
                            prs.start = True
                            prs.p_time.start_time = self._timer
                        prs.run_ms()
                        self._timer += 1
                        # self.add_to_chart(prs)
                        counter += 1
                        for other in self._ready_queue:
                            if other and other is not prs:
                                other.p_time.waiting_time += 1
                        self.new_to_ready()
                    if counter and not prs:
                        if self._io_times[prs.id]:
                            self.cpu_to_io(prs)
                            break
                        else:
                            prs.p_time.end_time = self._timer
                            break
            if nothing:
                self.wait()
        self.real_tat = time.time() - start_time



class Machine(object):
   
    def __init__(self, data_path: str = '') -> None:
        self.os = OS()
        self._data_path = data_path

    def set_data_path(self, data_path: str) -> None:
    
        self._data_path = "inputs.csv"

    def sim_exe(self) -> None: 
        
        if not self._data_path:
            raise ValueError('data_path is not set')
        t1 = OS()
        t2 = OS()
        t3 = OS()
        t1.set_data(self._data_path)
        t2.set_data(self._data_path)
        t3.set_data(self._data_path)
        th1 = threading.Thread(name='fcfs', target=t1.fcfs)
        th2 = threading.Thread(name='sjf', target=t2.sjf)
        th3 = threading.Thread(name='rr', target=t3.rr)
        th1.start()
        th2.start()
        th3.start()
        th1.join()
        th2.join()
        th3.join()
        print()
        print()
        print('============================================================================')
        print('                                     FCFS ' , t1)
        print('============================================================================')
        print('                                     SJF ' , t2)
        print('============================================================================')
        print('                                     RR ' , t3)


def csv_parser(file_path: str) -> list:
    
    with open(file_path, 'r') as file:
        lst = [[elm for elm in line.strip().split(',')][:5] for line in file.readlines()[1:]]
    return lst


if __name__ == '__main__':
    machine = Machine('inputs.csv')
    machine.sim_exe()


