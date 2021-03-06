import wikipedia
from googletrans import Translator
# import boto3

from flask import request, Flask
app = Flask(__name__)

from AI.test import prediction
from AI.word_extraction import word_extraction
from AI.wiki import search_on_wikipedia
from AI.get_def import get_def
from scrapper.data_scrapper import data_scrapping
from va.chatter import chatter

"""
BUCKET_NAME = "ency-ai"
MODEL_FILE_NAME = "distilbert.pt"
"""
def get_lang(g_words):
	translator = Translator()
	word = translator.translate(g_words, dest='en')
	return str(word.src)
#test
'''
@app.route('/suggest-articles', methods=['GET', 'POST'])
def get_ka():
	if not request.json:
		return { "error": "No json body found in request" }

	if "text" not in request.json:
		return { "error": "field text not found. Expected string" }

	doc = request.json['text']

	lang = get_lang(doc)
	wikipedia.set_lang(lang) 
	keywords = word_extraction(str(doc), lang) # TODO : get language
	recommended_articles = search_on_wikipedia(keywords, lang)

	out = {
			"keywords": keywords,
			"recommended_articles": recommended_articles
		  }
	return out
'''

@app.route('/ai-tips', methods=['GET', 'POST'])
def aiTips():
	if not request.json:
		return { "error": "No json body found in request" }
	if "word" not in request.json:
		return { "error": "field text not found. Expected string" }

	doc = request.json['word']
	doc = str(doc)
	doc = doc.replace('_', ' ')
	out = {}
	word = doc
	if len(word.split())==1:
		try:
			definition, lang = get_def(word)
			wikipedia.set_lang(lang) 
		except:
			definition = ""
			lang = get_lang(word)
		out["definition"] = definition
	else:
		lang = get_lang(word)

	recommended_articles = wikipedia.search(word)
	websites_url = []
	for c in recommended_articles:
		article = c
		article = article.replace(' ', '_')
		tmp = "https://" + lang + '.wikipedia.org/wiki/' + article
		websites_url.append(tmp)

	#print(scrapped_data["output"])
	try:
		k = []
		get_first = recommended_articles[0]
		url = 'https://' + lang + '.wikipedia.org/wiki/' + get_first
		#print(url)
		scrapped_data = data_scrapping(url)
		output = prediction(scrapped_data["output"], 3)
		if "error" in scrapped_data:
			return {"error": "Website does not allow scrapping"}
		keywords = word_extraction(str(output), lang)
		for i in keywords:
			k.append(i[1])
	except:
		output = None
		keywords = []
		recommended_articles = []
	#recommended_articles = search_on_wikipedia(keywords)

	out[word] = {
			"output": output,
			"keywords": k,
			"recommended_articles": websites_url
		}
	return out


@app.route('/chatter', methods=['GET', 'POST'])
def chatterReq():
	if not request.json:
		return { "error": "No json body found in request" }

	if "text" not in request.json:
		return { "error": "field text not found. Expected string" }

	doc = request.json['text']
	
	output = chatter(doc)
	out = {
			"output": output
		  }
	return out


@app.route('/summarize-text', methods=['GET', 'POST'])
def summary():
	if not request.json:
		return { "error": "No json body found in request" }

	if "text" not in request.json:
		return { "error": "field text not found. Expected string" }

	length = 5
	if "length" in request.json:
		length = request.json['length']

	doc = request.json['text']
	
	k = []
	output = prediction(doc, length)
	lang = get_lang(output[0])
	wikipedia.set_lang(lang) 
	keywords = word_extraction(str(output), lang) # TODO : get language
	for i in keywords:
		k.append(i[1])
	recommended_articles = search_on_wikipedia(keywords, lang)

	out = {
			"output": output, 
			"keywords": k,
			"recommended_articles": recommended_articles
		  }
	return out


@app.route('/summarize-url')
def summarise_url():
	if not request.json:
		return { "error": "No json body found in request" }
	
	if "url" not in request.json:
		return { "error": "field url not found. Expected string" }

	url = request.json["url"]

	length = 5
	if "length" in request.json:
		length = request.json['length']

	scrapped_data = data_scrapping(url)
	if "error" in scrapped_data:
		return {"error": "Website does not allow scrapping"}

	k = []
	output = prediction(scrapped_data["output"], length) #length
	lang = get_lang(output[0])
	wikipedia.set_lang(lang) 
	keywords = word_extraction(str(output), lang) #TODO : get language
	for i in keywords:
		k.append(i[1])
	recommended_articles = search_on_wikipedia(keywords, lang)

	out = {
			"output": output, 
			"keywords": k,
			"recommended_articles": recommended_articles
		  }
	return out

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, port=80)
