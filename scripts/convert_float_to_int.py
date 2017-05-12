with open("../media/data/markers_snapped.csv") as f:
    fw = open("../media/data/markers_snapped2.csv","w")
    num_row_skip = 3
    cnt = 0
    for line in f:
        if cnt >= num_row_skip:
            parts = line.split(",")
            parts[-1] = str(int(float(parts[-1].strip())))
            parts[-2] = str(int(float(parts[-2].strip())))
            new_line = ",".join(parts)
            print(new_line, file=fw)
        else:
            print(line, file=fw, end="")
            cnt += 1
    fw.close()
