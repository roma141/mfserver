# -*- coding: utf-8 -*-
'''
Created on 02/01/2015

@author: Carlos Botello
'''
# import json
# import datetime, decimal

def loginf(email, clave, bd):
    rows = bd.Ejecuta("select * from usuarios where email='%s' and clave='%s'" % (email, clave))
    if rows:
        return rows[0]
    return None

def ChequeaUsuarioMovimiento(IDmovimiento, usuario, bd):
    rows = bd.Ejecuta("select * from movimientos where ID=%s and IDusuario=%s" % (IDmovimiento, usuario["ID"]))
    if rows:
        return rows[0]
    return None

def ChequeaUsuarioCuenta(IDcuenta, usuario, bd):
    rows = bd.Ejecuta("select * from cuentas where ID=%s and IDcliente=%s" % (IDcuenta, usuario["IDcliente"]))
    if rows:
        return rows[0]
    return None

def EntradasySalidasPeriodo(desde, hasta, IDcuenta, bd):
    f = 1
    if desde==hasta:
        return 0, 0
    elif desde>hasta:
        desde, hasta = hasta, desde
        f = -1
        
    entradas = bd.Ejecuta("""
        select sum(movimientos.valor) as total 
        from movimientos 
        where movimientos.fecha>='%s' and movimientos.fecha<'%s' and movimientos.IDcuentamas='%s'
        """ % (desde, hasta, IDcuenta))[0]["total"]

    salidas = bd.Ejecuta("""
        select sum(movimientos.valor) as total 
        from movimientos 
        where movimientos.fecha>='%s' and movimientos.fecha<'%s' and movimientos.IDcuentamenos='%s'
        """ % (desde, hasta, IDcuenta))[0]["total"]
              
    if not salidas: salidas=0
    if not entradas: entradas=0

    return f*entradas, f*salidas

def Cuentas(desde, hasta, usuario, bd):
    bd.Ejecuta("""
        create temporary table xcuentas 
        select ID, nombre, saldo as saldoant, saldo as entradas, saldo as salidas, saldo, escontinua, fechasaldo 
        from cuentas 
        where IDcliente=%s and activo=1
        order by Orden
        """ % usuario["IDcliente"]);
    bd.Ejecuta("update xcuentas set entradas=0, salidas=0, saldo=0")
    bd.Ejecuta("update xcuentas set saldoant=0 where escontinua=0")
    
    rows = bd.Ejecuta("select ID, fechasaldo, escontinua from xcuentas")
    for row in rows:
        if row["escontinua"]==1:
            entradas,salidas = EntradasySalidasPeriodo(str(row["fechasaldo"]), desde, row["ID"], bd)
            bd.Ejecuta("update xcuentas set saldoant=saldoant+%s-%s where ID=%s" % (entradas, salidas, row["ID"]))
    
        entradas,salidas = EntradasySalidasPeriodo(desde, hasta, row["ID"], bd)
        bd.Ejecuta("update xcuentas set entradas=%s, salidas=%s where ID=%s" % (entradas, salidas, row["ID"]))
                                    
    bd.Ejecuta("update xcuentas set saldo=saldoant+entradas-salidas")
    bd.Ejecuta("update xcuentas set saldoant=0, saldo=0 where escontinua=0")
    rows = bd.Ejecuta("select ID,nombre, format(saldoant,0) as saldoant, format(entradas,0) as entradas, format(salidas,0) as salidas, format(saldo,0) as saldo from xcuentas")
    bd.Ejecuta("drop table xcuentas")
    return rows

def Entradas(IDcuenta, desde, hasta, bd):
    return bd.Ejecuta("""
        select movimientos.*, usuarios.nombrecorto, format(valor,0) as valorf, cuentas.nombre as contra
            , concat('onclick="eliminar(',movimientos.ID,')"') as funcion, 'X' as eliminar 
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
            inner join cuentas on cuentas.ID=movimientos.IDcuentamenos
        where IDcuentamas=%s and fecha>='%s' and fecha<'%s'
        order by ID desc
        """ % (IDcuenta, desde, hasta))

