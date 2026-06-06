from flask import Flask, render_template, request
import psycopg2
import pandas as pd

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname='rus_it',
        user='user',
        password='123',
        host='db',
        port=5432
    )
    return conn


@app.route('/')
def home():
    return render_template('home.html')

# Подкорпус русских пословиц
@app.route('/search_rus', methods=['GET', 'POST'])
def search_rus():
    results = {'sentence': [], 'lemma': [], 'pos_tag': [], 
    'topic': [], 'ipm': [], 'instance': [], 'total_words': []}
    
    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        search_type = request.form.get('search_type', '').strip()
        pos = request.form.get('pos', '').strip()
        topic = request.form.get('topic', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        if topic:
            
            if pos:
            
                sql = f"""SELECT DISTINCT "Текст_пословицыРус", "Словоформа_рус" 
                FROM "Русские_пословицы" w1 
                JOIN "Тематика" w2 
                ON w1."idPh_ru" = w2."idPh_ru" 
                JOIN "Слов_рус" w3 
                ON w1."idPh_ru" = w3."idPh_ru" 
                JOIN "Рус_морф" w4 
                ON w3."Лемма_рус" = w4."id_morf" 
                WHERE w2."Тема" = '{topic}' AND w4."Часть_речиРус" = '{pos}';"""
                df = pd.read_sql_query(sql, conn)
                results['sentence'].extend(df["Текст_пословицыРус"])
                results['lemma'].extend(df["Словоформа_рус"])
                
                
            elif word:
                if search_type == 'lemma':
                    
                    sql = f"""SELECT DISTINCT "Текст_пословицыРус", "Словоформа_рус" 
                    FROM "Русские_пословицы" w1 
                    JOIN "Тематика" w2 
                    ON w1."idPh_ru" = w2."idPh_ru" 
                    JOIN "Слов_рус" w3 
                    ON w1."idPh_ru" = w3."idPh_ru" 
                    JOIN "Рус_морф" w4 
                    ON w3."Лемма_рус" = w4."id_morf" 
                    WHERE w2."Тема" = '{topic}' AND w4."Рус_лемма" = '{word}';"""
                    df = pd.read_sql_query(sql, conn)
                    results['sentence'].extend(df["Текст_пословицыРус"])
                    results['lemma'].extend(df["Словоформа_рус"])
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус" w1
                    JOIN "Рус_морф" w2 ON w1."Лемма_рус" = w2."id_morf"
                    JOIN "Русские_пословицы" w3 ON w3."idPh_ru" = w1."idPh_ru"
                    JOIN "Тематика" w4 ON w4."idPh_ru" = w3."idPh_ru"
                    WHERE w2."Рус_лемма" = %s AND w4."Тема" = %s;""", (word, topic))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус" w3
                    JOIN "Тематика" w4 ON w4."idPh_ru" = w3."idPh_ru"
                    WHERE w4."Тема" = %s;""", (topic,))
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0]
                    / results['total_words'][0][0] * 1000000, 2)
                    
                elif search_type == 'wordform':
                    
                    cursor.execute("""SELECT DISTINCT "Текст_пословицыРус"
                    FROM "Русские_пословицы" w1
                    JOIN "Тематика" w2
                    ON w1."idPh_ru" = w2."idPh_ru"
                    JOIN "Слов_рус" w3
                    ON w1."idPh_ru" = w3."idPh_ru"
                    JOIN "Рус_морф" w4
                    ON w3."Лемма_рус" = w4."id_morf" 
                    WHERE w2."Тема" = %s AND w3."Словоформа_рус" = %s;""", (topic, word))
                    results['sentence'] = cursor.fetchall()
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус" w1
                    JOIN "Русские_пословицы" w3 ON w3."idPh_ru" = w1."idPh_ru"
                    JOIN "Тематика" w4 ON w4."idPh_ru" = w3."idPh_ru"
                    WHERE w1."Словоформа_рус" = %s AND w4."Тема" = %s;""", (word, topic))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус" w3
                    JOIN "Тематика" w4 ON w4."idPh_ru" = w3."idPh_ru"
                    WHERE w4."Тема" = %s;""", (topic,))
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
            else:
                
                cursor.execute("""SELECT DISTINCT "Текст_пословицыРус"
                FROM "Русские_пословицы" w1
                JOIN "Тематика" w2
                ON w1."idPh_ru" = w2."idPh_ru"
                WHERE w2."Тема" = %s;""", (topic,))
                results['sentence'] = cursor.fetchall()
            
        else:
            
            if pos:
                
                sql = f"""SELECT DISTINCT "Текст_пословицыРус", "Словоформа_рус" 
                FROM "Русские_пословицы" w1 
                JOIN "Слов_рус" w3 
                ON w1."idPh_ru" = w3."idPh_ru" 
                JOIN "Рус_морф" w4 
                ON w3."Лемма_рус" = w4."id_morf" 
                WHERE w4."Часть_речиРус" = '{pos}';"""
                df = pd.read_sql_query(sql, conn)
                results['sentence'].extend(df["Текст_пословицыРус"])
                results['lemma'].extend(df["Словоформа_рус"])
                
            elif word:
                if search_type == 'lemma':
                    
                    sql = f"""SELECT DISTINCT "Текст_пословицыРус", "Словоформа_рус" 
                    FROM "Русские_пословицы" w1 
                    JOIN "Слов_рус" w3 
                    ON w1."idPh_ru" = w3."idPh_ru" 
                    JOIN "Рус_морф" w4 
                    ON w3."Лемма_рус" = w4."id_morf" 
                    WHERE w4."Рус_лемма" = '{word}';"""
                    df = pd.read_sql_query(sql, conn)
                    results['sentence'].extend(df["Текст_пословицыРус"])
                    results['lemma'].extend(df["Словоформа_рус"])
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус" w1
                    JOIN "Рус_морф" w2 ON w1."Лемма_рус" = w2."id_morf"
                    WHERE w2."Рус_лемма" = %s;""", (word,))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус";""")
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
                    
                elif search_type == 'wordform':
                    
                    cursor.execute("""SELECT DISTINCT "Текст_пословицыРус" 
                    FROM "Русские_пословицы" w1
                    JOIN "Слов_рус" w3 ON w1."idPh_ru" = w3."idPh_ru"
                    JOIN "Рус_морф" w4 ON w3."Лемма_рус" = w4."id_morf" 
                    WHERE w3."Словоформа_рус" = %s;""", (word,))
                    results['sentence'] = cursor.fetchall()
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус" w1
                    JOIN "Русские_пословицы" w3 ON w3."idPh_ru" = w1."idPh_ru"
                    WHERE w1."Словоформа_рус" = %s;""", (word,))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_рус";""")
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
                    
            else:
            
                sql = """SELECT DISTINCT "Текст_пословицыРус", "Тема" 
                FROM "Русские_пословицы" w1 
                JOIN "Тематика" w2 
                ON w1."idPh_ru" = w2."idPh_ru";"""
                df = pd.read_sql_query(sql, conn)
                results['sentence'].extend(df["Текст_пословицыРус"])
                results['topic'].extend(df["Тема"])
            
            
       
    return render_template('search_rus.html', results=results)        
            

