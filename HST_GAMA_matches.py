#use to match multiple HST catalogs with GamaCoreDR1

# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import sys, os, time
import urllib, urlparse, string, time
import csv
import urllib2 
import subprocess
import glob
import os

def distance(GAMA_RA, RA2, GAMA_DEC, DEC2):    
    dist = ((((GAMA_RA-RA2)*(np.cos((1/2)*(GAMA_DEC+DEC2))))**(2))+(GAMA_DEC-DEC2)**(2))**(1/2)
    return dist

def match(cat):
	hstcat = cat
	GAMA_RA = GamaCoreDR1['GAMA_RA']
	GAMA_DEC = GamaCoreDR1['GAMA_DEC']
	RA2 = hstcat['RA2'] 
	DEC2 = hstcat['DEC2'] 
	hst_index_array = []
	gama_index_array = []
	deltaRA = []
	deltaDEC = []
	for i in range(len(hstcat)):
		#print i
		n = 1 * 1/3600
		index_array = np.where((GAMA_RA>(RA2[i]-n/2))\
			& (GAMA_RA<(RA2[i]+n/2))\
			& (GAMA_DEC>(DEC2[i]-n/2))\
			& (GAMA_DEC<(DEC2[i]+n/2)))[0]
		if index_array.size: #print index_array
			if len(index_array) == 1:
				deltaRA.append(RA2[i]-GAMA_RA[index_array])
				deltaDEC.append(DEC2[i]-GAMA_DEC[index_array])
				hst_index_array.append(i) 
				gama_index_array.append(index_array)
		elif len(index_array) >> 1: 
#use disance formula for len>1 to find closest match
			DIST = distance(RA2[i], GAMA_RA[index_array], DEC2[i],GAMA_DEC[index_array])
			min_arg = np.argmin(DIST)
			GAMA_RA_match = GAMA_RA[index_array][min_arg]
			GAMA_DEC_match = GAMA_DEC[index_array][min_arg]
			deltaRA.append(RA2[i]-GAMA_RA_match)
			deltaDEC.append(DEC2[i]-GAMA_DEC_match)
			hst_index_array.append(i)
			gama_index_array.append(index_array[min_arg])
		else: continue
	return hst_index_array, gama_index_array

imagedir = '/data2/bdm/G09/new_matches/G09_HSTdatav2/132.138.-1.2/' 

GAMA_names = ['GAMA_ID', 'GAMA_RA', 'GAMA_DEC']
HST_names = [ 'RA2', 'DEC2'] 

GamaCoreDR1 = np.genfromtxt('/data2/bdm/GamaCoreDR1_v1.cat', names=GAMA_names, dtype=None, usecols=(1,3,4), skip_header=1, delimiter = ',') #dlimiter = ',' means numbers in cat are separated by comma, space is default

gama_id = []
gama_ra = []
gama_dec = []
hst_ra = []
hst_dec = []
hst_dataset_name = []

#make a function for match and put it in the loop (see test_func.py)
for fl in glob.glob(imagedir + "*_drc.cat"):
    print os.path.basename(fl)
    hstcat = np.genfromtxt(fl, dtype=None, names=HST_names, skip_header=9, usecols=(5,6))
    hst_ind_arr, gama_ind_arr = match(hstcat)
    if len(hst_ind_arr) != len(gama_ind_arr):
        print "Error! The number of matched indices are not equal. Exiting..."
        sys.exit()
    if hst_ind_arr: 
        for j in range(len(hst_ind_arr)):
            hst_ra.append(hstcat["RA2"][hst_ind_arr][j])
            hst_dec.append(hstcat["DEC2"][hst_ind_arr][j])
            hst_dataset_name.append(os.path.basename(fl).split("_")[0])
            gama_ra.append(GamaCoreDR1["GAMA_RA"][gama_ind_arr[j]])
            gama_dec.append(GamaCoreDR1["GAMA_DEC"][gama_ind_arr[j]])
            gama_id.append(GamaCoreDR1["GAMA_ID"][gama_ind_arr[j]])

gama_id = np.asarray(gama_id)
gama_ra = np.asarray(gama_ra)
gama_dec = np.asarray(gama_dec)
hst_ra = np.asarray(hst_ra)
hst_dec = np.asarray(hst_dec)
hst_dataset_name = np.asarray(hst_dataset_name)
# Issues -- 
# 1. there are matches that aren't unique. Needs to be fixed
# 2. Only 17 unique matches? WHY??

outdir = '/data2/bdm/G09/new_matches/G09_HSTdatav2/'
data = np.array(zip(gama_id, gama_ra, gama_dec, hst_ra, hst_dec, hst_dataset_name),\
                dtype=[('gama_id', 'i4'), ('gama_ra', 'f8'), ('gama_dec', 'f8'), ('hst_ra', 'f8'), ('hst_dec', 'f8'), ('hst_dataset_name', 'S10')])

np.savetxt(outdir + 'HST_G09_matches2.txt', data, fmt=['%d', '%.4f', '%.4f', '%.4f', '%.4f', '%s'], delimiter=' ')
# the keyword -- header -- will not work in savetxt here. this is because we have numpy version 1.4.1 
# and header was introduced in version 1.7.0

