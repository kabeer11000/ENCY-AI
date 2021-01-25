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
	for word in doc.split():
		if len(word)>3:
			definition, lang = get_def(word)
			wikipedia.set_lang(lang) 
			recommended_articles = wikipedia.search(word)
			get_first = recommended_articles[0]
			url = 'https://' + lang + '.wikipedia.org/wiki/' + get_first
			scrapped_data = data_scrapping(url)
			if "error" in scrapped_data:
				return {"error": "Website does not allow scrapping"}
			#print(scrapped_data["output"])
			output = prediction(scrapped_data["output"], 3)
			keywords = word_extraction(str(output), lang)
			#recommended_articles = search_on_wikipedia(keywords)

			out[word] = {
					"definition": definition,
					"output": output,
					"keywords": keywords,
					"recommended_articles": recommended_articles
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


@app.route('/summary', methods=['GET', 'POST'])
def summary():
	if not request.json:
		return { "error": "No json body found in request" }

	if "text" not in request.json:
		return { "error": "field text not found. Expected string" }

	length = 5
	if "length" in request.json:
		length = request.json['length']

	doc = request.json['text']
	
	output = prediction(doc, length)
	lang = get_lang(output)
	wikipedia.set_lang(lang) 
	keywords = word_extraction(str(output), lang) # TODO : get language
	recommended_articles = search_on_wikipedia(keywords)

	out = {
			"output": output, 
			"keywords": keywords,
			"recommended_articles": recommended_articles
		  }
	return out


@app.route('/summarise-url')
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

	output = prediction(scrapped_data["output"], length) #length
	lang = get_lang(output)
	wikipedia.set_lang(lang) 
	keywords = word_extraction(str(output), lang) #TODO : get language
	recommended_articles = search_on_wikipedia(keywords)

	out = {
			"output": output, 
			"keywords": keywords,
			"recommended_articles": recommended_articles
		  }
	return out

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, port=80)
