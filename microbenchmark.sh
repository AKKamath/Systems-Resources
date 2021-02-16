#!/bin/bash

# microbenchmark for the KVS library
# some points - data integrity HAS to be enabled in the YCSB workload characteristics

# defining some variables
YCSB_ROOT="/home/shreyas/YCSB"
YCSB_WORKLOADS="$YCSB_ROOT/workloads"
YCSB_BIN="$YCSB_ROOT/bin"
CURRENT_DIR=$(pwd)
ME=$(basename "$0")

# check if the args are not empty
[[ -z "$1" ]] && echo "Correct usage : ./${ME} <Number of records> <Number of operations> <Key size> <Value size>" && exit 1

[[ -z "$2" ]] && echo "Correct usage : ./${ME} <Number of records> <Number of operations> <Key size> <Value size>" && exit 1

[[ -z "$3" ]] && echo "Correct usage : ./${ME} <Number of records> <Number of operations> <Key size> <Value size>" && exit 1

[[ -z "$4" ]] && echo "Correct usage : ./${ME} <Number of records> <Number of operations> <Key size> <Value size>" && exit 1

echo "insertorder =ordered/hashed (Default : ordered)"
read ins_order
if [ -z "$ins_order" ]
then
    ORDER="ordered"
else
    ORDER="$ins_order"
fi

# digits=$(echo $1 | wc -c)
# digits=$((digits-1))
# [[ $digits -gt $3 ]] && echo "Invalid number of records, number of digits must be <= Key size" && exit 1

# cd to the YCSB project folder
cd ${YCSB_ROOT}

#need to modify the workload parameters
sed -i "s/\(recordcount=\)\(.*\)/recordcount=$1/" ${YCSB_WORKLOADS}/kvs_workload
sed -i "s/\(operationcount=\)\(.*\)/operationcount=$2/" ${YCSB_WORKLOADS}/kvs_workload
sed -i "s/\(fieldlength=\)\(.*\)/fieldlength=$4/" ${YCSB_WORKLOADS}/kvs_workload
sed -i "s/\(insertorder=\)\(.*\)/insertorder=${ORDER}/" ${YCSB_WORKLOADS}/kvs_workload

# running the workload
[[ -f "${YCSB_ROOT}/load_kvs.txt" ]] && rm ${YCSB_ROOT}/load_kvs.txt

$(${YCSB_BIN}/ycsb load kvs -P ${YCSB_WORKLOADS}/kvs_workload >/dev/null)

[[ -f "${YCSB_ROOT}/load_kvs.txt" ]] && cp ${YCSB_ROOT}/load_kvs.txt ${CURRENT_DIR}/load_trace.txt && rm ${YCSB_ROOT}/load_kvs.txt

$(${YCSB_BIN}/ycsb run kvs -P ${YCSB_WORKLOADS}/kvs_workload >/dev/null)

[[ -f "${YCSB_ROOT}/load_kvs.txt" ]] && cp ${YCSB_ROOT}/load_kvs.txt ${CURRENT_DIR}/run_trace.txt

cd ${CURRENT_DIR}

[[ -f load_trace.txt ]] && [[ -f run_trace.txt ]] && cat load_trace.txt run_trace.txt | ./trace $3 $4 >/dev/null 2>/dev/null

# now that we have generated our trace, we can call our traceprogram
LOAD_REQUESTS=$(cat "load_trace.txt" | wc -l)
RUN_REQUESTS=$(cat "run_trace.txt" | wc -l)

python kvs_tracer.py $LOAD_REQUESTS $RUN_REQUESTS
