from sklearn.svm import SVC

from ride.models import Pothole, Constants


def load_model():
    x = []
    y = []
    for l in open('staticfiles/model/data-smooth.csv'):
        vals = l.split(',')
        x.append([vals[0], vals[1]])
        y.append(vals[2])

    clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
              kernel='linear', max_iter=-1, probability=True, random_state=None,
              shrinking=True, tol=0.001, verbose=False)
    clf.fit(x, y)
    return clf


def run():
    clf = load_model()
    potholes = Pothole.objects.filter(intensity__exact=Constants.null_intensity)
    # print(len(potholes))
    for p in potholes:
        p.intensity = clf.decision_function([(p.max_min, p.sd)])
        p.save()
