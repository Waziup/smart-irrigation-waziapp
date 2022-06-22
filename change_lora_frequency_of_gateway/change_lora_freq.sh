#!/bin/sh

# copy config files to wazigate to change lora frequencies:
# usage: copy contents of folder to your gateway and run the code
# use following arguments: EU433 or EU868 	e.g. $sudo bash change_lora_freq.sh EU433


echo "copy $1/global_conf.json to /var/lib/wazigate/apps/waziup.wazigate-lora/forwarders/single_chan_pkt_fwd/"
cp single_chan_pkt_fwd/$1/global_conf.json /var/lib/wazigate/apps/waziup.wazigate-lora/forwarders/single_chan_pkt_fwd/

echo "copy $1/chirpstack-network-server.toml /var/lib/wazigate/apps/waziup.wazigate-lora/chirpstack-network-server/"
docker cp chirpstack_conf/$1/chirpstack-network-server.toml /var/lib/wazigate/apps/waziup.wazigate-lora/chirpstack-network-server/

echo "copy $1/chirpstack-gateway-bridge.toml /var/lib/wazigate/apps/waziup.wazigate-lora/chirpstack-application-server/"
docker cp chirpstack_conf/$1/chirpstack-gateway-bridge.toml /var/lib/wazigate/apps/waziup.wazigate-lora/chirpstack-application-server/