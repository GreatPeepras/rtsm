#!/bin/bash
docker run -d \
  --network host \
  --ipc=host \
  -e ROS_DOMAIN_ID=30 \
  -e ROS_LOCALHOST_ONLY=0 \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -e CYCLONEDDS_URI=file:///cyclonedds.xml \
  -v /home/peep/cyclonedds.xml:/cyclonedds.xml:ro \
  -v /home/peep/rtsm-ingest:/workspace/rtsm-ingest \
  --name rtsm-ingest \
  rtsm-ingest:skeleton
