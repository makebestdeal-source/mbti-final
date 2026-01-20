"""
🎯 MBTI 매칭 테스트 v3.3
=====================================
수정사항:
1. 공유 링크 수정 (카카오/X 정상 작동)
2. 테스트 메뉴 텍스트 + 강조
3. 배경 흰색 기반으로 변경
4. 이미지 로딩 개선 (placeholder + 빠른 CDN)
5. 언어팩 위치 개선 (우측 상단 눈에 띄게)
"""

import streamlit as st
import json
import hashlib
import random
from datetime import datetime
import streamlit.components.v1 as components
import urllib.parse

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
# 📊 테스트 설정
# ============================================
TEST_CONFIG = {
    "anime": {
        "emoji": "💕", 
        "title": {"ko": "애니 캐릭터", "en": "Anime Character", "ja": "アニメキャラ", "zh": "动漫角色", "es": "Personaje Anime"},
        "title_full": {"ko": "나와 어울리는 애니 캐릭터는?", "en": "Which Anime Character Matches You?", 
                       "ja": "あなたに合うアニメキャラは?", "zh": "你适合哪个动漫角色?", "es": "¿Qué personaje de anime eres?"},
        "data_file": "data/characters.json",
        "image_type": "robohash", "image_set": "set5",
        "question_type": "relationship"
    },
    "dogs": {
        "emoji": "🐕", 
        "title": {"ko": "강아지 품종", "en": "Dog Breed", "ja": "犬種", "zh": "狗品种", "es": "Raza de Perro"},
        "title_full": {"ko": "나랑 어울리는 강아지 품종은?", "en": "Which Dog Breed Suits You?",
                       "ja": "あなたに合う犬種は?", "zh": "你适合哪种狗?", "es": "¿Qué raza de perro te va?"},
        "data_file": "data/dogs.json",
        "image_type": "dog_ceo",
        "question_type": "pet"
    },
    "cats": {
        "emoji": "🐈", 
        "title": {"ko": "고양이 품종", "en": "Cat Breed", "ja": "猫種", "zh": "猫品种", "es": "Raza de Gato"},
        "title_full": {"ko": "나랑 어울리는 고양이 품종은?", "en": "Which Cat Breed Suits You?",
                       "ja": "あなたに合う猫種は?", "zh": "你适合哪种猫?", "es": "¿Qué raza de gato te va?"},
        "data_file": "data/cats.json",
        "image_type": "robohash", "image_set": "set4",
        "question_type": "pet"
    },
    "cities": {
        "emoji": "🌆", 
        "title": {"ko": "도시", "en": "City", "ja": "都市", "zh": "城市", "es": "Ciudad"},
        "title_full": {"ko": "나랑 어울리는 도시는?", "en": "Which City Suits You?",
                       "ja": "あなたに合う都市は?", "zh": "你适合哪个城市?", "es": "¿Qué ciudad te va?"},
        "data_file": "data/cities.json",
        "image_type": "robohash", "image_set": "set3",
        "question_type": "place"
    },
    "destinations": {
        "emoji": "🏝️", 
        "title": {"ko": "여행지", "en": "Travel Spot", "ja": "旅行先", "zh": "旅游地", "es": "Destino"},
        "title_full": {"ko": "나랑 어울리는 여행지는?", "en": "Which Travel Spot Suits You?",
                       "ja": "あなたに合う旅行先は?", "zh": "你适合哪个旅游地?", "es": "¿Qué destino te va?"},
        "data_file": "data/destinations.json",
        "image_type": "robohash", "image_set": "set3",
        "question_type": "travel"
    },
    "cars": {
        "emoji": "🚗", 
        "title": {"ko": "자동차", "en": "Car", "ja": "車", "zh": "汽车", "es": "Coche"},
        "title_full": {"ko": "나랑 어울리는 자동차는?", "en": "Which Car Suits You?",
                       "ja": "あなたに合う車は?", "zh": "你适合哪种车?", "es": "¿Qué coche te va?"},
        "data_file": "data/cars.json",
        "image_type": "robohash", "image_set": "set2",
        "question_type": "car"
    },
    "stars": {
        "emoji": "⭐", 
        "title": {"ko": "글로벌 스타", "en": "Global Star", "ja": "スター", "zh": "明星", "es": "Estrella"},
        "title_full": {"ko": "나랑 어울리는 글로벌 스타는?", "en": "Which Global Star Matches You?",
                       "ja": "あなたに合うスターは?", "zh": "你适合哪个明星?", "es": "¿Qué estrella te va?"},
        "data_file": "data/global_stars.json",
        "image_type": "robohash", "image_set": "set5",
        "question_type": "relationship"
    },
    "idols": {
        "emoji": "🎤", 
        "title": {"ko": "K-POP 아이돌", "en": "K-Pop Idol", "ja": "K-POPアイドル", "zh": "韩国偶像", "es": "Idol K-Pop"},
        "title_full": {"ko": "나랑 어울리는 아이돌은?", "en": "Which K-Pop Idol Matches You?",
                       "ja": "あなたに合うアイドルは?", "zh": "你适合哪个偶像?", "es": "¿Qué idol de K-Pop te va?"},
        "data_file": "data/idols.json",
        "image_type": "robohash", "image_set": "set5",
        "question_type": "relationship"
    },
    "games": {
        "emoji": "🎮", 
        "title": {"ko": "게임 캐릭터", "en": "Game Character", "ja": "ゲームキャラ", "zh": "游戏角色", "es": "Personaje Juego"},
        "title_full": {"ko": "나랑 어울리는 게임 캐릭터는?", "en": "Which Game Character Matches You?",
                       "ja": "あなたに合うゲームキャラは?", "zh": "你适合哪个游戏角色?", "es": "¿Qué personaje de juego te va?"},
        "data_file": "data/game_characters.json",
        "image_type": "robohash", "image_set": "set2",
        "question_type": "game"
    },
    "tinipings": {
        "emoji": "🎀", 
        "title": {"ko": "캐치티니핑", "en": "Catch Tiniping", "ja": "ティニピン", "zh": "迷你乒", "es": "Tiniping"},
        "title_full": {"ko": "나는 어떤 캐치티니핑?", "en": "Which Tiniping Are You?",
                       "ja": "あなたはどのティニピン?", "zh": "你是哪个迷你乒?", "es": "¿Qué Tiniping eres?"},
        "data_file": "data/tinipings.json",
        "image_type": "robohash", "image_set": "set4",
        "question_type": "character"
    }
}

