import pandas as pd
import numpy as np
import duckdb as db
import awswrangler as wr
import warnings
import argparse

warnings.filterwarnings("ignore", category=FutureWarning, module="IPython.core.formatters")

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

def filtro_dias_sku(data,dias_ventas,porcentaje_dias_ventas):
    data['FLAG_DIAS'] = 1
    data['Fecha'] = pd.to_datetime(data['Fecha'])
    df_skus = data.groupby('Sku').agg({'Sku':'count','Fecha':['nunique','min','max']}).reset_index()
    cols = ['_'.join(col) if len(col[1])>0 else col[0] for col in df_skus.columns.values]
    df_skus.columns = cols
    df_skus['DIAS_POTENCIALES'] = (df_skus['Fecha_max']-df_skus['Fecha_min']).dt.days + 1
    df_skus['PORC_DIAS'] = df_skus['Fecha_nunique'] / df_skus['DIAS_POTENCIALES']
    lista_skus = df_skus[(df_skus['Fecha_nunique']>=dias_ventas)&(df_skus['PORC_DIAS']>=porcentaje_dias_ventas)]['Sku'].tolist()
    data.loc[data['Sku'].isin(lista_skus), 'FLAG_DIAS'] = 0
    return data

ventas = wr.s3.read_parquet(f's3://{pbucket}/{pcliente}/data_procesada/df.parquet')
ventas = ventas.loc[~((ventas['PROD_LDC'] == 'SI') & (ventas['CLI_LDC'] == 'SI') & (ventas['Dia'] == 'Lunes'))]
a = ventas['Sku'].nunique()
print(f'Antes del filtro {a}')
df = filtro_dias_sku(ventas, 180, 0.6)
sku_fecha = df.groupby(['Sku', 'Fecha']).agg({'PrecioUnitario':["mean", "std"]},).reset_index()
cols = ['_'.join(col) if len(col[1])>0 else col[0] for col in sku_fecha.columns.values]
sku_fecha.columns = cols
sku_fecha['PrecioUnitario_std'] = sku_fecha['PrecioUnitario_std'].fillna(0)
df = pd.merge(df, sku_fecha, how='left', on=['Sku','Fecha'])
df['ZSCORE'] = np.where(df['PrecioUnitario_std']>0, np.abs((df['PrecioUnitario']-df['PrecioUnitario_mean'])/df['PrecioUnitario_std']), 0)
df['FLAG_ZSCORE']=np.where(df['ZSCORE']>3, 1, 0)
df = df.loc[(df['FLAG_DIAS'] == 0) & (df['Cantidad'] > 0) & (df['PrecioUnitario'] > 0) & (df['FLAG_ZSCORE'] == 0)]

query = """
    SELECT 
        Regional AS store_code,
        Sku AS product_code,
        Fecha AS date,
        SUM(Cantidad) AS quantity,
        MEDIAN(ImporteLineaBs/Cantidad) AS price,
        MEDIAN(CostoUnitario) AS cost,
        MAX(Producto) AS description,
        MAX(Categoria) AS category,
        MAX(SubCategoria) AS subcategory,
        MAX(SubSubCatego) AS subsubcategory
    FROM df
    GROUP BY 1,2,3
    ORDER BY date
    """

data = db.query(query).to_df()
a = data['product_code'].nunique()
print(f'Después del filtro {a}')
data.to_csv(f's3://{pbucket}/{pcliente}/data_procesada/df_preprocesada.csv', index=False)
print("Data Preprocesada")