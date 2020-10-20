docker run      --gpus=all --name nnvision --net=host \
                -e NVIDIA_VISIBLE_DEVICES=all \
                -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,video  \
                -v nn_settings_client:/NNvision/settings \
                -v nn_camera:/NNvision/camera \
                -v nn_ssh:/root/.ssh/id_rsa \
                --rm roboticia/protecia:1.0 &