from sklearn import svm
from sklearn.svm import SVC
from sklearn.externals import joblib

X = []
Y = []
for l in open('data-smooth.csv'):	
	vals = l.split(',')		
	X.append([vals[0],vals[1]])
	Y.append(vals[2])

clf = SVC(probability = True)
clf.fit(X, Y)  

joblib.dump(clf, 'model.pkl') 
	
