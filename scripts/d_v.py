#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 07:48:06 2017

@author: vikrant
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import text

from ride.models import PotholeCluster


def plot_cluster(speed, intensity, axes, coeff):
    #    plt.suptitle('speed vs distance from hyperplane')
    axes.scatter(speed, intensity)
    text(0.2, 0.9, 'r = {:.2f}'.format(coeff), ha='center', va='center', transform=axes.transAxes)


def correlation(speed, intensities):
    if len(speed) <= 1:
        return 0
    speed_array = np.array(speed)
    intensity_array = np.array(intensities)
    speed_mean = speed_array.mean()
    # speed_std = df["intensity"].std()
    intensity_mean = intensity_array.mean()
    # intensity_std = df["intensity"].std()
    # print("sm {}, sdev = {}, im = {}, idev = {}".format(speed_mean,speed_std,intensity_mean,intensity_std))

    norm_speed = (speed_array - speed_mean)
    norm_intensity = (intensity_array - intensity_mean)
    norm_speed2 = (speed_array - speed_mean) ** 2
    norm_intensity2 = (intensity_array - intensity_mean) ** 2

    z = norm_speed * norm_intensity
    num = z.sum()
    deno = (norm_speed2.sum() ** .5) * (norm_intensity2.sum() ** .5)
    return num / deno


def get_new_fig(cnt, rows, cols):
    total = rows * cols
    fig = plt.figure(cnt // total)
    fig.set_size_inches(12, 9)
    fig, axes = plt.subplots(rows, cols)
    fig.set_size_inches(12, 9)
    plot = fig.add_subplot(111, frameon=False)
    plot.tick_params(
        axis='both',  # changes apply to the both axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        left='off',  # ticks along the left edge are off
        right='off',  # ticks along the rigth edge are off
        labelbottom='off',  # labels along the bottom edge are off
        labeltop='off',  # labels along the top edge are off
        labelleft='off',
        labelright='off'
    )
    # plot.tick_params(axis='both', which='major', labelsize=7)
    # plot.tick_params(axis='both', which='minor', labelsize=5)
    # if cnt > 0:
    plt.suptitle('Intensity vs GPS speed (in kmph) for different potholes')
    # plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.xlabel("GPS speed (in kmph)", labelpad=30)
    plt.ylabel("Intensity", labelpad=30)
    return axes


def plot_graphs():
    cnt = 0
    rows = 3
    cols = 3
    total = rows * cols

    axes = get_new_fig(cnt=cnt, rows=rows, cols=cols)

    for pc in PotholeCluster.objects.all():
        size = len(pc.pothole_set.all())
        if size > 5:
            speed = []
            intensities = []
            for p in pc.pothole_set.all():
                if p.intensity > 0:
                    speed.append(p.location.speed)
                    intensities.append(p.intensity)

            coeff = correlation(speed, intensities)
            if coeff > 0.7 and len(intensities) > 10:
                plot_cluster(speed, intensities, axes=axes[(cnt % total) // rows, (cnt % total) % cols], coeff=coeff)
                cnt += 1
                print(pc.id, coeff, size,cnt)
                if (cnt % total) == 0:
                    print("saving fig")
                    plt.savefig(str(cnt) + ".eps")
                    # plt.close()
                    axes = get_new_fig(cnt, rows, cols)

    plt.savefig(str(cnt) + ".eps")


def run():
    plot_graphs()


run()
