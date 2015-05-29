#!/bin/tcsh
set sourced=($_)
if ("$sourced" != "") then
    echo "sourced $sourced[2]"
    set rootdir = `dirname $sourced[2]`       # may be relative path
    echo $rootdir
    set bindir = `cd $rootdir/../bin && pwd`    # ensure absolute path
    echo $bindir 
    set path = ($path $bindir)
endif

