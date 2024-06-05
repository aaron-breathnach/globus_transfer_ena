import itertools
import os
import pandas as pd
import subprocess
import sys

## endpoints
# ena_endpoint = 'fd9c190c-b824-11e9-98d7-0a63aa6b37da'
# our_endpoint = 'b8858ea4-2c3d-11ec-95db-853490a236f9'

def filereport():
    filereport = 'https://www.ebi.ac.uk/ena/portal/api/filereport?accession={}&result=read_run&fields=run_accession,fastq_ftp,fastq_md5,fastq_bytes'
    return(filereport)

def make_batch_file(accession, out_dir):
    ## download the filereport from ENA
    url = filereport().format(accession)
    dat = pd.read_csv(url, sep='\t')
    dat.to_csv('{}_filereport.txt'.format(accession), sep='\t')
    ## get the ftp links from the filereport
    links = list(itertools.chain(*[x.split(';') for x in dat['fastq_ftp'].to_list()]))
    ## make the batch file
    with open('{}_batch_file.txt', 'w') as f:
        for link in links:
            path = link.split('/fastq/')[1]
            filename = os.path.basename(link)
            globus = '/gridftp/ena/fastq/{} ~/{}/{}'
            cmd = globus.format(path, out_dir, filename)
            f.write(cmd + '\n')

def run_globus_transfer(accession, ena_endpoint, our_endpoint, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    batch_file = '{}/{}_batch_file.txt'.format(out_dir, accession)
    if not os.path.exists(batch_file):
        make_batch_file(accession, out_dir)
    globus_transfer = 'globus transfer --batch \'{}\' \'{}\' < {}'
    globus_transfer = globus_transfer.format(ena_endpoint, our_endpoint, batch_file)
    subprocess.run(globus_transfer, shell=True)

if __name__ == '__main__':
    accession = sys.argv[0]
    ena_endpoint = sys.argv[1]
    our_endpoint = sys.argv[2]
    out_dir = sys.argv[3]
    run_globus_transfer(accession, ena_endpoint, our_endpoint, out_dir)
