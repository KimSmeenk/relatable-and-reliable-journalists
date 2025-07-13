import io
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# %matplotlib inline

#import documents from local drive
#needed: reliable-and-relatable-journalists-dataset-II-metadata.csv / reliable-and-relatable-journalists-ethos-utterances-metadasa.csv

from google.colab import files
uploaded = files.upload()

#transform documents to df and add IDs

contexts = pd.read_csv(io.BytesIO(uploaded['reliable-and-relatable-journalists-ethos-utterances-metadasa.csv']))
metadata = pd.read_csv(io.BytesIO(uploaded['reliable-and-relatable-journalists-dataset-II-metadata.csv']))
contexts.zip.fillna(method='ffill', inplace=True)
contexts.docx.fillna(method='ffill', inplace=True)
metadata['ID'] = metadata['zip'] + ' ' + metadata['docx']
contexts['ID'] = contexts['zip'] + ' ' + contexts['docx']

#add year and paper to contexts and metadata file

contexts['year'] = [x.split('date-')[1][0:4] for x in contexts.zip]
contexts['year'] = contexts['year'].astype(float)
contexts['paper'] = [x.split('-')[0] for x in contexts.zip]

#get overview of amount of personal journalism per newspaper

metadata.groupby(['paper', 'year'])['is personal'].value_counts().to_excel('metadata_personal_journalism.xlsx')

#get overview of personal journalism per year

metadata.groupby('year')['is personal'].value_counts().to_excel('metadata_personal_journalism_year.xlsx')

#get overview of the 10 most used verbs in ethos utterances

contexts['source:VERB'].value_counts()[:10]

#get overview of relative frequency per witnessing verb

witnessing_verbs = ['zien', 'kijken', 'horen', 'luisteren', 'proeven', 'ruiken', 'tasten', 'voelen', 'aanraken']
rf_witnessing_verbs = (contexts['source:VERB'].value_counts()/len(contexts)*100).round(5)[witnessing_verbs]
