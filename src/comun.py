'''
Created on 16/03/2015

@author: BOTPI
'''
import datetime, decimal
    
def periodo(fecha):
    fechad = datetime.datetime.strptime(fecha,'%Y-%m-%d')
    desde = fechad.replace(day=1)
    if desde.month==12:
        hasta = desde.replace(year=desde.year+1, month=1)
    else:
        hasta = desde.replace(month=desde.month+1)
    desde = str(desde).split(' ')[0]
    hasta = str(hasta).split(' ')[0]
    return desde, hasta
        