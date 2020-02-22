docker run --name nnvision  --net=host -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,video -v nn_settings_client:/NNvision/settings -v nn_camera:/NNvision/camera --runtime=nvidia --rm roboticia/protecia:0.4 &

