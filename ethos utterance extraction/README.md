# Word Collocation

## Preparation

To analyze the contexts of personal pronouns, these notebooks were used to create a dataset of articles manually
annotated for personal pronouns and whether the entire article is or isn't to be considered as personal. 

 * [01. Read downloads from Nexis Uni.ipynb](notebooks/01.%20Read%20downloads%20from%20Nexis%20Uni.ipynb)
 * [02. Removal of similar articles.ipynb](notebooks/02.%20Removal%20of%20similar%20articles.ipynb)
 * [03. Run quote, POS and dependency detection.ipynb](notebooks/03.%20Run%20quote,%20POS%20and%20dependency%20detection.ipynb)
 * [04. Labelstudio export for mannual annotation of personal pronouns.ipynb](notebooks/04.%20Labelstudio%20export%20for%20mannual%20annotation%20of%20personal%20pronouns.ipynb)

## Nexis Uni data and preprocessing

 * [01. Read downloads from Nexis Uni.ipynb](notebooks/01.%20Read%20downloads%20from%20Nexis%20Uni.ipynb)
 * [02. Removal of similar articles.ipynb](notebooks/02.%20Removal%20of%20similar%20articles.ipynb)

We've manually downloaded 66,197 articles of `de Volkskrant`, `AD/Algemeen Dagblad` and `NRC Handelsblad` for these dates as docx-files, as we
found this was the cleanest format.

| paper            | dates (count)                                                |
|:-----------------|:-------------------------------------------------------------|
| Algemeen Dagblad | ![Algemeen Dagblad](images/dates-paper-Algemeen Dagblad.png) |
| NRC Handelsblad  | ![NRC Handelsblad](images/dates-paper-NRC Handelsblad.png)   |
| de Volkskrant    | ![de Volkskrant](images/dates-paper-de Volkskrant.png)       |

Algemeen Dagblad and de Volkskrant start respectively in 1993 and 1995, instead of 1991, because there were
no articles or significantly less compared to the rest of the time period.

Opinion articles were identified as those from sections called `opinie`, `debat`, `trefpunt`, `forum`, `service`, `u-pagina`, `u pagina` and
`advertentie` and were removed.

Several articles were very similar, e.g. two articles were exactly the same, except for the semicolon after
"SAMENVATTING". In this case the shorter one, without semicolon, was removed. This filtering was applied to
all articles  with Levenshtein distance smaller than 0.37, that means any articles that matches 63% than another one,
and that is shorter, was removed.

    SAMENVATTING:
    
    Magazinelezers proeven en keuren. Deze week: graskaas
    
    VOLLEDIGE TEKST:
    
    ...

The 0.37 was determined by plotting the distribution of Levenshtein distance as well:

![Algemeen Dagblad](images/levenshtein.png) 

# Manual annotation

We applied the quote model (see quotemodels repository) on these articles and selected those with personal pronouns
outside of detected quotes as personal, the others are considered non-personal without further inspection. The 13,692
articles were considere potentially personal, and the pronouns outside of detected quotes were marked but also manually
corrected. The automatic annotations can be shared with other researchers upon reasonable request. The preannotations also contains the non-personal articles.  
 
 * [03. Run quote, POS and dependency detection.ipynb]
 * [04. Labelstudio export for mannual annotation of personal pronouns.ipynb]

Metadata of all articles, including statistics on pronouns, can be found [here](data/reliable-and-relatable-journalists-dataset-II-metadata.csv)

# Word collocations

The contexts of these pronouns were determined via dependency parsing. The script below finds contexts of all words with
a personal pronoun as a direct child, including the children that have have relation `nsubj`, `obj`, `fixed`, `aux`,
`mod`, `obl`, `obl:agent`, `nsubj:pass`, `xcomp`, `nmod:poss`, `iobj`, `advmod` or `cop` to their parent. An example is
shown in the figure below, which results in these two contexts due to the pronouns `ik` and `mijn`:

| parent (VERB) | advmod          | nsubj | parent (NOUN) | nmod:poss |
|---------------|-----------------|-------|---------------|-----------|
| schrok        | toen, wel, even | ik    |               |           |
|               |                 |       | leven         |  mijn     |

