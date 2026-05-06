# rtsm-ingest: ROS 2 subscriber bridging Albert's D435i into rtsm-dev.
# Skeleton stage — only proves the container can see Albert's DDS traffic.
FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    ros-humble-compressed-image-transport \
    ros-humble-compressed-depth-image-transport \
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    numpy \
    requests

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV ROS_DOMAIN_ID=30
ENV ROS_LOCALHOST_ONLY=0

WORKDIR /workspace/rtsm-ingest

# Sanity-check CMD: source ROS, list topics, stay alive so we can docker exec in.
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && echo '=== rtsm-ingest skeleton up ===' && ros2 topic list && echo '=== sleeping ===' && sleep infinity"]
