import io
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from wordcloud import WordCloud
from collections import Counter
from scipy.stats import pearsonr
from scipy.stats import ttest_ind
from sklearn.linear_model import LinearRegression

# %matplotlib inline

#import documents from local drive
#needed: reliable-and-relatable-journalists-dataset-II-metadata.csv / reliable-and-relatable-journalists-ethos-utterances-metadasa.csv / allpersonalverbs.xlsx / allpersonaladjectives.xlsx / allpersonalnouns.xlsx / allpersonalxcomps.xlsx

from google.colab import files
uploaded = files.upload()

#transform documents to df and add IDs

contexts = pd.read_csv(io.BytesIO(uploaded['reliable-and-relatable-journalists-ethos-utterances-metadasa.csv']))
metadata = pd.read_csv(io.BytesIO(uploaded['reliable-and-relatable-journalists-dataset-II-metadata.csv']))
contexts.zip.fillna(method='ffill', inplace=True)
contexts.docx.fillna(method='ffill', inplace=True)
metadata['ID'] = metadata['zip'] + ' ' + metadata['docx']
contexts['ID'] = contexts['zip'] + ' ' + contexts['docx']

#reading the data from the annoted word lists
verbs = pd.read_excel(io.BytesIO(uploaded['allpersonalverbs.xlsx']))
adjectives = pd.read_excel(io.BytesIO(uploaded['allpersonaladjectives.xlsx']))
nouns = pd.read_excel(io.BytesIO(uploaded['allpersonalnouns.xlsx']))
xcomps = pd.read_excel(io.BytesIO(uploaded['allpersonalxcomps.xlsx']))

all_words = pd.concat([verbs, adjectives, nouns, xcomps])
all_words = all_words[['Unnamed: 0', 'appraisal', 'valence']]

positive_dict = all_words[all_words['valence'] == 'positive']['Unnamed: 0'].to_list()
negative_dict = all_words[all_words['valence'] == 'negative']['Unnamed: 0'].to_list()
happy_dict = all_words[all_words['appraisal'].isin(['cheer', 'affection'])]['Unnamed: 0'].to_list()
tot_dict = positive_dict + negative_dict

tot_dict

def scatterplot_data(data, metadata, dictionary):
  #create list of words that are present in the context data and are related to the category

  category_list = dictionary

  # keep only the values for adj & xcomp if they have 'zijn' or 'voelen' as verb
  data['source:ADJ'] = [data.loc[i, 'source:ADJ'] if data.loc[i, 'cop'] == 'zijn' and data.loc[i, 'nsubj'] in ['ik', 'we', 'wij'] else np.nan for i in data.index]
  #interne_kopie['source:NOUN'] = [interne_kopie.loc[i, 'source:NOUN'] if interne_kopie.loc[i, 'cop'] == 'zijn' and interne_kopie.loc[i, 'nsubj'] in ['ik', 'we', 'wij'] else np.nan for i in interne_kopie.index]
  data['xcomp'] = [data.loc[i, 'xcomp'] if data.loc[i, 'source:VERB'] == 'voelen' and data.loc[i, 'nsubj'] in ['ik', 'we', 'wij'] else np.nan for i in data.index]
  data['source:NOUN'] = [data.loc[i, 'source:NOUN'] if data.loc[i, 'nmod:poss'] in ['mijn', 'ons'] else np.nan for i in data.index]

  # maak regex van de woordenlijst zodat de woorden in dataframe daaraan gematcht kunnen worden
  rgx_emo = r'\b(' + '|'.join(category_list) + r')\b'

  #check per sentence if there is one of the words
  interne_kopie = data.copy()
  for col in interne_kopie.columns[-29:-1]:
    interne_kopie[col] = (interne_kopie[col].str.match(rgx_emo)).astype('float')
  interne_kopie['emo_score'] = interne_kopie.loc[:, ['source:ADJ', 'xcomp', 'source:VERB', 'source:NOUN']].sum(axis=1)

  #turn sentence scores into article scores
  data.text = data.text.fillna(method='ffill')
  sentence_data_IDS = interne_kopie[interne_kopie['emo_score'] > 0].index
  sentence_data = data[data.index.isin(sentence_data_IDS)]
  article_data = interne_kopie.groupby('ID')['emo_score'].sum().reset_index()

  #calculate relative scores per article
  article_data['year'] = [row.split('date-')[-1][0:4] for row in article_data['ID']]
  article_data = article_data.sort_values('year')
  article_data = article_data[article_data['emo_score'] > 0]
  category_metadata = metadata[metadata['ID'].isin(article_data['ID'])].reset_index()
  article_data = article_data.sort_values('ID').reset_index()
  category_metadata = category_metadata.sort_values('ID').reset_index()
  article_data['length'] = [x for x in category_metadata['n words']]
  article_data['relative'] = article_data['emo_score'].div(article_data['length'])

  return category_list, article_data, category_metadata, sentence_data

pos_list, pos_data, pos_metadata, pos_sentences = scatterplot_data(contexts, metadata, positive_dict)

neg_list, neg_data, neg_metadata, neg_sentences = scatterplot_data(contexts, metadata, negative_dict)

tot_list, tot_data, tot_metadata, tot_sentences = scatterplot_data(contexts, metadata, tot_dict)

hap_list, hap_data, hap_metadata, hap_sentences = scatterplot_data(contexts, metadata, happy_dict)

#create dataset for further qualitative analysis

hap_sentences.to_excel('happy_sentences_appraisal.xlsx')

#calculate number of articles within a category journalism

