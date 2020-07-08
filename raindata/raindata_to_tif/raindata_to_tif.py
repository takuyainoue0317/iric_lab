import yaml
import os
import pathlib
import gzip
import struct
from osgeo import gdal, gdalconst, gdal_array
from osgeo import osr
import numpy as np
import datetime
import pandas as pd

class RasterDataProfile:
    def __init__(self):
        self.name = ''
        self.cols = 0
        self.rows = 0
        self.originx = 0
        self.originy = 0
        self.cellsize = 0
        self.dx = 0.1
        self.dy = -0.1
        self.band = 1
        self.nodata = -9999
        self.EPSG = 4326
        self.dtype = gdal.GDT_Float64

def create_geotif(p, data):
    
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(p.name, p.cols, p.rows, p.band, p.dtype)
    outRaster.SetGeoTransform((p.originx, p.dx, 0, p.originy, 0,p.dy))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(data)
    outband.SetNoDataValue(p.nodata)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(p.EPSG)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

    return 0
#--------------------------------------------------
# About GRIB2 ALAL Rain data
# variable is rainfall rate(mm) in previous an hour
# domain 118E-150E, 20N-48N
# grid resolustion is dx = 0.0125, dy = 0.00833333 in degree
# temporal 1 dataset is distributed every 30 minites.
#--------------------------------------------------
def grib2_to_tif(wgrib_path, fgrib2, out_path):
    import netCDF4
    import subprocess
    ier = 0

    fname = os.path.basename(fgrib2)
    fnetcdf = fgrib2  + '.nc'
    ftif = out_path + '/' + fname + '.tif'

    if os.path.exists(fnetcdf) != True:
        cp = subprocess.run([wgrib_path, fgrib2, '-netcdf', fnetcdf])
        if cp.returncode != 0:
            print('wgrib2.exe failed.', file=sys.stderr)
            sys.exit(1)
    else:
        print(fnetcdf + ' exits already.')

    if os.path.exists(ftif) == True:
        ier = 1
        print(ftif + ' exits already.')
        return ier

    #tif profile
    print("generating..." + ftif)
    tif_profile = RasterDataProfile()
    tif_profile.name = ftif
    tif_profile.cols = 2560
    tif_profile.rows = 3360
    tif_profile.dx = 0.0125
    tif_profile.dy = -0.00833333
    tif_profile.originx = 118.000
    tif_profile.originy = 20.000 - tif_profile.rows * tif_profile.dy
    tif_profile.nodata = -9999

    nc = netCDF4.Dataset(fnetcdf, 'r')
    # print(nc)
    # print(nc.dimensions)
    # print(nc.variables.keys())
    # print(nc['time'][:])
    df = pd.DataFrame(nc['var0_1_200_surface'][0][:][:])
    #replace nan
    df = df.fillna(tif_profile.nodata)
    # sort reverse
    df = df.sort_index(ascending=False)
    rain_data = df.values

    #create tif file with data
    create_geotif(tif_profile, rain_data)

    return ier

#--------------------------------------------------
# About GSMAPS Rain data
# variable is rainfall rate(mm/hour)
# domain -180W-180E, 60N-60S
# grid resolustion is 0.1 degree
# temporal resolution is 1 hour
#--------------------------------------------------
def gsmaps_to_tif(fgsmaps, out_path):
    ier = 0
    fname = os.path.basename(fgsmaps)
    ftif = out_path + '/' + fname + '.tif'

    if pathlib.Path(ftif).exists() == True:
        ier = 1
        print(ftif + ' exits already.')
        return ier
    
    #binary profile
    record_format = '3600f'
    record_size = struct.calcsize(record_format)

    #tif profile
    print("generating..." + ftif)
    tif_profile = RasterDataProfile()
    tif_profile.name = ftif
    tif_profile.cols = 3600
    tif_profile.rows = 1200
    tif_profile.originx = -180
    tif_profile.originy = 60
    tif_profile.dx = 0.1
    tif_profile.dy = -0.1
    tif_profile.nodata = -9999

    #空の配列を作成
    rain_data = np.zeros((tif_profile.rows, tif_profile.cols), dtype =float)

    # #gzファイルからデータを読み込み
    fi = gzip.open(fgsmaps, mode='rb')
    pos = 0
    for l in range(0, tif_profile.rows, 1):
        data = fi.read(record_size)
        vals = struct.unpack(record_format, data)
        v_west = list(vals[1800:3600])
        v_west.reverse()
        v_east = list(vals[0:1800])
        rain_data[l,0:1800] = v_west
        rain_data[l,1800:3600] = v_east
    fi.close()

    #create tif file with data
    create_geotif(tif_profile, rain_data)

    return ier

