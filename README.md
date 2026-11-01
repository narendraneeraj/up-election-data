# Uttar Pradesh Election App — GitHub data (Phase 1)

Independent public-information database for a proposed Uttar Pradesh Vidhan Sabha Android app. **No personal voter lists, voter names, EPIC numbers or phone numbers are included.**

## Current contents

| Path | What it contains |
|---|---|
| `data/districts.json` | **75 districts**, stable district IDs, English/Hindi district names, primary-seat counts and seat number arrays |
| `data/assemblies.json` | **403 seats**, numbered 1–403, reservation (GEN/SC/ST), district ID, aliases, cross-district flags |
| `data/district_assemblies.json` | District-to-Assembly primary grouping (each seat counted once) |
| `data/metadata.json` | Version, source links, release date, voter-service URLs |
| `data/districts.csv` | Spreadsheet-friendly district list |
| `data/assemblies.csv` | Spreadsheet-friendly constituency list |
| `scripts/validate.py` | Data validation (also runs in GitHub Actions) |
| `seat_seed.txt` / `build_data.py` | Editable source input and reproducible JSON/CSV generation |

## Publish on GitHub

1. Create a **public** repository named `up-election-data` in your own GitHub account.
2. Upload the contents of this package to the repository root, preserving the folders.
3. Check the **Actions** tab: the `Validate UP election data` workflow should pass.
4. Use these links in your Android app, replacing `YOUR_GITHUB_USERNAME`:

```
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/up-election-data/main/data/metadata.json
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/up-election-data/main/data/districts.json
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/up-election-data/main/data/assemblies.json
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/up-election-data/main/data/district_assemblies.json
```

GitHub Raw is adequate for a small read-only dataset and early app traffic. It is not a guaranteed high-volume production API. For a larger audience, consider versioned GitHub Releases distributed through a CDN (observe cache freshness), or a managed static host. **Bundle the latest verified dataset with your Android APK for offline fallback**; update from GitHub when connected.

## Example record

`data/assemblies.json`:

```json
{
  "ac_number": 61,
  "name_en": "Noida",
  "reservation": "GEN",
  "primary_district_id": "up-d029",
  "district_ids": ["up-d029"],
  "district_name_en": "Gautam Buddha Nagar",
  "aliases": [],
  "slug": "noida",
  "state_code": "UP",
  "cross_district": false
}
```

The `primary_district_id` is the stable district key used to join files. English and Hindi names are included for districts; constituency names are English in this initial release.

## District mapping notes

- `assembly_count` counts constituencies against their **primary** district only. The 75 counts total 403.
- Four Assembly constituencies have recorded parts in two districts: **30 Bilari** (Moradabad/Sambhal), **58 Dhaulana** (Hapur/Ghaziabad), **184 Jagdishpur** (Amethi/Sultanpur), and **271 Rudauli** (Ayodhya/Barabanki). They have multiple entries in `district_ids` while keeping only one `primary_district_id`.
- Example: Noida is AC **61**, Dadri is **62**, Jewar is **63**.
- Search with both `name_en` and `aliases`. Names differ between older ECI sources and modern administrative naming (e.g. Allahabad/Prayagraj).
- Reservation counts are based on the ECI's **2022** election notification: **317 GEN, 84 SC, 2 ST**. Unlike some secondary lists, **Duddhi (403)** is **ST**, as is **Obra (402)**.

## Updating data

Edit the `seat_seed.txt` only when a verified constituency number, spelling or reservation designation changes, then run:

```
python build_data.py
python scripts/validate.py
```

If you update the primary district or order of district identifiers, **preserve the existing district `id` values** and explicitly migrate app data and bookmarks. IDs are a data contract; do not silently renumber them.

Increment the version in `data/metadata.json` on every published data change. For future MLA and election-result datasets, create separate files and use `ac_number` as the joining key; do not mix current MLAs with historical winners.

## Attribution and limitations

- [Election Commission of India — 2022 election press note](https://static.pib.gov.in/writereaddata/userfiles/PN_3.pdf): official constituency numbers, names and reservation classifications.
- [Government of India directory — UP districts](https://igod.gov.in/index.php/sg/UP/E042/organizations): 75 district reference.
- [UP Legislative Assembly constituency table](https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Uttar_Pradesh_Legislative_Assembly): secondary constituency-to-district mapping reference.
- [Electoral-roll 2023 research index](https://github.com/in-rolls/electoral_rolls_up_2023): evidence of district-spanning constituency parts; not a source for publishing voters' personal data.

This is an **independent public-information dataset**, not endorsed by or affiliated with the Election Commission of India or the Uttar Pradesh government. Future changes to districts, delimitation, names, or reservations must be checked against authoritative current notices. This package does **not** contain constituency boundary geometry, district boundary GeoJSON, sitting-MLA rosters, electoral roll PDFs, or election results; those are separate later phases.
