# 1- İş Problemi ( Bussines Problem)
# 2- Veriyi Anlama ( Data Understanding)
# 3 Veri Hazırlama (Data Preparation)
# 4- RFM Metriklerinin Hesaplanması ( Calculating RFM Metrics)
# 5- RFM Skorlarının Hesaplanması ( Calculating RFM Scores)
# 6- RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7- Tüm Sürecin Fonskiyonlaştırılması


# 1. İş Problemi (Business Problem)


# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Değişkenler
#
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.


# 2. Veriyi Anlama (Data Understanding)


import datetime as dt
import pandas as pd

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

df_ = pd.read_excel("Miuul_CRM/Datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")

df = df_.copy()
df.head()
df.shape
df.isnull().sum()

# Eşsiz urun sayısı nedir?
df["Description"].nunique()

df["Description"].value_counts()

df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]

df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()

# 3. Veri Hazırlama (Data Preparation)


df.isnull().sum()
df.dropna(inplace=True)

df.describe().T

df = df[~df["Invoice"].str.contains("C", na=False)]

# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)


# Recency, Frequency, Monetary

df.head()

df["InvoiceDate"].max()

today_date = dt.datetime(2010, 12, 11)  # Analiz yaptığımız tarih
type(today_date)

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                     "Invoice": lambda num: num.nunique(),
                                     "TotalPrice": lambda TotalPrice: TotalPrice.sum()})

rfm.columns = ["Recency", "Frequency", "Monetary"]

rfm.describe().T

rfm = rfm[rfm["Monetary"] > 0]

rfm.shape

# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)


rfm["Recency_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["Frequency_score"] = pd.qcut(rfm["Frequency"].rank(method='first'), 5, [1, 2, 3, 4, 5])

rfm["Monetary_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm["Recency_score"].astype(str) + rfm["Frequency_score"].astype(str))

rfm[rfm["RFM_SCORE"] == "55"]  # Champion Customer

# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)

# regex

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

rfm[["segment", "Recency", "Frequency", "Monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "cant_loose"].head()

rfm[rfm["segment"] == "cant_loose"].index

new_df = pd.DataFrame()

new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index

new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

new_df.to_csv("new_customers.csv")

rfm.to_csv("rfm.csv")


# 7. Tüm Sürecin Fonksiyonlaştırılması


def create_rfm(df, to_csv=False):
    # Data Preparation
    df["TotalPrice"] = df["Quantity"] * df["Price"]
    df.dropna(inplace=True)
    df = df[~df["Invoice"].str.contains("C", na=False)]

    # Calculating RFM Metrics
    today_date = dt.datetime(2010, 12, 11)  # Analiz yaptığımız tarih

    rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                         "Invoice": lambda num: num.nunique(),
                                         "TotalPrice": lambda TotalPrice: TotalPrice.sum()})
    rfm.columns = ["Recency", "Frequency", "Monetary"]
    rfm = rfm[rfm["Monetary"] > 0]

    # Calculating RFM Scores
    rfm["Recency_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])

    rfm["Frequency_score"] = pd.qcut(rfm["Frequency"].rank(method='first'), 5, [1, 2, 3, 4, 5])

    rfm["Monetary_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

    rfm["RFM_SCORE"] = (rfm["Recency_score"].astype(str) + rfm["Frequency_score"].astype(str))

    # Creating & Analysing RFM Segments
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
    rfm = rfm[["Recency", "Frequency", "Monetary", "segment"]]

    rfm.index = rfm.index.astype(int)

    if to_csv:
        rfm.to_csv("rfm_new.csv")

    return rfm


df = df_.copy()

rfm_new = create_rfm(df, to_csv=True)
