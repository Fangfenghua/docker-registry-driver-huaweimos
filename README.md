config
=========
mos: &mos
    <<: *common
    storage: mos
    storage_path: _env:STORAGE_PATH:/registry/
    mos_host: _env:MOS_HOST
    mos_bucket: _env:MOS_BUCKET
    mos_accessid: _env:MOS_KEY
    mos_accesskey: _env:MOS_SECRET
    
options
=========
if you run in host:
export SETTINGS_FLAVOR=mos
export STORAGE_PATH=<your storage_path>
export MOS_HOST=<your mos server>
export MOS_BUCKET=<your buker name>
export MOS_KEY=<your mos AK>
export MOS_SECRECT=<you mos SK>

if you run in container:
    * if you run docker-registry on your docker container, remmeber to specify these settings as cmd args:
        docker run \
         -e SETTINGS_FLAVOR=mos \
         -e STORAGE_PATH=/dockerregistry/ \
         -e MOS_BUCKET=docker-registry \
         -e MOS_HOST=<your mos server address>
         -e MOS_KEY=<your access id> \
         -e MOS_SECRECT=<your access key> \
         -p 5000:5000 \
         registry
    
License
=========
This is licensed under the Apache license. Most of the code here comes from docker-registry, under an Apache license as well.
    