# ============================================
# 🎯 카테고리별 질문
# ============================================
QUESTIONS = {
    "relationship": {
        "ko": {"q": "어떤 관계?", "o": {"ideal": "💕 이상형", "romance": "💝 연애", "marriage": "💍 결혼", "fan": "⭐ 최애"}},
        "en": {"q": "Relationship?", "o": {"ideal": "💕 Ideal", "romance": "💝 Dating", "marriage": "💍 Marriage", "fan": "⭐ Fave"}},
        "ja": {"q": "どんな関係?", "o": {"ideal": "💕 理想", "romance": "💝 恋愛", "marriage": "💍 結婚", "fan": "⭐ 推し"}},
        "zh": {"q": "什么关系?", "o": {"ideal": "💕 理想型", "romance": "💝 恋爱", "marriage": "💍 结婚", "fan": "⭐ 最爱"}},
        "es": {"q": "¿Relación?", "o": {"ideal": "💕 Ideal", "romance": "💝 Cita", "marriage": "💍 Boda", "fan": "⭐ Fav"}}
    },
    "pet": {
        "ko": {"q": "어떤 관계?", "o": {"want": "🏠 키우고싶은", "similar": "🪞 닮은", "soulmate": "💫 소울메이트"}},
        "en": {"q": "What match?", "o": {"want": "🏠 Want", "similar": "🪞 Similar", "soulmate": "💫 Soulmate"}},
        "ja": {"q": "どんなマッチ?", "o": {"want": "🏠 飼いたい", "similar": "🪞 似てる", "soulmate": "💫 運命"}},
        "zh": {"q": "什么匹配?", "o": {"want": "🏠 想养", "similar": "🪞 像我", "soulmate": "💫 灵魂伴侣"}},
        "es": {"q": "¿Qué tipo?", "o": {"want": "🏠 Quiero", "similar": "🪞 Similar", "soulmate": "💫 Alma"}}
    },
    "place": {
        "ko": {"q": "어떤 목적?", "o": {"live": "🏠 거주", "travel": "✈️ 여행", "month": "📅 한달살기"}},
        "en": {"q": "Purpose?", "o": {"live": "🏠 Live", "travel": "✈️ Travel", "month": "📅 Month"}},
        "ja": {"q": "目的は?", "o": {"live": "🏠 住む", "travel": "✈️ 旅行", "month": "📅 1ヶ月"}},
        "zh": {"q": "什么目的?", "o": {"live": "🏠 居住", "travel": "✈️ 旅行", "month": "📅 月住"}},
        "es": {"q": "¿Propósito?", "o": {"live": "🏠 Vivir", "travel": "✈️ Viajar", "month": "📅 Mes"}}
    },
    "travel": {
        "ko": {"q": "여행 스타일?", "o": {"healing": "🌴 힐링", "adventure": "🏔️ 모험", "bucket": "⭐ 버킷"}},
        "en": {"q": "Travel style?", "o": {"healing": "🌴 Healing", "adventure": "🏔️ Adventure", "bucket": "⭐ Bucket"}},
        "ja": {"q": "旅行スタイル?", "o": {"healing": "🌴 癒し", "adventure": "🏔️ 冒険", "bucket": "⭐ バケリス"}},
        "zh": {"q": "旅行风格?", "o": {"healing": "🌴 治愈", "adventure": "🏔️ 冒险", "bucket": "⭐ 心愿"}},
        "es": {"q": "¿Estilo?", "o": {"healing": "🌴 Relax", "adventure": "🏔️ Aventura", "bucket": "⭐ Lista"}}
    },
    "car": {
        "ko": {"q": "어떤 차?", "o": {"dream": "🌟 드림카", "first": "🔰 첫차", "practical": "💼 실용"}},
        "en": {"q": "What car?", "o": {"dream": "🌟 Dream", "first": "🔰 First", "practical": "💼 Practical"}},
        "ja": {"q": "どんな車?", "o": {"dream": "🌟 ドリーム", "first": "🔰 最初", "practical": "💼 実用"}},
        "zh": {"q": "什么车?", "o": {"dream": "🌟 梦想", "first": "🔰 第一辆", "practical": "💼 实用"}},
        "es": {"q": "¿Qué coche?", "o": {"dream": "🌟 Sueño", "first": "🔰 Primero", "practical": "💼 Práctico"}}
    },
    "game": {
        "ko": {"q": "어떤 캐릭터?", "o": {"play": "🕹️ 플레이", "party": "👥 파티원", "similar": "🪞 닮은"}},
        "en": {"q": "What character?", "o": {"play": "🕹️ Play", "party": "👥 Party", "similar": "🪞 Similar"}},
        "ja": {"q": "どんなキャラ?", "o": {"play": "🕹️ プレイ", "party": "👥 パーティー", "similar": "🪞 似てる"}},
        "zh": {"q": "什么角色?", "o": {"play": "🕹️ 玩", "party": "👥 队友", "similar": "🪞 像我"}},
        "es": {"q": "¿Personaje?", "o": {"play": "🕹️ Jugar", "party": "👥 Equipo", "similar": "🪞 Similar"}}
    },
    "character": {
        "ko": {"q": "어떤 타입?", "o": {"similar": "🪞 닮은", "friend": "👫 친구", "guardian": "🛡️ 수호"}},
        "en": {"q": "What type?", "o": {"similar": "🪞 Similar", "friend": "👫 Friend", "guardian": "🛡️ Guardian"}},
        "ja": {"q": "どんなタイプ?", "o": {"similar": "🪞 似てる", "friend": "👫 友達", "guardian": "🛡️ 守護"}},
        "zh": {"q": "什么类型?", "o": {"similar": "🪞 像我", "friend": "👫 朋友", "guardian": "🛡️ 守护"}},
        "es": {"q": "¿Qué tipo?", "o": {"similar": "🪞 Similar", "friend": "👫 Amigo", "guardian": "🛡️ Guardián"}}
    }
}

