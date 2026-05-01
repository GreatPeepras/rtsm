sudo docker run -it --rm \
  --runtime nvidia \
  --network host \
  -v /home/peep/rtsm:/workspace/rtsm \
  -v /mnt/rtsm-data:/mnt/rtsm-data \
  -w /workspace/rtsm \
  --name rtsm-dev \
  dustynv/pytorch:2.7-r36.4.0-cu128-24.04 \
  bash
