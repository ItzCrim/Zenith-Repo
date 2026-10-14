#!/usr/bin/env python3
"""Shard one connected Valhalla graph into complementary ZIP packages."""
import argparse, gzip, hashlib, json, pathlib, re, shutil, tempfile, zipfile

def main():
    p=argparse.ArgumentParser()
    for name in ("tiles","output","name","region","parts","graph-set"):
        p.add_argument("--"+name,required=True)
    p.add_argument("--auto-max-raw-bytes",type=int,default=0,
                   help="Balance bins by raw tile size to keep each Release asset small")
    p.add_argument("--tile-encoding",choices=("raw","gzip"),default="raw",
                   help="Raw v2 .gph or experimental v3 .gph.gz retained on device")
    p.add_argument("--gzip-level",type=int,choices=range(1,10),default=6)
    a=p.parse_args()
    tiles=pathlib.Path(a.tiles)
    output=pathlib.Path(a.output)
    parts=int(a.parts)
    assert 1<=parts<=128
    assert re.fullmatch(r"[a-z0-9_-]{4,120}",a.graph_set)
    assert re.fullmatch(r"[a-z0-9_-]{3,80}",a.name)
    files=sorted(tiles.rglob("*.gph"))
    assert files,"No .gph graph tiles found"
    validated=[]
    for file in files:
        relative=file.relative_to(tiles).as_posix()
        assert re.fullmatch(r"[0-9]+(?:/[0-9]+)+\.gph",relative),relative
        validated.append((file,relative,file.stat().st_size))
    if a.auto_max_raw_bytes:
        assert 500_000_000<=a.auto_max_raw_bytes<=1_800_000_000
        total=sum(x[2] for x in validated)
        parts=max(parts,(total+a.auto_max_raw_bytes-1)//a.auto_max_raw_bytes)
        assert parts<=128,"Full graph requires more than 128 route ZIPs; adjust the build"
        assert len(validated)>=parts,"Not enough graph tiles for requested shard count"
        buckets=[[] for _ in range(parts)]
        weights=[0]*parts
        # Deterministic byte-balanced bin packing. Upper limit is on raw bytes,
        # so the ZIPs should fit below GitHub's 2-GiB asset limit even on
        # poorly compressible graphs.
        for file,relative,size in sorted(validated,key=lambda x:(-x[2],x[1])):
            index=min(range(parts),key=lambda i:weights[i])
            buckets[index].append((file,relative))
            weights[index]+=size
        assert max(weights)<1_900_000_000,"Routing shard too large even before compression"
    else:
        buckets=[[] for _ in range(parts)]
        for file,relative,_ in validated:
            shard=int.from_bytes(hashlib.sha256(relative.encode()).digest()[:8],"big")%parts
            buckets[shard].append((file,relative))
    assert all(buckets),"More output parts than graph tiles"
    (output/"parts.txt").parent.mkdir(parents=True,exist_ok=True)
    (output/"parts.txt").write_text(str(parts)+"\n")
    output.mkdir(parents=True,exist_ok=True)
    raw_total=0
    stored_total=0
    with tempfile.TemporaryDirectory(prefix="zenith-tile-gzip-") as work:
      scratch=pathlib.Path(work)
      for index,items in enumerate(buckets,1):
        filename=f"{a.name}-part-{index}.crimroute"
        dest=output/filename
        manifest={
          "format":("crims-valhalla-tiles-v3" if a.tile_encoding=="gzip"
                    else "crims-valhalla-tiles-v2"),
          "tile_encoding":a.tile_encoding,
          "graph_set":a.graph_set,
          "part":f"part-{index}",
          "parts":parts,
          "region":a.region,
          "tile_count":len(items),
          "source":"Connected graph from one Valhalla build",
          "license":"OpenStreetMap ODbL 1.0"}
        method=zipfile.ZIP_STORED if a.tile_encoding=="gzip" else zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(dest,"w",method,compresslevel=(None if method==zipfile.ZIP_STORED else 6),
                             allowZip64=True) as f:
            f.writestr("manifest.json",json.dumps(manifest).encode(),compress_type=zipfile.ZIP_DEFLATED)
            for file,relative in items:
                raw_total+=file.stat().st_size
                if a.tile_encoding=="gzip":
                    compressed=scratch/"tile.gph.gz"
                    # One tile at a time: avoid a complete second graph copy
                    # on the build runner, and keep gzip metadata reproducible.
                    with compressed.open("wb") as target:
                        with gzip.GzipFile(filename="",fileobj=target,mode="wb",
                                           compresslevel=a.gzip_level,mtime=0) as out:
                            with file.open("rb") as inp:
                                shutil.copyfileobj(inp,out,1024*1024)
                    stored_total+=compressed.stat().st_size
                    f.write(compressed,"tiles/"+relative+".gz",compress_type=zipfile.ZIP_STORED)
                    compressed.unlink()
                else:
                    stored_total+=file.stat().st_size
                    f.write(file,"tiles/"+relative)
        assert dest.stat().st_size<2*1024**3,"Exceeds GitHub Release 2 GiB"
        with zipfile.ZipFile(dest) as f:assert f.testzip() is None
        sha=hashlib.sha256()
        with dest.open("rb") as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b""):sha.update(chunk)
        (output/(filename+".sha256")).write_text(sha.hexdigest()+"  "+filename+"\n")
        print(filename,len(items),dest.stat().st_size,"bytes")
    (output/"tile-size-report.json").write_text(json.dumps({
        "format":("v3-gzip" if a.tile_encoding=="gzip" else "v2-raw"),
        "raw_tile_bytes":raw_total,
        "installed_tile_bytes":stored_total,
        "savings_percent":round(100*(raw_total-stored_total)/raw_total,2),
        "parts":parts,
    },indent=2)+"\n")

if __name__=="__main__":
    main()