# ============================================
# 🌍 다국어 번역
# ============================================
LANG_OPTIONS = {
    "ko": "🇰🇷 한국어",
    "en": "🇺🇸 English", 
    "ja": "🇯🇵 日本語",
    "zh": "🇨🇳 中文",
    "es": "🇪🇸 Español"
}

T = {
    "ko": {
        "nick": "닉네임", "nick_ph": "이름 입력",
        "mbti": "MBTI", "gender": "성별", "m": "남", "f": "여",
        "age": "나이대", "pers": "💭 성격 3개 선택",
        "submit": "✨ 결과 보기", "result": "{}님의 매칭 결과",
        "rate": "매칭률", "retry": "🔄 다시 테스트하기",
        "other": "🎁 다른 테스트도 해보세요!",
        "ages": ["10대", "20대", "30대", "40대", "50+"],
        "p": {"따뜻한": "따뜻한", "냉정한": "냉정한", "열정적인": "열정적",
              "차분한": "차분한", "활발한": "활발한", "겸손한": "겸손한",
              "배려심많은": "배려심", "독립적인": "독립적",
              "낙천적인": "낙천적", "유머러스한": "유머"},
        "disclaimer": "⚠️ 오락 목적 테스트",
        "privacy": "🔒 개인정보 미수집",
        "share": "📤 결과 공유하기"
    },
    "en": {
        "nick": "Nickname", "nick_ph": "Your name",
        "mbti": "MBTI", "gender": "Gender", "m": "M", "f": "F",
        "age": "Age", "pers": "💭 Pick 3 Traits",
        "submit": "✨ See Results", "result": "{}'s Match",
        "rate": "Match", "retry": "🔄 Try Again",
        "other": "🎁 Try More Tests!",
        "ages": ["Teen", "20s", "30s", "40s", "50+"],
        "p": {"따뜻한": "Warm", "냉정한": "Cool", "열정적인": "Passionate",
              "차분한": "Calm", "활발한": "Active", "겸손한": "Humble",
              "배려심많은": "Caring", "독립적인": "Independent",
              "낙천적인": "Optimistic", "유머러스한": "Funny"},
        "disclaimer": "⚠️ Entertainment only",
        "privacy": "🔒 No data collected",
        "share": "📤 Share Result"
    },
    "ja": {
        "nick": "ニックネーム", "nick_ph": "名前",
        "mbti": "MBTI", "gender": "性別", "m": "男", "f": "女",
        "age": "年代", "pers": "💭 性格3つ",
        "submit": "✨ 結果を見る", "result": "{}さんの結果",
        "rate": "マッチ率", "retry": "🔄 もう一度",
        "other": "🎁 他のテストも!",
        "ages": ["10代", "20代", "30代", "40代", "50+"],
        "p": {"따뜻한": "温かい", "냉정한": "クール", "열정적인": "情熱的",
              "차분한": "穏やか", "활발한": "活発", "겸손한": "謙虚",
              "배려심많은": "思いやり", "독립적인": "独立的",
              "낙천적인": "楽天的", "유머러스한": "面白い"},
        "disclaimer": "⚠️ エンタメ目的",
        "privacy": "🔒 個人情報なし",
        "share": "📤 シェア"
    },
    "zh": {
        "nick": "昵称", "nick_ph": "名字",
        "mbti": "MBTI", "gender": "性别", "m": "男", "f": "女",
        "age": "年龄", "pers": "💭 选3个",
        "submit": "✨ 看结果", "result": "{}的结果",
        "rate": "匹配率", "retry": "🔄 再试",
        "other": "🎁 更多测试!",
        "ages": ["10代", "20代", "30代", "40代", "50+"],
        "p": {"따뜻한": "温暖", "냉정한": "冷静", "열정적인": "热情",
              "차분한": "沉稳", "활발한": "活泼", "겸손한": "谦虚",
              "배려심많은": "体贴", "독립적인": "独立",
              "낙천적인": "乐观", "유머러스한": "幽默"},
        "disclaimer": "⚠️ 仅供娱乐",
        "privacy": "🔒 不收集信息",
        "share": "📤 分享"
    },
    "es": {
        "nick": "Apodo", "nick_ph": "Nombre",
        "mbti": "MBTI", "gender": "Género", "m": "H", "f": "M",
        "age": "Edad", "pers": "💭 Elige 3",
        "submit": "✨ Ver Resultado", "result": "Resultado de {}",
        "rate": "Match", "retry": "🔄 Otra vez",
        "other": "🎁 ¡Más tests!",
        "ages": ["Teen", "20s", "30s", "40s", "50+"],
        "p": {"따뜻한": "Cálido", "냉정한": "Frío", "열정적인": "Apasionado",
              "차분한": "Tranquilo", "활발한": "Activo", "겸손한": "Humilde",
              "배려심많은": "Atento", "독립적인": "Independiente",
              "낙천적인": "Optimista", "유머러스한": "Gracioso"},
        "disclaimer": "⚠️ Solo entretenimiento",
        "privacy": "🔒 Sin datos",
        "share": "📤 Compartir"
    }
}

