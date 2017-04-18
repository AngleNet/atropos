#!/usr/bin/env bash
if [ ! -d ./atropos ]; then
	git clone git://github.com/anglenet/atropos
else
	cd atropos && git pull && cd -
fi
spider=spider
extract_loc=extractor
if [ ! -d ./$spider ]; then
	mkdir $spider
else
	rm -rf $spider/*
fi
cp -rf atropos/* $spider/;
if [ ! -d $extract_loc ];then
	echo "Directory $extract_loc does not exist"
	exit 0
fi
cp $extract_loc/result/user_links.original.no_pid $spider/data
cp sub/15.sub $spider/data/.sub
cd $spider/Runner && python spideOriginalUsers.py
