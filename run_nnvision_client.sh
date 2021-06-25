docker run      -it --gpus=all --name nnvision --net=host \
                -e NVIDIA_VISIBLE_DEVICES=all \
                -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,video  \
                -v nn_settings_client:/NNvision/python_client/settings \
                -v /usr/src/jetson_multimedia_api:/usr/src/jetson_multimedia_api \
                -v nn_camera:/NNvision/python_client/camera \
                -v nn_ssh:/root/.ssh/id_rsa \
                -v /proc/device-tree/chosen:/NNvision/uuid \
                --rm roboticia/nnvision_jetson_nano:0.1 bash