def pers_art_avg(categorydata, metadata):
  metadata['year'] = [row.split('date-')[-1][0:4] for row in metadata['zip']]
  metadata['year'] = metadata['year'].astype(float)
  avg = []
  for year in categorydata['year'].value_counts().index:
    avg.append(len(categorydata[categorydata['year'] == year])/len(metadata[(metadata['year'] == year)])*100)
  df = pd.DataFrame(avg, index=categorydata['year'].value_counts().index.to_list()).sort_index()
  return df

#calculate number of articles within personal journalism

def pers_art_avg_pers(categorydata, metadata):
  metadata = metadata[metadata['is personal'] == True]
  avg = []
  for year in categorydata['year'].value_counts().index:
    avg.append(len(categorydata[categorydata['year'] == year])/len(metadata[(metadata['year'] == year)])*100)
  df = pd.DataFrame(avg, index=categorydata['year'].value_counts().index.to_list()).sort_index()
  return df

def pers_art_avg_contexts(categorydata, contexts):
  contexts['year'] = [x.split('date-')[1][0:4] for x in contexts.zip]
  contexts['year'] = contexts['year'].astype(float)
  categorydata['year'] = [x.split('date-')[1][0:4] for x in categorydata.ID]
  categorydata['year'] = categorydata['year'].astype(float)
  avg = []
  for year in categorydata['year'].value_counts().index:
    avg.append(len(categorydata[categorydata['year'] == year])/len(contexts[(contexts['year'] == year)])*100)
  df = pd.DataFrame(avg, index=categorydata['year'].value_counts().index.to_list()).sort_index()
  return df

#calculate # of emo/pos/neg articles journalism
avg_pos = pers_art_avg(pos_metadata, metadata)
avg_neg = pers_art_avg(neg_metadata, metadata)
avg_tot = pers_art_avg(tot_metadata, metadata)
avg_pos_cont = pers_art_avg_contexts(pos_data, contexts)
avg_neg_cont = pers_art_avg_contexts(neg_data, contexts)
avg_tot_cont = pers_art_avg_contexts(tot_data, contexts)
avg_pos_pers = pers_art_avg_pers(pos_data, metadata)
avg_neg_pers = pers_art_avg_pers(neg_data, metadata)
avg_tot_pers = pers_art_avg_pers(tot_data, metadata)

#make linear regression on relative frequency over time

year = avg_tot_pers.index.values.reshape(-1, 1)  
emo = avg_tot_pers.iloc[:, 0].values.reshape(-1, 1)  
linear_regressor = LinearRegression()  
linear_regressor.fit(year, emo)  
emo_pred = linear_regressor.predict(year) 

#make linear regression again in statsmodels to get p-value and r-squared

x = range(1, 17, 1)

import statsmodels.api as sm

x = x
y = avg_tot_pers.iloc[:, 0].values
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
predictions = model.predict(x)

#plot average % of articles with emotions in Dutch personal newspaper journalism

plt.figure(dpi=1200)
plt.scatter(year, emo, color='#009CEF')
plt.plot(year, emo_pred, color='#dc002d')
plt.xlabel('year')
plt.ylabel('% of personal journalism')
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
plt.xticks(rotation=90)
#plt.title('Personal journalism articles with denoted authorial emotions (n= 4104)')
rsquared_emo = 'rsquared = ' + str(round(model.rsquared,3))
p = 'p-value = ' + str(round(model.pvalues[1],3))
plt.annotate(rsquared_emo, xy = (0, -0.3), xycoords='axes fraction')
plt.annotate(p, xy = (0, -0.35), xycoords='axes fraction')
plt.ylim(0, 30)

plt.show()

#make linear regression on relative frequency over time

year_tot = avg_tot.index.values.reshape(-1, 1)  
emo_tot = avg_tot.iloc[:, 0].values.reshape(-1, 1)  
linear_regressor = LinearRegression()  
linear_regressor.fit(year_tot, emo_tot)  
emo_pred_tot = linear_regressor.predict(year_tot) 

#make linear regression again in statsmodels to get p-value and r-squared

x = range(1, 17, 1)

import statsmodels.api as sm

x = x
y = avg_tot.iloc[:, 0].values

x = sm.add_constant(x)

model_tot = sm.OLS(y, x).fit()
predictions_tot = model.predict(x)

#plot average % of articles with emotions in Dutch personal newspaper journalism

plt.figure(dpi=1200)
plt.scatter(year_tot, emo_tot, color='#009CEF')
plt.plot(year_tot, emo_pred_tot, color='#dc002d')
plt.xlabel('year')
plt.ylabel('% of Dutch newspaper journalism')
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
plt.xticks(rotation=90)
#plt.title('Articles with denoted authorial emotions in Dutch newspaper journalism (n=' + str(len(metadata)) + ')')
rsquared_emo_tot = 'rsquared = ' + str(round(model_tot.rsquared,3))
p_tot = 'p-value = ' + str(round(model_tot.pvalues[1],3))
plt.annotate(rsquared_emo_tot, xy = (0, -0.3), xycoords='axes fraction')
plt.annotate(p_tot, xy = (0, -0.35), xycoords='axes fraction')
plt.ylim(0, 5)

plt.show()

#plot average % of articles with pos/neg journalistic feelings in Dutch newspaper journalism

plt.figure(dpi=1200)
plt.plot(avg_pos, marker = '.', label='positive', color='#009CEF')
plt.plot(avg_neg, marker = '.', label='negative', color='#dc002d')
plt.legend(loc='upper left')
plt.xlabel('year')
plt.ylabel('% of Dutch newspaper journalism')
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
plt.xticks(rotation=90)
ttest_p = 'p-value ttest =' + str(round(ttest_ind(avg_neg, avg_pos)[1][0], 3))
plt.annotate(ttest_p, xy= (0, -0.3), xycoords='axes fraction')
plt.ylim(0, 5)

plt.show()
