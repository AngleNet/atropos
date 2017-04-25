#!/usr/bin/env bash
set -x
input=
runner=
for i in {13..13}; do
    mkdir -p $i
    cp -r atropos/* $i;
    cp $i.sub $i/data/.sub;
    cp $input$i $i/data/$input;
    cd $i/Runner;
    screen python $runner $(pwd)/../data/
    cd -
done

