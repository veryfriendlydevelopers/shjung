#tensorflow 가상환경에서 
#pip install sentence_transformers 
from sentence_transformers import SentenceTransformer, util

# SBERT 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')

# 비교할 문장
sentence1 = "학생들은 시험을 준비하고 있다."
sentence2 = "시험을 준비 중인 학생들이 있다."

# 문장을 임베딩 벡터로 변환
embedding1 = model.encode(sentence1, convert_to_tensor=True)
embedding2 = model.encode(sentence2, convert_to_tensor=True)

# 코사인 유사도 계산
similarity = util.pytorch_cos_sim(embedding1, embedding2)

print(f"문장 유사도: {similarity.item():.4f}")