CID=$(docker create redroid/redroid:13.0.0-latest)
docker export $CID | tar tf - | grep -E "build.prop|/etc/"
docker rm $CID
