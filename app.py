from flask import Flask, render_template, request
from tkinter import filedialog
import re
import time
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

app = Flask(__name__)

# Setup stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Distance function (Levenshtein Distance)
def dld(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    if lenstr1 == 0:
        return lenstr2
    if lenstr2 == 0:
        return lenstr1
    for i in range(-1, lenstr1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i-1, j)] + 1,      # deletion
                d[(i, j-1)] + 1,      # insertion
                d[(i-1, j-1)] + cost  # substitution
            )
    return d[(lenstr1-1, lenstr2-1)]

# Normalize & tokenize

def tokenize(text):
    result = text.lower()
    result = re.sub(r'[^a-z0-9 -]', ' ', result)
    result = re.sub(r'( +)', ' ', result)
    return result.strip()

@app.route("/")
def main():
    kalimat = {'Silahkan': 1, 'ketik': 2, 'di': 3, 'sini': 4}
    hasil = {'-': '-'}
    return render_template('index.html', kalimat=kalimat, hasil=hasil)

@app.route("/periksa", methods=['POST'])
def periksa():
    kamus = []
    with open("kamus.txt", 'r', encoding='utf-8') as f:
        kamusmasuk = f.read()
        kamus = kamusmasuk.split('\n')

    kalimat_input = request.form['inputan']
    kalimat = kalimat_input.split(' ')
    start = time.time()

    kalimatakhir = {}
    hasil_stemming = {}
    for x in kalimat:
        token = tokenize(x)
        stemmed = stemmer.stem(token)
        hasil_stemming[x] = stemmed

        if token in kamus:
            kalimatakhir[x] = 'benar'
        else:
            kalimatakhir[x] = 'salah'

    hasilakhir = {}
    sarankata = {}
    for original_word, stemmed in hasil_stemming.items():
        if stemmed not in kamus:
            kandidat = [y for y in kamus if dld(stemmed, y) == 1]
            sarankata[original_word] = kandidat if kandidat else "-"

    end = time.time()
    return render_template('index.html', waktu=end-start, hasil=sarankata, kalimat=kalimatakhir)

@app.route("/buka_file", methods=['POST'])
def buka_file():
    kalimatakhir = {}

    uploaded_file = request.files.get('file')
    if uploaded_file and uploaded_file.filename.endswith('.txt'):
        content = uploaded_file.read().decode('utf-8')
        kalimat = content.split()
        for x in kalimat:
            kalimatakhir[x] = 1
    else:
        kalimatakhir = {'Silahkan': 1, 'ketik': 2, 'di': 3, 'sini': 4}

    hasil = {'-': '-'}
    return render_template('index.html', kalimat=kalimatakhir, hasil=hasil)

if __name__ == "__main__":
    app.run()
