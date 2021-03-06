# http://mitodb.com/symptoms.php?oid=302060&symptoms=Show
import subprocess
from itertools import chain
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import pandas as pd


def download_disease_list():
    ## get all diseases
    url = "http://mitodb.com/"
    bs = BeautifulSoup(requests.get(url).text, "lxml")
    table = bs.find('td', text='Mitochondrial').find_parent("table")
    df = pd.read_html(str(table), converters={1: str})[0]
    omims = set(df.loc[:, 1].dropna())
    table = bs.find('td', text='Non mitochondrial').find_parent("table")
    df = pd.read_html(str(table), converters={1: str})[0]
    omims.update(set(df.loc[:, 1].dropna()))
    table = bs.find('td', text='Unknown pathogenesis or possibly mitochondrial').find_parent("table")
    df = pd.read_html(str(table), converters={1: str})[0]
    omims.update(set(df.loc[:, 1].dropna()))
    return omims


def download_disease_symptoms(omims):
    phenotypes = dict()
    for omim in tqdm(sorted(list(omims))):
        url = "http://mitodb.com/symptoms.php?oid={}&symptoms=Show".format(omim)
        bs = BeautifulSoup(requests.get(url).text, "lxml")
        table = bs.find('td', text='Symptom/sign').find_parent("table")
        df = pd.read_html(str(table))[0]
        df.columns = df.iloc[0]
        df = df.reindex(df.index.drop(0))
        df['Symptom/sign'] = df['Symptom/sign'].str.lower()
        del df['Edit/add reference']
        df['disease'] = omim
        phenotypes[omim] = df

    df = pd.concat(phenotypes.values())
    return df


def generate_hpo_labels():
    s = """
    prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?item ?label (GROUP_CONCAT(DISTINCT ?synonym;separator="|") AS ?synonyms)
    (GROUP_CONCAT(DISTINCT ?related;separator="|") AS ?relateds) where {
      ?item rdfs:label ?label .
      OPTIONAL {?item oboInOwl:hasExactSynonym ?synonym }
      OPTIONAL {?item oboInOwl:hasRelatedSynonym ?related }
    } GROUP BY ?item ?label
    """
    with open("labels.sparql", "w") as f:
        f.write(s)

    subprocess.check_call("robot query --input hp.owl --query labels.sparql labels.csv", shell=True)


def load_hpo_labels():
    hpo_label_df = pd.read_csv("labels.csv")
    hpo_label_df['item'] = hpo_label_df['item'].map(lambda x: x.replace("http://purl.obolibrary.org/obo/HP_", "HP:"))
    hpo_label = dict(zip(hpo_label_df.label.str.lower(), hpo_label_df.item))

    syn = hpo_label_df.set_index("item").synonyms.dropna()
    syn = pd.DataFrame(syn.str.split('|').tolist(), index=syn.index).stack().reset_index()[['item', 0]]
    hpo_syn = dict(zip(syn.loc[:, 0].str.lower(), syn['item']))

    rsyn = hpo_label_df.set_index("item").relateds.dropna()
    rsyn = pd.DataFrame(rsyn.str.split('|').tolist(), index=rsyn.index).stack().reset_index()[['item', 0]]
    hpo_rsyn = dict(zip(rsyn.loc[:, 0].str.lower(), rsyn['item']))

    return hpo_label, hpo_syn, hpo_rsyn


def main():
    omims = download_disease_list()
    df = download_disease_symptoms(omims)
    hpo_label, hpo_syn, hpo_rsyn = load_hpo_labels()

    df['hpo_label'] = df['Symptom/sign'].map(hpo_label.get)
    df['hpo_syn'] = df['Symptom/sign'].map(hpo_syn.get)
    df['hpo_rsyn'] = df['Symptom/sign'].map(hpo_rsyn.get)
    df['hpo'] = df['hpo_label'].combine_first(df['hpo_syn'])
    df['hpo'] = df['hpo'].combine_first(df['hpo_rsyn'])
    del df['hpo_label']
    del df['hpo_syn']
    del df['hpo_rsyn']

    df.to_csv("mitodb.csv", index=False)

    # look at what is missing
    df2 = df[df.hpo.isnull()]
    print("{} out of {} unique symptoms missing".format(len(set(df2['Symptom/sign'])), len(set(df['Symptom/sign']))))
    print("accounting for {} out of {} links".format(len(df2), len(df)))
    # most used missing
    from collections import Counter
    print("most used missing phenotypes")
    print(Counter(df2['Symptom/sign']).most_common(10))

    print("all missing phenotypes")
    df3 = df2.groupby("Symptom/sign").agg(
        {"Pubmed id": lambda x: ";".join(list(x)), "disease": lambda x: ";".join(list(x))})
    df3.to_csv("mitodb_missing.csv")


if __name__ == '__main__':
    main()
