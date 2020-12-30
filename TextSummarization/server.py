import os, sys
import formatSent
from fastapi import FastAPI, Request, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from typing import List
from fastapi.logger import logger
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings, BaseModel
from fastapi.staticfiles import StaticFiles
from summarizer import Summarizer
from summarizer2.summarize import summarize as Summarizer2
from summarizer.sentence_handler import SentenceHandler
from nltk import tokenize
import nltk
from utilities import is_link, get_text_from_link
from topic_classifier import predict_topic
nltk.download('punkt')


#!pip -q install pyngrok
#!USE_NGROK=True uvicorn server:app

# class Settings(BaseSettings):
#     BASE_URL = "http://localhost:8000"
#     USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"

# settings = Settings()

# Initialize the FastAPI app for a simple web server
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory = 'templates')

class Parser(object):

    def __init__(self, raw_text: str):
        self.all_data = raw_text.split('\n')

    def __isint(self, v) -> bool:
        try:
            int(v)
            return True
        except:
            return False

    def __should_skip(self, v) -> bool:
        return self.__isint(v) or v == '\n' or '-->' in v

    def __process_sentences(self, v) -> List[str]:
        sentence = tokenize.sent_tokenize(v)
        return sentence

    def save_data(self, save_path, sentences) -> None:
        with open(save_path, 'w') as f:
            for sentence in sentences:
                f.write("%s\n" % sentence)

    def run(self) -> List[str]:
        total: str = ''
        for data in self.all_data:
            if not self.__should_skip(data):
                cleaned = data.replace('&gt;', '').replace('\n', '').strip()
                if cleaned:
                    total += ' ' + cleaned
        sentences = self.__process_sentences(total)
        return sentences

    def convert_to_paragraphs(self) -> str:
        sentences: List[str] = self.run()
        return ' '.join([sentence.strip() for sentence in sentences]).strip()


@app.get("/", response_class = HTMLResponse)
def root(request: Request):
	return templates.TemplateResponse("capstone2.html", {"request": request})

@app.post('/')
def summarize(request: Request, textuser: str = Form(...), num_sentences: int = Form(...)):
    textuser = textuser.strip()
    pt = ""
    title = ""
    summary = ""
    summary2 =""
    summary3 = ""
    if is_link(textuser) is True:
        data, title = get_text_from_link(textuser)
    else:
        data = textuser
    try:
        if data is not None and len(data) != 0:
            data = formatSent.clean_tone(data)
            parsed = Parser(data).convert_to_paragraphs()
            model = Summarizer(hidden = -2)
            pt = predict_topic(parsed)
            print(pt)
            sh = SentenceHandler()
            length = sh.process(parsed)
            nums_k  = len(length)
            if num_sentences != 0 and num_sentences < nums_k:
                summary = model(parsed, num_sentences = num_sentences)
                #sumbasic algorithm
                summary2 = Summarizer2(parsed, sentences_count = num_sentences, sum_index= 1)
                #textrank algorithm
                summary3 = Summarizer2(parsed, sentences_count = num_sentences, sum_index= 0)
            else:
                print(nums_k)
                if (nums_k) > 10:
                    ratio = 0.2
                    k = int(ratio*nums_k)
                elif 1 < nums_k <= 10:
                    ratio = 0.4
                    k = int(ratio*nums_k)
                else:
                    ratio = 1  
                    k = 1 
                print(k)   
                #phobert model
                summary = model(parsed, num_sentences = k)
                #sumbasic algorithm
                summary2 = Summarizer2(parsed, sentences_count = k, sum_index= 1)
                #textrank algorithm
                summary3 = Summarizer2(parsed, sentences_count = k, sum_index= 0)

            summary = summary.replace('_',' ')
            if title != "":
                summary = title.upper() + "\n" + summary
                summary2 = title.upper() + "\n" + summary2
                summary3 = title.upper() + "\n" + summary3
        else:
            summary = "Can get summarize! please try with text or another url!"
    except:
        summary = "Can get summarize! please try with text or another url!"

    return templates.TemplateResponse("capstone2.html", context = {"request": request, "result": summary, "result2": summary2, "result3": summary3, "textinput": parsed, "predicttopic": pt})


if __name__ == "__main__":
    import nest_asyncio
    from pyngrok import ngrok
    import uvicorn

    ngrok_tunnel = ngrok.connect(8000)
    print('Public URL:', ngrok_tunnel.public_url)
    nest_asyncio.apply()
    uvicorn.run(app, port=8000)