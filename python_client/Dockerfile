FROM nnvision_client_base

WORKDIR /NNvision
COPY . /NNvision

RUN apt-get update
RUN pip3 install WSdiscovery
CMD ["/NNvision/start.sh"]
