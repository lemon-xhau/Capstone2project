import gensim
import pickle
import numpy as np
from pyvi import ViTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn import preprocessing
from keras.models import model_from_json

model_path = '/content/drive/MyDrive/Capstone 2 - AVTS/Project/TextSummarization/model/'
data_path = '/content/drive/MyDrive/Capstone 2 - AVTS/Project/TextSummarization/data/'

tfidf_vect = pickle.load(open(model_path+"tfidf_vectorizer.pickle", "rb"))
svd = pickle.load(open(model_path+"svd_selector.pickle", "rb"))

with open(model_path+'model.json', 'r') as json_file:
	loaded_model_json = json_file.read()


def preprocess(doc):
    lines = gensim.utils.simple_preprocess(doc)
    lines = ' '.join(lines)
    lines = ViTokenizer.tokenize(lines)
    with open(data_path+'vietnamese-stopwords-dash.txt', 'r') as f:
        stopwords = set([w.strip() for w in f.readlines()])
    try:
        split_words =  [x.strip('0123456789%@$.,=+-!;/()*"&^:#|\n\t\'').lower() for x in lines.split()]
    except TypeError:
        split_words =  []
    lines = ' '.join([word for word in split_words if word not in stopwords])

    x = [lines]
    return x

def normalize_result(raw_result):
    raw_results = ["Chinh tri Xa hoi", "Doi song", "Vi tinh", 
                   "Khoa hoc", "Kinh doanh", "Phap luat", "Suc khoe", "The gioi", "The thao", "Van hoa"]
    final_results = ["Chính trị - Xã hội", "Đời sống", "Công nghệ", 
                     "Khoa học", "Kinh doanh", "Pháp luật", "Sức khỏe", "Thế giới", "Thể thao", "Văn hóa"]

    index = [i for i, s in enumerate(raw_results) if raw_result in s][0]

    return final_results[index]

def predict_topic(data):
    data = preprocess(data)
    encoder = preprocessing.LabelEncoder()
    encoder.classes_ = np.load(model_path+'classes.npy')
    tfidf_x = tfidf_vect.transform(data)
    tfidf_x_svd = svd.transform(tfidf_x)
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(model_path+"model.h5")
    predict = encoder.inverse_transform([np.argmax(loaded_model.predict(np.array(tfidf_x_svd))[0])])[0]
    return normalize_result(predict) 




