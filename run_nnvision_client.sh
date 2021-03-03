docker run --name nnvision  --net=host --gpus=all \
           -e NVIDIA_VISIBLE_DEVICES=all \
		   -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,video \
		   -v nn_settings_client:/NNvision/settings \
		   -v nn_cron:/var/spool/cron/crontabs \
		   -v nn_camera:/NNvision/camera --rm jouvencia/nnvision_client:nano_tx1

