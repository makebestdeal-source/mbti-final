
import streamlit as st
import json
import random
import urllib.parse
import os
import streamlit.components.v1 as components
import traceback # 디버깅용

# 1. 페이지 설정 (반드시 맨 위)
st.set_page_config(page_title="SoulFinder", page_icon="💘", layout="centered")

# [안전장치] 메인 로직을 try-except로 감싸서 에러 발생 시 내용을 화면에 출력
try:
    # 2. 광고 코드
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
        components.html(ad_code, height=120)

    # 3. CSS 스타일 (버튼, 로고, 모바일 최적화)
    st.markdown("""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        html, body, [class*="st-"] { font-family: Pretendard, sans-serif !important; }
        
        .jm-logo { text-align: center; color: #aaa; font-weight: 900; letter-spacing: 2px; margin-bottom: 10px; font-size: 14px; }
        
        /* Primary 버튼 (보라색, 흰글씨) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            height: 50px !important;
            opacity: 1 !important;
        }
        div.stButton > button[kind="primary"] p { color: white !important; }
        
        /* Secondary 버튼 (흰색) */
        div.stButton > button[kind="secondary"] {
            background: white !important;
            color: #333 !important;
            border: 1px solid #ddd !important;
            height: 100px !important;
        }
        
        .center-box { display: flex; justify-content: center; margin: 20px 0; }
        .res-img { width: 250px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .desc-box { background: #fff; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #eee; color: #555; margin-top: 15px; }
        .footer { text-align: center; margin-top: 50px; color: #ccc; font-size: 0.8rem; }
        </style>
    """, unsafe_allow_html=True)

    # 4. 상수 및 설정
    CATEGORIES = {
        "dogs": {"icon": "🐶", "ko": "강아지", "en": "Dog"},
        "cats": {"icon": "🐱", "ko": "고양이", "en": "Cat"},
        "cities": {"icon": "🏙️", "ko": "도시", "en": "City"},
        "destinations": {"icon": "✈️", "ko": "여행지", "en": "Travel"},
        "cars": {"icon": "🚗", "ko": "자동차", "en": "Car"},
        "stars": {"icon": "🌟", "ko": "해외 스타", "en": "Global Star"},
        "idols": {"icon": "🎤", "ko": "아이돌", "en": "K-Pop Idol"},
        "tinipings": {"icon": "🎀", "ko": "티니핑", "en": "Tiniping"},
        "anime": {"icon": "🦄", "ko": "애니 캐릭터", "en": "Anime"},
        "games": {"icon": "🎮", "ko": "게임 캐릭터", "en": "Game Char"}
    }

    TRANS = {
        "ko": {"title": "SoulFinder", "desc": "나와 완벽하게 통하는 운명의 단짝 찾기", "btn": "결과 확인하기", "res": "당신의 영혼의 단짝은...", "intro": "소개", "retry": "다시 하기", "privacy": "개인정보는 수집되지 않습니다.", "pl": "이름 입력", "warn": "MBTI를 선택해주세요!"},
        "en": {"title": "SoulFinder", "desc": "Find your perfect soulmate match!", "btn": "See Result", "res": "Your Soulmate is...", "intro": "About", "retry": "Retry", "privacy": "No data collected.", "pl": "Name", "warn": "Select MBTI!"},
        "ja": {"title": "SoulFinder", "desc": "運命のソウルメイトを見つけよう！", "btn": "結果を見る", "res": "あなたのソウルメイトは...", "intro": "紹介", "retry": "もう一度", "privacy": "個人情報は収集されません。", "pl": "名前", "warn": "MBTIを選択!"},
        "zh": {"title": "SoulFinder", "desc": "寻找你的完美灵魂伴侣！", "btn": "查看结果", "res": "你的灵魂伴侣是...", "intro": "介绍", "retry": "重试", "privacy": "不收集个人信息。", "pl": "名字", "warn": "选择MBTI!"},
        "es": {"title": "SoulFinder", "desc": "¡Encuentra tu alma gemela!", "btn": "Ver Resultado", "res": "Tu alma gemela es...", "intro": "Descripción", "retry": "Reintentar", "privacy": "Sin datos.", "pl": "Nombre", "warn": "MBTI!"}
    }

    COMPATIBILITY = {
        "INFP": ["ENFJ", "ENTJ"], "ENFJ": ["INFP", "ISFP"],
        "INFJ": ["ENFP", "ENTP"], "ENFP": ["INFJ", "INTJ"],
        "INTJ": ["ENFP", "ENTP"], "ENTP": ["INFJ", "INTJ"],
        "INTP": ["ENTJ", "ESTJ"], "ENTJ": ["INTP", "ISFP"],
        "ISFP": ["ESFJ", "ESTJ", "ENFJ"], "ESFJ": ["ISFP", "ISTP"],
        "ISTP": ["ESFJ", "ESTJ"], "ESTJ": ["ISFP", "ISTP"],
        "ISFJ": ["ESFP", "ESTP"], "ESFP": ["ISFJ", "ISTJ"],
        "ISTJ": ["ESFP", "ESTP"], "ESTP": ["ISFJ", "ISTJ"]
    }

    # 5. 데이터 로드 (안전 장치 포함)
    def load_data(file):
        try:
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data: return data
        except Exception:
            pass
        
        # 비상용 데이터
        return [{
            "id": "fallback",
            "names": {"ko": "로딩 오류", "en": "Error"},
            "mbti": "XXXX",
            "description": {"ko": "데이터를 불러올 수 없습니다.", "en": "Data load failed."},
            "traits": {"energy": 5, "social": 5, "indep": 5, "sense": 5, "play": 5},
            "image_url": "https://api.dicebear.com/9.x/notionists/png?seed=error"
        }]

    # 6. 매칭 로직
    def calc_score(user, item):
        score = 100
        diff_sum = 0
        for k in ['energy', 'social', 'indep', 'sense', 'play']:
            u_val = user['traits'][k]
            i_val = item['traits'].get(k, 5)
            diff_sum += abs(u_val - i_val)
        score -= (diff_sum * 1.5)
        
        u_mbti = user['mbti']
        i_mbti = item.get('mbti', '')
        if i_mbti:
            if i_mbti in COMPATIBILITY.get(u_mbti, []): score += 15
            elif u_mbti == i_mbti: score += 10
            elif u_mbti[0] == i_mbti[0] and u_mbti[3] == i_mbti[3]: score += 5
        return int(max(0, min(100, score)))

    # 7. 메인 화면 로직
    st.markdown("<div class='jm-logo'>JM STUDIO</div>", unsafe_allow_html=True)

    if 'page' not in st.session_state: st.session_state.page = 'intro'
    if 'lang' not in st.session_state: st.session_state.lang = 'ko'
    
    # 언어 선택
    c1, c2 = st.columns([3, 1])
    with c2:
        lang_map = {"🇰🇷 KO": "ko", "🇺🇸 EN": "en", "🇯🇵 JA": "ja", "🇨🇳 ZH": "zh", "🇪🇸 ES": "es"}
        sel = st.selectbox("Lang", list(lang_map.keys()), label_visibility="collapsed")
        st.session_state.lang = lang_map[sel]
    
    t = TRANS[st.session_state.lang]

    # PAGE: INTRO
    if st.session_state.page == 'intro':
        st.markdown(f"<h1 style='text-align:center;'>{t['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>{t['desc']}</p>", unsafe_allow_html=True)
        
        show_ad()
        
        keys = list(CATEGORIES.keys())
        for i in range(0, len(keys), 2):
            cols = st.columns(2)
            for j in range(2):
                if i+j < len(keys):
                    k = keys[i+j]
                    cat = CATEGORIES[k]
                    label = cat['ko'] if st.session_state.lang == 'ko' else cat['en']
                    with cols[j]:
                        if st.button(f"{cat['icon']}\\n{label}", key=k, type="secondary", use_container_width=True):
                            st.session_state.cat = k
                            st.session_state.page = 'test'
                            st.rerun()

    # PAGE: TEST
    elif st.session_state.page == 'test':
        cat_info = CATEGORIES[st.session_state.cat]
        label = cat_info['ko'] if st.session_state.lang == 'ko' else cat_info['en']
        st.markdown(f"<h2 style='text-align:center;'>{cat_info['icon']} {label}</h2>", unsafe_allow_html=True)
        
        show_ad()
        
        with st.form("f"):
            name = st.text_input(t['pl'])
            mbti = st.selectbox("MBTI", ["-"]+["ENFJ","ENFP","ENTJ","ENTP","ESFJ","ESFP","ESTJ","ESTP","INFJ","INFP","INTJ","INTP","ISFJ","ISFP","ISTJ","ISTP"])
            
            st.write("---")
            t1 = st.slider("⚡ Energy (1-10)", 1, 10, 5)
            t2 = st.slider("💬 Sociability (1-10)", 1, 10, 5)
            t3 = st.slider("🦅 Independence (1-10)", 1, 10, 5)
            t4 = st.slider("💧 Sensitivity (1-10)", 1, 10, 5)
            t5 = st.slider("🎢 Playfulness (1-10)", 1, 10, 5)
            
            if st.form_submit_button(t['btn'], type="primary", use_container_width=True):
                if mbti == "-": st.error(t['warn'])
                else:
                    st.session_state.user = {
                        "name": name, "mbti": mbti, 
                        "traits": {"energy": t1, "social": t2, "indep": t3, "sense": t4, "play": t5}
                    }
                    st.session_state.page = 'result'
                    st.rerun()
        
        if st.button("🏠 Home", type="secondary", use_container_width=True):
            st.session_state.page = 'intro'
            st.rerun()

    # PAGE: RESULT
    elif st.session_state.page == 'result':
        data = load_data(f"{st.session_state.cat}.json")
        
        best = max(data, key=lambda x: calc_score(st.session_state.user, x))
        score = calc_score(st.session_state.user, best)
        
        lang = st.session_state.lang
        r_name = best['names'].get(lang, best['names']['en'])
        r_desc = best['description'].get(lang, best['description']['en'])
        
        st.balloons()
        st.caption(t['res'])
        st.markdown(f"<h1 style='text-align:center; color:#ff4b4b;'>{r_name}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align:center;color:#666'>Match: {score}%</h4>", unsafe_allow_html=True)
        
        st.markdown(f'<div class="center-box"><img src="{best["image_url"]}" class="res-img"></div>', unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'><b>{t['intro']}</b><br>{r_desc}</div>", unsafe_allow_html=True)
        
        show_ad()
        
        st.divider()
        link = f"SoulFinder: {r_name} ({score}%)"
        c1, c2 = st.columns(2)
        with c1: st.link_button("🐦 Twitter", f"https://twitter.com/intent/tweet?text={urllib.parse.quote(link)}", use_container_width=True)
        with c2: st.link_button("📘 Facebook", "https://www.facebook.com", use_container_width=True)
        
        if st.button(t['retry'], type="primary", use_container_width=True):
            st.session_state.page = 'intro'
            st.rerun()
            
    st.markdown(f"<div class='footer'>© 2024 JM STUDIO.<br>{t['privacy']}</div>", unsafe_allow_html=True)

# [안전장치] 에러 캡처
except Exception:
    st.error("🚨 앱 실행 중 오류가 발생했습니다.")
    st.code(traceback.format_exc())
