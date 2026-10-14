# Zenith experiment: CoMaps routing without CoMaps' renderer

**Status:** non-production feasibility experiment, October 14, 2026.
**Repository:** https://github.com/comaps/comaps (primary development at Codeberg).
**Repeatable native probe:** https://github.com/ItzCrim/Zenith-Repo/actions/workflows/probe-comaps-routing.yml

## Reason for experiment

Zenith must retain the existing MapLibre true-globe renderer, offline PMTiles,
download interface, place search, and Valhalla fallback while testing whether
CoMaps' mature offline driving router can work as an independent navigation
component. This experiment must not quietly replace or corrupt user data.

## What source inspection establishes

- CoMaps implements offline routing in `libs/routing/`. The `routing`
  CMake target links `indexer`, `routing_common`, `platform`, `geometry`,
  `storage`-related dependencies, but does not directly require the CoMaps
  map/drape renderer target. Source: `libs/routing/CMakeLists.txt`.
- The `IndexRouter` API exposes `CalculateRoute(Checkpoints, ...)` and
  accepts a `DataSource &`. See `libs/routing/index_router.hpp`; it is not a
  PMTiles reader. The route object includes named road segments, turns,
  turn lanes, timing and distance: see `libs/routing/route.hpp`.
- CoMaps provides an independent native CLI `routes_builder_tool` and
  `routing_tests`, including a cross-border graph serialization test.
  See `libs/routing/routes_builder/` and `libs/routing/routing_tests/`.
- Native Android code currently builds through its own large JNI/SDK module,
  `android/sdk/src/main/cpp/CMakeLists.txt`. We cannot copy that JNI whole:
  doing so would drag in the CoMaps framework and display stack. We need a
  smaller original bridge calling only the necessary native routing objects.
- CoMaps reads **.mwm** regional map packages, not Zenith's **.pmtiles**.
  Routing indexes, geometry, connections, types and metadata are serialized
  in MWM. There is NO validated standalone routing-only MWM or direct PMTiles
  decoder. Supporting both file formats consumes extra storage.

## Real initial map-file footprint

The published `data/countries.txt` catalog at version **261004** and map
series **2026.06.28** lists:

| Region | MWM bytes | MiB |
| --- | ---: | ---: |
| US_Arizona_Phoenix | 209,060,569 | 199.38 |
| US_Arizona_Tucson | 92,917,672 | 88.61 |
| US_Arizona_Flagstaff | 102,520,939 | 97.77 |
| All three | 404,499,180 | 385.76 |

These are **complete map archives**, containing more than navigation. Their
total is not comparable to a compressed Valhalla-only routing graph because
the datasets, areas and feature content differ. Do not assume CoMaps reduces
Zenith's storage until we measure equivalent coverage.

Catalog source: https://github.com/comaps/comaps/blob/main/data/countries.txt

## Verified probe 1 (GitHub Actions 38546793403)

The headless C++ build on the standard ubuntu-latest Actions runner
**succeeded** for both `routing_tests` and `routes_builder_tool`.
The native compile step took 4 minutes 12.73 seconds with a measured
peak *build-command* RSS of 2,620,236 KiB (~2.5 GiB), and 105
Ninja build steps. The DEBUG executables are 241,927,224 and
143,589,320 bytes respectively. These are unstripped *debug* binaries,
not estimates of an Android .so or a production APK.

The original unit test invocation failed immediately when it could not
find `data/types.txt`: the probe deliberately skipped rendering
resource generation, not realizing it also produces **routing-required**
classifier resources. This is an experiment configuration failure,
not a native routing compile error. The revised probe enables that
resource generation and attempts the selected unit tests plus a
checksum-verified Phoenix regional .mwm route.

**Important qualification:** Although the build sets
`SKIP_QT_GUI=ON`, it still compiles the upstream static `drape`
library as a transitive dependency of the combined test targets.
We have NOT proven a minimal JNI library can exclude all renderer code.

Logs: https://github.com/ItzCrim/Zenith-Repo/actions/runs/38546793403

## Verified probe 2: Phoenix offline driving (GitHub Actions 38547988899)

