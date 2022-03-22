# -*- coding: utf-8 -*-
"""drona.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XSYoKqNegTOlK6UtqdiJTDWn8_LSXDBZ

**Project: Automated Question-Answering**
"""

# Importing libraries

# Data handling
import numpy as np
import pandas as pd
import re

# machine learning
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Text processing
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import string

# Data reading
import pkgutil   # provides binary data
from io import StringIO # for binary to high level data conversion

# # required during test time
# !pip install transformers

from transformers import pipeline
ques_ans_pipeline = pipeline("question-answering")

# # reading the data during test time
# data_science_df_clean=pd.read_csv('data_science_df_clean.csv')

# reading the data
bytes_data = pkgutil.get_data(__name__, "data_science_df_clean.csv")

s=str(bytes_data,'utf-8')
data = StringIO(s) 
data_science_df_clean=pd.read_csv(data)

# writing abbreviation processing function
def abbreviation_process(text):
    abbreviation_dict= {'ml':'machine learning','cnn':'convolutional neural network',
                        'rnn':'recurrent neural network','Sequence Models':'recurrent neural network',
                        'pca':'principal component analysis','svm':'support vector machine',
                        'knn':'k-nearest neighbors','ann':'artificial neural network',
                        'nn':'neural network','sgd':'stochastic gradient descent',
                        'gd':'gradient descent','nlp':'natural language processing',
                        'nlu':'natural language understanding','api': 'application programming interface',
                        'gui':'graphical user interface','mlops': 'ml lifecycle',
                        'lda':'latent dirichlet allocation','svd':'singular value decomposition',
                        'cf':'collaborative filtering','cpu':'central processing unit',
                        'anova':'analysis of variance','auc':'area under the curve',
                        'cv':'cross validation','dnn':'deep neural network',
                        'eda':'exploratory data analysis','gbm':'gradient boosting machine',
                        'glm':'generalized linear model','gru':'gated recurrent unit',
                        'hmm':'hidden marcov model','ica':'independent component analysis',
                        'lstm':'long short term memory','mape':'mean absolute percentage error',
                        'mse':'mean squared error','rmse':'root mean squared error',
                        'nldr':'non-linear dimensionality reduction','r2':'r-squared',
                        'rf':'random forest','roc':'receiver operating characteristic',
                        'ai':'artificial intelligence', 'shap': 'shapley additive explanations',
                        'lime': 'local interpretable model-agnostic explanations', 'eli5': 'explain like I am 5',
                        'xai': 'explainable artificial intelligence', 'opp': 'object oriented programming',
                        'idle': 'integrated development and learning environment', 'sql': 'structured query language',
                        'rdbms' : 'relational database management system', 'iqr': 'interquartile range',
                        'iid': 'independent and indentically distributed', 'clt': 'central limit theorem',
                        'ols': 'ordinary least squares', 'vif': 'variance inflation factor',
                        'xgboost': 'extreme gradient boosting', 'gmlos': 'geometric mean length of stay',
                        'los': 'length of stay', 'smote': 'synthetic minority over-sampling technique',
                        'snn': 'standard neural network', 'brnn': 'idirectional recurrent neural network',
                        'nlg': 'natural language generation', 'bfs': 'breadth first search',
                        'dfs': 'depth first search', 'os': 'operating system',
                        'cvcs' : 'central version control system','dvcs': 'distributed version control system',
                        'wsgi': 'web server gateway interface', 'asgi': 'asynchronous server gateway interface',
                        'mle': 'machine learning engineering', 'gpu': 'graphics processing unit',
                        'dag': 'directed acyclic graph', 'rdd': 'resilient distributed dataset'}
                        
    text = text.lower()    # converting to lowercase
    text= text.replace('?','') # removing '?' mark
    text = [re.sub('\s+', ' ', sent) for sent in text] # Removing new line characters
    text = [re.sub("\'", "", sent) for sent in text] # Removing distracting single quotes
    text=''.join(text)

    for k in text.split():   # loop for replacing the abbreviations
      for i in abbreviation_dict.keys():
        if k==i:
          text=text.replace(k,abbreviation_dict.get(i))
  
    return text

# writing text pre-processing function
def text_process(text):
    text = text.lower()    # converting to lowercase
    text =[char for char in text if char not in string.punctuation] # removing punctuations
    text=''.join(text) 
    text=[word for word in text.split() if word not in stopwords.words('english')]  # removing stopwords
    stemmer = SnowballStemmer("english") 
    text=' '.join(text) 
    text = [stemmer.stem(word) for word in text.split()] # stemming operation
    return ' '.join(text)

"""# **Building of Question-Answering Model**

Countvec ngram and Question-Answering Model
"""

# Writing a function for question answering
def tellme(question):
  '''
  This model gives answer to data science related questions.
  '''
  global data_science_df_clean
  
  # Processing the question
  question_abbre_processed =abbreviation_process(question)
  question_processed = text_process(question_abbre_processed)
    
  # Appending question in the dataset to match the dimension of question and document vector
  data_science_df_clean=data_science_df_clean[(data_science_df_clean.documents!=data_science_df_clean.documents_processed)]
  data_science_df_clean.loc[(data_science_df_clean.index.max()+1)] = question_processed

  # vectorization of text samples
  ngram_model = CountVectorizer(ngram_range=(1,3)) # Downloading pre-trained vectorization model (ngram)
  document_term_matrix = ngram_model.fit_transform(data_science_df_clean.documents_processed.values)

  # CountVec ngram question-answering model
  topic_match=[]
  short_answer_dict={}
  long_answer_dict={}
  
  vec_1=document_term_matrix[-1:]     # Question vector

  for k in range(len(data_science_df_clean.documents[:-1])):
    vec_2=document_term_matrix[k:(k+1)]     # Individual document vector
    topic_match.append(cosine_similarity(vec_1 , vec_2)[0][0])
    
  try:
    
    if max(topic_match)<0.25:  # Deciding the margins through hit and trial for perfect answer
      answer=print("Sorry ! I have no experience for this question.\n\n::BEGINNERS MAY TYPE 'HELP LINES'")
              
    else:
      for i in topic_match:
        if i>0.7*max(topic_match): # Deciding the margins through hit and trial for perfect answer
          context=data_science_df_clean.first_100_letters[topic_match.index(i)]
          ans = ques_ans_pipeline(question=question_abbre_processed, context=context)
          short_answer_dict[ans['score']] =ans['answer']
          long_answer_dict[ans['score']]=data_science_df_clean.documents[topic_match.index(i)]
                  
      if max(list(short_answer_dict.keys()))>0.01: # Deciding the margins through hit and trial for perfect answer
        answer=print(f"{long_answer_dict.get(max(list(long_answer_dict.keys())))}\n\n::BEGINNERS MAY TYPE 'HELP LINES'")
                        
      else:
        answer=print("Sorry ! I have no experience for this question.\n\n::BEGINNERS MAY TYPE 'HELP LINES'")
        
  except:
    answer=print("There is an exception\n\n::BEGINNERS MAY TYPE 'HELP LINES'")
    
  return answer