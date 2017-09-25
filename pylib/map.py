#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    WGS84: 地球坐标系， 国际上通用的坐标系。从包含GPS芯片或者北斗芯片的设备获取的经纬度为WGS84地理坐标系，
           谷歌地图在非中国地区使用的坐标系。
    GCJ02: 火星坐标系，中国国家测绘局制定的坐标系，WGS84坐标系加密后的坐标系，使用地图：高德地图，谷歌国内地图，
           搜搜地图。
    BD09:  百度坐标系，百度在GCJ02的基础上进行二次加密，使用地图：百度地图。

    天地图使用的国标2000坐标系和WGS84坐标系偏差很小，可等同为WGS84坐标系。
"""

from __future__ import division
import math
import requests

try:
    import simplejson as json
except ImportError:
    import json


__all__ = ['is_out_china', 'map_factory',
           'wgs84_to_gcj02', 'gcj02_to_wgs84',
           'gcj02_to_bd09', 'bd09_to_gcj02',
           'wgs84_to_bd09', 'bd09_to_wgs84',
           'BaseMap', 'GaodeMap',
           'MapException']


x_pi = 3.14159265358979324 * 3000 / 180
pi = 3.1415926535897932384
# 长半轴
a = 6378245.0
# 扁率
ee = 0.00669342162296594323


def is_out_china(wgs_lon, wgs_lat):
    """
    判断给定坐标是否在中国.
    :param wgs_lon: WGS84坐标系的经度
    :param wgs_lat: WGS84坐标系的纬度
    :return:
    """
    return not (72.004 <= wgs_lon <= 137.8347 and
                0.8293 <= wgs_lat <= 55.8271)


def _delta(lon, lat):
    # Krasovsky 1940
    # a = 6378245.0, 1 / f = 298.3
    # b = a * (1 - f)
    # ee = (a ^ 2 - b ^ 2) / a ^ 2;
    d_lon = _transform_lon(lon - 105.0, lat - 35.0)
    d_lat = _transform_lat(lon - 105.0, lat - 35.0)
    red_lat = lat / 180.0 * pi
    magic = 1 - ee * (math.sin(red_lat) ** 2)
    sqrt_magic = math.sqrt(magic)
    d_lon = (d_lon * 180.0) / (a / sqrt_magic * math.cos(red_lat) * pi)
    d_lat = (d_lat * 180.0) / (a * (1 - ee) / (magic * sqrt_magic) * pi)
    return d_lon, d_lat


def _transform_lon(lon, lat):
    ret = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + \
        0.1 * lon * lat + 0.1 * math.sqrt(math.fabs(lon))
    ret += (20.0 * math.sin(6.0 * lon * pi) +
            20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(1.0 * lon * pi) +
            40.0 * math.sin(lon / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lon / 12.0 * pi) +
            300.0 * math.sin(lon / 30.0 * pi)) * 2.0 / 3.0
    return ret


def _transform_lat(lon, lat):
    ret = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + \
        0.1 * lon * lat + 0.2 * math.sqrt(math.fabs(lon))
    ret += (20.0 * math.sin(6.0 * lon * pi) +
            20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(1.0 * lat * pi) +
            40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) +
            320.0 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(wgs_lon, wgs_lat):
    """
    WGS84:地球坐标系 --> GCJ02:火星坐标系
    :param wgs_lon: WGS84坐标系的经度
    :param wgs_lat: WGS84坐标系的纬度
    """
    d_lon, d_lat = _delta(wgs_lon, wgs_lat)
    return wgs_lon + d_lon, wgs_lat + d_lat


def gcj02_to_wgs84(gcj_lon, gcj_lat):
    """
    GCJ02:火星坐标系 --> WGS84:地球坐标系
    :param gcj_lon: GCJ02坐标系的经度
    :param gcj_lat: GCJ02坐标系的纬度
    """
    d_lon, d_lat = _delta(gcj_lon, gcj_lat)
    return gcj_lon - d_lon, gcj_lat - d_lat


def gcj02_to_bd09(gcj_lon, gcj_lat):
    """
    GCJ02:火星坐标系 --> BD09:百度坐标系
    :param gcj_lon: GCJ02坐标系的经度
    :param gcj_lat: GCJ02坐标系的纬度
    """
    x, y = gcj_lon, gcj_lat
    z = math.sqrt(x ** 2 + y ** 2) + 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi)
    bd_lon = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lon, bd_lat


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    BD09:百度坐标系 --> GCJ02:火星坐标系
    :param bd_lon: BD09坐标系的经度
    :param bd_lat: BD09坐标系的纬度
    """
    x, y = bd_lon - 0.0065, bd_lat - 0.006
    z = math.sqrt(x ** 2 + y ** 2) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gcj_lon = z * math.cos(theta)
    gcj_lat = z * math.sin(theta)
    return gcj_lon, gcj_lat