def Salidas(IDcuenta, desde, hasta, bd):
    return bd.Ejecuta("""
        select movimientos.*, movimientos.concepto as conceptos, movimientos.fecha as fechas, movimientos.valor as valors
            , usuarios.nombrecorto as nombrecortos, format(valor,0) as valorfs, cuentas.nombre as contras
            , concat('onclick="eliminar(',movimientos.ID,')"') as funcion, 'X' as eliminars
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
            inner join cuentas on cuentas.ID=movimientos.IDcuentamas
        where IDcuentamenos=%s and fecha>='%s' and fecha<'%s'
        order by ID desc
        """ % (IDcuenta, desde, hasta))

def MovimientosPeriodo(IDcuenta, desde, hasta, tags, usuario, bd):
    stags = ""
    if tags:
        if tags[0] > "":
            for tag in tags:
                stags += " and MATCH(concepto) AGAINST('%s')" % tag
    bd.Ejecuta("""
        create temporary table x1
        select movimientos.*, valor as entrada, valor as salida, cuentas.nombre as contra
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
            inner join cuentas on cuentas.ID=movimientos.IDcuentamenos
        where fecha>='%s' and fecha<='%s' and usuarios.IDcliente=%s and IDcuentamas=%s
        %s
        """ % (desde, hasta, usuario["IDcliente"], IDcuenta, stags))
    bd.Ejecuta("update x1 set salida=0")
    bd.Ejecuta("""
        insert into x1
        select movimientos.*, 0, valor as salida, cuentas.nombre as contra
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
            inner join cuentas on cuentas.ID=movimientos.IDcuentamas
        where fecha>='%s' and fecha<='%s' and usuarios.IDcliente=%s and IDcuentamenos=%s
        %s
        """ % (desde, hasta, usuario["IDcliente"], IDcuenta, stags))
    
    response = bd.Ejecuta("select * from x1 order by fecha, ID")
    bd.Ejecuta("drop table x1")
    
    return response

def ModificaMov(datos, bd):
    bd.Ejecuta("""
        update movimientos set IDcuentamas=%s, IDcuentamenos=%s, fecha='%s', concepto='%s', valor=%s
        where ID=%s
        """ % (datos["IDcuentamas"], datos["IDcuentamenos"], datos["fecha"], datos["concepto"], datos["valor"], datos["IDmov"]))

def AgregaCliente(email, clave, datos, bd):
    bd.Ejecuta("insert into clientes (Nombre) values ('%s')" % datos["nombre"])
    IDcliente = bd.UltimoID()
    bd.Ejecuta("insert into usuarios (IDcliente,nombre,nombreCorto,email,clave) values (%s,'%s','%s','%s','%s')"
                % (IDcliente, datos["nombre"], datos["nombre"][:2], email, clave))

    bd.Ejecuta("create temporary table x1 select * from cuentasnuevas")
    bd.Ejecuta("update x1 set IDcliente=%s" % IDcliente)
    bd.Ejecuta("insert into cuentas (IDcliente,Nombre,Limite,esGasto,esContinua,Orden) select IDcliente,Nombre,Limite,esGasto,esContinua,Orden from x1")
    bd.Ejecuta("drop table x1")
    return "ok"
    
def CuentasEditor(usuario, bd):
    bd.Ejecuta("""
        create temporary table x1
        SELECT IDcuentamas AS IDcuenta
        FROM movimientos 
            INNER JOIN usuarios ON usuarios.ID=movimientos.IDusuario
        WHERE IDcliente=%s 
        GROUP BY IDcuentamas
        """ % usuario["IDcliente"])    
    
    bd.Ejecuta("""
        insert into x1
        SELECT IDcuentamenos AS IDcuenta
        FROM movimientos 
            INNER JOIN usuarios ON usuarios.ID=movimientos.IDusuario
        WHERE IDcliente=%s 
        GROUP BY IDcuentamenos
        """ % usuario["IDcliente"])    

    bd.Ejecuta("create temporary table x2 select IDcuenta from x1 group by IDcuenta")

    rows = bd.Ejecuta("""
        select cuentas.*, if(x2.IDcuenta is null,1,0) as borrable 
        from cuentas
            left join x2 on x2.IDcuenta=cuentas.ID
        where IDcliente=%s 
        order by orden
        """ % usuario["IDcliente"])
    
    bd.Ejecuta("drop table x1,x2")
    return rows
    

