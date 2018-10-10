#encoding: utf-8
import mikatools
import os
from uralicApi import __find_writable_folder, __model_base_folders, ModelNotFound
import sqlite3

semfi_urls = "https://mikakalevi.com/semfi/static/whereis.json"

__connections = {}

def supported_languages():
	urls = mikatools.download_json(semfi_urls)
	return urls.keys()

def download(lang):
	urls = mikatools.download_json(semfi_urls)
	if lang not in urls:
		raise "Language not supported. Currently supported languages " + ", ".join(urls.keys())
	save_to = os.path.join(os.path.join(__find_writable_folder(__model_base_folders()), lang), "sem.db")
	mikatools.download_file(urls[lang], save_to, True)

def __where_semfi(lang):
	folders = __model_base_folders()
	for folder in folders:
		try_file = os.path.join(os.path.join(folder, lang), "sem.db")
		e = os.path.exists(try_file)
		if e:
			return try_file
	raise ModelNotFound()

def __get_connection(lang):
	if lang in __connections:
		return __connections[lang]
	else:
		db_file = __where_semfi(lang)
		conn = sqlite3.connect(db_file)
		c = conn.cursor()
		__connections[lang] = c
		return c

def __column_headers(lang, table):
	if table == "words":
		hs = ["id", "word", "pos", "frequency", "relative_frequency"]
		if lang == "fin":
			hs.append("compund")
		else:
			hs.append("mwe")
	else:
		hs = ["word1", "word2", "relation", "frequency", "relative_frequency", "zscore"]
	return hs

def __add_titles(rows, lang, table):
	keys = __column_headers(lang, table)
	ret = []
	for row in rows:
		d = {}
		for i in range(len(row)):
			d[keys[i]] = row[i]
		ret.append(d)
	return ret

def __replace_by_word_object(word1, word2, relations, lang):
	c = __get_connection(lang)
	if word2 is not None:
		for relation in relations:
			relation["word1"] = word1
			relation["word2"] = word2
		return relations
	else:
		for relation in relations:
			relation["word1"] = word1
			relation["word2"] = get_word_by_id(relation["word2"], lang)
		return relations

def get_word(lemma, pos, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM words WHERE word="'+lemma+'" and pos="' + pos +'"')
	all_rows = c.fetchall()
	return __add_titles(all_rows, lang, "words")[0]

def get_word_by_id(id, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM words WHERE id="'+id+'"')
	all_rows = c.fetchall()
	return __add_titles(all_rows, lang, "words")[0]

def get_words(lemma, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM words WHERE word="'+lemma+'"')
	all_rows = c.fetchall()
	return __add_titles(all_rows, lang, "words")

def get_all_relations(word_object, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM relations WHERE word1="'+word_object["id"]+'"')
	all_rows = c.fetchall()
	all_rows = __add_titles(all_rows, lang, "relations")
	rows = __replace_by_word_object(word_object, None, all_rows, lang)
	return rows

def get_by_relation(word_object, relation, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM relations WHERE word1="'+word_object["id"]+'" and relation_name="' + relation +'"')
	all_rows = c.fetchall()
	all_rows = __add_titles(all_rows, lang, "relations")
	rows = __replace_by_word_object(word_object, None, all_rows, lang)
	return rows

def get_by_word(word_object1, word_object2, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM relations WHERE word1="'+word_object["id"]+'" and word2="' + word_object2["id"] +'"')
	all_rows = c.fetchall()
	all_rows = __add_titles(all_rows, lang, "relations")
	rows = __replace_by_word_object(word_object1, word_object2, all_rows, lang)
	return rows

def get_by_word_and_relation(word_object1, word_object2, relation, lang):
	c = __get_connection(lang)
	c.execute('SELECT * FROM relations WHERE word1="'+word_object["id"]+'" and word2="' + word_object2["id"] +'" and relation_name="' + relation +'"')
	all_rows = c.fetchall()
	all_rows = __add_titles(all_rows, lang, "relations")
	rows = __replace_by_word_object(word_object1, word_object2, all_rows, lang)
	return rows
