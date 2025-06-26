import pandas as pd
import jieba
import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 数据加载
data = pd.read_csv('ads_dataset.csv')

# 自定义 tokenizer
def tokenizer(text):
    return list(jieba.cut(text))
vectorizer = TfidfVectorizer(tokenizer=tokenizer)

# 向量化
X_vec = vectorizer.fit_transform(data['text'])
y = data['label']

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.00000001)#0.2)

# 模型
model = MultinomialNB()
model.fit(X_train, y_train)

# 测试
print("准确率:", model.score(X_test, y_test))
print(classification_report(y_test, model.predict(X_test)))

# 保存模型
pickle.dump(model, open('model.pkl', 'wb'))
pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))
print('模型保存成功')