def wgs84_to_bd09(wgs_lon, wgs_lat):
    """
    WGS84:地球坐标系 --> BG09:百度坐标系
    :param wgs_lon: WGS84坐标系的经度
    :param wgs_lat: WGS84坐标系的纬度
    """
    return gcj02_to_bd09(*wgs84_to_gcj02(wgs_lon, wgs_lat))


def bd09_to_wgs84(bd_lon, bd_lat):
    """
    BD09:百度坐标系 --> WGS84:地球坐标系
    :param bd_lon: BD09坐标系的经度
    :param bd_lat: BD09坐标系的纬度
    """
    return gcj02_to_wgs84(*bd09_to_gcj02(bd_lon, bd_lat))


class MapException(Exception):
    """地图工具异常"""
    pass


class BaseMap(object):
    """地图工具基类"""
    def geo_decode(self, lon, lat, is_gps=True):
        return u''


class GaodeMap(BaseMap):
    """高德地图工具类"""

    # 高德地图服务接口
    _url_d = {
        # 地理编码服务接口
        'geo_encode': 'http://restapi.amap.com/v3/geocode/geo',
        # 逆地理编码服务接口
        'geo_decode': 'http://restapi.amap.com/v3/geocode/regeo'
    }
    _out_fmt = 'JSON'

    def __init__(self, **kw):
        self.key = kw.get('key', '')

    def geo_decode(self, lon, lat, is_gps=True):
        """
        逆地理编码, 给定经纬度获取对应的结构化地址
        116.42546, 39.98695 --> 北京市朝阳区太阳宫镇芍药居北里世奥国际中心
        :param lon: WGS84坐标系的经度
        :param lat: WGS84坐标系的纬度
        :param is_gps: 经纬度的坐标系, True是WGS84, False是GCJ02
        """
        url = self._url_d.get('geo_decode')
        params = {
            'key': self.key,
            'output': self._out_fmt
        }
        gcj_lon, gcj_lat = wgs84_to_gcj02(lon, lat) if is_gps else (lon, lat)
        params['location'] = '{:.6f},{:.6f}'.format(gcj_lon, gcj_lat)
        res = requests.get(url, params=params)
        obj = json.loads(res.content, encoding=res.encoding)

        # 请求失败
        if not obj['status']:
            raise MapException('Gaode: ' + 'REQUEST FAILED')

        # 请求成功 有错误
        if obj['infocode'] != '10000':
            raise MapException('Gaode: ' + obj['info'])

        address = obj['regeocode'].get('formatted_address')
        return u'' if not address else address


def map_factory(name='gaode', **kw):
    _class_d = {
        'gaode': GaodeMap,
        'base': BaseMap
    }

    name = name if name in _class_d else 'base'
    return _class_d.get(name)(**kw)


if __name__ == '__main__':
    print wgs84_to_gcj02(116.42546, 32.98695)
    print gcj02_to_bd09(116.42546, 32.98695)
    print bd09_to_gcj02(*gcj02_to_bd09(116.42546, 32.98695))
    print gcj02_to_wgs84(*wgs84_to_gcj02(116.42546, 32.98695))
    gd = map_factory(key='34b2c1dd98f01d03133b8194c4c9e454')
    print gd.geo_decode(116.42546, 39.98695)