def tif_to_asc(f, out_path):
    ier = 0
    fname = os.path.basename(f)
    fasc = out_path + '/' + fname + '.asc'

    if pathlib.Path(fasc).exists() == True:
        ier = 1
        print(fasc + ' exits already.')
        return ier

    src = gdal.Open(f, gdalconst.GA_ReadOnly) # tifの読み込み (read only)
    type(src) # "osgeo.gdal.Dataset"

    n_cols = src.RasterXSize # 水平方向ピクセル数
    n_rows = src.RasterYSize # 鉛直方向ピクセル数
    profile = src.GetGeoTransform()
    #print(profile)
    
    dx = profile[1]
    dy = - profile[5]
    xll = profile[0]
    yll = profile[3] - dy * n_rows

    # 第１バンド numpy array
    #print(src.RasterCount) # バンド数
    nodata = src.GetRasterBand(1).GetNoDataValue()
    df = pd.DataFrame(src.GetRasterBand(1).ReadAsArray())

    # Output to asc format
    print("generating..." + fasc)
    with open(fasc, mode='w') as f:
        s = 'ncols ' + str(n_cols) + '\n'; f.write(s)
        s = 'nrows ' + str(n_rows) + '\n'; f.write(s)
        s = 'xllcorner ' + str(xll) + '\n'; f.write(s)
        s = 'yllcorner ' + str(yll) + '\n';  f.write(s)
        s = 'dx ' + str(dx) + '\n'; f.write(s)
        s = 'dy ' + str(dy) + '\n'; f.write(s)
        s = 'NODATA_value ' + str(nodata) + '\n'; f.write(s)

    df.to_csv(fasc, sep=' ', index=False, header=False, mode='a')

    #dtid = src.GetRasterBand(1).DataType # 型番号 (ex: 6 -> numpy.float32)
    #gdal_array.GDALTypeCodeToNumericTypeCode(dtid) # 型番号 -> 型名 変換

    return ier

def asc_to_dat(tt, fin, fout):
    ier = 0

    df = pd.read_csv(fin, sep=' ', header=None, skiprows=7)
    n_rows, n_cols = df.shape
    print(n_rows, n_cols)
    
    s = str(tt) + ' ' + str(n_cols) + ' ' + str(n_rows) + '\n'
    fout.write(s)

    df.to_csv(fout, sep=' ', index=False, header=False, mode='a')
    return ier

def tif_to_dat(tt, fin, fout):
    ier = 0

    src = gdal.Open(fin, gdalconst.GA_ReadOnly) # tifの読み込み (read only)
    type(src) # "osgeo.gdal.Dataset"

    df = pd.DataFrame(src.GetRasterBand(1).ReadAsArray())
    n_cols = src.RasterXSize # 水平方向ピクセル数
    n_rows = src.RasterYSize # 鉛直方向ピクセル数

    s = str(tt) + ' ' + str(n_cols) + ' ' + str(n_rows) + '\n'
    fout.write(s)
    df.to_csv(fout, sep=' ', index=False, header=False, mode='a')
    return ier

# URL for each GSMAPS data type
def get_url(name):
    
    if name == 'GSMaP_NRT':
        url = './realtime_ver/v6/hourly/'

    elif name == 'GSMaP_Gauge_NRT':
        url = './realtime_ver/v6/hourly_G/'

    elif name == 'GSMaP_MVK':
        url = './standard/v7/hourly/'

    elif name == 'GSMaP_Gauge':
        url = './standard/v6/hourly_G/'
    
    else:
        print('Error : unknown rain data name.')
        exit(1)

    return url

#download GSMAPS data into local
def download_gsmpas(config):
    from ftplib import FTP
    
    #download directory
    gsmaps_dir = config['gsmaps']['path']['gsmaps_dir']

    #set FTP connection
    ftp = FTP(
        config['gsmaps']['ftp_info']['url'],
        config['gsmaps']['ftp_info']['user'],
        config['gsmaps']['ftp_info']['ps']
    )

    #data name of GSMAPS
    data_name = config['gsmaps']['rain_data']['name']

    #set date
    sdate = config['gsmaps']['date_range']['start_date']
    tdate = datetime.datetime.strptime(sdate, '%Y-%m-%d')
    ndays = int(config['gsmaps']['date_range']['days'])
    for it in range(ndays):

        tdate = tdate + datetime.timedelta(days=it)
        sdate = tdate.strftime('%Y-%m-%d')
        yy, mm, dd = sdate.split('-')
        
        ftp_path = get_url(data_name) + yy + '/' + mm + '/' + dd
        items = ftp.mlsd(ftp_path)
        for item in items:

            #'.gz'ファイルのみダウンロード
            if '.gz' in item[0]:
                path_from = ftp_path + "/" + item[0]
                path_to   = gsmaps_dir + '/' + item[0]

                if pathlib.Path(path_to).exists() == True:
                    print(path_to + ' exits already.')
                    continue

                #ファイルの取得（バイナリー）
                print("downloading..." + item[0])
                f = open(path_to, "wb")
                ftp.retrbinary("RETR " + path_from, f.write)
                f.close()

    return 0

#main function
def main(args):
    import glob

    ier = 0
    with open(args[1], 'r') as yml:
        config = yaml.load(yml)

    #***** grib2-ANAL to tif *****
    if config['run_mode']['data_type'] == 0:

        #grib2 to tif
        wgrib_path = config['wgrib_path']
        grib2_dir = config['grib2']['path']['grib2_dir']
        tif_dir = config['grib2']['path']['tif_dir']
        flist = glob.glob(grib2_dir + '/*.bin')
        for f in flist:
            ier = grib2_to_tif(wgrib_path, f, tif_dir)

    #***** gsmaps to tif *****
    elif config['run_mode']['data_type'] == 1:
        
        #download
        ier = download_gsmpas(config)

        #binary to tif
        gsmaps_dir = config['gsmaps']['path']['gsmaps_dir']
        tif_dir = config['gsmaps']['path']['tif_dir']
        flist = glob.glob(gsmaps_dir + '/*.gz')
        for f in flist:
            ier = gsmaps_to_tif(f, tif_dir)

    return ier

#root
if __name__ == "__main__":
    import sys
    args = sys.argv
    print(main(args))
    print('>>> Completed the rain data decoding.')