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

## Connected Valhalla routing, not independent state extracts

[Build Connected Valhalla Routes](https://github.com/ItzCrim/Zenith-Repo/actions/workflows/build-connected-routes.yml) builds a **single coherent Valhalla graph** from two or more adjacent Geofabrik PBFs, then publishes it in complementary `.crimroute` ZIP pieces. The default test includes Arizona and Nevada and produces two parts. Both parts are required to activate that graph in Zenith 0.3.3.

This is different from the old `.crimroute` v1 workflow, which compiles each state separately and cannot reliably route across state borders. The new `crims-valhalla-tiles-v2` format includes a `graph_set` identity and required part count; the app stores route ZIPs independently and expands compatible shards into one native Valhalla tile directory. It only activates a set when **all parts** have arrived.

Up to three routing archives are **downloaded simultaneously**, with no arbitrary three-pack storage limit. Building a full-US graph may require a much larger runner than GitHub's standard hosted runners. Do not combine independently built graph shards merely because their paths look compatible.


## One-click US-wide *connected* Valhalla route building

[Build Complete US Connected Valhalla Routing Graph](https://github.com/ItzCrim/Zenith-Repo/actions/workflows/build-us-valhalla.yml) is a **single manual workflow** that downloads Geofabrik's `north-america/us-latest.osm.pbf` (all 50 states), compiles ONE Valhalla routing graph, automatically divides its loose routing tiles into approximately 1.4 GB-or-smaller groups, verifies ZIPs and SHA-256 files, and publishes the complementary `.crimroute` parts to this repository's GitHub Releases.

**Prerequisite: a sufficiently powerful Actions runner.** Standard free GitHub-hosted machines are too small (public Linux runners have about 16 GB RAM and 14 GB storage). The workflow deliberately does not start a doomed full-USA build on them. On a personal GitHub account, register a large cloud/owned Linux x64 Actions runner with labels `self-hosted, linux, x64, zenith-us-routing`, and at least **~128 GB RAM and 350+ GB free SSD** (preferably more). The workflow checks resources before starting. In GitHub Settings → Actions → Runners, use **New self-hosted runner** on a machine you control; do not add GitHub's runner registration token to the repository. Personal-account users should choose `runner_mode=self-hosted`.

The optional `runner_mode=github-large` uses an explicitly configured 32-core GitHub Larger Runner (`ubuntu-24.04-32core`). As of October 2026, that option is available only to eligible GitHub Team/Enterprise organizations with a configured paid larger runner; personal GitHub repositories do not automatically have access. No nationwide build has been run or its success verified yet.

Even with a large runner, US graph computation can exceed the workflow's six-hour job deadline or source/machine limits; this configuration is an informed starting point, **not a guarantee**. A full-USA routing archive needs many gigabytes of phone storage in addition to PMTiles basemaps. Zenith requires **all parts** of a graph set before enabling the connected native Valhalla graph; already-published map data remains unchanged.
