Welcom Docker registry huaweimos driver!
===================


This is a [docker-registry backend driver](https://github.com/docker/docker-registry/tree/master/depends/docker-registry-core) for [Huawei cloud services](http://www.hwclouds.com/).

----------



-------------

This driver enable you store you docker images in Huawei Cloud Storage.Go to 

> **Note:**

> - You must  take a Huawei Cloud Storage count and sign up a Object Storage Services.Go to [Huawei cloud services](http://www.hwclouds.com/) to get your access_key first.



----------


Installation
-------------------

####Installation in host


##### Install docker-registry
	git clone https://github.com/docker/docker-registry.git
	python setup.py  install

#####Install  docker-registry-driver-huaweimos
	git clone https://github.com/ldpc/docker-registry-driver-huaweimos.git
	python setup.py install

####Install in registry  container

	docker pull regitry
	docker run -i -t -p 5000:5000  regitry /bin/bash
	git clone https://github.com/ldpc/docker-registry-driver-huaweimos.git
	python setup.py install


----------
Configuration flavors
-------------------
Your must add  flavors in [config_sample.yml](https://github.com/docker/docker-registry/blob/master/config/config_sample.yml)<br /> 
Huawei mos flavor like:

    mos: &mos
        <<: *common 
        storage: mos
        storage_path: _env:STORAGE_PATH:/registry/
        mos_host: _env:MOS_HOST
        mos_bucket: _env:MOS_BUCKET
        mos_accessid: _env:MOS_KEY
        mos_accesskey: _env:MOS_SECRET
        search_backend: _env:SEARCH_BACKEND:sqlalchemy

----------
###Run in hosts
-------------------
####Export  environment variable
	 export SETTINGS_FLAVOR=mos
     export STORAGE_PATH=<your storage_path>
     export MOS_HOST=<your mos server>
     export MOS_BUCKET=<your buker name>
     export MOS_KEY=<your mos AK>
     export MOS_SECRECT=<you mos SK>
####Run docker-registry
docker-registry

----------
###Run in container
-------------------
####You must have commit your changes in org registry images.
	 docker run 
	 -e SETTINGS_FLAVOR=mos  
	 -e STORAGE_PATH=/dockerregistry  
	 -e MOS_BUCKET=docker-registry   
	 -e MOS_HOST=<your mos server address>  
	 -e MOS_KEY=<your access id>  
	 -e MOS_SECRECT=<your access key>  
	 -p 5000:5000 registry

#License
	This is licensed under the Apache license. Most of the code here comes from docker-registry, under an Apache license as well.

[TOC]