def t(k, lang): return T.get(lang, T["en"]).get(k, k)

# ============================================
# 🎨 CSS (흰색 배경 + 가독성)
# ============================================
def load_css():
    st.markdown("""<style>
    /* 깔끔한 흰색/연회색 배경 */
    .stApp {
        background: #f5f5f5 !important;
    }
    
    .block-container {
        padding: 1rem 0.8rem !important;
        max-width: 100% !important;
    }
    
    /* 언어 선택 박스 */
    .lang-box {
        background: #667eea;
        color: white;
        padding: 8px 15px;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    /* 카드 */
    .card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    
    /* 헤더 박스 */
    .header-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        color: white;
    }
    
    .header-emoji {
        font-size: 50px;
    }
    
    .header-title {
        color: white;
        margin: 10px 0 0 0;
        font-size: 20px;
        font-weight: 700;
    }
    
    /* 결과 카드 */
    .result {
        background: white;
        padding: 25px 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .result-title {
        color: #667eea;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    /* 이미지 */
    .match-img {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #667eea;
        margin: 10px auto;
        display: block;
        background: #f0f0f0;
    }
    
    /* 이름 - 검은색 */
    .match-name {
        font-size: 24px;
        font-weight: 800;
        color: #1a1a1a;
        margin: 10px 0 5px 0;
    }
    
    /* 시리즈 */
    .match-series {
        color: #666;
        font-size: 14px;
        margin-bottom: 15px;
    }
    
    /* 점수 박스 */
    .score-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 15px 20px;
        border-radius: 15px;
        margin: 15px auto;
        max-width: 140px;
    }
    
    .score-label {
        color: rgba(255,255,255,0.9);
        font-size: 12px;
    }
    
    .score-num {
        font-size: 42px;
        font-weight: 800;
        color: white;
    }
    
    .score-msg {
        color: white;
        font-size: 14px;
    }
    
    /* 태그 */
    .tag {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 3px;
        font-size: 13px;
    }
    
    /* MBTI 배지 */
    .mbti-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 16px;
        margin: 10px 0;
    }
    
    /* 공유 섹션 */
    .share-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        text-align: center;
    }
    
    .share-title {
        color: #333;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    /* 다른 테스트 섹션 - 강조! */
    .other-tests {
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
        border-radius: 16px;
        padding: 20px 15px;
        margin: 20px 0;
        border: 2px solid #ff6b9d;
    }
    
    .other-tests-title {
        text-align: center;
        color: #c0392b;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .test-btn {
        display: block;
        background: white;
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 10px 5px;
        margin: 5px 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .test-btn:hover {
        background: #667eea;
        color: white;
    }
    
    .test-btn-emoji {
        font-size: 24px;
        display: block;
    }
    
    .test-btn-text {
        font-size: 11px;
        color: #333;
        font-weight: 600;
        margin-top: 3px;
    }
    
    /* 푸터 */
    .footer {
        background: white;
        border-radius: 12px;
        text-align: center;
        padding: 15px;
        margin-top: 20px;
        font-size: 11px;
        color: #666;
        border: 1px solid #e0e0e0;
    }
    
    /* 반응형 */
    @media (max-width: 768px) {
        .stButton > button {
            min-height: 44px !important;
            font-size: 14px !important;
        }
        .header-emoji {
            font-size: 40px;
        }
        .header-title {
            font-size: 18px;
        }
        .match-img {
            width: 130px;
            height: 130px;
        }
        .match-name {
            font-size: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# 🔝 화면 상단 이동
# ============================================
def scroll_to_top():
    components.html("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """, height=0)

