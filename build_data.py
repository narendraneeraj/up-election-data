#!/usr/bin/env python3
"""Build UP election master lists. No personal voter records."""
from __future__ import annotations
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)

ALIAS_DISTRICTS = {
    'Budaun': ['Badaun', 'Budaun District'],
    'Gautam Buddha Nagar': ['Gautam Budh Nagar', 'GB Nagar'],
    'Lakhimpur Kheri': ['Kheri', 'Lakhimpur-Kheri'],
    'Raebareli': ['Rae Bareli', 'Rai Bareilly'],
    'Prayagraj': ['Allahabad'],
    'Ayodhya': ['Faizabad'],
    'Hapur': ['Panchsheel Nagar'],
    'Amroha': ['Jyotiba Phule Nagar'],
    'Sambhal': ['Bhim Nagar'],
    'Shrawasti': ['Shravasti'],
    'Bhadohi': ['Sant Ravidas Nagar'],
    'Siddharthnagar': ['Siddharth Nagar'],
    'Maharajganj': ['Mahrajganj'],
    'Barabanki': ['Bara Banki'],
}

DISTRICT_HI_BY_ORDER = '''आगरा|अलीगढ़|अम्बेडकर नगर|अमेठी|अमरोहा|औरैया|अयोध्या|आज़मगढ़|बागपत|बहराइच|बलिया|बलरामपुर|बांदा|बाराबंकी|बरेली|बस्ती|भदोही|बिजनौर|बदायूँ|बुलंदशहर|चंदौली|चित्रकूट|देवरिया|एटा|इटावा|फर्रुखाबाद|फतेहपुर|फिरोजाबाद|गौतम बुद्ध नगर|गाजियाबाद|गाजीपुर|गोंडा|गोरखपुर|हमीरपुर|हापुड़|हरदोई|हाथरस|जालौन|जौनपुर|झांसी|कन्नौज|कानपुर देहात|कानपुर नगर|कासगंज|कौशाम्बी|कुशीनगर|लखीमपुर खीरी|ललितपुर|लखनऊ|महाराजगंज|महोबा|मैनपुरी|मथुरा|मऊ|मेरठ|मिर्जापुर|मुरादाबाद|मुजफ्फरनगर|पीलीभीत|प्रतापगढ़|प्रयागराज|रायबरेली|रामपुर|सहारनपुर|संभल|संत कबीर नगर|शाहजहांपुर|शामली|श्रावस्ती|सिद्धार्थनगर|सीतापुर|सोनभद्र|सुल्तानपुर|उन्नाव|वाराणसी'''.split('|')
assert len(DISTRICT_HI_BY_ORDER) == 75

SEAT_ALIASES = {
    30: ['Bilari (partly Sambhal district)'],
    58: ['Dhaulana (partly Ghaziabad district)'],
    83: ['Govardhan'],
    115: ['Budaun'],
    139: ['Gola Gokarnnath'],
    162: ['Bangermau'],
    166: ['Bhagwant Nagar'],
    169: ['Bakshi Ka Talab'],
    175: ['Lucknow Cantt.'],
    184: ['Jagdishpur (partly Sultanpur district)'],
    206: ['Akbarpur Raniya', 'Akbarpur - Raniya'],
    212: ['Govindnagar'],
    216: ['Kanpur Cantt.'],
    219: ['Madhaugarh'],
    261: ['Prayagraj West'],
    262: ['Prayagraj North'],
    263: ['Prayagraj South'],
    271: ['Rudauli (partly Barabanki district)'],
    319: ['Paniyra'],
    320: ['Campierganj'],
    328: ['Chillupar'],
    375: ['Ghazipur'],
    403: ['Dudhi'],
}
EXTRA_DISTRICTS = {
    30: ['Sambhal'],
    58: ['Ghaziabad'],
    184: ['Sultanpur'],
    271: ['Barabanki'],
}


def slug(s: str) -> str:
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')


