from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
import NLP_Utils
from Logger import Logger
from config import *
from sklearn.model_selection import cross_val_score
import pydotplus
from config import vectorMode

def combineLabels(dataLabels, srcLabel, dstLabel):

    newDataLabels = list()

    for originalLabel in dataLabels:
        if originalLabel == srcLabel:
            newDataLabels.append(dstLabel)
        else:
            newDataLabels.append(originalLabel)
    return newDataLabels

def removeLabel(dataLabels, dataSamples,  label):
    newLabels = list()
    newDataSamples = list()

    for i in range(0,len(dataLabels)):
        if dataLabels[i] != label:
            newLabels.append(dataLabels[i])
            newDataSamples.append(dataSamples[i])

    return newLabels, newDataSamples

def train_qualityrank(data_path, data_field, vocabulary_path, mode):

    target_field = "qualityrank"
    #target_field = "fast_rank"

    vocabulary   = NLP_Utils.read_vocabulary(vocabulary_path)

    data, target = NLP_Utils.prepare_tagged_data_to_train(datasetFilePath=data_path,
                                                          data_field=data_field,
                                                          target_field=target_field,
                                                          vocabulary=vocabulary,
                                                          mode=mode)
    #data, target = np.array(data), np.array(target)

    Logger.log_debug("Target labels:")
    Logger.log_debug(target)
    Logger.log_debug("Combining labels 2 and 1:")
    target = combineLabels(target, 2, 1)
    Logger.log_info("Combined labels 2 and 3")
    Logger.log_debug(target)

    #Logger.log_info("Removing label: 0")
    #target, data = removeLabel(target, data, 0)
    """
    train_data = data[: -config.testSetSize]
    train_target = target[:-config.testSetSize]
    test_data = data[-config.testSetSize:]
    test_target = target[-config.testSetSize:]
    
    
    a = dict()
    for i in train_target:
        a[i] = a.get(i, 0) + 1

    Logger.log_debug(a)

    Logger.log_info("Trying Decision Tree Score:")

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(train_data, train_target)
    clfPrediction = list(clf.predict(test_data))

    Logger.log_debug("P: " + str(clfPrediction))
    Logger.log_debug("R: " + str(test_target))
    Logger.log_info ("Decision Tree Score:")
    Logger.log_info(clf.score(test_data, test_target))

    #dot_data = tree.export_graphviz(clf, out_file=None)
    #graph = pydotplus.graph_from_dot_data(dot_data)
    #graph.write_pdf('decision_tree.pdf')

    Logger.log_info("Trying Gaussian Naive Bayes")

    gnb = GaussianNB()
    gnb.fit(train_data, train_target)
    gnbPrediction = list(gnb.predict(test_data))

    Logger.log_debug("P: " + str(gnbPrediction))
    Logger.log_debug("R: " + str(test_target))
    Logger.log_info("Gaussian Naive Bayes Score:")
    Logger.log_info(gnb.score(test_data, test_target))
    """
    Logger.log_info( "Trying Support Vector Machine")
    svc = SVC(kernel='linear')
    scores = cross_val_score(svc, data, target)
    #svc.fit(train_data, train_target)
    #svcPrediction = list(svc.predict(test_data))
    Logger.log_info(scores)
"""
    Logger.log_debug("P: " + str(svcPrediction))
    Logger.log_debug("R: " + str(test_target))
    Logger.log_info( "Support Vector Machine Score:")
    Logger.log_info(svc.score(test_data, test_target))
    """