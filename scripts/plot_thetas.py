import os

import matplotlib.pyplot as plt
import pandas as pd

# df = pd.read_csv("../data3/4824/110688513")
# xaxis = (df['time']-df.iloc[0][0])/1000.0
# plt.scatter(xaxis,df['theta_x'],label="theta_x")
# plt.scatter(xaxis,df['theta_y'],label="theta_y")
# plt.axvline(x=(110688515 - df.iloc[0][0])/1000)

flag = False
i = 0
fig = None
percentages = []
for (dirpath, dirnames, filenames) in os.walk("../data3/"):
    # print(dirpath, dirnames,filenames)+
    if len(filenames) > 0:
        j = 0
#        print(dirpath)
        cnt = 0
        for filename in filenames:
            f = os.path.join(dirpath, filename)
            #            print(f)
            df = pd.read_csv(f)
            if len(df) > 4:
#                try:
                t1 = df[df['time'] >=  int(filename)].index[0]
                t2 = df[df['time'] >=  int(filename)-5000].index[0]
#                except Exception as e:
#                    continue
                theta_x1 = df.ix[t1]['theta_x']
                theta_x2 = df.ix[t2]['theta_x']
                theta_y1 = df.ix[t1]['theta_y']
                theta_y2 = df.ix[t2]['theta_y']
                diff_theta_x = abs(theta_x1-theta_x2)
                diff_theta_y = abs(theta_y1-theta_y2)
                diff_time = df.ix[t1]['time'] - df.ix[t2]['time']
                if diff_time >= 4500 and (diff_theta_x >= 20 or diff_theta_y >= 20):
                    cnt += 1
#                    print(diff_theta_x,diff_theta_y, t1-t2)
#                    print(df.ix[t1], df.ix[t2])
        total = len(filenames)
        if total > 50:
            percent_fp = cnt/total*100
            print("total reports {}, fp = {} percentage = {}".format(total,cnt,percent_fp))
            percentages.append(percent_fp)
percentages = np.array(percentages)
print("mean = {}".format(percentages.mean()))
        #         event_timestamp = int(filename)
        #         x = (event_timestamp - df.iloc[0][0]) / 1000
        #         if x > 20:
        #             continue
        #
        #         fig = plt.figure(i + 1)
        #         fig.set_size_inches(12, 9)
        #         #                ax = plt.subplot(2,1,i%2 + 1)
        #         xaxis = (df['time'] - df.iloc[0][0]) / 1000.0
        #         plt.suptitle('Phone orientation angle theta vs time')
        #         plt.scatter(xaxis, df['theta_x'], label="theta_x" + str(j))
        #         plt.scatter(xaxis, df['theta_y'], label="theta_y" + str(j))
        #         plt.xlabel('time (in seconds)')
        #         plt.ylabel('theta(in degree)')
        #         event_timestamp = int(filename)
        #         x = (event_timestamp - df.iloc[0][0]) / 1000
        #         plt.axvline(x=(event_timestamp - df.iloc[0][0]) / 1000)
        #         j += 1
        #         #                manager = plt.get_current_fig_manager()
        #         #                manager.window.showMaximized()
        #         #               plt.savefig("" + str(i//2) + ".eps",dpi = 600)
        #         if j % 5 == 0:
        #             plt.legend(loc='upper right')
        #             plt.savefig("graphs/" + str(i) + ".eps")
        #             plt.close(fig)
        #             i += 1
        #         if i == 500:
        #             flag = True
        #             break
        # i += 1
        # plt.legend(loc='upper right')
        # plt.savefig("graphs/" + str(i) + ".eps")
        # plt.close(fig)
        # if flag:
        #     break;
# f.extend(os.path.join(dirnames,filenames))
