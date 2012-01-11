#!/usr/bin/env python 
import re

ad_domains = set(['yougetpaidtoadvertise.co.uk', 'spn.tw', 'revtwt.com',\
    'ads.tt', 'c.enhance.com', 'mylikes.com', 'mlks.co', 'jol.ly', 'shm.ag',\
    'sharemagnet.com', 'viralurl.com', 'vur.me', 'p.gs', 'q.gs', 'adf.ly',\
    'spn.sr', 'feedzebirds.com'])

ad_domain_patterns = [re.compile(r'(^|\.)%s$' % ad_domain)\
    for ad_domain in ad_domains]

adwords = ['advertisement', 'sponsored', 'ad']
adword_patterns = [re.compile('^' + adword + '[: ]| ' +\
        adword + '[: ]', flags = re.I) for adword in adwords]
