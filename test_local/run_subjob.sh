#!/bin/bash
/home/sumin/kbsdk-workspace/coverm/test_local/run_docker.sh run --rm -v /home/sumin/kbsdk-workspace/coverm/test_local/subjobs/$1/workdir:/kb/module/work -v /home/sumin/kbsdk-workspace/coverm/test_local/workdir/tmp:/kb/module/work/tmp $4 -e "SDK_CALLBACK_URL=$3" $2 async