**Passed all required steps.** With generated `types.txt` and
`classificator.txt`, targeted `CrossBorderGraph_SerDes` and
`RestrictionTest_CrossGraph_NoUTurn` native tests passed.

The CLI fetched and SHA-1-verified the **US_Arizona_Phoenix.mwm**
(209,060,569 bytes) under catalog version 261004. It calculated the
following **completely offline** car route using ONE native worker:

- From **Phoenix downtown (33.4484, -112.0740)** to
  **Tempe (33.4255, -111.9400)**.
- RouterResultCode=0 (NoError), route **16,347.48 metres**,
  estimated travel **1,195.81 seconds**, and **439 geometry points**.
- Route calculation **2.6773 s** (total CLI wall time **2.81 s**).
- CLI **peak RSS 137,680 KiB (~134.45 MiB)**, no swap.
- This test did not load `World.mwm` or `WorldCoasts.mwm`; the
  CLI logged that they were absent but still returned NoError.

This verifies **real local offline navigation**, not JNI embedding,
live phone navigation, spoken directions, or interstate routes. The
upstream CLI dumps route geometry/distance/time; Zenith would need a
thin custom JNI adapter to access turn/lane data available from
`routing::Route`.

Successful run:
https://github.com/ItzCrim/Zenith-Repo/actions/runs/38547988899

A separate run attempts **Phoenix → Tucson across two MWMs** to
evaluate actual inter-region continuity; this will need a different
dataset and should not be conflated with the passing single-region route.

## Trial sequence and no-go criteria

1. **Independent native compile:** clone a pinned CoMaps source revision and
   build `routing_tests` + `routes_builder_tool` on an ordinary GitHub runner,
   with `SKIP_QT_GUI=ON`. Record exact revision, compilation success/failure,
   route test results, tool sizes and any shared dependencies.
2. **Real Phoenix offline route:** download or generate a compatible
   `US_Arizona_Phoenix.mwm` for **trial execution only**. Run the upstream CLI
   using the matching `countries.txt` and resource directory, for example
   Phoenix downtown (33.4484,-112.0740) to Tempe (33.4255,-111.9400). Measure
   success, route distance, time estimate, runtime and RSS. Do not redistribute
   unapproved third-party binary maps as Zenith Releases.
3. **Android headless JNI adapter:** use CoMaps routing, indexer and data
   source objects; expose start/end/via points to Zenith and convert route
   segments into `RoadRoute` (polyline, ETA, street names, turn types,
   lane guidance and optional speed limits). No UI or Drape renderer.
4. **Multi-region routing:** load adjacent regional MWMs and check interstate
   continuity. A single-region result is not sufficient to approve the engine.
5. **Phone and storage comparison:** benchmark an equivalent Arizona area
   against the already-compressed Valhalla solution. Count downloaded MWMs
   **and** existing PMTiles, native .so size, working set, turn quality, road
   restrictions and driving reroute times. Test airplane mode, long routes,
   and missing adjacent regions. Do not enable live driving guidance before
   instructions have been verified in a parked/simulation test.

**No-go:** requires replacing MapLibre globe; route file duplicates exceed
the acceptable storage budget; JNI needs all rendering/UI layers; licensing
prevents redistribution; or turn/road access cannot be validated.

## License precautions

CoMaps engine sources are Apache 2.0; check attribution and transitive native
dependencies before copying/building into Zenith. Official Organic Maps MWM
binaries are under a **separate data license**, not necessarily the same
terms as CoMaps sources or independently generated OSM map files. This probe
only compiles third-party source in a CI runner, publishes textual logs, and
does not redistribute MWMs or third-party binaries.

CoMaps source: https://github.com/comaps/comaps/blob/main/LICENSE
Organic Maps map data license: https://github.com/organicmaps/organicmaps/blob/master/DATA_LICENSE.txt
OpenStreetMap: https://www.openstreetmap.org/copyright

## Existing Zenith stability

The actual Android Zenith branch stays at its last tested build during this
probe. Its MapLibre, PMTiles, Valhalla v2/v3 routing and BRouter disabled-by-default
test are not modified. The results of the native probe determine whether
the Android JNI work is worth implementing.
