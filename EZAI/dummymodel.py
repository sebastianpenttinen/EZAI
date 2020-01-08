import pickle

from sklearn.linear_model import LogisticRegression 
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split 

data = load_iris()
Xtrain, Xtest, Ytrain, Ytest = train_test_split(
  data.data, 
  data.target, 
  test_size=0.3,
  random_state=4
)

model = LogisticRegression(C=0.1,
                          max_iter=20,
                          fit_intercept=True,
                          n_jobs=3,
                          solver='liblinear')

model.fit(Xtrain, Ytrain)

pkl_filename = "dummy_model.pkl"
with open(pkl_filename, 'wb') as file:
  pickle.dump(model, file)

def get_model(filename): 
  with open(filename, 'rb') as file:
    return pickle.load(file)

pickle_model = get_model(pkl_filename)

print(type(pickle_model))

score = pickle_model.score(Xtest, Ytest)
print("Test score: {0:.2f} %".format(100 * score))

Ypredict = pickle_model.predict(Xtest)