# Подкорпус итальянских пословиц
@app.route('/search_it', methods=['GET', 'POST'])
def search_it():
    results = {'sentence': [], 'lemma': [], 'pos_tag': [], 'topic': [], 'ipm': [], 
    'instance': [], 'total_words': []}
    
    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        search_type = request.form.get('search_type', '').strip()
        pos = request.form.get('pos', '').strip()
        topic = request.form.get('topic', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        if topic:
            
            if pos:
            
                sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Словоформа_ит" 
                FROM "Итальянские_пословицы" w1 
                JOIN "Тематика" w2 
                ON w1."idPh_it" = w2."idPh_it" 
                JOIN "Слов_ит" w3 
                ON w1."idPh_it" = w3."idPh_it" 
                JOIN "Ит_морф" w4 
                ON w3."Лемма_ит" = w4."id_morf" 
                WHERE w2."Тема" = '{topic}' AND w4."Часть_речиИт" = '{pos}';"""
                df = pd.read_sql_query(sql, conn)
                results['sentence'].extend(df["Текст_пословицыИт"])
                results['lemma'].extend(df["Словоформа_ит"])
                
                
            elif word:
                if search_type == 'lemma':
                    
                    sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Словоформа_ит" 
                    FROM "Итальянские_пословицы" w1 
                    JOIN "Тематика" w2 
                    ON w1."idPh_it" = w2."idPh_it" 
                    JOIN "Слов_ит" w3 
                    ON w1."idPh_it" = w3."idPh_it" 
                    JOIN "Ит_морф" w4 
                    ON w3."Лемма_ит" = w4."id_morf" 
                    WHERE w2."Тема" = '{topic}' AND w4."Ит_лемма" = '{word}';"""
                    df = pd.read_sql_query(sql, conn)
                    results['sentence'].extend(df["Текст_пословицыИт"])
                    results['lemma'].extend(df["Словоформа_ит"])
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит" w1
                    JOIN "Ит_морф" w2 ON w1."Лемма_ит" = w2."id_morf"
                    JOIN "Итальянские_пословицы" w3 ON w3."idPh_it" = w1."idPh_it"
                    JOIN "Тематика" w4 ON w4."idPh_it" = w3."idPh_it"
                    WHERE w2."Ит_лемма" = %s AND w4."Тема" = %s;""", (word, topic))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит" w3
                    JOIN "Тематика" w4 ON w4."idPh_it" = w3."idPh_it"
                    WHERE w4."Тема" = %s;""", (topic,))
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
                    
                elif search_type == 'wordform':
                    
                    cursor.execute("""SELECT DISTINCT "Текст_пословицыИт"
                    FROM "Итальянские_пословицы" w1
                    JOIN "Тематика" w2
                    ON w1."idPh_it" = w2."idPh_it"
                    JOIN "Слов_ит" w3
                    ON w1."idPh_it" = w3."idPh_it"
                    JOIN "Ит_морф" w4
                    ON w3."Лемма_ит" = w4."id_morf" 
                    WHERE w2."Тема" = %s AND w3."Словоформа_ит" = %s;""", (topic, word))
                    results['sentence'] = cursor.fetchall()
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит" w1
                    JOIN "Итальянские_пословицы" w3 ON w3."idPh_it" = w1."idPh_it"
                    JOIN "Тематика" w4 ON w4."idPh_it" = w3."idPh_it"
                    WHERE w1."Словоформа_ит" = %s AND w4."Тема" = %s;""", (word, topic))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит" w3
                    JOIN "Тематика" w4 ON w4."idPh_it" = w3."idPh_it"
                    WHERE w4."Тема" = %s;""", (topic,))
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
                    
            else:
                
                cursor.execute("""SELECT DISTINCT "Текст_пословицыИт"
                FROM "Итальянские_пословицы" w1
                JOIN "Тематика" w2
                ON w1."idPh_it" = w2."idPh_it"
                WHERE w2."Тема" = %s;""", (topic,))
                results['sentence'] = cursor.fetchall()
            
        else:
            
            if pos:
                
                sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Словоформа_ит" 
                FROM "Итальянские_пословицы" w1 
                JOIN "Слов_ит" w3 
                ON w1."idPh_it" = w3."idPh_it" 
                JOIN "Ит_морф" w4 
                ON w3."Лемма_ит" = w4."id_morf" 
                WHERE w4."Часть_речиИт" = '{pos}';"""
                df = pd.read_sql_query(sql, conn)
                results['sentence'].extend(df["Текст_пословицыИт"])
                results['lemma'].extend(df["Словоформа_ит"])
                
            elif word:
                if search_type == 'lemma':
                    
                    sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Словоформа_ит" 
                    FROM "Итальянские_пословицы" w1 
                    JOIN "Слов_ит" w3 
                    ON w1."idPh_it" = w3."idPh_it" 
                    JOIN "Ит_морф" w4 
                    ON w3."Лемма_ит" = w4."id_morf" 
                    WHERE w4."Ит_лемма" = '{word}';"""
                    df = pd.read_sql_query(sql, conn)
                    results['sentence'].extend(df["Текст_пословицыИт"])
                    results['lemma'].extend(df["Словоформа_ит"])
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит" w1
                    JOIN "Ит_морф" w2 ON w1."Лемма_ит" = w2."id_morf"
                    WHERE w2."Ит_лемма" = %s;""", (word,))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит";""")
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
                    
                elif search_type == 'wordform':
                    
                    cursor.execute("""SELECT DISTINCT "Текст_пословицыИт" 
                    FROM "Итальянские_пословицы" w1
                    JOIN "Слов_ит" w3 ON w1."idPh_it" = w3."idPh_it"
                    JOIN "Ит_морф" w4 ON w3."Лемма_ит" = w4."id_morf" 
                    WHERE w3."Словоформа_ит" = %s;""", (word,))
                    results['sentence'] = cursor.fetchall()
                    
                    #для IPM, ipm, instance, total_words
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит" w1
                    WHERE w1."Словоформа_ит" = %s;""", (word,))
                    results['instance'] = cursor.fetchall()
                    
                    cursor.execute("""SELECT COUNT(*) FROM "Слов_ит";""")
                    results['total_words'] = cursor.fetchall()
                    
                    results['ipm'] = round(results['instance'][0][0] 
                    / results['total_words'][0][0] * 1000000, 2)
                    
            else:
            
                sql = """SELECT DISTINCT "Текст_пословицыИт", "Тема" 
                FROM "Итальянские_пословицы" w1 
                JOIN "Тематика" w2 
                ON w1."idPh_it" = w2."idPh_it";"""
                df = pd.read_sql_query(sql, conn)
                results['sentence'].extend(df["Текст_пословицыИт"])
                results['topic'].extend(df["Тема"])
    
    return render_template('search_it.html', results=results)  


# Сравнительный корпус
@app.route('/search_both', methods=['GET', 'POST'])
def search_both():
    results = {'lemma': [], 'topic': [], 'it_text': [], 'rus_text': []}
    
    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        search_type = request.form.get('search_type', '').strip()
        topic = request.form.get('topic', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if topic:
        
            sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Текст_пословицыРус", "Тема"
            FROM "Итальянские_пословицы" w1
            JOIN "Тематика" w2
            ON w1."idPh_it" = w2."idPh_it" 
            JOIN "Русские_пословицы" w3
            ON w3."idPh_ru" = w2."idPh_ru"
            WHERE w2."Тема" = '{topic}';"""
            df = pd.read_sql_query(sql, conn)
            results['it_text'] = df['Текст_пословицыИт']
            results['rus_text'] = df['Текст_пословицыРус']
        
        else:
            
            if search_type == 'lemma':
                
                sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Текст_пословицыРус"
                FROM "Итальянские_пословицы" w1
                JOIN "Русские_пословицы" w3
                ON w1."idPh_it" = w3."idPh_ru"
                JOIN "Слов_ит" w2
                ON w2."idPh_it" = w1."idPh_it" 
                JOIN "Слов_рус" w4
                ON w3."idPh_ru" = w4."idPh_ru"
                JOIN "Ит_морф" w5
                ON w5."id_morf" = w2."Лемма_ит" 
                JOIN "Рус_морф" w6
                ON w6."id_morf" = w4."Лемма_рус" 
                WHERE w5."Ит_лемма"  = '{word}' OR 
                w6."Рус_лемма"  = '{word}';"""
                df = pd.read_sql_query(sql, conn)
                results['it_text'] = df['Текст_пословицыИт']
                results['rus_text'] = df['Текст_пословицыРус']
                
            elif search_type == 'wordform':
                
                sql = f"""SELECT DISTINCT "Текст_пословицыИт", "Текст_пословицыРус"
                FROM "Итальянские_пословицы" w1
                JOIN "Русские_пословицы" w3
                ON w1."idPh_it" = w3."idPh_ru"
                JOIN "Слов_ит" w2
                ON w2."idPh_it" = w1."idPh_it" 
                JOIN "Слов_рус" w4
                ON w3."idPh_ru" = w4."idPh_ru"
                WHERE w4."Словоформа_рус" = '{word}' OR 
                w2."Словоформа_ит" = '{word}';"""
                df = pd.read_sql_query(sql, conn)
                results['it_text'] = df['Текст_пословицыИт']
                results['rus_text'] = df['Текст_пословицыРус']
                
            
            else:
            
                sql = """SELECT DISTINCT "Текст_пословицыИт", "Текст_пословицыРус", "Тема" 
                FROM "Итальянские_пословицы" w1 
                JOIN "Тематика" w2 
                ON w1."idPh_it" = w2."idPh_it" 
                JOIN "Русские_пословицы" w3 
                ON w2."idPh_ru" = w3."idPh_ru";"""
                df = pd.read_sql_query(sql, conn)
                results['it_text'] = df['Текст_пословицыИт']
                results['rus_text'] = df['Текст_пословицыРус']
                results['topic'] = df['Тема']
    
    return render_template('search_both.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
