import matplotlib.pyplot as plt
import string
import re
import numpy as np
import pandas as pd
import seaborn as sns
import nltk
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, learning_curve, ShuffleSplit
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import label_binarize, MultiLabelBinarizer, binarize
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve, mean_squared_error, r2_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from bs4 import BeautifulSoup, NavigableString

def clean_up_article(article):
    """
    Function to remove HTML tags </br> and replace n\\'t with not, it\\s with it is, and \\'s with s.
    """
    article = re.sub('</br>','', article)
    article = re.sub("(n\\'t)","not", article)
    article = re.sub("(it\\'s)","it is", article)
    article = re.sub("(\\'s)","s", article)
    article = re.sub("(\\t)"," ", article)
    article = re.sub("\W+", " ", article)
    return article

# Below if we want to pass a list of invalid_tags.
#def strip_tags(html, invalid_tags):
def strip_tags(html):
    """
    # # http://stackoverflow.com/questions/1765848/remove-a-tag-using-beautifulsoup-but-keep-its-contents
    Function to remove HTML tags using BeautifulSoup.
    You can pass a custom list of HTML tags, like:
    invalid_tags = ["!--","!DOCTYPE","a","abbr","acronym","address","applet","area","article","aside","audio","b","base",\
                "basefont","bdi","bdo","big","blockquote","body","br","button","canvas","caption","center","cite","code",\
                "col","colgroup","datalist","dd","del","details","dfn","dialog","dir","div","dl","dt","em","embed","fieldset",\
                "figcaption","figure","font","footer","form","frame","frameset","h1","h6","head","header","hr","html",\
                "i","iframe","img","input","ins","kbd","keygen","label","legend","li","link","main","map","mark","menu",\
                "menuitem","meta","meter","nav","noframes","noscript","object","ol","optgroup","option","output","p",\
                "param","pre","progress","q","rp","rt","ruby","s","samp","script","section","select","small","source",\
                "span","strike","strong","style","sub","summary","sup","table","tbody","td","textarea","tfoot","th",\
                "thead","time","title","tr","track","tt","u","ul","var","video","wbr"]
    """
    invalid_tags = ["!--","!DOCTYPE","a","abbr","acronym","address","applet","area","article","aside","audio","b","base",\
                "basefont","bdi","bdo","big","blockquote","body","br","button","canvas","caption","center","cite","code",\
                "col","colgroup","datalist","dd","del","details","dfn","dialog","dir","div","dl","dt","em","embed","fieldset",\
                "figcaption","figure","font","footer","form","frame","frameset","h1","h6","head","header","hr","html",\
                "i","iframe","img","input","ins","kbd","keygen","label","legend","li","link","main","map","mark","menu",\
                "menuitem","meta","meter","nav","noframes","noscript","object","ol","optgroup","option","output","p",\
                "param","pre","progress","q","rp","rt","ruby","s","samp","script","section","select","small","source",\
                "span","strike","strong","style","sub","summary","sup","table","tbody","td","textarea","tfoot","th",\
                "thead","time","title","tr","track","tt","u","ul","var","video","wbr"]

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.findAll(True):
        if tag.name in invalid_tags:
            s = ""

            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = strip_tags(str(c), invalid_tags)
                s += str(c)

            tag.replaceWith(s)

    # Important, convert from soup object to string one.
    return str(soup)

def process_dataframe_text(article):
    """
    Function that takes text from a dataframe and 1st removes punctuation, 2nd removes stopwords and converts
    into lower case, and finally using PorterStemmer, stems the words, returning a list of the processed text in lowercase.
    """
    stemmer = nltk.stem.PorterStemmer()
    
    # Removing punctuation by checking every character in the text passed to the function.
    remove_punctuation = [char for char in article if char not in string.punctuation]

    # Once punctuation has been removed, we join them again to form a string.
    remove_punctuation = ''.join(remove_punctuation)
    
    # Removing stopwords and converting to lower case.
    remove_stop = [word.lower() for word in remove_punctuation.split() if word.lower() not in nltk.corpus.stopwords.words('english')]
    
    # Stemming words using PorterStemmer.
    return [stemmer.stem(word) for word in remove_stop]
    
    # NOTE:
    # Below would be the return function without stemming.
    #return [word.lower() for word in remove_punctuation.split() if word.lower() not in nltk.corpus.stopwords.words('english')]

def process_dataframe_stem(article):
    """
    Function that takes text from a dataframe and 1st removes punctuation, 2nd using PorterStemmer, stems the words, 
    returning a list of the processed text in lowercase.
    """
    stemmer = nltk.stem.PorterStemmer()
    
    # Removing punctuation by checking every character in the text passed to the function.
    remove_punctuation = [char for char in article if char not in string.punctuation]

    # Once punctuation has been removed, we join them again to form a string.
    remove_punctuation = ''.join(remove_punctuation)
    
    # Stemming words using PorterStemmer.
    return [stemmer.stem(word) for word in remove_punctuation.split()]
    
    # NOTE:
    # Below would be the return function without stemming.

def process_dataframe_text_stop(article):
    """
    Function that takes text from a dataframe and 1st removes punctuation, returning a list of the processed text in lowercase
    and removing stopwords.
    """
    
    # Removing punctuation by checking every character in the text passed to the function.
    remove_punctuation = [char for char in article if char not in string.punctuation]

    # Once punctuation has been removed, we join them again to form a string.
    remove_punctuation = ''.join(remove_punctuation)
    
    return [word.lower() for word in remove_punctuation.split() if word.lower() not in nltk.corpus.stopwords.words('english')]

