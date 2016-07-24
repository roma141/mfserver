# -*- coding: utf-8 -*-
'''
Created on 02/01/2015

@author: Carlos Botello
'''
from apiDB import DB
from subfinan import *
from comun import *

def LoginF(email, clave):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        bd.cierra()
        return usuario
    
    bd.cierra()
    return None

def LeeCuentasF(email, clave):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        response = {}
        response["cuentas"] = bd.Ejecuta("select ID, nombre from cuentas where IDcliente=%s" % usuario["IDcliente"])
        response["usuario"] = usuario
        bd.cierra()
        return response
    
    bd.cierra()
    return None

def CuentasF(email, clave, fecha):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        desde, hasta = periodo(fecha)
        response = {}
        response["datos"] = Cuentas(desde, hasta, usuario, bd)
        response["usuario"]=usuario        

        bd.cierra()
        return response;
    
    bd.cierra()
    return None

def EntradasySalidasF(email, clave, fecha, IDcuenta):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        desde, hasta = periodo(fecha)
        response = {}      
        response["entradas"] = Entradas(IDcuenta, desde, hasta, bd)        
        response["salidas"] = Salidas(IDcuenta, desde, hasta, bd)
        bd.cierra()
        return response;
    
    bd.cierra()
    return None
    
def AgregaMovimientoF(email, clave, datos):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        if ChequeaUsuarioCuenta(datos["IDcuentamas"], usuario, bd) and ChequeaUsuarioCuenta(datos["IDcuentamenos"], usuario, bd):
            bd.Ejecuta("insert into movimientos (IDusuario, IDcuentamas, IDcuentamenos, concepto, valor, fecha) values(%s,%s,%s,'%s',%s,'%s')" 
                       % (usuario["ID"], datos["IDcuentamas"], datos["IDcuentamenos"], datos["concepto"], datos["valor"], datos["fecha"]))
    
    bd.cierra()
            
def EliminaMovimientoF(email, clave, IDmovimiento):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        if ChequeaUsuarioMovimiento(IDmovimiento, usuario, bd):
            bd.Ejecuta("delete from movimientos where ID=%s" % IDmovimiento)
    
    bd.cierra()

def MovimientosF(email, clave, IDcuenta, desde, hasta, tags):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        tags = tags.split(",")
        response = MovimientosPeriodo(IDcuenta, desde, hasta, tags, usuario, bd)
        bd.cierra()
        return response
    
    bd.cierra()
    return None

def ModificaMovF(email, clave, datos):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        ModificaMov(datos, bd)
    
    bd.cierra()
    return None

def AgregaClienteF(email, clave, lang, datos):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        bd.cierra()
        return "ok"
    else:
        rows = bd.Ejecuta("select * from usuarios where email='%s'" % email)
        if rows:
            bd.cierra()
            return "existe"
        else:
            if datos["d1"]=="myfinan@gtienda.com" and datos["d2"]=="gtienda":
                resp = AgregaCliente(email, clave, lang, datos, bd)
                bd.cierra()
                return resp
        
    bd.cierra()

def CuentasEditorF(email, clave):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        response = {}
        response["datos"] = CuentasEditor(usuario, bd)
        response["usuario"] = usuario
        bd.cierra()
        return response
    
    bd.cierra()
    return None  

def AgregaCuentaF(email, clave, datos):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        AgregaCuenta(usuario["IDcliente"], datos["nombre"], bd)
    
    bd.cierra()
    return None

def ModificaCuentaF(email, clave, datos):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        ModificaCuenta(datos, bd)
    
    bd.cierra()
    return None

def EliminaCuentaF(email, clave, datos):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        EliminaCuenta(datos["IDcuenta"], bd)
    
    bd.cierra()
    return None
                
def YearsF(email, clave):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        response = {}
        response["datos"] = Years(usuario["IDcliente"], bd)
        response["usuario"] = usuario
        bd.cierra()
        return response
    
    bd.cierra()
    return None  
                
def YearF(email, clave, year):
    bd = DB(nombrebd="myfinan")
    usuario = loginf(email, clave, bd)
    if usuario:
        response = {}
        response["datos"] = Year(year, usuario["IDcliente"], bd)
        response["usuario"] = usuario
        bd.cierra()
        return response
    
    bd.cierra()
    return None  
                