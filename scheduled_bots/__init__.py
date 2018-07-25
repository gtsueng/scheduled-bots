PROPS = {
    'ATC code': 'P267',
    'Archive url': 'P1065',
    'CAS registry number': 'P231',
    'CIViC variant ID': 'P3329',
    'ChEBI ID': 'P683',
    'ChEMBL ID': 'P592',
    'ChemSpider ID': 'P661',
    'DOI': 'P356',
    'Disease Ontology ID': 'P699',
    'Drugbank ID': 'P715',
    'EC Number': 'P591',
    'Encoded By': 'P702',
    'Ensembl Gene ID': 'P594',
    'Ensembl Protein ID': 'P705',
    'Ensembl Transcript ID': 'P704',
    'Entrez Gene ID': 'P351',
    'GARD rare disease ID': 'P4317',
    'Gene Ontology ID': 'P686',
    'Genomic end position': 'P645',
    'Genomic start position': 'P644',
    'HGNC gene symbol': 'P353',
    'HGNC symbol': 'P354',
    'HGVS nomenclature': 'P3331',
    'Human Gene symbol': 'P353',
    'Human Phenotype Ontology ID': 'P3841',
    'ICD-10': 'P494',
    'ICD-10-CM': 'P4229',
    'ICD-9': 'P493',
    'ICD-9-CM': 'P1692',
    'IUPHAR ID': 'P595',
    'InChI': 'P234',
    'InChIKey': 'P235',
    'InterPro ID': 'P2926',
    'Isomeric SMILES': 'P2017',
    'KEGG ID': 'P665',
    'MGI': 'P671',
    'MeSH Code': 'P672',
    'MeSH ID': 'P486',
    'Mondo ID': 'P5270',
    'NCBI Locus tag': 'P2393',
    'NCBI Taxonomy ID': 'P685',
    'NCI Thesaurus ID': 'P1748',
    'NDF-RT NUI': 'P2115',
    'National Cancer Thesaurus ID': 'P1395',
    'OMIM': 'P492',
    'OMIM ID': 'P492',
    'Orphanet ID': 'P1550',
    'PDB ID': 'P638',
    'PMC ID': 'P932',
    'Protein Structure Image': 'P18',
    'PubChem ID (CID)': 'P662',
    'PubMed ID': 'P698',
    'RTECS Number': 'P657',
    'RefSeq RNA ID': 'P639',
    'Refseq Genome ID': 'P2249',
    'Refseq Protein ID': 'P637',
    'SMILES': 'P233',
    'Saccharomyces Genome Database ID': 'P3406',
    'Sequence Ontology ID': 'P3986',
    'UBERON ID': 'P1554',
    'UMLS CUI': 'P2892',
    'UNII': 'P652',
    'Uniprot ID': 'P352',
    'Word Health Organisation International Nonproprietary Name': 'P1805',
    'anatomical location': 'P927',
    'biological process': 'P682',
    'biological variant of': 'P3433',
    'cell component': 'P681',
    'chemical formula': 'P274',
    'chromosome': 'P1057',
    'curator': 'P1640',
    'determination method': 'P459',
    'develops from': 'P3094',
    'encodes': 'P688',
    'equivalent class': 'P1709',
    'exact match': 'P2888',
    'found in taxon': 'P703',
    'genetic association': 'P2293',
    'genomic assembly': 'P659',
    'genomic end': 'P645',
    'genomic start': 'P644',
    'has cause': 'P828',
    'has part': 'P527',
    'homologene id': 'P593',
    'instance of': 'P31',
    'location': 'P276',
    'medical condition treated': 'P2175',
    'miRBase mature miRNA ID': 'P2871',
    'miRBase pre-miRNA ID': 'P2870',
    'mirTarBase ID': 'P2646',
    'molecular function': 'P680',
    'offical website': 'P856',
    'ortholog': 'P684',
    'parent taxon': 'P171',
    'part of': 'P361',
    'reference URL': 'P854',
    'regulates (molecular biology)': 'P128',
    'retrieved': 'P813',
    'route of administration': 'P636',
    'stated in': 'P248',
    'subclass of': 'P279',
    'subject has role': 'P2868',
    'symptoms': 'P780',
    'taxon name': 'P225',
    'uberon id': 'P1554'
}

ITEMS = {
    'Cancer Biomarkers database': 'Q38100115',
    'Genome assembly GRCh37': 'Q21067546',
    'sequence variant': 'Q15304597',
    'Missense Variant': 'Q27429979',
    'MyVariant.info': 'Q38104308',
    'CGI Evidence Clinical Practice': 'Q38145055',
    'CGI Evidence Clinical Trials III-IV': 'Q38145539',
    'CGI Evidence Clinical Trials I-II': 'Q38145727',
    'CGI Evidence Case Reports': 'Q38145865',
    'CGI Evidence Pre-Clinical Data': 'Q38145925',
    'combination therapy': 'Q1304270'
}

DEFAULT_CORE_PROPS = ['NCBI Taxonomy ID', 'National Cancer Thesaurus ID', 'UNII', 'MeSH Code', 'IUPHAR ID',
                      'Archive url', 'Uniprot ID', 'RefSeq RNA ID', 'Entrez Gene ID', 'DOI', 'Refseq Genome ID',
                      'Protein Structure Image', 'NCBI Locus tag', 'PMC ID', 'PubMed ID', 'NCI Thesaurus ID',
                      'InterPro ID', 'InChIKey', 'ChEBI ID', 'mirTarBase ID', 'ChemSpider ID', 'MGI',
                      'miRBase mature miRNA ID', 'OMIM', 'Disease Ontology ID', 'PubChem ID (CID)', 'HGNC symbol',
                      'RTECS Number', 'NDF-RT NUI', 'Gene Ontology ID', 'Drugbank ID', 'miRBase pre-miRNA ID',
                      'KEGG ID', 'Word Health Organisation International Nonproprietary Name', 'InChI', 'MeSH ID',
                      'Human Gene symbol', 'ChEMBL ID', 'Orphanet ID']
DEFAULT_CORE_PROPS_PIDS = set(PROPS[x] for x in DEFAULT_CORE_PROPS)


def get_default_core_props(sparql_endpoint_url='https://query.wikidata.org/sparql'):
    # get the distinct value props from wikidata, and merge that list with the default_core_props listed here
    from wikidataintegrator import wdi_core, wdi_helpers
    h = wdi_helpers.WikibaseHelper(sparql_endpoint_url)
    pids = set(h.get_pid(x) for x in DEFAULT_CORE_PROPS_PIDS)
    wdi_core.WDItemEngine.get_distinct_value_props(sparql_endpoint_url)
    wdi_core.WDItemEngine.DISTINCT_VALUE_PROPS[sparql_endpoint_url].update(pids)
    core_props = wdi_core.WDItemEngine.DISTINCT_VALUE_PROPS[sparql_endpoint_url]
    return core_props