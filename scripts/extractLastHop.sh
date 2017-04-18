#!/usr/bin/env bash
if [ ! -d ./atropos ]; then
	git clone git://github.com/anglenet/atropos
else
	cd atropos && git pull && cd -
fi
extract_loc=extractor
spider=spider
if [ ! -d ./$extract_loc ]; then
	mkdir $extract_loc
else
	rm -rf $extract_loc/*
fi
cp -rf atropos/* $extract_loc/;
cd $extract_loc/data
for i in {00..08}; do
	cp $HOME/4.2/user_weibo/$i/data/*.tweet .
	cp $HOME/4.2/user_weibo/$i/data/*.origin_tweet .
	cp $HOME/4.2/users/user_links.new .
done
cd -

if [ -e $spider/result/user_links.original.new ]; then
	cat $spider/result/user_links.original.new >> $extract_loc/data/user_links.new
fi
cd $extract_loc/Runner && python extractLastHopUsers.py $(pwd)/../ && cd -
