#!/bin/bash
version=v1.0.4
pd_data="/tmp/pd"
tikv_data="/tmp/tikv"
tidb_data="/tmp/tidb"

read -p "Input local ip [example: 192.168.1.10]:" local_ip
while [ "${local_ip}" == "" ]
do
	read -p "Input local ip [example: 192.168.1.10]:" local_ip
done

mkdir -p ${pd_data}/data
mkdir -p ${pd_data}/log
mkdir -p ${tikv_data}/data
mkdir -p ${tikv_data}/log
mkdir -p ${tidb_data}/log

docker pull pingcap/pd:$version
docker pull pingcap/tidb:$version
docker pull pingcap/tikv:$version

docker run \
  -p 2379:2379 \
  -p 2380:2380 \
  -v /etc/localtime:/etc/localtime:ro \
  -v "${pd_data}/data:/data" \
  -v "${pd_data}/log:/var/log" \
  --ulimit nofile=1000000:1000000 \
  --name "pd" \
  -d \
  pingcap/pd:${version} \
  --name="pd1" \
  --client-urls=http://0.0.0.0:2379 \
  --advertise-client-urls=http://${local_ip}:2379 \
  --peer-urls=http://0.0.0.0:2380 \
  --advertise-peer-urls=http://${local_ip}:2380 \
  --data-dir=/data \
  --log-file="/var/log/pd.log"

docker run \
  -p 20160:20160 \
  -v /etc/localtime:/etc/localtime:ro \
  -v "${tikv_data}/data:/data" \
  -v "${tikv_data}/log:/var/log" \
  --ulimit nofile=1000000:1000000 \
  --name "tikv" \
  -d \
  pingcap/tikv:${version} \
  --addr="0.0.0.0:20160" \
  --advertise-addr="${local_ip}:20160" \
  --data-dir=/data \
  --log-file="/var/log/tikv.log" \
  --pd="${local_ip}:2379"

docker run \
  -p 4000:4000 \
  -p 10080:10080 \
  -v /etc/localtime:/etc/localtime:ro \
  -v "${tidb_data}/log:/var/log" \
  --ulimit nofile=1000000:1000000 \
  --name "tidb" \
  -d \
  pingcap/tidb:${version} \
  --log-file="/var/log/tidb.log" \
  --path="${local_ip}:2379" \
  --store="tikv"
