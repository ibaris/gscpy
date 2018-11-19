#!/usr/bin/env python#%module#% description: Download Sentinel 1 Data#% keyword: download#%end#%option G_OPT_F_INPUT#% key: timestart#% description: Starting time of observation period (YYYY-MM-DD).#%end#%option G_OPT_F_INPUT#% key: timend#% description: End time of observation period (YYYY-MM-DD).#%end#%option G_OPT_F_INPUT#% key: username#% description: Username for Copernicus Open Acces Hub.#%end#%option G_OPT_F_INPUT#% key: password#% description:  Password for Copernicus Open Acces Hub.#%end#%option G_OPT_F_INPUT#% key: orbitnumber#% required: no#% description: Choose the orbitnumber.#%end#%option#% key: polarisationmode#% required: no#% options: HH, VV, HV, VH, HH HV, VV VH, HH VV HV VH HH HV VV VH#% answer: HH VV HV VH HH HV VV VH#% description: Choose the polarisationmode.#%end#%option#% key: producttype#% options: SLC, GRD, OCN#% answer: SLC#% description: Choose the producttype.#%end#%option#% options: SM, IW, EW, WV#% answer: SM#% key: sensoroperationalmode#% required: no#% description: Choose the sensoroperationalmode.#%end#%option#% key: swathidentifier#% options: S1, S2, S3, S4, S5, S6, IW, IW1, IW2, IW3, EW, EW1, EW2, EW3, EW4, EW5#% answer: S1#% required: no#% description: Choose the swathidentifier.#%end#%option G_OPT_F_INPUT#% key: region#% type: string#% description: Choose geojson file to define the observation area.import sysimport osimport grass.script as gscriptfrom sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wktfrom datetime import datedef main():    options, flags = gscript.parser()    timestart = options['timestart']    timeend = options['timend']    orbitnumber = options['orbitnumber']    polarisationmode = options['polarisationmode']    producttype = options['producttype']    sensoroperationalmode = options['sensoroperationalmode']    swathidentifier = options['swathidentifier']    username = options['username']    password = options['password']    region = os.path.normpath(options['region'])    region = region.split("\\")    regs = ""    for i in region:        regs = regs + i + "\\" + "\\"    regs = regs[:-2]    region = regs    timestart_split = timestart.split('-')    timestart = ''    for item in timestart_split:        timestart += item    timeend_split = timestart.split('-')    timeend = ''    for item in timeend_split:        timeend += item    date = (timestart, timeend)    if orbitnumber is '':        orbitnumber = None    if polarisationmode is '':        polarisationmode = None    if producttype is '':        producttype = None    if sensoroperationalmode is '':        sensoroperationalmode = None    if swathidentifier is '':        swathidentifier = None    # print(timestart)    # # connect to the API    username = 'yaqxswcdevfrbgt'    password = '12345678'    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')    #    # print(date)    # # search by polygon, time, and Hub query keywords    footprint = geojson_to_wkt(read_geojson(region))    products = api.query(footprint,                         date=date,                         platformname='Sentinel-1'                         #orbitnumber=orbitnumber,                         #polarisationmode=polarisationmode,                         #producttype=producttype,                         #sensoroperationalmode=sensoroperationalmode,                         #swathidentifier=swathidentifier                         )    api.download_all(products)# # download all results from the search    # api.download_all(products)    return 0if __name__ == "__main__":    sys.exit(main())