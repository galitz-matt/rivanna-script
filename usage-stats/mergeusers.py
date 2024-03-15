#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Sun Sep 13 21:32:40 2020

@author: khs3z
"""
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:52:13 2020

@author: khs3z
"""


import pandas as pd
import os
import sys


uidfile = sys.argv[1]
output_path = sys.argv[2]
outputfile = f"{output_path}/Combined_{os.path.basename(uidfile)}"
officehours = f"{output_path}/Combined_Office Hours Attendees-curated.csv"
report = f"{output_path}/Office_Hours_Attendees-report.xlsx"

schools = {'AS': ['e0:as', 's0:as', 's1:as', 's3:as', 'arts', 'global public health', 'english','economics', 'psychology', 'environmental', 'politics', 'biology', 'chemistry'],
           'EN': ['e0:en', 's0:en', 's1:en', 's2:en','engineer', 'systems', 'computer', 'materials'], 
           'MD': ['e0:interns and  resident','e0:md', 'som', 'global health', 'cphg', 'physical therapy', 'public health genomics', 'public health science', 'public health services', 'pharma', 'md-micr', 'biomed', 'infect', 'neuroscience', 'medicine', 'cardiovascular', 'cell bio', 'pediatrics', 'immunology', 'microbio'],
           'DS': ['data', 'dsi', 'sds', 'e0:ds'],
           'DA': ['da:', 'e0:da', 'darden', 'business'],
           'ED': ['ed:', 'education', 'teaching'],
           'MC': ['e0:mc', 'mcintire', 'commerce', 'mc-'],
           'BA': ['e0:cu-leadshp','batten'],
           'RC': ['e0:it-research computing', 'research-computing'],
           'BI': ['e0:pv-bii', 's0:pv-bii', 'biocomplexity'],
           'PV': ['pv-'],
           'CP': ['school for continuing and professional studies'],
           'AR': ['architecture'],
           'NR': ['nursing']}

def lookup_school(df):
    depthit = (s for s in schools for entry in schools[s] if entry in df['Dept'].lower())
    try:
        return next(depthit)
    except:
        affilhit = (s for s in schools for entry in schools[s] if entry in df['Affiliation'].lower())
        try:
            affil = next(affilhit)
            return affil
        except:
            return 'OTHER'


uid_df = pd.read_csv(uidfile, names=["UserID", "Lastname", "Firstname", "Affiliation", "Status"])
uid_df['School'] = uid_df.apply(lookup_school, axis=1)
uid_df.to_csv(outputfile)
print(uid_df)
print('-------------------------------------------')
