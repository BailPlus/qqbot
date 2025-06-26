import jieba
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# 加载模型
with open('model.pkl', 'rb') as file:
    model: MultinomialNB = pickle.load(file)
def tokenizer(text):
    return list(jieba.cut(text))
with open('vectorizer.pkl', 'rb') as file:
    vectorizer: CountVectorizer = pickle.load(file)
    jieba #type: ignore # 用于使编辑器认为已经使用了jieba

# 读取数据
def load_data(data: str):
    return vectorizer.transform([data])

def predict(text: str) -> bool:
    return bool(
        model.predict(
            load_data(text)
        )
    )

def test():
    print(
        predict(
            input()
        )
    )

if __name__ == '__main__':
    test()
