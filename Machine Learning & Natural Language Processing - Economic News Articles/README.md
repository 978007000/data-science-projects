## Economic News Article Tone and Relevance.
http://dbgroup.cs.tsinghua.edu.cn/ligl/crowddata/

Contributors read snippets of news articles. They then noted if the article was relevant to the US economy and, if so, what the tone of the article was. Tone was judged on a 9 point scale (from 1 to 9, with 1 representing the most negativity). Dataset contains these judgments as well as the dates, source titles, and text. Dates range from 1951 to 2014.

Table of Contents:
----
- EDA & SQL: taking a look at the data.
- Data cleanup and store dataframe as pickle file.
- Vocabulary.
- Choosing between different pre-processing: punctuation, stem and stop words.
- Choosing between CountVectorizer and TfidfVectorizer.
- Plot of learning curves.
- Machine Learning: running some models with defaults with the chosen bags of words representation and pre-processing.
- Machine Learning: grid search.
- Unsupervised learning: LDA.
- Word Cloud visualization.
- Word2Vec demonstration.

The functions used can be found in this file: nlp_ml_functions.py

The Word Cloud visualizations can be found here:

https://github.com/carlespoles/PyTagCloud

I have created a Python environment with the corresponding "environment.yml" file.

The kernel used contains the following Python dependencies and libraries:

  - python = 3.5
  - ipython > 5.0
  - jupyter
  - numpy
  - nltk
  - textblob
  - spacy
  - matplotlib
  - pandas
  - seaborn
  - scikit-learn
  - tensorflow
  - setuptools
  - plotly
  - gensim
  - pip
  - rise
  - pip:
      - ftfy
      - nbbrowserpdf
      - ipython-sql
      - tabulate
      - pytagcloud
      - pygame
      - simplejson

Note: wordclod from https://github.com/amueller/word_cloud does not install.
