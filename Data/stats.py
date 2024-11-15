import time
import matplotlib.dates as mdates
from file_read_backwards import FileReadBackwards
import matplotlib.pyplot as plt
import datetime
import matplotlib as mpl
mpl.use('Agg')


def main():
    plt.clf()
    plt.style.use('dark_background')
    count = 0
    firstLine = True
    timeStart = 0

    def parseTime(line):
        t2 = [*map(int, line[0].split("/"))]
        t = [*map(int, line[1].split(":"))]
        return datetime.datetime(*t2, *t)

    minutes = {}

    def initMinute(m):
        minutes[m] = {"ips": {}, "count_moves": {
            "/getMove": 0, "/getMoveSlow": 0, "/getMoveUltra": 0}}

    def delta_t(t):
        return datetime.datetime.now() - t

    init_time = -1
    bin_size = 3*60
    with FileReadBackwards(r"../log.txt") as frb:
        for l in frb:
            splitted = [x for x in l.split(" ") if x != ""]
            t = parseTime(splitted)
            minute = delta_t(t).seconds//bin_size
            if (minute > (12*60*60)//bin_size):
                break
            if minute not in minutes:
                initMinute(minute)
            m = minute
            mO = minutes[m]

            # print(l[:100])
            if (len(splitted) < 4):
                print("Weird line:", splitted)
                break

            if splitted[2] == "GET":
                mO["count_moves"][splitted[3]] += 1
                ip = splitted[5].split(":")[0]
                if ip not in mO["ips"]:
                    mO["ips"][ip] = 0
                mO["ips"][ip] += 1

    minuteSorted = sorted(minutes.keys())
    slow = []
    fast = []
    ultra = []
    ips_c = []
    for minute in minuteSorted:
        slow.append(minutes[minute]["count_moves"]
                    ["/getMoveSlow"] * (60 / bin_size))
        fast.append(minutes[minute]["count_moves"]
                    ["/getMove"] * (60 / bin_size))
        ultra.append(minutes[minute]["count_moves"]
                     ["/getMoveUltra"] * (60 / bin_size))
        ips_c.append(len(minutes[minute]["ips"]))

    plt.rcParams['axes.facecolor'] = '#323232'
    plt.rcParams['savefig.facecolor'] = '#323232'

    x_axis = [datetime.datetime.now() - datetime.timedelta(minutes=(i*bin_size)//60)
              for i in minuteSorted]
    plt.subplot(211)
    plt.title("Leela-Deala stats, UTC+1")
    plt.plot(x_axis, slow, label="Hard reqs count")
    plt.plot(x_axis, fast, label="Normal reqs count")
    plt.plot(x_axis, ultra, label="Easy reqs count")
    plt.ylabel("reqs/m")
    plt.legend()
    ax = plt.subplot(212)
    plt.plot(x_axis, ips_c, label="Unique IPs")
    plt.ylim(ymin=0)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.savefig("stats.png")
    print("Done")


while True:
    main()
    time.sleep(120)
