"""
Makes a chromosome or plasmid item

Example mouse chromosome 5
https://www.wikidata.org/wiki/Q15304656

Example yeast chromosome XII
https://www.wikidata.org/wiki/Q27525657

"""
import os
from datetime import datetime

import pandas as pd
from wikidataintegrator import wdi_core, wdi_helpers


class ChromosomeBot:

    chr_type_map = {'Chromosome': 'Q37748',
                    'Mitochondrion': 'Q18694495',
                    'Chloroplast': 'Q22329079'}

    def __init__(self):
        self.retrieved = None
        self.login = None
        self.ass_sum = None
        self.chr_df = dict()

    def get_assembly_summaries(self):
        names = ['assembly_accession', 'bioproject', 'biosample', 'wgs_master', 'refseq_category', 'taxid',
                 'species_taxid', 'organism_name', 'infraspecific_name', 'isolate', 'version_status', 'assembly_level',
                 'release_type', 'genome_rep', 'seq_rel_date', 'asm_name', 'submitter', 'gbrs_paired_asm',
                 'paired_asm_comp', 'ftp_path', 'excluded_from_refseq']
        self.ass_sum = pd.read_csv("ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt", sep="\t",
                                   comment="#", names=names, low_memory=False)

    def get_assembly_report(self, taxid):
        if self.ass_sum is None:
            self.get_assembly_summaries()
        df = self.ass_sum.query("taxid == {} & refseq_category == 'reference genome'".format(taxid))
        if len(df) != 1:
            raise ValueError("unknown reference: {}".format(df))
        ftp_path = list(df.ftp_path)[0]
        assembly = os.path.split(ftp_path)[1]
        url = os.path.join(ftp_path, assembly + "_assembly_report.txt")
        names = ['Sequence-Name', 'Sequence-Role', 'Assigned-Molecule', 'Assigned-Molecule-Location/Type',
                 'GenBank-Accn', 'Relationship',
                 'RefSeq-Accn', 'Assembly-Unit', 'Sequence-Length', 'UCSC-style-name']
        self.chr_df[taxid] = pd.read_csv(url, sep="\t", names=names, comment='#')

    def get_chrom_info(self, chr_name, taxid):
        """ result looks like:
        {'Assembly-Unit': 'C57BL/6J',
        'Assigned-Molecule': '1',
        'Assigned-Molecule-Location/Type': 'Chromosome',
        'GenBank-Accn': 'CM000994.2',
        'RefSeq-Accn': 'NC_000067.6',
        'Relationship': '=',
        'Sequence-Length': 195471971,
        'Sequence-Name': '1',
        'Sequence-Role': 'assembled-molecule',
        'UCSC-style-name': 'chr1'}
        """

        if taxid not in self.chr_df:
            self.get_assembly_report(taxid)
        d = self.chr_df[taxid][self.chr_df[taxid]['Sequence-Name'] == chr_name].to_dict('records')[0]

        return d

    def get_or_create(self, organism_info, retrieved=None, login=None):
        """
        Make sure all chromosome items exist
        return a map of chr num to wdid. looks like:
        {'1': 'Q28114580',  '2': 'Q28114581', ..., 'MT': 'Q28114585'}

        :param organism_info: {'name': name, 'taxid': taxid, 'wdid': wdid, 'type': type}
        :type organism_info: dict
        :param retrieved: for reference statement
        :type retrieved: datetime
        :param login:
        :return:
        """
        self.login = login
        self.retrieved = datetime.now() if retrieved is None else retrieved

        taxid = int(organism_info['taxid'])
        if taxid not in self.chr_df:
            self.get_assembly_report(taxid)

        # map of chr_num to wdid for this taxon ("1" -> "Q1234")
        chr_num_wdid = dict()

        # get assembled chromosomes, which we will create items for
        chrdf = self.chr_df[taxid][self.chr_df[taxid]['Sequence-Role'] == 'assembled-molecule']

        existing_chr = wdi_helpers.id_mapper("P2249")
        existing_chr = {k.split(".")[0]: v for k, v in existing_chr.items()}

        for record in chrdf.to_dict("records"):
            chrom_num = record['Sequence-Name']
            genome_id = record['RefSeq-Accn']
            genome_id = genome_id.split(".")[0]
            chr_type = record['Assigned-Molecule-Location/Type']
            # {'Chromosome','Mitochondrion'}
            # chrom_type = record['Assigned-Molecule-Location/Type']
            if genome_id in existing_chr:
                chr_num_wdid[chrom_num] = existing_chr[genome_id]
            else:
                # chromosome doesn't exist in wikidata. create it
                print("chromosome being created: {}, {}".format(chrom_num, genome_id))
                chr_num_wdid[chrom_num] = self.create_chrom(organism_info, chrom_num, genome_id, chr_type, login)

        return chr_num_wdid

    def create_chrom(self, organism_info, chrom_num, genome_id, chr_type, login):

        def make_ref(retrieved, genome_id):
            """
            Create reference statement for chromosomes
            :param retrieved: datetime
            :type retrieved: datetime
            :param genome_id: refseq genome id
            :type genome_id: str
            :return:
            """
            refs = [
                wdi_core.WDItemID(value='Q20641742', prop_nr='P248', is_reference=True),  # stated in ncbi gene
                wdi_core.WDString(value=genome_id, prop_nr='P2249', is_reference=True),  # Link to Refseq Genome ID
                wdi_core.WDTime(retrieved.strftime('+%Y-%m-%dT00:00:00Z'), prop_nr='P813', is_reference=True)
            ]
            return refs

        item_name = '{} chromosome {}'.format(organism_info['name'], chrom_num)
        item_description = '{} chromosome'.format(organism_info['type'])
        print(item_name)
        print(genome_id)

        reference = make_ref(self.retrieved, genome_id)

        # subclass of chr_type
        if chr_type not in ChromosomeBot.chr_type_map:
            raise ValueError("unknown chromosome type: {}".format(chr_type))
        statements = [wdi_core.WDItemID(value=ChromosomeBot.chr_type_map[chr_type], prop_nr='P279', references=[reference])]
        # found in taxon
        statements.append(wdi_core.WDItemID(value=organism_info['wdid'], prop_nr='P703', references=[reference]))
        # genome id
        statements.append(wdi_core.WDString(value=genome_id, prop_nr='P2249', references=[reference]))

        wd_item = wdi_core.WDItemEngine(item_name=item_name, domain='chromosome', data=statements,
                                        append_value=['P279'], fast_run=True,
                                        fast_run_base_filter={'P703': organism_info['wdid'], 'P2249': ''})
        if wd_item.wd_item_id:
            return wd_item.wd_item_id

        wd_item.set_label(item_name)
        wd_item.set_description(item_description, lang='en')
        wdi_helpers.try_write(wd_item, genome_id, 'P2249', login)
        return wd_item.wd_item_id

