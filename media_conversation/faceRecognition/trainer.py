#!/usr/bin/env python2
#
# Example to classify faces.
# Brandon Amos
# 2015/10/11
#
# Copyright 2015-2016 Carnegie Mellon University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import pickle

from operator import itemgetter

import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.lda import LDA
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.grid_search import GridSearchCV
from sklearn.mixture import GMM
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB


def prepareImages():
    # Delete old cache file
    if os.path.exists("./faceRecognition/aligned-images/cache.t7"):
        os.remove("./faceRecognition/aligned-images/cache.t7")
    # Do pose detection and alignment
    os.system("./faceRecognition/util/align-dlib.py ./faceRecognition/training-images/ align outerEyesAndNose" +
    " ./faceRecognition/aligned-images/ --size 96")
    # Generate representations from the aligned images
    os.system("./faceRecognition/batch-represent/main.lua -outDir ./faceRecognition/generated-embeddings/ -data"
    + " ./faceRecognition/aligned-images/")


def train(folder, classifier):
    print("Loading embeddings.")
    fname = "{}labels.csv".format(folder)
    labels = pd.read_csv(fname, header=None).as_matrix()[:, 1]
    labels = map(itemgetter(1),
                 map(os.path.split,
                     map(os.path.dirname, labels)))  # Get the directory.
    fname = "{}reps.csv".format(folder)
    embeddings = pd.read_csv(fname, header=None).as_matrix()
    le = LabelEncoder().fit(labels)
    labelsNum = le.transform(labels)
    nClasses = len(le.classes_)
    print("Training for {} classes.".format(nClasses))

    if classifier == 'LinearSvm':
        clf = SVC(C=1, kernel='linear', probability=True)
    elif classifier == 'GridSearchSvm':
        print("""
        Warning: In our experiences, using a grid search over SVM hyper-parameters only
        gives marginally better performance than a linear SVM with C=1 and
        is not worth the extra computations of performing a grid search.
        """)
        param_grid = [
            {'C': [1, 10, 100, 1000],
             'kernel': ['linear']},
            {'C': [1, 10, 100, 1000],
             'gamma': [0.001, 0.0001],
             'kernel': ['rbf']}
        ]
        clf = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5)
    elif classifier == 'GMM':  # Doesn't work best
        clf = GMM(n_components=nClasses)

    # ref:
    # http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html#example-classification-plot-classifier-comparison-py
    elif classifier == 'RadialSvm':  # Radial Basis Function kernel
        # works better with C = 1 and gamma = 2
        clf = SVC(C=1, kernel='rbf', probability=True, gamma=2)
    elif classifier == 'DecisionTree':  # Doesn't work best
        clf = DecisionTreeClassifier(max_depth=20)
    elif classifier == 'GaussianNB':
        clf = GaussianNB()

    # if args.ldaDim > 0:
    #     clf_final = clf
    #     clf = Pipeline([('lda', LDA(n_components=args.ldaDim)),
    #                     ('clf', clf_final)])

    clf.fit(embeddings, labelsNum)

    fName = "{}classifier.pkl".format(folder)
    print("Saving classifier to '{}'".format(fName))
    with open(fName, 'w') as f:
        pickle.dump((le, clf), f)


def classify():
    cwd = os.path.join(os.getcwd(), "facerecognition.py")
    os.system('{} {}'.format('python', cwd))


def run():
    """Train new model and prepare images."""
    classifier = "LinearSvm"
    prepareImages()
    train("./faceRecognition/generated-embeddings/", classifier)


if __name__ == '__main__':
    # TODO: miss classifier als argument ofzo
    classifier = "LinearSvm"
    prepareImages()
    train("./faceRecognition/generated-embeddings/", classifier)
    # To test the newly trained classifier
    # classify()
