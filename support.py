import hashlib, collections, csv, os, sys, zipfile

from zipfile import ZipFile

# http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj
import pyproj

WGS84 = pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used for geojson
MIDNR = pyproj.Proj("+init=EPSG:3078", preserve_units=True) # datum used by Michigan

MOTOR_VEHICLE_FIELDS = ['ORV','ATV','Motorbike','MCCCT','Snowmobile']

### SUPPORT FUNCTIONS

def unzip_input(file):
    print "* Unzipping" + file
    zfile = zipfile.ZipFile(os.getcwd()+'/input/'+file+'.zip')
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        zfile.extract(name, os.getcwd()+'/input/')
    zfile.close()

def zip_output():
    with ZipFile('./output/MI_DNR_OpenTrails.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
        myzip.write('./output/named_trails.csv')
        myzip.write('./output/stewards.csv')
        myzip.write('./output/trailheads.geojson')
        myzip.write('./output/trail_segments.geojson')

def get_steward_id(steward_name):
    result = None
    if steward_name in STEWARD_MAP:
        result = STEWARD_MAP[steward_name]
    return result

def is_motor_vehicles(atr):
    result = False
    for field in MOTOR_VEHICLE_FIELDS:
        if field.upper() in atr:
            result = (atr[field.upper()] == 'Yes') or result
    yesno = 'yes' if result else 'no'
    return yesno

def build_osm_tags(atr):
    result = ""
    tags = []
    if atr['SURFACE'].strip():
        tags.append('surface=' + atr['SURFACE'])
    if atr['WIDTH'].strip():
        tags.append('width=' + atr['WIDTH'])
    return ";".join(tags)

def transform_geometry(geom):
    if geom['type'] == 'LineString':
        return transform_linestring(geom['coordinates'])
    elif geom['type'] == 'MultiLineString':
        return transform_multilinestring(geom['coordinates'])
    elif geom['type'] == 'Point':
        return transform_coordinates(geom['coordinates'])

def transform_linestring(linestring):
    n_geom = []
    for point in linestring:
        n_geom.append(transform_coordinates(point))
    return n_geom

def transform_multilinestring(multilinestring):
    n_geom = []
    for linestring in multilinestring:
        n_geom.append(transform_linestring(linestring))
    return n_geom

def transform_coordinates(coordinates):
    return pyproj.transform(MIDNR, WGS84, coordinates[0], coordinates[1])
