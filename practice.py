import time
initial_time = time.time()
#time.sleep(30)
end_time = time.time()
seconds = int(initial_time-end_time)
seconds = 7200
hours, seconds =  seconds // 3600, seconds % 3600
minutes, seconds = seconds // 60, seconds % 60
format_time = '%d:%d:%d' % (hours, minutes, seconds)
print seconds, format_time