def AgregaCuenta(IDcliente, nombre, bd):
    bd.Ejecuta("create temporary table x1 select IDcuenta from movimientos where IDcliente=%s group by IDcuenta" % IDcliente)
    bd.Ejecuta("insert into cuentas (IDcliente, nombre) values (%s, '%s')" % (IDcliente, nombre))

def ModificaCuenta(datos, bd):
    bd.Ejecuta("""
        update cuentas set nombre='%s', saldo=%s, fechasaldo='%s', esContinua=%s, esgasto=%s, orden=%s, activo=%s
        where ID=%s
        """ % (datos["nombre"], datos["saldo"], datos["fechasaldo"], datos["esContinua"], datos["esgasto"] ,datos["orden"], datos["activo"], datos["IDcuenta"]))

def EliminaCuenta(IDcuenta, bd):
    bd.Ejecuta("delete from cuentas where ID=%s" % (IDcuenta))

def Years(IDcliente, bd):
    return bd.Ejecuta("""
        select year(fecha) as ID, year(fecha) as nombre 
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
        where IDcliente=%s 
        group by ID
        """ % IDcliente)

def Year(year, IDcliente, bd):
    bd.Ejecuta("""
        create temporary table x1
        select cuentas.ID, cuentas.nombre, cuentas.orden, month(fecha) as mes, sum(movimientos.valor) as valor 
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
            inner join cuentas on cuentas.ID=movimientos.IDcuentamas
        where usuarios.IDcliente=%s and year(fecha)=%s 
        group by movimientos.IDcuentamas, mes
        """ % (IDcliente,year))

    bd.Ejecuta("""
        insert into x1
        select cuentas.ID, cuentas.nombre, cuentas.orden, month(fecha) as mes, -sum(movimientos.valor) as valor 
        from movimientos
            inner join usuarios on usuarios.ID=movimientos.IDusuario
            inner join cuentas on cuentas.ID=movimientos.IDcuentamenos
        where usuarios.IDcliente=%s and year(fecha)=%s 
        group by movimientos.IDcuentamenos, mes
        """ % (IDcliente,year))
    
    bd.Ejecuta("create temporary table x2 select ID, nombre, mes, sum(valor) as valor, orden from x1 group by ID, nombre, mes" )
    
    bd.Ejecuta("""
        create temporary table x3
        SELECT ID, nombre, orden
            ,IF(mes=1, valor, 0) AS ene
            ,IF(mes=2, valor, 0) AS feb
            ,IF(mes=3, valor, 0) AS mar
            ,IF(mes=4, valor, 0) AS abr
            ,IF(mes=5, valor, 0) AS may
            ,IF(mes=6, valor, 0) AS jun
            ,IF(mes=7, valor, 0) AS jul
            ,IF(mes=8, valor, 0) AS ago
            ,IF(mes=9, valor, 0) AS sep
            ,IF(mes=10, valor, 0) AS oct
            ,IF(mes=11, valor, 0) AS nov
            ,IF(mes=12, valor, 0) AS dic
        FROM x2
        GROUP BY ID, mes
        ORDER BY orden
        """)
    
    rows = bd.Ejecuta("""
        select ID, nombre
            , format(sum(ene),0) as ene, format(sum(feb),0) as feb, format(sum(mar),0) as mar 
            , format(sum(abr),0) as abr, format(sum(may),0) as may, format(sum(jun),0) as jun
            , format(sum(jul),0) as jul, format(sum(ago),0) as ago, format(sum(sep),0) as sep
            , format(sum(oct),0) as oct, format(sum(nov),0) as nov, format(sum(dic),0) as dic
        from x3
        group by ID, nombre
        order by orden
        """)
    
    bd.Ejecuta("drop table x1,x2,x3")
    return rows
