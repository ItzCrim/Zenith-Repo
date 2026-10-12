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
