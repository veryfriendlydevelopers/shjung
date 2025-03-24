import pandas as pd
import numpy as np
import re
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("📂 현재 경로:", os.getcwd())

# 1. 데이터 불러오기
df = pd.read_csv(r'./프로젝트/플레저_result3.csv', encoding='cp949')
print(df.head())

# 2. 텍스트 & 라벨 추출
texts = df['Reviews'].astype(str)
labels = df['label']

# 3. 한글 정제 함수
def clean_text(text):
    text = re.sub(r'[^가-힣0-9a-zA-Z\s]', '', text)
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

# 7. 모델 존재 여부 확인 후 분기
model_path = 'lstm_model.h5'
if os.path.exists(model_path):
    model = load_model(model_path)
    print("✅ 저장된 모델을 불러왔습니다.")
else:
    # 8. LSTM 모델 구성
    model = Sequential([
        Embedding(input_dim=10000, output_dim=128, input_length=max_len),
        LSTM(64, return_sequences=False),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # 9. 모델 학습
    history = model.fit(X_train, y_train, epochs=5, batch_size=64,
                        validation_split=0.2, verbose=1)

    # 10. 저장
    model.save(model_path)
    print("💾 모델이 저장되었습니다.")

# 11. 평가
loss, acc = model.evaluate(X_test, y_test)
print(f'\n✅ Test Accuracy: {acc:.4f}')

# 12. 예측
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("\n📊 분류 결과:")
print(classification_report(y_test, y_pred))
