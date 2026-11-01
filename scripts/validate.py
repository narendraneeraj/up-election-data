#!/usr/bin/env python3
"""Independent validation of GitHub-published UP election JSON datasets."""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / 'data'
def load(f): return json.loads((BASE / f).read_text(encoding='utf-8'))

def validate():
    ds, acs, grouped, meta = (load(n) for n in ['districts.json', 'assemblies.json', 'district_assemblies.json', 'metadata.json'])
    assert len(ds) == 75, f'Expected 75 districts, found {len(ds)}'
    assert len(acs) == 403, f'Expected 403 constituencies, found {len(acs)}'
    assert len(grouped) == 75
    assert [s['ac_number'] for s in acs] == list(range(1,404)), 'Assembly number sequence must be exactly 1..403'
    assert len(set(d['id'] for d in ds)) == 75
    assert len(set(d['name_en'] for d in ds)) == 75
    assert Counter(s['reservation'] for s in acs) == {'GEN':317, 'SC':84, 'ST':2}
    assert sum(d['assembly_count'] for d in ds) == 403
    district_by_id = {d['id']: d for d in ds}
    seat_by_id = {a['ac_number']: a for a in acs}
    assert {x['district_id'] for x in grouped} == set(district_by_id)
    seen = set()
    for d in ds:
        nums = d['assembly_numbers']
        assert len(nums) == d['assembly_count'] == len(set(nums)), d['name_en']
        for num in nums:
            assert num in seat_by_id
            assert seat_by_id[num]['primary_district_id'] == d['id']
            assert seat_by_id[num]['district_name_en'] == d['name_en']
            assert num not in seen, f'Multiple primary district assignments for {num}'
            seen.add(num)
        matching = next(x for x in grouped if x['district_id'] == d['id'])
        assert matching['assembly_numbers'] == nums
    assert seen == set(range(1,404))
    for a in acs:
        assert a['primary_district_id'] in a['district_ids']
        assert all(di in district_by_id for di in a['district_ids'])
        assert len(set(a['district_ids'])) == len(a['district_ids'])
        assert a['cross_district'] == (len(a['district_ids']) > 1)
        assert a['slug'] and a['name_en']
    assert sorted(a['ac_number'] for a in acs if a['cross_district']) == [30,58,184,271]
    assert (acs[401]['name_en'],acs[401]['reservation']) == ('Obra','ST')
    assert (acs[402]['name_en'],acs[402]['reservation']) == ('Duddhi','ST')
    assert meta['district_count'] == 75 and meta['assembly_count'] == 403
    print('PASS: 75 districts, 403 unique Assembly seats, 84 SC, 2 ST, 317 GEN')
    print('PASS: 403 district memberships, 4 cross-district seats recorded')

if __name__ == '__main__': validate()
