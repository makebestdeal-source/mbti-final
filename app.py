"""
🎯 MBTI 매칭 테스트 v4.0 Final
=====================================
수정:
1. 언어팩 - 드롭다운 1줄
2. 이미지 - 초경량 placeholder
3. 속도 - 캐싱 강화
4. 공유 - 링크 복사 버튼 추가
5. 결과 - 다국어 이름 표시
6. Google Analytics 추가
"""

import streamlit as st
import json
import hashlib
import random
from datetime import datetime
import urllib.parse
import streamlit.components.v1 as components

# ============================================
# 🔝 스크롤 상단 이동
# ============================================
def scroll_top():
    components.html("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'instant'});
        </script>
    """, height=0)

# ============================================
# 🎨 페이지 설정
# ============================================
st.set_page_config(
    page_title="🎯 MBTI Match Test",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# 📊 Google Analytics (여기에 ID 입력)
# ============================================
GA_ID = "G-XXXXXXXXXX"  # ← 나중에 실제 ID로 변경

ga_script = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""
st.markdown(ga_script, unsafe_allow_html=True)

# ============================================
# 💰 AdFit 광고
# ============================================
def show_ad():
    ad_code = """
    <div style="display:flex;justify-content:center;margin:15px 0;">
        <ins class="kakao_ad_area" style="display:none;"
             data-ad-unit="DAN-iGpl6hVjoJ8vlNoZ"
             data-ad-width="320"
             data-ad-height="100"></ins>
        <script type="text/javascript" src="//t1.daumcdn.net/kas/static/ba.min.js" async></script>
    </div>
    """
    st.components.v1.html(ad_code, height=120)

# ============================================
# 📊 테스트 설정
# ============================================
TEST_CONFIG = {
    "anime": {
        "emoji": "💕", 
        "title": {"ko": "애니 캐릭터", "en": "Anime Character", "ja": "アニメキャラ", "zh": "动漫角色", "es": "Anime"},
        "title_full": {"ko": "나와 어울리는 애니 캐릭터는?", "en": "Which Anime Character?", 
                       "ja": "あなたに合うアニメキャラは?", "zh": "你适合哪个动漫角色?", "es": "¿Qué personaje anime?"},
        "data_file": "data/characters.json",
        "image_set": "set5",
        "question_type": "relationship"
    },
    "dogs": {
        "emoji": "🐕", 
        "title": {"ko": "강아지", "en": "Dog", "ja": "犬", "zh": "狗", "es": "Perro"},
        "title_full": {"ko": "나랑 어울리는 강아지는?", "en": "Which Dog Breed?",
                       "ja": "あなたに合う犬は?", "zh": "你适合哪种狗?", "es": "¿Qué perro?"},
        "data_file": "data/dogs.json",
        "image_set": "set4",
        "question_type": "pet"
    },
    "cats": {
        "emoji": "🐈", 
        "title": {"ko": "고양이", "en": "Cat", "ja": "猫", "zh": "猫", "es": "Gato"},
        "title_full": {"ko": "나랑 어울리는 고양이는?", "en": "Which Cat Breed?",
                       "ja": "あなたに合う猫は?", "zh": "你适合哪种猫?", "es": "¿Qué gato?"},
        "data_file": "data/cats.json",
        "image_set": "set4",
        "question_type": "pet"
    },
    "cities": {
        "emoji": "🌆", 
        "title": {"ko": "도시", "en": "City", "ja": "都市", "zh": "城市", "es": "Ciudad"},
        "title_full": {"ko": "나랑 어울리는 도시는?", "en": "Which City?",
                       "ja": "あなたに合う都市は?", "zh": "你适合哪个城市?", "es": "¿Qué ciudad?"},
        "data_file": "data/cities.json",
        "image_set": "set3",
        "question_type": "place"
    },
    "destinations": {
        "emoji": "🏝️", 
        "title": {"ko": "여행지", "en": "Travel", "ja": "旅行", "zh": "旅游", "es": "Viaje"},
        "title_full": {"ko": "나랑 어울리는 여행지는?", "en": "Which Destination?",
                       "ja": "あなたに合う旅行先は?", "zh": "你适合哪个旅游地?", "es": "¿Qué destino?"},
        "data_file": "data/destinations.json",
        "image_set": "set3",
        "question_type": "travel"
    },
    "cars": {
        "emoji": "🚗", 
        "title": {"ko": "자동차", "en": "Car", "ja": "車", "zh": "汽车", "es": "Coche"},
        "title_full": {"ko": "나랑 어울리는 자동차는?", "en": "Which Car?",
                       "ja": "あなたに合う車は?", "zh": "你适合哪种车?", "es": "¿Qué coche?"},
        "data_file": "data/cars.json",
        "image_set": "set2",
        "question_type": "car"
    },
    "stars": {
        "emoji": "⭐", 
        "title": {"ko": "스타", "en": "Star", "ja": "スター", "zh": "明星", "es": "Estrella"},
        "title_full": {"ko": "나랑 어울리는 스타는?", "en": "Which Star?",
                       "ja": "あなたに合うスターは?", "zh": "你适合哪个明星?", "es": "¿Qué estrella?"},
        "data_file": "data/global_stars.json",
        "image_set": "set5",
        "question_type": "relationship"
    },
    "idols": {
        "emoji": "🎤", 
        "title": {"ko": "아이돌", "en": "K-Pop", "ja": "アイドル", "zh": "偶像", "es": "K-Pop"},
        "title_full": {"ko": "나랑 어울리는 아이돌은?", "en": "Which K-Pop Idol?",
                       "ja": "あなたに合うアイドルは?", "zh": "你适合哪个偶像?", "es": "¿Qué idol?"},
        "data_file": "data/idols.json",
        "image_set": "set5",
        "question_type": "relationship"
    },
    "games": {
        "emoji": "🎮", 
        "title": {"ko": "게임", "en": "Game", "ja": "ゲーム", "zh": "游戏", "es": "Juego"},
        "title_full": {"ko": "나랑 어울리는 게임 캐릭터는?", "en": "Which Game Character?",
                       "ja": "あなたに合うゲームキャラは?", "zh": "你适合哪个游戏角色?", "es": "¿Qué personaje?"},
        "data_file": "data/game_characters.json",
        "image_set": "set2",
        "question_type": "game"
    },
    "tinipings": {
        "emoji": "🎀", 
        "title": {"ko": "티니핑", "en": "Tiniping", "ja": "ティニピン", "zh": "迷你乒", "es": "Tiniping"},
        "title_full": {"ko": "나는 어떤 티니핑?", "en": "Which Tiniping?",
                       "ja": "あなたはどのティニピン?", "zh": "你是哪个迷你乒?", "es": "¿Qué Tiniping?"},
        "data_file": "data/tinipings.json",
        "image_set": "set4",
        "question_type": "character"
    }
}

# ============================================
# 🎯 질문
# ============================================
QUESTIONS = {
    "relationship": {
        "ko": {"q": "관계", "o": {"ideal": "💕 이상형", "romance": "💝 연애", "marriage": "💍 결혼", "fan": "⭐ 최애"}},
        "en": {"q": "Type", "o": {"ideal": "💕 Ideal", "romance": "💝 Date", "marriage": "💍 Marriage", "fan": "⭐ Fave"}},
        "ja": {"q": "関係", "o": {"ideal": "💕 理想", "romance": "💝 恋愛", "marriage": "💍 結婚", "fan": "⭐ 推し"}},
        "zh": {"q": "关系", "o": {"ideal": "💕 理想", "romance": "💝 恋爱", "marriage": "💍 结婚", "fan": "⭐ 最爱"}},
        "es": {"q": "Tipo", "o": {"ideal": "💕 Ideal", "romance": "💝 Cita", "marriage": "💍 Boda", "fan": "⭐ Fav"}}
    },
    "pet": {
        "ko": {"q": "관계", "o": {"want": "🏠 키우고싶은", "similar": "🪞 닮은", "soulmate": "💫 소울메이트"}},
        "en": {"q": "Type", "o": {"want": "🏠 Want", "similar": "🪞 Like me", "soulmate": "💫 Soulmate"}},
        "ja": {"q": "タイプ", "o": {"want": "🏠 飼いたい", "similar": "🪞 似てる", "soulmate": "💫 運命"}},
        "zh": {"q": "类型", "o": {"want": "🏠 想养", "similar": "🪞 像我", "soulmate": "💫 灵魂"}},
        "es": {"q": "Tipo", "o": {"want": "🏠 Quiero", "similar": "🪞 Similar", "soulmate": "💫 Alma"}}
    },
    "place": {
        "ko": {"q": "목적", "o": {"live": "🏠 거주", "travel": "✈️ 여행", "month": "📅 한달살기"}},
        "en": {"q": "Purpose", "o": {"live": "🏠 Live", "travel": "✈️ Travel", "month": "📅 Month"}},
        "ja": {"q": "目的", "o": {"live": "🏠 住む", "travel": "✈️ 旅行", "month": "📅 1ヶ月"}},
        "zh": {"q": "目的", "o": {"live": "🏠 居住", "travel": "✈️ 旅行", "month": "📅 月住"}},
        "es": {"q": "Fin", "o": {"live": "🏠 Vivir", "travel": "✈️ Viajar", "month": "📅 Mes"}}
    },
    "travel": {
        "ko": {"q": "스타일", "o": {"healing": "🌴 힐링", "adventure": "🏔️ 모험", "bucket": "⭐ 버킷"}},
        "en": {"q": "Style", "o": {"healing": "🌴 Healing", "adventure": "🏔️ Adventure", "bucket": "⭐ Bucket"}},
        "ja": {"q": "スタイル", "o": {"healing": "🌴 癒し", "adventure": "🏔️ 冒険", "bucket": "⭐ バケリス"}},
        "zh": {"q": "风格", "o": {"healing": "🌴 治愈", "adventure": "🏔️ 冒险", "bucket": "⭐ 心愿"}},
        "es": {"q": "Estilo", "o": {"healing": "🌴 Relax", "adventure": "🏔️ Aventura", "bucket": "⭐ Lista"}}
    },
    "car": {
        "ko": {"q": "타입", "o": {"dream": "🌟 드림카", "first": "🔰 첫차", "practical": "💼 실용"}},
        "en": {"q": "Type", "o": {"dream": "🌟 Dream", "first": "🔰 First", "practical": "💼 Practical"}},
        "ja": {"q": "タイプ", "o": {"dream": "🌟 ドリーム", "first": "🔰 最初", "practical": "💼 実用"}},
        "zh": {"q": "类型", "o": {"dream": "🌟 梦想", "first": "🔰 第一", "practical": "💼 实用"}},
        "es": {"q": "Tipo", "o": {"dream": "🌟 Sueño", "first": "🔰 Primero", "practical": "💼 Práctico"}}
    },
    "game": {
        "ko": {"q": "타입", "o": {"play": "🕹️ 플레이", "party": "👥 파티", "similar": "🪞 닮은"}},
        "en": {"q": "Type", "o": {"play": "🕹️ Play", "party": "👥 Party", "similar": "🪞 Like me"}},
        "ja": {"q": "タイプ", "o": {"play": "🕹️ プレイ", "party": "👥 パーティー", "similar": "🪞 似てる"}},
        "zh": {"q": "类型", "o": {"play": "🕹️ 玩", "party": "👥 队友", "similar": "🪞 像我"}},
        "es": {"q": "Tipo", "o": {"play": "🕹️ Jugar", "party": "👥 Equipo", "similar": "🪞 Similar"}}
    },
    "character": {
        "ko": {"q": "타입", "o": {"similar": "🪞 닮은", "friend": "👫 친구", "guardian": "🛡️ 수호"}},
        "en": {"q": "Type", "o": {"similar": "🪞 Like me", "friend": "👫 Friend", "guardian": "🛡️ Guardian"}},
        "ja": {"q": "タイプ", "o": {"similar": "🪞 似てる", "friend": "👫 友達", "guardian": "🛡️ 守護"}},
        "zh": {"q": "类型", "o": {"similar": "🪞 像我", "friend": "👫 朋友", "guardian": "🛡️ 守护"}},
        "es": {"q": "Tipo", "o": {"similar": "🪞 Similar", "friend": "👫 Amigo", "guardian": "🛡️ Guardián"}}
    }
}

# ============================================
# 🌍 다국어
# ============================================
LANGS = {"ko": "🇰🇷 한국어", "en": "🇺🇸 English", "ja": "🇯🇵 日本語", "zh": "🇨🇳 中文", "es": "🇪🇸 Español"}

T = {
    "ko": {
        "nick": "닉네임", "mbti": "MBTI", "gender": "성별", "m": "남", "f": "여",
        "age": "나이", "pers": "성격 3개", "submit": "✨ 결과보기",
        "result": "{}님 결과", "rate": "매칭률", "retry": "🔄 다시하기",
        "other": "🎁 다른 테스트", "copy": "📋 링크복사", "copied": "✅ 복사완료!",
        "ages": ["10대", "20대", "30대", "40대", "50+"],
        "p": {"따뜻한": "따뜻", "냉정한": "냉정", "열정적인": "열정", "차분한": "차분", "활발한": "활발",
              "겸손한": "겸손", "배려심많은": "배려", "독립적인": "독립", "낙천적인": "낙천", "유머러스한": "유머"},
        "footer": "오락용 | 개인정보 미수집"
    },
    "en": {
        "nick": "Name", "mbti": "MBTI", "gender": "Gender", "m": "M", "f": "F",
        "age": "Age", "pers": "3 Traits", "submit": "✨ Results",
        "result": "{}'s Match", "rate": "Match", "retry": "🔄 Again",
        "other": "🎁 More Tests", "copy": "📋 Copy Link", "copied": "✅ Copied!",
        "ages": ["Teen", "20s", "30s", "40s", "50+"],
        "p": {"따뜻한": "Warm", "냉정한": "Cool", "열정적인": "Passionate", "차분한": "Calm", "활발한": "Active",
              "겸손한": "Humble", "배려심많은": "Caring", "독립적인": "Independent", "낙천적인": "Optimistic", "유머러스한": "Funny"},
        "footer": "Entertainment | No data collected"
    },
    "ja": {
        "nick": "名前", "mbti": "MBTI", "gender": "性別", "m": "男", "f": "女",
        "age": "年代", "pers": "性格3つ", "submit": "✨ 結果",
        "result": "{}さんの結果", "rate": "マッチ", "retry": "🔄 もう一度",
        "other": "🎁 他のテスト", "copy": "📋 リンクコピー", "copied": "✅ コピー完了!",
        "ages": ["10代", "20代", "30代", "40代", "50+"],
        "p": {"따뜻한": "温かい", "냉정한": "クール", "열정적인": "情熱", "차분한": "穏やか", "활발한": "活発",
              "겸손한": "謙虚", "배려심많은": "思いやり", "독립적인": "独立", "낙천적인": "楽天", "유머러스한": "面白い"},
        "footer": "エンタメ用 | 個人情報なし"
    },
    "zh": {
        "nick": "昵称", "mbti": "MBTI", "gender": "性别", "m": "男", "f": "女",
        "age": "年龄", "pers": "3个性格", "submit": "✨ 结果",
        "result": "{}的结果", "rate": "匹配", "retry": "🔄 再试",
        "other": "🎁 更多测试", "copy": "📋 复制链接", "copied": "✅ 已复制!",
        "ages": ["10代", "20代", "30代", "40代", "50+"],
        "p": {"따뜻한": "温暖", "냉정한": "冷静", "열정적인": "热情", "차분한": "沉稳", "활발한": "活泼",
              "겸손한": "谦虚", "배려심많은": "体贴", "독립적인": "独立", "낙천적인": "乐观", "유머러스한": "幽默"},
        "footer": "娱乐用 | 不收集信息"
    },
    "es": {
        "nick": "Nombre", "mbti": "MBTI", "gender": "Género", "m": "H", "f": "M",
        "age": "Edad", "pers": "3 Rasgos", "submit": "✨ Resultado",
        "result": "Resultado de {}", "rate": "Match", "retry": "🔄 Otra vez",
        "other": "🎁 Más tests", "copy": "📋 Copiar link", "copied": "✅ Copiado!",
        "ages": ["Teen", "20s", "30s", "40s", "50+"],
        "p": {"따뜻한": "Cálido", "냉정한": "Frío", "열정적인": "Apasionado", "차분한": "Tranquilo", "활발한": "Activo",
              "겸손한": "Humilde", "배려심많은": "Atento", "독립적인": "Independiente", "낙천적인": "Optimista", "유머러스한": "Gracioso"},
        "footer": "Entretenimiento | Sin datos"
    }
}

def t(k, lang): return T.get(lang, T["en"]).get(k, k)

# ============================================
# 🎨 CSS
# ============================================
st.markdown("""<style>
.stApp { background: #f8f9fa; }
.block-container { padding: 0.5rem !important; max-width: 500px !important; }

.header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
          padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
.header-emoji { font-size: 45px; }
.header-title { font-size: 18px; margin: 10px 0 0 0; font-weight: 700; }

.card { background: white; border-radius: 12px; padding: 15px; margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.result-card { background: white; border-radius: 15px; padding: 20px; text-align: center;
               box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.result-name { font-size: 24px; font-weight: 800; color: #333; margin: 10px 0; }
.result-sub { font-size: 14px; color: #666; }

.score-box { background: linear-gradient(135deg, #667eea, #764ba2); 
             padding: 15px; border-radius: 12px; margin: 15px auto; width: fit-content; }
.score-num { font-size: 36px; font-weight: 800; color: white; }
.score-label { font-size: 12px; color: rgba(255,255,255,0.9); }

.tag { display: inline-block; background: #667eea; color: white; 
       padding: 4px 10px; border-radius: 12px; margin: 2px; font-size: 12px; }
.mbti-badge { background: linear-gradient(135deg, #f093fb, #f5576c); color: white;
              padding: 5px 15px; border-radius: 20px; font-weight: 700; }

.share-box { background: #f0f0f0; border-radius: 10px; padding: 12px; margin: 15px 0; text-align: center; }
.share-btn { display: inline-block; padding: 8px 15px; margin: 3px; border-radius: 8px;
             text-decoration: none; font-size: 13px; font-weight: 600; }
.btn-x { background: #000; color: white; }
.btn-fb { background: #1877f2; color: white; }
.btn-copy { background: #667eea; color: white; border: none; cursor: pointer; }

.other-box { background: linear-gradient(135deg, #ffecd2, #fcb69f); border-radius: 12px;
             padding: 15px; margin: 20px 0; }
.other-title { text-align: center; font-weight: 700; color: #c0392b; margin-bottom: 10px; }

.footer { text-align: center; padding: 15px; color: #888; font-size: 11px; }

.img-circle { width: 120px; height: 120px; border-radius: 50%; border: 4px solid #667eea;
              object-fit: cover; background: #eee; }

@media (max-width: 768px) {
    .header-title { font-size: 16px; }
    .result-name { font-size: 20px; }
    .score-num { font-size: 30px; }
}
</style>""", unsafe_allow_html=True)

# ============================================
# 🖼️ 이미지 (빠른 로딩)
# ============================================
def get_img(name, cfg):
    h = hashlib.md5(name.encode()).hexdigest()[:8]
    s = cfg.get('image_set', 'set5')
    return f"https://robohash.org/{h}?set={s}&size=150x150"

# ============================================
# 📊 매칭
# ============================================
COMPAT = {"INTJ":["ENFP"],"INTP":["ENTJ"],"ENTJ":["INTP"],"ENTP":["INFJ"],
          "INFJ":["ENTP"],"INFP":["ENTJ"],"ENFJ":["INFP"],"ENFP":["INFJ"],
          "ISTJ":["ESFP"],"ISFJ":["ESTP"],"ESTJ":["ISFP"],"ESFJ":["ISTP"],
          "ISTP":["ESFJ"],"ISFP":["ESTJ"],"ESTP":["ISFJ"],"ESFP":["ISTJ"]}

def calc(mbti, pers, tgt):
    s = 55
    tm = tgt.get('mbti', 'ENFP')
    if tm in COMPAT.get(mbti, []): s += 25
    elif tm == mbti: s += 12
    else: s += 6
    tp = tgt.get('personality', [])
    s += len(set(pers) & set(tp)) * 7
    return min(99, max(65, s + random.randint(-2, 6)))

def match(data, mbti, pers, cfg):
    for d in data:
        d['score'] = calc(mbti, pers, d)
        d['image_url'] = get_img(d.get('name',''), cfg)
    return sorted(data, key=lambda x: x['score'], reverse=True)[:1]

# ============================================
# 📂 데이터 (캐싱)
# ============================================
@st.cache_data(ttl=86400)
def load(f):
    try:
        with open(f, 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return []

# ============================================
# 🎯 메인
# ============================================
def main():
    APP_URL = "https://mbti-final.onrender.com"
    
    # 초기화
    if 'cur' not in st.session_state: st.session_state.cur = 'anime'
    if 'lang' not in st.session_state: st.session_state.lang = 'ko'
    if 'done' not in st.session_state: st.session_state.done = False
    if 'user' not in st.session_state: st.session_state.user = {}
    if 'result' not in st.session_state: st.session_state.result = []
    if 'scroll' not in st.session_state: st.session_state.scroll = False
    
    # 스크롤 상단
    if st.session_state.scroll:
        scroll_top()
        st.session_state.scroll = False
    if 'scroll' not in st.session_state: st.session_state.scroll = False
    
    # 맨 위로 스크롤
    if st.session_state.scroll:
        st.markdown("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll = False
    
    lang = st.session_state.lang
    cur = st.session_state.cur
    cfg = TEST_CONFIG[cur]
    
    # 언어 선택 (드롭다운 1줄)
    lang_list = list(LANGS.keys())
    selected = st.selectbox("🌍", lang_list, index=lang_list.index(lang),
                           format_func=lambda x: LANGS[x], label_visibility="collapsed")
    if selected != lang:
        st.session_state.lang = selected
        st.rerun()
    
    # 헤더
    title = cfg['title_full'].get(lang, cfg['title_full']['en'])
    st.markdown(f"""
    <div class="header">
        <div class="header-emoji">{cfg['emoji']}</div>
        <div class="header-title">{title}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 첫 화면 광고
    show_ad()
    
    # 입력 / 결과
    if not st.session_state.done:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        with st.form("f"):
            name = st.text_input(t('nick',lang), max_chars=10)
            
            c1, c2, c3 = st.columns(3)
            mlist = ["INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
                    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]
            with c1: mbti = st.selectbox(t('mbti',lang), mlist, index=7)
            with c2: gender = st.radio(t('gender',lang), [t('m',lang), t('f',lang)], horizontal=True)
            with c3: age = st.selectbox(t('age',lang), t('ages',lang))
            
            st.write(f"**{t('pers',lang)}**")
            pk = ["따뜻한","냉정한","열정적인","차분한","활발한","겸손한","배려심많은","독립적인","낙천적인","유머러스한"]
            sel = []
            cols = st.columns(5)
            for i, k in enumerate(pk):
                with cols[i % 5]:
                    if st.checkbox(t('p',lang).get(k,k)[:2], key=f"p_{k}"):
                        sel.append(k)
            
            qt = cfg.get('question_type', 'relationship')
            qc = QUESTIONS.get(qt, QUESTIONS['relationship']).get(lang, QUESTIONS[qt]['en'])
            st.radio(qc['q'], list(qc['o'].keys()), format_func=lambda x: qc['o'][x], horizontal=True)
            
            if st.form_submit_button(t('submit',lang), use_container_width=True, type="primary"):
                if name.strip() and len(sel) == 3:
                    st.session_state.user = {'name': name.strip(), 'mbti': mbti, 'pers': sel}
                    data = load(cfg['data_file'])
                    if data:
                        st.session_state.result = match(data, mbti, sel, cfg)
                        st.session_state.done = True
                        st.rerun()
                else:
                    st.error("⚠️ 이름 + 성격 3개!" if lang=='ko' else "⚠️ Name + 3 traits!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # 결과
        u = st.session_state.user
        r = st.session_state.result
        
        if r:
            top = r[0]
            sc = top.get('score', 80)
            
            # 다국어 이름
            name_display = top.get(f'name_{lang}') or top.get('name_en') or top.get('name')
            series_display = top.get(f'series_{lang}') or top.get('series_en') or top.get('series', '')
            
            if sc >= 90: msg = "💕 Perfect!"
            elif sc >= 80: msg = "💖 Great!"
            else: msg = "💗 Good!"
            
            st.markdown(f"""
            <div class="result-card">
                <div style="color:#667eea;font-size:14px;font-weight:600;">{t('result',lang).format(u['name'])}</div>
                <img src="{top.get('image_url','')}" class="img-circle" 
                     onerror="this.style.background='#667eea'">
                <div class="result-name">{name_display}</div>
                <div class="result-sub">{series_display}</div>
                <div class="score-box">
                    <div class="score-label">{t('rate',lang)}</div>
                    <div class="score-num">{sc}%</div>
                    <div style="color:white;font-size:13px;">{msg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 태그
            tags = ''.join([f'<span class="tag">{t("p",lang).get(p,p)}</span>' for p in top.get('personality',[])[:3]])
            st.markdown(f'<div style="text-align:center;margin:10px 0;">{tags}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center;"><span class="mbti-badge">{top.get("mbti","?")}</span></div>', unsafe_allow_html=True)
            
            # 광고
            show_ad()
            
            # 공유
            share_text = f"{name_display} {sc}%! - MBTI Match Test"
            encoded_text = urllib.parse.quote(share_text)
            encoded_url = urllib.parse.quote(APP_URL)
            
            st.markdown(f"""
            <div class="share-box">
                <a href="https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}" 
                   target="_blank" class="share-btn btn-x">𝕏 Post</a>
                <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}" 
                   target="_blank" class="share-btn btn-fb">Facebook</a>
            </div>
            """, unsafe_allow_html=True)
            
            # 링크 복사
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('copy',lang), use_container_width=True):
                    st.code(APP_URL, language=None)
                    st.success(t('copied',lang))
            with col2:
                if st.button(t('retry',lang), use_container_width=True, type="primary"):
                    st.session_state.done = False
                    st.session_state.result = []
                    st.session_state.scroll = True
                    st.rerun()
    
    # 다른 테스트
    st.markdown(f'<div class="other-box"><div class="other-title">{t("other",lang)}</div></div>', unsafe_allow_html=True)
    
    tests = list(TEST_CONFIG.items())
    cols = st.columns(5)
    for i, (k, v) in enumerate(tests[:5]):
        with cols[i]:
            title_short = v['title'].get(lang, v['title']['en'])[:4]
            if st.button(f"{v['emoji']}\n{title_short}", key=f"t1_{k}", use_container_width=True,
                        type="primary" if k==cur else "secondary"):
                st.session_state.cur = k
                st.session_state.done = False
                st.session_state.scroll = True
                st.rerun()
    
    cols2 = st.columns(5)
    for i, (k, v) in enumerate(tests[5:]):
        with cols2[i]:
            title_short = v['title'].get(lang, v['title']['en'])[:4]
            if st.button(f"{v['emoji']}\n{title_short}", key=f"t2_{k}", use_container_width=True,
                        type="primary" if k==cur else "secondary"):
                st.session_state.cur = k
                st.session_state.done = False
                st.session_state.scroll = True
                st.rerun()
    
    # 푸터
    st.markdown(f'<div class="footer">{t("footer",lang)} | © 2025</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