def process_dataframe_text_split(article):
    """
    Function that takes text from a dataframe and 1st removes punctuation, returning a list of the processed text in lowercase.
    """
    
    # Removing punctuation by checking every character in the text passed to the function.
    remove_punctuation = [char for char in article if char not in string.punctuation]

    # Once punctuation has been removed, we join them again to form a string.
    remove_punctuation = ''.join(remove_punctuation)
    
    return [word.lower() for word in remove_punctuation.split()]

def plot_roc(y_test, y_prediction, model_label, plot_title):
    """
    The function takes as parameters the test labels (observations), the test predictions and 
    two strings to customize the plot: the name of the model, and a title for the plot.
    It relies on sklearn.metrics.roc_curve to extract fpr and tpr to make the plot.
    IMPORTANT: the predictions must be probabilities in order to plot the curve: not .predict(X_test), but .predict_proba(X_test)
    """
    fpr, tpr, thresholds = roc_curve(y_test, y_prediction)
    plt.plot(fpr, tpr, label=model_label)
    plt.xlim([0.0,1.0])
    plt.ylim([0.0,1.0])
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity)")
    plt.plot([0, 1], [0, 1], 'k--', color="red", label="Random guess")
    plt.legend(loc='best')
    plt.grid()
    plt.title("ROC Curve - " + plot_title + "");

def show_confusion_matrix(C,class_labels=['0','1']):
    """
    C: ndarray, shape (2,2) as given by scikit-learn confusion_matrix function
    class_labels: list of strings, default simply labels 0 and 1.

    Draws confusion matrix with associated metrics.
    
    Minimum required imports:
    
    import matplotlib.pyplot as plt
    import numpy as np

    Source: http://notmatthancock.github.io/2015/10/28/confusion-matrix.html
    
    """
    assert C.shape == (2,2), "Confusion matrix should be from binary classification only."
    
    # true negative, false positive, etc...
    tn = C[0,0]; fp = C[0,1]; fn = C[1,0]; tp = C[1,1];

    NP = fn+tp # Num positive examples
    NN = tn+fp # Num negative examples
    N  = NP+NN

    fig = plt.figure(figsize=(8,8))
    ax  = fig.add_subplot(111)
    ax.imshow(C, interpolation='nearest', cmap=plt.cm.gray)

    # Draw the grid boxes
    ax.set_xlim(-0.5,2.5)
    ax.set_ylim(2.5,-0.5)
    ax.plot([-0.5,2.5],[0.5,0.5], '-k', lw=2)
    ax.plot([-0.5,2.5],[1.5,1.5], '-k', lw=2)
    ax.plot([0.5,0.5],[-0.5,2.5], '-k', lw=2)
    ax.plot([1.5,1.5],[-0.5,2.5], '-k', lw=2)

    # Set xlabels
    ax.set_xlabel('Predicted Label', fontsize=16)
    ax.set_xticks([0,1,2])
    ax.set_xticklabels(class_labels + [''])
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    # These coordinate might require some tinkering. Ditto for y, below.
    ax.xaxis.set_label_coords(0.34,1.06)

    # Set ylabels
    ax.set_ylabel('True Label', fontsize=16, rotation=90)
    ax.set_yticklabels(class_labels + [''],rotation=90)
    ax.set_yticks([0,1,2])
    ax.yaxis.set_label_coords(-0.09,0.65)


    # Fill in initial metrics: tp, tn, etc...
    ax.text(0,0,
            'True Neg: %d\n(Num Neg: %d)'%(tn,NN),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(0,1,
            'False Neg: %d'%fn,
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(1,0,
            'False Pos: %d'%fp,
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))


    ax.text(1,1,
            'True Pos: %d\n(Num Pos: %d)'%(tp,NP),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    # Fill in secondary metrics: accuracy, true pos rate, etc...
    ax.text(2,0,
            'False Pos Rate: %.2f'%(fp / (fp+tn+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(2,1,
            'True Pos Rate: %.2f'%(tp / (tp+fn+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(2,2,
            'Accuracy: %.2f'%((tp+tn+0.)/N),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(0,2,
            'Neg Pre Val: %.2f'%(1-fn/(fn+tn+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))

    ax.text(1,2,
            'Pos Pred Val: %.2f'%(tp/(tp+fp+0.)),
            va='center',
            ha='center',
            bbox=dict(fc='w',boxstyle='round,pad=1'))


    plt.tight_layout()
    plt.show();

def classification_metrics(model_string, y_test, y_pred):
    """
    This function prints different metrics to evaluate a model. Metrics are calculated using
    sklearn package: roc_auc_score, accuracy_score, precision_score, recall_score, f1_score and classification report.
    """
    print("Precision Score of " + model_string + " model: {:.2%}\n".format(precision_score(y_test, y_pred)))
    print("AUC: {:.2%}\n".format(roc_auc_score(y_test, y_pred)))
    print("Accuracy Score of " + model_string + " model: {:.2%}\n".format(accuracy_score(y_test, y_pred)))
    print("Recall Score of " + model_string + " model: {:.2%}\n".format(recall_score(y_test, y_pred)))
    print("F1 Score of " + model_string + " model: {:.2%}\n".format(f1_score(y_test, y_pred)))
    print("Classification Report of " + model_string + ":\n\n", classification_report(y_test, y_pred))

def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=None, 
                        train_sizes=np.linspace(.1, 1.0, 5)):
    """
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_learning_curve.html
    
    Generate a simple plot of the test and training learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - An object to be used as a cross-validation generator.
          - An iterable yielding train/test splits.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : integer, optional
        Number of jobs to run in parallel (default 1).
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, 
        n_jobs=n_jobs, 
        train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt
