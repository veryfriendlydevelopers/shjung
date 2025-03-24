import pandas as pd
import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

print("📂 현재 경로:", os.getcwd())

# 1. 데이터 불러오기
# df = pd.read_csv('./플레저_result3.csv', encoding='utf-8')
df = pd.read_csv(r'./프로젝트/플레저_result3.csv', encoding='cp949')

print(df.head())   # 데이터 확인
# 2. 텍스트 & 라벨 추출
texts = df['내용'].astype(str)   # 텍스트 칼럼명에 맞게 수정하세요
labels = df['판별 결과']             # 광고성: 1, 일반 글: 0

# 3. 한글 정제 함수
def clean_text(text):
    text = re.sub(r'[^가-힣0-9a-zA-Z\s]', '', text)  # 한글, 영문, 숫자만
    return text.strip()

texts = texts.apply(clean_text)

# 4. 토큰화
tokenizer = Tokenizer(num_words=10000, oov_token='<OOV>')
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)

# 5. 시퀀스 패딩
max_len = 100
padded = pad_sequences(sequences, maxlen=max_len, padding='post')

# 6. 훈련/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(
    padded, labels, test_size=0.2, random_state=42)

# 7. LSTM 모델 구성
model = Sequential([
    Embedding(input_dim=10000, output_dim=128, input_length=max_len),
    LSTM(64, return_sequences=False),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# 8. 모델 학습
history = model.fit(X_train, y_train, epochs=5, batch_size=64,
                    validation_split=0.2, verbose=1)

# 9. 평가
loss, acc = model.evaluate(X_test, y_test)
print(f'\n✅ Test Accuracy: {acc:.4f}')

# 10. 예측 결과 출력
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("\n📊 분류 결과:")
print(classification_report(y_test, y_pred))
