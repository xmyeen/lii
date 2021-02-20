from dataclasses import dataclass

@dataclass
class ImageProf(object):
    image_from: str
    image_maintainer: str
    name: str
    version: str