# ============================================
# 🖼️ 이미지 URL (빠른 로딩)
# ============================================
def get_img(name, name_en, cfg):
    # RoboHash 사용 (빠르고 안정적)
    seed = hashlib.md5((name + (name_en or "")).encode()).hexdigest()
    img_set = cfg.get('image_set', 'set5')
    return f"https://robohash.org/{seed}.png?set={img_set}&size=200x200&bgset=bg1"

# ============================================
# 📊 MBTI 궁합
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

def match(data, mbti, pers):
    res = sorted([{**d, 'score': calc(mbti, pers, d)} for d in data], 
                 key=lambda x: x['score'], reverse=True)
    return res[:1] if res else []

# ============================================
# 📂 데이터 로드
# ============================================
@st.cache_data(ttl=3600)
def load(f, cfg):
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for d in data:
                d['image_url'] = get_img(d.get('name',''), d.get('name_en',''), cfg)
            return data
    except: return []

# ============================================
# 💰 광고
# ============================================
def ad(lang):
    if st.session_state.get('ad_shown'): return
    components.html("""
    <div style="text-align:center;padding:12px;margin:15px 0;
                background:#f0f0f0;border-radius:10px;border:1px dashed #ccc;">
        <p style="color:#999;font-size:11px;margin:0;">Ad Space</p>
    </div>
    """, height=50)
    st.session_state['ad_shown'] = True

