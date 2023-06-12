# library import
import re
# import numpy as np
import string

# import pandas
import pandas as pd

# library
from newspaper import Article
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import json
import sys
import mysql.connector

# mysql
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_ta_rini"
)

mycursor = mydb.cursor()

idBerita = sys.argv[1]
statusBerita = sys.argv[2]

# sql = "SELECT link FROM berita_latih ORDER BY id DESC LIMIT 1"
if statusBerita == 'latih':
    sql = "SELECT link FROM berita_latih WHERE id=" + str(idBerita)
else:
    sql = "SELECT link FROM berita_uji WHERE id=" + str(idBerita)


mycursor.execute(sql)

myresult = mycursor.fetchall()

for link in myresult:
    berita = link[0]

# persiapan variabel untuk stemming
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# persiapan tanda baca
symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"

# download article for prepocessing
article = Article(
    berita, 'id')
# article = Article(
#     'https://health.detik.com/berita-detikhealth/d-6616767/3-produk-jamu-oplosan-ditarik-bpom-mengandung-bahan-kimia-obat', 'id')

article.download()
article.parse()

# memberikan nilai pada variabel kalimat
kalimat = article.text

# tahap case folding
# 1 lower all case
lower = kalimat.lower()

# 2 menghapus angka
hapus_angka = re.sub(r"\d+", "", lower)

# 3 menghapus tanda baca
# string = '!”#$%&’()*+,-./:;<=>?@[\]^_`{|}~'
# hapus_tanda_baca = hapus_angka.translate(str.maketrans("","",string.punctuation))
# for i in symbols:
#     #print(sentence)
#     hapus_tanda_baca = np.char.replace(hapus_angka, i, ' ')
text = hapus_angka
text = text.replace('-', ' ')
text = text.replace('\\t', " ").replace(
    '\\n', " ").replace('\\u', " ").replace('\\', " ")
text = text.encode('ascii', 'replace').decode('ascii')
text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", text).split())
text = text.translate(str.maketrans(" ", " ", string.punctuation))
text = re.sub('\s+', ' ', text)

# 4 menghapus whitepace
# hapus_whitespace = hapus_tanda_baca.strip()


# menyimpan hasil case folding ke variabel baru
case_folding = text

# stemming
kata_dasar = stemmer.stem(case_folding)

# filtering stopword
tokens = word_tokenize(kata_dasar)
listStopword = set(stopwords.words('indonesian'))
listStopwordEng = set(stopwords.words('English'))

remove = []
for t in tokens:
    if t not in listStopword:
        remove.append(t)

removed = []
for t in remove:
    if t not in listStopwordEng:
        removed.append(t)


kemunculan = FreqDist(removed)

# print(kemunculan.most_common())
numpy_array = kemunculan.most_common()

# df = pd.DataFrame(numpy_array)


# print(df.head)
print(json.dumps(numpy_array))
# return numpy_array
# print("text")
# df.to_excel(r"F:\Python\Skripsi_Rini\Data_set.xlsx", index=False)
