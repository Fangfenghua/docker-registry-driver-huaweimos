# -*- coding: utf-8 -*-
"""
docker_registry.drivers.mos
~~~~~~~~~~~~~~~~~~~~~~~~~~
mos is Open Storage Service provided by huawei.com
http://www.hwclouds.com/
"""



from docker_registry.core import dirver
from docker_registry.core import exceptions
from docker_registry.core import lru

class Storage(dirver.Base):
    def __init__(self):
        pass

    def get_content(self, path):
        pass

    def put_content(self, path, content):
        """Method to put content."""
        pass

    def stream_read(self, path, bytes_range=None):
        """Method to stream read."""
        pass
    
    def stream_write(self, path, fp):
        """Method to stream write."""
        pass

    def list_directory(self, path=None):
        """Method to list directory."""
        pass

    def exists(self, path):
        """Method to test exists."""
        pass

    def remove(self, path):
        """Method to remove."""
       pass

    def get_size(self, path):
        """Method to get the size."""
        pass
