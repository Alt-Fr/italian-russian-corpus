# Fix PyTorch DLL loading issue on Windows
# You need to add this at the beginning, before importing torch and other conflicting modules

# Testing
#from PyQt6.QtWidgets import QApplication

# Imports successfully

import os
import platform

if platform.system() == "Windows":
    import ctypes
    from importlib.util import find_spec
    try:
        if (spec := find_spec("stanza")) and spec.origin and os.path.exists(
            dll_path := os.path.join(os.path.dirname(spec.origin), "lib", "c10.dll")
        ):
            ctypes.CDLL(os.path.normpath(dll_path))
    except Exception:
        pass


import re
import stanza
import torch
import pandas as pd
import subprocess
import os
import psycopg2

from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)


# параметы БД
db_params = {
    "dbname": "rus_it",
    "user": "user",
    "password": "123",
    "host": "db",
    "port": "5432"
}

# файл с пословицами
csv_file_path = '/usr/src/app/data.csv'

df = pd.read_csv(csv_file_path)
# для итальянского
nlp = stanza.Pipeline('it', processors='tokenize,pos,lemma')

# для русского
segmenter = Segmenter()
morph_vocab = MorphVocab()
embedding = NewsEmbedding()
morph_tagger = NewsMorphTagger(embedding)

#---------------переделать------------------------------------------
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    print('Подключились к БД')
    
# заполняем с. итальянские_пословицы, русские_пословицы, тематика
    print('Заполняем...')
    dict_rus = {'DET': 'PRON', 'AUX': 'VERB'}
    
    for index, row in df.iterrows():
        text_rus = row['Пословицы_русская']
        
        cursor.execute("""
            INSERT INTO "Русские_пословицы" ("Текст_пословицыРус")
            VALUES (%s)
            RETURNING "idPh_ru";
        """, (text_rus,))
        id_text_rus = cursor.fetchone()[0]

        text_it = row['Пословица_итальянская']
        
        cursor.execute("""
            INSERT INTO "Итальянские_пословицы" ("Текст_пословицыИт")
            VALUES (%s)
            RETURNING "idPh_it";
        """, (text_it.replace("'", "''"),))
        id_text_it = cursor.fetchone()[0]

        theme = row['Тематика']
        
        cursor.execute("""
            INSERT INTO "Тематика" ("idPh_ru", "idPh_it", "Тема")
            VALUES (%s, %s, %s);
        """, (id_text_rus, id_text_it, theme))
# закончили их заполнять

# заполняем Слов_ит, Ит_морф
        print('Заполняем...')
        #токенизация, лемматизация, pos с помощью stanza
        text_processed = re.sub(r'[^\w\s]', '', text_it)
        doc = nlp(text_processed.lower())
        
        for sentence in doc.sentences:
            for word in sentence.words:
                
                # ит_морф (подумать еще)
                cursor.execute("""
                    INSERT INTO "Ит_морф" ("Ит_лемма", "Часть_речиИт")
                    VALUES (%s, %s)
                    RETURNING "id_morf";
                """, (word.lemma, word.pos))
                #print(word.text, word.lemma, word.pos)
                id_morf_it = cursor.fetchone()[0]
                
                # слов_ит
                cursor.execute("""
                    INSERT INTO "Слов_ит" ("Словоформа_ит", "Лемма_ит", "idPh_it")
                    VALUES (%s, %s, %s);
                """, (word.text, id_morf_it, id_text_it))
# закончили заполнять

# заполняем Слов_рус, Рус_морф (тоже подумать еще)
        print('Заполняем...')
        
        text_processed = re.sub(r'[^\w\s]', '', text_rus)
        doc = Doc(text_processed.lower())
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        
        for token in doc.tokens:
            token.lemmatize(morph_vocab)
            word_rus = token.text
            lem_word_rus = token.lemma
            pos_word_rus = token.pos
            
            if dict_rus.get(pos_word_rus, False):
                pos_word_rus = dict_rus[pos_word_rus]
            
            cursor.execute("""
                INSERT INTO "Рус_морф" ("Часть_речиРус", "Рус_лемма")
                VALUES (%s, %s)
                RETURNING "id_morf";
            """, (pos_word_rus, lem_word_rus))
            
            id_morf_rus = cursor.fetchone()[0]
            
            
            cursor.execute("""
                INSERT INTO "Слов_рус" ("idPh_ru", "Словоформа_рус", "Лемма_рус")
                VALUES (%s, %s, %s);
            """, (id_text_rus, word_rus, id_morf_rus))

    conn.commit()
    print("Hurraaa")

except Exception as e:
    print("Error:", e)
finally:
    if conn:
        cursor.close()
        conn.close()


