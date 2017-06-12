def separate_direction(grid):
    partition_index = 0
    prev_loc = None
    for location in grid:
        if prev_loc is None:
            prev_loc = location
            continue
        if prev_loc - location >= 150:
            break
        partition_index += 1
    print(partition_index)
    # smaller bearing
    # grid_in_one_direction = [180,179,0]
    grid_in_one_direction = grid[partition_index + 1:]

    # larger bearing
    # grid_in_another_direction = [359,355,340]
    grid_in_another_direction = grid[:partition_index + 1]

    if len(grid_in_another_direction) > 0 and grid_in_another_direction[0] > 350:
        while len(grid_in_one_direction) > 0 and grid_in_one_direction[-1] < 10:
            grid_in_another_direction.append(grid_in_one_direction.pop())
    return grid_in_one_direction, grid_in_another_direction
from sklearn.svm import SVC

def load_model():
    x = []
    y = []
    for l in open('../staticfiles/model/data-smooth.csv'):
        vals = l.split(',')
        x.append([vals[0], vals[1]])
        y.append(vals[2])

    clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
              kernel='linear', max_iter=-1, probability=True, random_state=None,
              shrinking=True, tol=0.001, verbose=False)
    clf.fit(x, y)
    return clf

clf = load_model()
# g1, g2 = separate_direction([360, 359, 355, 182, 181, 180, 1])
# print(g1)
# print(g2)


#from helper import from_csv_to_js

#from_csv_to_js("../media/data/pothole_pred1000.csv","../media/data/pothole_pred.js")


