import pandas as pd
import numpy as np
import duckdb
import warnings
import awswrangler as wr
import argparse
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument("--bucket", type=str)
parser.add_argument("--product", type=str)
parser.add_argument("--cliente", type=str)
parser.add_argument("--modelo", type=str)
args = parser.parse_args()

pbucket = args.bucket
pproduct = args.product
pcliente = args.cliente
pmodelo = args.modelo

now_utc = datetime.utcnow()
lima_time = now_utc - timedelta(hours=18)
hoy = lima_time.strftime('%Y-%m-%d')
#hoy = '2024-09-30'
print(f'fecha:{hoy}')
abucket = 'pricelab-mlops-analytics'
# demanda = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/demanda.csv')
# margen = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/margen.csv')
sucursales = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/sucursales.csv',encoding = "ISO-8859-1")
productos = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/productos.csv',encoding = "ISO-8859-1")
promos = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/promos.csv')
tipo_cliente = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/tipoclientes.csv',encoding = "ISO-8859-1")
scrap = wr.s3.read_csv(f's3://{pbucket}/{pcliente}/manual/scraping/*.csv')
# match = wr.s3.read_csv(f's3://{abucket}/{pcliente}/manual/match/rds_match.csv')

promos = promos.merge(productos[['SkuProducto','Categoria','SubCategoria','Area','Estado']],on='SkuProducto', how='inner')
promos = promos.loc[promos['Estado'] == 'VIGENTE']
tipo_cliente['NomTipoCliente'] = tipo_cliente['NomTipoCliente'].str.strip()
ventas = wr.s3.read_csv(path=f"s3://{pbucket}/{pcliente}/data_ventas/*.csv")
ventas['Fecha'] = pd.to_datetime(ventas['Fecha'])
ventas['Anio'] = ventas['Fecha'].dt.year
ventas['Mes'] = ventas['Fecha'].dt.month

q = """
    SELECT DISTINCT ventas.IDTransaccion,
            CAST(ventas.CodSuc AS INTEGER) AS CodSuc,
            sucursales.TamNivel,
            sucursales.Regional,
            TRIM(TRAILING ' ' FROM sucursales.NivelSocioeconomico) AS NivelSocioeconomico,
            ventas.CodCliente,
            ventas.CodChavez AS Sku,
            productos.Linea,
            productos.Grupo,
            productos.Categoria,
            productos.SubCategoria,
            productos.SubSubCatego,
            productos.Area,
            productos.Producto,
            productos.Estado,
            ventas.Fecha,
            ventas.HoraVenta,
            strftime('%Y-%W', ventas.Fecha) AS date_week,
            CASE
                WHEN isodow(Fecha) = 1 THEN 'Lunes'
                WHEN isodow(Fecha) = 2 THEN 'Martes'
                WHEN isodow(Fecha) = 3 THEN 'Miercoles'
                WHEN isodow(Fecha) = 4 THEN 'Jueves'
                WHEN isodow(Fecha) = 5 THEN 'Viernes'
                WHEN isodow(Fecha) = 6 THEN 'Sabado'
                WHEN isodow(Fecha) = 7 THEN 'Domingo'
                ELSE NULL
                END AS Dia,
            ventas.Anio,
            ventas.Mes,
            CASE
                WHEN ventas.Mes = 1 THEN 'Enero'
                WHEN ventas.Mes = 2 THEN 'Febrero'
                WHEN ventas.Mes = 3 THEN 'Marzo'
                WHEN ventas.Mes = 4 THEN 'Abril'
                WHEN ventas.Mes = 5 THEN 'Mayo'
                WHEN ventas.Mes = 6 THEN 'Junio'
                WHEN ventas.Mes = 7 THEN 'Julio'
                WHEN ventas.Mes = 8 THEN 'Agosto'
                WHEN ventas.Mes = 9 THEN 'Septiembre'
                WHEN ventas.Mes = 10 THEN 'Octubre'
                WHEN ventas.Mes = 11 THEN 'Noviembre'
                WHEN ventas.Mes = 12 THEN 'Diciembre'
                ELSE NULL
                END AS NombreMes,
            ventas.Cantidad,
            ventas.UnidadMedida,
            ventas.PesoNeto,
            ROUND(ventas.PrecioUnitario, 2) AS PrecioUnitario,
            ROUND(ventas.PorcDescuento, 3) AS PorcDescuento,
            ventas.ImporteLinea,
            ventas.ImpDescuento,
            ventas.ImporteLineaBs,
            ROUND(ventas.CostoDeVenta/0.87, 2) as CostoVenta,
            ROUND((CostoVenta)/(ventas.Cantidad), 2) AS CostoUnitario,
            ROUND((ventas.ImporteLinea - CostoVenta), 2) AS Margen_Bruto,
            ROUND((ventas.ImporteLineaBs - CostoVenta), 2) AS Margen_Neto,
            ROUND((ventas.PrecioUnitario - CostoUnitario)/ventas.PrecioUnitario, 2) AS MargenPorc,
            CASE
                WHEN promos.SkuProducto IS NULL THEN 'NO'
                ELSE 'SI'
                END AS PROD_LDC,
            promos.DescPorc,
            CASE
                WHEN tipo_cliente.CodCli IS NULL THEN 'NO'
                ELSE 'SI'
                END AS CLI_LDC,
            -- scrap.competitor_original_price as Precio_cc,
            CASE
                WHEN convert = 'UNIDAD' THEN scrap.competitor_original_price/convert_value
                WHEN convert = 'CAJA' THEN scrap.competitor_original_price*convert_value
                ELSE scrap.competitor_original_price
                END AS Precio_cc,
            scrap.stock_producto as Stock_cc
    FROM ventas
    LEFT JOIN productos ON ventas.CodChavez = productos.SkuProducto
    LEFT JOIN sucursales ON ventas.CodSuc = sucursales.CodSuc
    LEFT JOIN promos ON ventas.CodChavez = promos.SkuProducto
    LEFT JOIN tipo_cliente ON tipo_cliente.CodCli = ventas.CodCliente
                        AND tipo_cliente.NomTipoCliente = 'LUNES DE CHAVEZ'
    -- LEFT JOIN match ON match.Sku = ventas.CodChavez
    LEFT JOIN scrap ON ventas.CodChavez = scrap.client_product_sku AND scrap.date = ventas.Fecha
    WHERE ventas.ImpDescuento >= 0
    AND ventas.ImporteLineaBs >= 0
    AND ventas.PorcDescuento >= 0
    ORDER BY CodSuc,Sku,Fecha,HoraVenta
    """
print("Iniciando query")
#ventas = duckdb.query(q).to_df()
#ventas.to_parquet(f's3://{pbucket}/{pcliente}/data_procesada/df.parquet.gzip', compression='gzip')

ventas = duckdb.query(q).to_df()
ventas['HoraVenta'] = ventas['HoraVenta'].str.split('.').str[0]
ventas['HoraVenta'] = pd.to_datetime(ventas['HoraVenta'], format='%H:%M:%S').dt.time
ventas['HoraVenta'] = ventas['HoraVenta'].apply(lambda x: x.strftime('%H:%M:%S'))
ventas = ventas.drop_duplicates()

ventas.to_parquet(f's3://{pbucket}/{pcliente}/data_procesada/df.parquet', index=False)                  # prod
ventas.to_parquet(f's3://{abucket}/{pcliente}/data_procesada/parquet/df.parquet', index=False)          # analytics

print("ETL terminado")