def save_json(name: str, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    seats, district_numbers = {}, defaultdict(list)
    for line_no, raw in enumerate((ROOT / 'seat_seed.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip() or raw.startswith('#'):
            continue
        district, start, names = raw.split('|', 2)
        start = int(start)
        for index, marked_name in enumerate(names.split(';')):
            number = start + index
            assert number not in seats, f'duplicate seat {number} on line {line_no}'
            reserved = 'ST' if marked_name.endswith('^') else 'SC' if marked_name.endswith('~') else 'GEN'
            clean_name = marked_name.rstrip('~^').strip()
            seats[number] = dict(ac_number=number, name_en=clean_name,
                                 reservation=reserved, primary_district=district)
            district_numbers[district].append(number)
    assert len(seats) == 403 and set(seats) == set(range(1,404)), 'incorrect or missing assembly numbers'
    assert len(district_numbers) == 75, 'incorrect district count'
    assert Counter(a['reservation'] for a in seats.values()) == Counter(GEN=317, SC=84, ST=2), 'reservation mismatch'

    # Stable IDs follow alphabetical order. They must not change between updates.
    names = sorted(district_numbers, key=str.casefold)
    dids = {name: f'up-d{i:03d}' for i, name in enumerate(names, 1)}
    hi_lookup = dict(zip(names, DISTRICT_HI_BY_ORDER))
    districts = []
    for district in names:
        ids = sorted(district_numbers[district])
        districts.append(dict(
            id=dids[district], state_code='UP', name_en=district, name_hi=hi_lookup[district],
            slug=slug(district), aliases=ALIAS_DISTRICTS.get(district, []),
            assembly_count=len(ids), assembly_numbers=ids
        ))

    assemblies = []
    for number in range(1, 404):
        seat = seats[number]
        primary = seat.pop('primary_district')
        names_associated = [primary] + EXTRA_DISTRICTS.get(number, [])
        seat['primary_district_id'] = dids[primary]
        seat['district_ids'] = [dids[name] for name in names_associated]
        seat['district_name_en'] = primary
        seat['aliases'] = SEAT_ALIASES.get(number, [])
        seat['slug'] = slug(seat['name_en'])
        seat['state_code'] = 'UP'
        seat['cross_district'] = len(names_associated) > 1
        assemblies.append(seat)

    district_assemblies = [
        {'district_id': d['id'], 'district_name_en': d['name_en'], 'district_name_hi': d['name_hi'],
         'assembly_numbers': d['assembly_numbers'], 'assembly_count': d['assembly_count']}
        for d in districts
    ]
    meta = {
        'dataset': 'UP Assembly Constituencies — master index',
        'version': '1.0.0', 'prepared_on': '2026-11-02',
        'state_code': 'UP', 'state_name': 'Uttar Pradesh',
        'district_count': 75, 'assembly_count': 403,
        'assembly_reservation_count': {'GEN': 317, 'SC': 84, 'ST': 2},
        'classification_reference_year': 2022,
        'language_coverage': {'district_names': ['en', 'hi'], 'assembly_names': ['en']},
        'data_scope': 'District and Assembly master lists, not MLA records or personal electoral rolls',
        'district_mapping_method': 'Primary district association for navigation. Some seats span multiple districts; see district_ids.',
        'cross_district_assembly_numbers': sorted(EXTRA_DISTRICTS),
        'sources': [
            {'name': 'ECI 2022 Assembly election press note (constituency names and SC/ST categories)',
             'url': 'https://static.pib.gov.in/writereaddata/userfiles/PN_3.pdf'},
            {'name': 'Uttar Pradesh Legislative Assembly constituency and district table (secondary mapping cross-check)',
             'url': 'https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Uttar_Pradesh_Legislative_Assembly'},
            {'name': 'Government of India directory, UP districts (75 districts)',
             'url': 'https://igod.gov.in/index.php/sg/UP/E042/organizations'},
            {'name': 'Public research index of UP Electoral Rolls 2023 (cross-district evidence)',
             'url': 'https://github.com/in-rolls/electoral_rolls_up_2023'}
        ],
        'voter_services': {
            'eci_elector_search': 'https://electoralsearch.eci.gov.in/',
            'eci_roll_download': 'https://voters.eci.gov.in/download-eroll',
        },
        'disclaimer': 'Independent informational data. Not an official ECI or Government of Uttar Pradesh application. Verify changes against current ECI/CEO publications.'
    }
    save_json('districts.json', districts)
    save_json('assemblies.json', assemblies)
    save_json('district_assemblies.json', district_assemblies)
    save_json('metadata.json', meta)
    with (DATA / 'districts.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['district_id', 'district_name_en', 'district_name_hi', 'assembly_count', 'assembly_numbers'])
        for d in districts:
            w.writerow([d['id'], d['name_en'], d['name_hi'], d['assembly_count'], ','.join(map(str,d['assembly_numbers']))])
    with (DATA / 'assemblies.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ac_number', 'name_en', 'reservation', 'primary_district_id', 'district_name_en', 'district_ids', 'cross_district', 'aliases'])
        for a in assemblies:
            w.writerow([a['ac_number'],a['name_en'],a['reservation'],a['primary_district_id'],a['district_name_en'],','.join(a['district_ids']),str(a['cross_district']).lower(),','.join(a['aliases'])])
    print('Generated: 75 districts, 403 constituencies, 84 SC, 2 ST')

if __name__ == '__main__':
    main()
