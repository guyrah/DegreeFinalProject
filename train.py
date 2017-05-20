from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
import NLP_Utils
from Logger import Logger
import pydotplus
from config import vectorMode


def train_qualityrank(data_path, data_field, vocabulary_path, testset_size, mode):

    target_field = "qualityrank"

    vocabulary   = NLP_Utils.read_vocabulary(vocabulary_path)

    data, target = NLP_Utils.prepare_tagged_data_to_train(src_path=data_path,
                                 data_field=data_field,
                                 target_field=target_field,
                                 vocabulary=vocabulary,
                                 mode=mode)
    #data, target = np.array(data), np.array(target)


    train_data = data[:-testset_size]
    train_target = target[:-testset_size]
    test_data = data[-testset_size:]
    test_target = target[-testset_size:]

    a = dict()
    for i in train_target:
        a[i] = a.get(i, 0) + 1

    Logger.log_debug(a)

    Logger.log_info("Trying Decision Tree Score:")

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(train_data, train_target)
    clfPrediction = list(clf.predict(test_data))

    Logger.log_debug(clfPrediction)
    Logger.log_debug(test_target)
    Logger.log_info ("Decision Tree Score:")
    Logger.log_info(clf.score(test_data, test_target))

    #dot_data = tree.export_graphviz(clf, out_file=None)
    #graph = pydotplus.graph_from_dot_data(dot_data)
    #graph.write_pdf('decision_tree.pdf')

    Logger.log_info("Trying Gaussian Naive Bayes")

    gnb = GaussianNB()
    gnb.fit(train_data, train_target)
    gnbPrediction = list(gnb.predict(test_data))

    Logger.log_debug(gnbPrediction)
    Logger.log_debug(test_target)
    Logger.log_info("Gaussian Naive Bayes Score:")
    Logger.log_info(gnb.score(test_data, test_target))

    Logger.log_info( "Trying Support Vector Machine")
    svc = SVC(kernel='poly', degree=5, C=7.0)
    svc.fit(train_data, train_target)
    svcPrediction = list(svc.predict(test_data))

    Logger.log_debug(svcPrediction)
    Logger.log_debug(test_target)
    Logger.log_info( "Support Vector Machine Score:")
    Logger.log_info(svc.score(test_data, test_target))

"""
    print "Combined Result:"
    for i in range(0, len(svcPrediction)):
        clfRes = clfPrediction[i]
        gnbRes =  gnbPrediction[i]
        svcRes = svcPrediction[i]
        print clfRes,gnbRes,svcRes
"""