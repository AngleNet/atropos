#!/usr/bin/env bash
#!/usr/bin/env bash
set -x

for i in {00..02}; do
    mkdir -p $i
    cp -r atropos/* $i;
    cp $i.sub $i/data/.sub;
    cp {input}$i $i/data/{input};
    cd $i/Runner;
    screen python {runner.py} $(pwd)/../data/
    cd -
done