# ============================================
# 📤 공유 (수정됨 - URL 인코딩)
# ============================================
def share(name, score, title, lang, app_url):
    texts = {
        "ko": f"나와 어울리는 {title}: {name}! 매칭률 {score}% 🎯",
        "en": f"My {title} match: {name}! {score}% 🎯",
        "ja": f"私の{title}マッチ: {name}! {score}% 🎯",
        "zh": f"我的{title}匹配: {name}! {score}% 🎯",
        "es": f"Mi {title}: {name}! {score}% 🎯"
    }
    txt = texts.get(lang, texts["en"])
    
    # URL 인코딩 (특수문자 처리)
    encoded_text = urllib.parse.quote(txt, safe='')
    encoded_url = urllib.parse.quote(app_url, safe='')
    
    # 각 플랫폼 공유 URL
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
    
    st.markdown(f"""
    <div class="share-section">
        <div class="share-title">{t('share', lang)}</div>
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">
            <a href="{twitter_url}" target="_blank" 
               style="background:#000;color:white;padding:10px 20px;border-radius:25px;
                      text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">
                𝕏 Post
            </a>
            <a href="{facebook_url}" target="_blank"
               style="background:#1877f2;color:white;padding:10px 20px;border-radius:25px;
                      text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">
                Facebook
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 🔄 하단 테스트 메뉴 (텍스트 + 강조)
# ============================================
def bottom_menu(cur, lang):
    st.markdown(f"""
    <div class="other-tests">
        <div class="other-tests-title">🎁 {t('other', lang)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    tests = list(TEST_CONFIG.items())
    
    # 2줄 (5개씩) - 텍스트 포함
    cols1 = st.columns(5)
    for i, (k, v) in enumerate(tests[:5]):
        with cols1[i]:
            title = v['title'].get(lang, v['title']['en'])
            # 긴 텍스트 줄이기
            short_title = title[:6] + ".." if len(title) > 6 else title
            btn_type = "primary" if k == cur else "secondary"
            if st.button(f"{v['emoji']}\n{short_title}", key=f"b1_{k}", use_container_width=True, type=btn_type):
                st.session_state.cur = k
                st.session_state.done = False
                st.session_state.result = []
                st.session_state.ad_shown = False
                st.session_state.scroll_top = True
                st.rerun()
    
    cols2 = st.columns(5)
    for i, (k, v) in enumerate(tests[5:]):
        with cols2[i]:
            title = v['title'].get(lang, v['title']['en'])
            short_title = title[:6] + ".." if len(title) > 6 else title
            btn_type = "primary" if k == cur else "secondary"
            if st.button(f"{v['emoji']}\n{short_title}", key=f"b2_{k}", use_container_width=True, type=btn_type):
                st.session_state.cur = k
                st.session_state.done = False
                st.session_state.result = []
                st.session_state.ad_shown = False
                st.session_state.scroll_top = True
                st.rerun()

# ============================================
# 📜 푸터
# ============================================
def footer(lang):
    st.markdown(f"""
    <div class="footer">
        <p>{t('disclaimer', lang)} | {t('privacy', lang)}</p>
        <p>© {datetime.now().year} MBTI Match Test</p>
        <p style="margin-top:5px;font-size:10px;color:#999;">Images: RoboHash (AI Generated)</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 🎯 메인 앱
# ============================================
def main():
    load_css()
    
    # ⚠️ 여기에 실제 앱 URL 입력!
    APP_URL = "https://anime-character-test.streamlit.app"
    
    # 초기화
    if 'cur' not in st.session_state: st.session_state.cur = 'anime'
    if 'lang' not in st.session_state: st.session_state.lang = 'ko'
    if 'done' not in st.session_state: st.session_state.done = False
    if 'user' not in st.session_state: st.session_state.user = {}
    if 'result' not in st.session_state: st.session_state.result = []
    if 'ad_shown' not in st.session_state: st.session_state.ad_shown = False
    if 'scroll_top' not in st.session_state: st.session_state.scroll_top = False
    
    if st.session_state.scroll_top:
        scroll_to_top()
        st.session_state.scroll_top = False
    
    lang = st.session_state.lang
    cur = st.session_state.cur
    cfg = TEST_CONFIG[cur]
    
    # ============================================
    # 🌍 언어 선택 (눈에 띄는 위치)
    # ============================================
    st.markdown(f'<div class="lang-box">🌍 Language / 언어</div>', unsafe_allow_html=True)
    
    lang_cols = st.columns(5)
    for i, (code, label) in enumerate(LANG_OPTIONS.items()):
        with lang_cols[i]:
            btn_type = "primary" if lang == code else "secondary"
            if st.button(label.split()[0], key=f"lang_{code}", use_container_width=True, type=btn_type):
                st.session_state.lang = code
                st.rerun()
    
    # ============================================
    # 📝 헤더
    # ============================================
    title_full = cfg['title_full'].get(lang, cfg['title_full']['en'])
    st.markdown(f"""
    <div class="header-box">
        <div class="header-emoji">{cfg['emoji']}</div>
        <h2 class="header-title">{title_full}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # 📝 입력 폼 또는 결과
    # ============================================
    if not st.session_state.done:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        prev = st.session_state.user
        
        with st.form("f"):
            name = st.text_input(t('nick',lang), value=prev.get('name',''), 
                                placeholder=t('nick_ph',lang), max_chars=12)
            
            c1, c2, c3 = st.columns(3)
            mlist = ["INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
                    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]
            with c1:
                idx = mlist.index(prev.get('mbti','ENFP')) if prev.get('mbti') in mlist else 7
                mbti = st.selectbox(t('mbti',lang), mlist, index=idx)
            with c2:
                gender = st.radio(t('gender',lang), [t('m',lang), t('f',lang)], horizontal=True)
            with c3:
                age = st.selectbox(t('age',lang), t('ages',lang))
            
            st.markdown(f"**{t('pers',lang)}**")
            pk = ["따뜻한","냉정한","열정적인","차분한","활발한",
                  "겸손한","배려심많은","독립적인","낙천적인","유머러스한"]
            
            sel = []
            for grp in [pk[:4], pk[4:7], pk[7:]]:
                gc = st.columns(len(grp))
                for i,k in enumerate(grp):
                    with gc[i]:
                        lbl = t('p',lang).get(k,k)
                        if st.checkbox(lbl, key=f"p_{k}", value=k in prev.get('pers',[])):
                            sel.append(k)
            
            if len(sel) != 3:
                st.caption(f"✓ {len(sel)}/3")
            
            qt = cfg.get('question_type', 'relationship')
            qc = QUESTIONS.get(qt, QUESTIONS['relationship']).get(lang, QUESTIONS[qt]['en'])
            cat = st.radio(qc['q'], list(qc['o'].keys()), 
                          format_func=lambda x: qc['o'][x], horizontal=True)
            
            if st.form_submit_button(t('submit',lang), use_container_width=True, type="primary"):
                if not name.strip():
                    st.error("⚠️ " + t('nick', lang))
                elif len(sel) != 3:
                    st.error("⚠️ 3개 선택!" if lang == 'ko' else "⚠️ Select 3!")
                else:
                    st.session_state.user = {
                        'name': name.strip()[:12], 'mbti': mbti, 
                        'gender': gender, 'age': age, 'pers': sel
                    }
                    data = load(cfg['data_file'], cfg)
                    if data:
                        st.session_state.result = match(data, mbti, sel)
                        st.session_state.done = True
                        st.session_state.scroll_top = True
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # 결과
        u = st.session_state.user
        r = st.session_state.result
        
        if r:
            top = r[0]
            sc = int(top.get('score', 80))
            
            if sc >= 90: msg = "💕 Perfect!"
            elif sc >= 80: msg = "💖 Great!"
            else: msg = "💗 Good!"
            
            st.markdown(f"""
            <div class="result">
                <div class="result-title">{t('result',lang).format(u['name'])}</div>
                <img src="{top.get('image_url','')}" class="match-img" 
                     onerror="this.src='https://robohash.org/error.png?set=set5&size=200x200'" 
                     loading="lazy" alt="{top['name']}">
                <div class="match-name">{top['name']}</div>
                <div class="match-series">{top.get('series','')}</div>
                <div class="score-box">
                    <div class="score-label">{t('rate',lang)}</div>
                    <div class="score-num">{sc}%</div>
                    <div class="score-msg">{msg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 태그
            tags = ''.join([f'<span class="tag">{t("p",lang).get(p,p)}</span>' 
                           for p in top.get('personality',[])[:4]])
            st.markdown(f'<div style="text-align:center;margin:15px 0;">{tags}</div>', unsafe_allow_html=True)
            
            # MBTI
            st.markdown(f'<div style="text-align:center;"><span class="mbti-badge">MBTI: {top.get("mbti","?")}</span></div>', unsafe_allow_html=True)
            
            # 광고
            ad(lang)
            
            # 공유
            title = cfg['title'].get(lang, cfg['title']['en'])
            share(top['name'], sc, title, lang, APP_URL)
            
            # 다시하기
            if st.button(t('retry',lang), use_container_width=True, type="primary"):
                st.session_state.done = False
                st.session_state.result = []
                st.session_state.ad_shown = False
                st.session_state.scroll_top = True
                st.rerun()
    
    # ============================================
    # 📋 하단 테스트 메뉴
    # ============================================
    bottom_menu(cur, lang)
    footer(lang)

if __name__ == "__main__":
    main()
