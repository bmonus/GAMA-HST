"""
    Automated running Source Extractor on the reduced science frames.
"""

import subprocess
import glob
import os

sexbin = '/usr/bin/sex'
sexargs = ['-c', 'config.txt']
# keep the same config.txt for all images # also keep it in the same folder as this code

imagedir = '/data2/bdm/G09/new_matches/G09_HSTdatav2/'

def run_sex(image, catname):
    runcmd = [sexbin, image] + sexargs + ['-catalog_name', catname]
    print ' '.join(runcmd)
    subprocess.call(runcmd)

for fl in glob.glob(imagedir + "*_drc.fits"):
    cat = fl.replace('.fits', '.cat')
    cat = os.path.basename(cat)
    run_sex(fl, cat)
