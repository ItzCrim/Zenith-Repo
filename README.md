# Zenith offline map packages

This **public** repository hosts downloadable OpenMapTiles-compatible `.pmtiles` vector basemaps for the [Zenith Android app](https://github.com/ItzCrim/Crim-s-Maps/tree/Zenith).

## Build and publish a region

1. Open **Actions → Build and publish Zenith offline map → Run workflow**.
2. Select the region's Geofabrik path, e.g. `europe/monaco` for a test or `north-america/us/arizona`.
3. Choose a maximum tile zoom, preferably `13` for your first state test.
4. When the build finishes, it publishes the **raw `.pmtiles` file and a SHA-256 checksum** directly to [GitHub Releases](https://github.com/ItzCrim/Zenith-Repo/releases). You do **not** need to extract a GitHub Actions artifact ZIP.

The same region + zoom updates its matching release assets if you rebuild it. No manual uploads, tokens, or GitHub Actions artifact downloads are required. Your `.pmtiles` file is publicly downloadable without a GitHub sign-in.

**In Zenith:** Settings → Offline Maps → Browse Published Maps → choose a region → Download. On older versions of Zenith, you can use the Release's direct `.pmtiles` asset URL in the HTTPS download field, or download the file and import it manually.

## Limits and notes

- Release assets currently have a GitHub **2 GiB per-file** limit. Large states may exceed that limit or the GitHub Actions runner's memory/disk/time limits.
- GitHub Actions artifacts are transient ZIP bundles. **Release assets are the permanent public delivery method**. Files are not stored in Git commits.
- Each published map contains **visual vector map tiles only**. Offline turn-by-turn routing requires a separate `.crimroute` Valhalla pack.
- Zenith currently stores **one active offline basemap** at a time. Full in-app map pack catalog and automatic ZIP import require a compatible Zenith APK.
- Source data is OpenStreetMap via [Geofabrik](https://download.geofabrik.de/). OpenStreetMap data is made available under ODbL; copyright © OpenStreetMap contributors. Follow source licensing requirements for reuse and attribution.
- To avoid provider abuse, packages are generated from regional source extracts, **not scraped from OpenFreeMap's public tile servers**.
- The workflow must be manually started by an authorized repository collaborator. Publishing uses this repository's own `GITHUB_TOKEN` with `contents: write` permissions; no private-repository credentials are required.


## Automate all 50 U.S. states

You do **not** need to launch each state manually. Use [Actions → Build All US State Offline Maps](https://github.com/ItzCrim/Zenith-Repo/actions/workflows/build-all-states.yml) and choose **Run workflow**.

- **Test mode (default):** `test_delaware` runs just Delaware, to confirm the bulk pipeline is healthy.
- **All 50 states:** `all_50_states` queues every state using validated Geofabrik region paths, including all 50 states and excluding DC/territories.
- **Zoom:** Defaults to 14, matching previously published Arizona/Nevada/Washington packages; lower zoom uses less storage, but generates a separate release.
- **Concurrency:** Two regions build at a time. Other regions wait for a runner. Each region checks for an already-published `.pmtiles` and checksum before doing expensive work, and skips those if both are present.
- **Fault isolation:** One state failing does **not** cancel the remaining state builds. You can use **Re-run failed jobs** from the batch workflow or run a specific region manually afterward.
- **Build-minute and size caution:** Building all 50 can consume substantial Actions time, storage, and network bandwidth. A few high-volume states may exceed available runner disk/memory, timeouts, or the 2 GiB per Release asset limit. Failures are reported rather than silently treated as published maps.
- **Do not start two full batches concurrently.** Let outstanding manually started states finish first to minimize repeated build minutes.
- **Publication:** Successful regions publish raw `.pmtiles` Release assets and checksums, and automatically appear in Zenith 0.2.1's public map catalog.

The bulk workflow runs **only when manually dispatched**; adding it does not start 50 map builds or change the Android application.


## Build the rest of North America (fixed zoom 14)

Open [Build Remaining North America](https://github.com/ItzCrim/Zenith-Repo/actions/workflows/build-north-america.yml) → **Run workflow**.
- `test_belize` (default): one-region test.
- `all_north_america`: **33 targets**: eleven Canadian provinces/territories (excluding BC and Nunavut); two geographic BC parts; three official Nunavut subregions (Kitikmeot, Kivalliq and Qikiqtaaluk); Mexico and Greenland; eleven individually named Central America/Caribbean regions; Puerto Rico, US Virgin Islands, and Washington DC; and one optional combined Central America map for otherwise omitted island coverage. The last combined extract overlaps the individual countries.
- Map builds are **max zoom 14 only** (including the single-region and US bulk workflows). Two jobs execute concurrently; already-published releases with both raw PMTiles and SHA-256 files are skipped.
- Failures do not cancel unrelated builds. Output size is checked before publishing; an archive exceeding the **2 GiB** individual GitHub Release asset limit fails clearly.

### British Columbia: North + South

`north-america/canada/british-columbia/north` and `north-america/canada/british-columbia/south` are **virtual Zenith workflow inputs**, not Geofabrik download paths.

- **North** is built from Geofabrik's real `north-admreg-latest.osm.pbf`. Published asset: `british-columbia-north.pmtiles`.
- **South** merges `interior-admreg`, `island-admreg`, `kootenay-admreg`, `okanagan-admreg`, and `southcoast-admreg` using `osmium merge`. Published asset: `british-columbia-south.pmtiles`.

The two geographic packages cover BC's six official Geofabrik subregions. They are not arbitrary byte-splits, and each is a standalone map with its own Release and checksum. They must both be downloaded for full BC coverage. These parts save distribution size per asset, but do not guarantee final output sizes until they have actually been built.

**Zenith Android 0.3.0 limitation:** Multiple maps may be downloaded and stored, but only **one map is displayed at once**. Full seamless viewing of North + South together needs an additional multi-source renderer update; publishing these two packages does *not* automatically enable it.

Source directories: [North America](https://download.geofabrik.de/north-america.html), [Canada](https://download.geofabrik.de/north-america/canada.html), [British Columbia](https://download.geofabrik.de/north-america/canada/british-columbia.html), [Central America](https://download.geofabrik.de/central-america.html).

Nunavut's full PBF approaches the workflow's input size limit; the North America matrix builds its three [official Geofabrik subregions](https://download.geofabrik.de/north-america/canada/nunavut.html) instead of the combined province to reduce package sizes.
