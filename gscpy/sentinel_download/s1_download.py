import os
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import

class s1_download:
    def __init__(self, region, beginposition, endposition, orbitnumber, polarisationmode,
                 producttype, sensoroperationalmode, swathidentifier):
        self.platformname = 'Sentinel-1'
        self.beginposition = beginposition
        self.endposition = endposition

        if orbitnumber is None:
            self.orbitnumber = ''
        else:
            self.orbitnumber = orbitnumber

        if polarisationmode is None:
            self.polarisationmode = ''
        else:
            self.polarisationmode = polarisationmode

        self.producttype = producttype
        self. region = region

        if sensoroperationalmode is None:
            self.sensoroperationalmode = ''
        else:
            self.sensoroperationalmode = sensoroperationalmode

        if swathidentifier is None:
            self.swathidentifier = ''
        else:
            self.swathidentifier = swathidentifier


        # connect to the API
        user = 'yaqxswcdevfrbgt'
        password = '12345678'
        api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')


        # search by polygon, time, and Hub query keywords
        footprint = geojson_to_wkt(read_geojson(self.region))
        products = api.query(footprint,
                             platformname = 'Sentinel-1',
                             beginposition = self.beginposition,
                             endposition = self.endposition,
                             orbitnumber = self.orbitnumber,
                             polarisationmode = self.orbitnumber,
                             producttype = self.producttype,
                             sensoroperationalmode = self.sensoroperationalmode,
                             swathidentifier = self.swathidentifier
                             )

        # download all results from the search
        api.download_all(products)

