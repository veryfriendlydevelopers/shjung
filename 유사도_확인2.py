import pandas as pd
from sentence_transformers import SentenceTransformer, util

# ✅ SBERT 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ 광고성 문구 불러오기 (keywords.txt)
with open("./프로젝트/keywords.txt", "r", encoding="utf-8") as f:
    ad_keywords = [line.strip() for line in f.readlines() if line.strip()]  # 빈 줄 제거

# ✅ 리뷰 데이터 불러오기 (CSV 파일)
df = pd.read_csv("./프로젝트/gangnamunni_reviews.csv")  # 파일명을 본인 파일명으로 변경
if "내용" not in df.columns:
    raise ValueError("CSV 파일에 '내용' 컬럼이 필요합니다.")

# ✅ 리뷰 문장을 SBERT 벡터로 변환
df["embedding"] = df["내용"].apply(lambda x: model.encode(str(x), convert_to_tensor=True))

# ✅ 광고성 문구를 SBERT 벡터로 변환
ad_embeddings = [model.encode(keyword, convert_to_tensor=True) for keyword in ad_keywords]

# ✅ 유사도 비교 및 저장할 리스트
similarity_results = []

for _, row in df.iterrows():
    review_text = row["내용"]
    review_embedding = row["embedding"]

    max_similarity = 0
    most_similar_keyword = ""

    for keyword, ad_embedding in zip(ad_keywords, ad_embeddings):
        similarity = util.pytorch_cos_sim(review_embedding, ad_embedding).item()
        
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_keyword = keyword

    # ✅ 결과 저장 (유사도가 0.7 이상이면 광고성으로 간주)
    # 광고성 : 0, 정상 : 1
    similarity_results.append([review_text, most_similar_keyword, max_similarity, 0 if max_similarity >= 0.7 else 1]) 

# ✅ DataFrame으로 변환
result_df = pd.DataFrame(similarity_results, columns=["리뷰 문장", "가장 유사한 광고 키워드", "유사도", "판별 결과"])

# ✅ CSV 파일로 저장
result_df.to_csv("review_with_similarity.csv", index=False, encoding="utf-8-sig")

print("✅ 광고성 문구 유사도 분석 완료! 결과가 'review_with_similarity.csv' 파일에 저장되었습니다.")
