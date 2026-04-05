import streamlit as st
import anthropic
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CurateAI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# MOCK DATA — PRD Section 5
# ══════════════════════════════════════════════════════════════════════════════

SHOPPER = {
    "handle": "@singh_amarjyot",
    "name": "Amarjyot Singh",
    "first_name": "Amarjyot",
    "mobile": "+91 7014363367",
    "tier": "Platinum",
    "points": 8240,
    "cashback_rate": 12,
    "purchase_history": ["Roadster", "H&M", "boAt"],
    "style_profile": "Streetwear, casual fashion, tech gadgets, premium audio, earth tones, bold fits",
    "avg_order_value": 4500,
    "addresses": ["Home — Bengaluru, Karnataka", "Office — Bengaluru, Karnataka"],
    "payment": ["UPI — GPay", "Credit Card — HDFC Millennia"],
}

DM_SENDERS = {
    "@sonambajwa": {
        "name": "Sonam Bajwa", "type": "friend", "avatar": "SB", "color": "#E91E8C",
        "verified": False,
        "demo_trigger": "not_in_network",
        "demo_product": None,
        "similars": ["F001", "F003", "F005"],
        "time": "2m", "unread": 2,
        "preview": "Hey! Check out this ethnic look 🔥",
        "prefilled": [
            ("them", "Hey AJ!! 👋"),
            ("them", "Omg look at this ethnic look I found!! 😍"),
            ("them", "You should totally get this! 🔥"),
        ],
        "banner_msg": "Fashion photo detected — searching merchant network...",
    },
    "@diljitdosanjh": {
        "name": "Diljit Dosanjh", "type": "friend", "avatar": "DD", "color": "#FF6B35",
        "verified": False,
        "demo_trigger": "exact_match",
        "demo_product": "F001",
        "similars": [],
        "time": "45m", "unread": 0,
        "preview": "Bro check this jacket 🧥",
        "prefilled": [
            ("them", "Yo AJ! 🙌"),
            ("them", "Bro check this H&M jacket 🧥"),
            ("them", "Found it on their site — looks fire!"),
        ],
        "banner_msg": "Product link detected — checking merchant network...",
    },
    "@virat.kohli": {
        "name": "Virat Kohli", "type": "friend", "avatar": "VK", "color": "#0066CC",
        "verified": False,
        "demo_trigger": "exact_match",
        "demo_product": "G001",
        "similars": [],
        "time": "1m", "unread": 0,
        "preview": "These earbuds are fire 🔥",
        "prefilled": [
            ("them", "Bhai check this out! 🎧"),
            ("them", "These boAt earbuds are fire 🔥"),
            ("them", "Using them at gym — absolute beast mode 💪"),
        ],
        "banner_msg": "Product photo detected — searching merchant network...",
    },
    "@hm_india": {
        "name": "H&M India", "type": "brand", "avatar": "HM", "color": "#E50010",
        "verified": True,
        "demo_trigger": "exact_match",
        "demo_product": "F001",
        "similars": [],
        "time": "1h", "unread": 1,
        "preview": "New drop just landed 🛍️",
        "prefilled": [
            ("them", "Hi Amarjyot! 👋"),
            ("them", "New drop just landed — check this out 🛍️"),
            ("them", "Oversized Hoodie in Olive — perfect for your style!"),
        ],
        "banner_msg": "Brand post detected — H&M is in our merchant network ✓",
    },
    "@boat.nirvana": {
        "name": "boAt", "type": "brand", "avatar": "bA", "color": "#FF0000",
        "verified": True,
        "demo_trigger": "exact_match",
        "demo_product": "G001",
        "similars": [],
        "time": "3h", "unread": 0,
        "preview": "Bestseller back in stock ⚡",
        "prefilled": [
            ("them", "Hey Amarjyot! ⚡"),
            ("them", "Our bestseller Airdopes 141 is back in stock!"),
            ("them", "Grab it before it sells out again 🎧"),
        ],
        "banner_msg": "Brand post detected — boAt is in our merchant network ✓",
    },
    "@pumaindia": {
        "name": "Puma India", "type": "brand", "avatar": "PM", "color": "#1a1a1a",
        "verified": True,
        "demo_trigger": "not_in_network",
        "demo_product": None,
        "similars": ["F004", "F005"],
        "time": "2h", "unread": 0,
        "preview": "New season kicks 👟",
        "prefilled": [
            ("them", "Hey Amarjyot! 👟"),
            ("them", "New season collection just dropped!"),
            ("them", "Check out our latest running shoes 🏃"),
        ],
        "banner_msg": "Brand post detected — finding best alternatives in our network...",
    },
}

CATALOG = {
    "F001": {"id":"F001","name":"Oversized Drop Shoulder Hoodie","variant":"Olive","brand":"H&M","category":"Men's Fashion","emoji":"🧥","mrp":2999,"best_price":1979,"platform":"H&M.com","discount":34,"coupon":"HM30","cashback":180,"stock":"available"},
    "F002": {"id":"F002","name":"Slim Fit Chinos","variant":"Khaki","brand":"Roadster","category":"Men's Fashion","emoji":"👖","mrp":1799,"best_price":1079,"platform":"Myntra","discount":40,"coupon":"ROAD40","cashback":90,"stock":"available"},
    "F003": {"id":"F003","name":"Acid Wash Tee","variant":"Black","brand":"Bonkers Corner","category":"Men's Fashion","emoji":"👕","mrp":1299,"best_price":909,"platform":"BonkersCorner.com","discount":30,"coupon":"BONK20","cashback":70,"stock":"available"},
    "F004": {"id":"F004","name":"Casual Lace-Up Sneakers","variant":"White","brand":"Red Tape","category":"Footwear","emoji":"👟","mrp":3499,"best_price":2099,"platform":"RedTape.com","discount":40,"coupon":"RT40NOW","cashback":200,"stock":"available"},
    "F005": {"id":"F005","name":"Oversized Graphic Tee","variant":"White","brand":"Comet","category":"Men's Fashion","emoji":"👕","mrp":1499,"best_price":1049,"platform":"Comet.in","discount":30,"coupon":None,"cashback":80,"stock":"available"},
    "G001": {"id":"G001","name":"Airdopes 141","variant":"True Wireless Earbuds","brand":"boAt","category":"Audio","emoji":"🎧","mrp":1999,"best_price":999,"platform":"Amazon","discount":50,"coupon":"BOAT50","cashback":100,"stock":"available"},
    "G002": {"id":"G002","name":"Rockerz 450","variant":"Wireless Headphones","brand":"boAt","category":"Audio","emoji":"🎧","mrp":3990,"best_price":1799,"platform":"boAt.in","discount":55,"coupon":"ROCKERZ55","cashback":180,"stock":"available"},
    "G003": {"id":"G003","name":"WH-1000XM5","variant":"Noise Cancelling","brand":"Sony","category":"Audio","emoji":"🎧","mrp":29990,"best_price":22490,"platform":"Sony.in","discount":25,"coupon":"SONY25","cashback":2200,"stock":"available"},
    "G004": {"id":"G004","name":"Stone 352 Speaker","variant":"Blue","brand":"boAt","category":"Audio","emoji":"🔊","mrp":2999,"best_price":1299,"platform":"Flipkart","discount":57,"coupon":"STONE57","cashback":120,"stock":"low_stock"},
}

PROFILE_RECS = ["F001", "F002", "G001", "G002"]

# ── Loyalty calculation ────────────────────────────────────────────────────────
def calc_loyalty(cart_value, points):
    if cart_value <= 1000:      r_pct, lr_rate, e_pct, e_rate = 0.10, 0.5,  0.075, 0.2
    elif cart_value <= 2000:    r_pct, lr_rate, e_pct, e_rate = 0.075, 0.35, 0.05,  0.35
    elif cart_value <= 5000:    r_pct, lr_rate, e_pct, e_rate = 0.05,  0.30, 0.035, 0.4
    else:                       r_pct, lr_rate, e_pct, e_rate = 0.035, 0.25, 0.025, 0.5
    redeem_pts = min(points, cart_value * r_pct)
    return {
        "redeemable_pts": int(redeem_pts),
        "discount_rs": round(redeem_pts * lr_rate, 2),
        "points_earned": int(cart_value * e_pct * e_rate),
        "lr_rate": lr_rate,
    }

# ── LLM — only for product moments ────────────────────────────────────────────
def ask_llm(prompt, fallback):
    try:
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key or len(key) < 20:
            return fallback
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception:
        return fallback

PERSONA = "You are CurateAI, a warm personal shopping concierge inside Instagram DM. Be warm, concise (1-2 sentences), natural. Use first name."

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init():
    defaults = {
        "screen": "dm_list",
        "active_sender": None,
        "logged_in": False,
        "login_step": "mobile",
        "otp_attempts": 0,
        "messages": [],
        "trigger": None,
        "matched_product": None,
        "similars": [],
        "selected_pid": None,
        "loyalty_data": None,
        "shop_done": False,
        "price_done": False,
        "loyalty_done": False,
        "checkout_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

def reset_journey():
    for k in ["messages","trigger","matched_product","similars","selected_pid",
              "loyalty_data","shop_done","price_done","loyalty_done","checkout_done"]:
        if k in ["messages","similars"]:
            st.session_state[k] = []
        elif k in ["shop_done","price_done","loyalty_done","checkout_done"]:
            st.session_state[k] = False
        else:
            st.session_state[k] = None
    for k in list(st.session_state.keys()):
        if k.startswith("seeded_"):
            del st.session_state[k]

def add_msg(role, content, mtype="text", data=None):
    st.session_state.messages.append({
        "role": role, "content": content,
        "type": mtype, "data": data,
        "time": time.strftime("%I:%M %p")
    })

def ts():
    return time.strftime("%I:%M %p")

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #fff !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Sora', sans-serif;
}
#MainMenu, footer, header, [data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 430px !important; margin: 0 auto !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="element-container"] { padding: 0 !important; margin: 0 !important; }

/* Header */
.ig-hdr {
    background: #fff; border-bottom: 1px solid #EFEFEF;
    padding: 10px 16px; display: flex; align-items: center; gap: 10px;
    position: sticky; top: 0; z-index: 100;
}
.ig-av {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.ig-name { font-size: 14px; font-weight: 600; color: #000; }
.ig-sub  { font-size: 11px; color: #8E8E8E; }

/* Chat */
.chat-area { padding: 12px 14px 16px; background: #fff; }
.bubble-them {
    display: inline-block; max-width: 75%;
    background: #EFEFEF; color: #000;
    padding: 10px 14px; border-radius: 18px 18px 18px 4px;
    font-size: 14px; line-height: 1.45; margin-bottom: 2px;
}
.bubble-me {
    display: inline-block; max-width: 75%;
    background: #0095F6; color: #fff;
    padding: 10px 14px; border-radius: 18px 18px 4px 18px;
    font-size: 14px; line-height: 1.45; margin-bottom: 2px;
    margin-left: auto;
}
.msg-time { font-size: 10px; color: #C7C7C7; margin: 2px 0 8px; }
.msg-time.right { text-align: right; }
.banner-pill {
    background: #F5F5F5; border-radius: 20px;
    padding: 6px 14px; font-size: 12px; color: #555;
    text-align: center; margin: 8px 0;
}

/* Product card */
.p-card {
    background: #fff; border: 1px solid #EFEFEF;
    border-radius: 16px; overflow: hidden;
    margin: 6px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.p-card-img {
    background: linear-gradient(135deg, #F8F4FF, #EEF2FF);
    height: 140px; display: flex; align-items: center;
    justify-content: center; font-size: 64px; position: relative;
}
.p-card-disc {
    position: absolute; top: 10px; right: 10px;
    background: #FF3B30; color: #fff; font-size: 10px;
    font-weight: 700; padding: 2px 7px; border-radius: 20px;
}
.p-card-net {
    position: absolute; top: 10px; left: 10px;
    background: #0095F6; color: #fff; font-size: 9px;
    font-weight: 700; padding: 2px 7px; border-radius: 20px;
}
.p-card-body { padding: 12px 14px; }
.p-card-brand { font-size: 10px; color: #8E8E8E; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
.p-card-name { font-size: 15px; font-weight: 700; color: #000; margin-top: 2px; }
.p-card-var { font-size: 12px; color: #8E8E8E; }
.p-card-prices { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.p-card-price { font-size: 18px; font-weight: 700; color: #000; }
.p-card-mrp { font-size: 12px; color: #C7C7C7; text-decoration: line-through; }
.p-card-plat { font-size: 11px; color: #0095F6; margin-top: 4px; }
.p-card-coup { font-size: 11px; color: #FF9500; margin-top: 2px; }

/* Carousel card */
.c-card {
    background: #fff; border: 1px solid #EFEFEF;
    border-radius: 12px; padding: 11px;
    display: flex; gap: 10px; align-items: center;
    margin: 5px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.c-em { font-size: 30px; background: #F8F4FF; border-radius: 8px;
    width: 50px; height: 50px; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0; }
.c-brand { font-size: 9px; color: #8E8E8E; font-weight: 700; text-transform: uppercase; }
.c-name { font-size: 13px; font-weight: 600; color: #000; }
.c-price { font-size: 14px; font-weight: 700; color: #000; }
.c-mrp { font-size: 10px; color: #C7C7C7; text-decoration: line-through; margin-left: 4px; }
.c-disc { font-size: 9px; font-weight: 700; color: #FF3B30;
    background: rgba(255,59,48,.08); padding: 1px 5px; border-radius: 4px; margin-left: 4px; }

/* Skeleton */
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
.sk { background: linear-gradient(90deg,#F0F0F0 25%,#E8E8E8 50%,#F0F0F0 75%);
    background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 8px; }
.sk-card { border: 1px solid #EFEFEF; border-radius: 14px; overflow: hidden; margin: 6px 0; }
.sk-img { height: 100px; }
.sk-body { padding: 12px; }
.sk-line { height: 11px; margin-bottom: 7px; }

/* Price card */
.pr-card { background: #fff; border: 1px solid #EFEFEF; border-radius: 16px; overflow: hidden; margin: 6px 0; }
.pr-hdr { background: linear-gradient(135deg,#0095F6,#0066CC); padding: 12px 14px; }
.pr-hdr-t { font-size: 13px; font-weight: 700; color: #fff; }
.pr-hdr-s { font-size: 11px; color: rgba(255,255,255,.8); margin-top: 2px; }
.pr-body { padding: 12px 14px; }
.pr-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #F5F5F5; font-size: 13px; }
.pr-row:last-child { border-bottom: none; }
.pr-lbl { color: #8E8E8E; }
.pr-val { font-weight: 600; color: #000; }
.pr-val-g { font-weight: 600; color: #22C55E; }
.pr-val-o { font-weight: 600; color: #FF9500; }
.pr-val-s { text-decoration: line-through; color: #C7C7C7; }
.pr-final { font-size: 22px; font-weight: 700; color: #000; margin-top: 10px; }
.pr-final-s { font-size: 11px; color: #8E8E8E; }
.coup-box { background: rgba(255,149,0,.08); border: 1px dashed #FF9500;
    border-radius: 8px; padding: 8px 12px; margin-top: 10px;
    font-size: 12px; color: #FF9500; font-weight: 600; }

/* Loyalty card */
.loy-card { background: linear-gradient(135deg,#0a0a1a,#1a0a3a);
    border-radius: 16px; padding: 16px; margin: 6px 0; }
.loy-tier { font-size: 10px; font-weight: 700; color: #A855F7; letter-spacing: 1px; }
.loy-pts { font-size: 28px; font-weight: 700; color: #fff; margin-top: 4px; }
.loy-pts-s { font-size: 11px; color: rgba(255,255,255,.4); }
.loy-bar-bg { background: rgba(255,255,255,.1); border-radius: 99px; height: 4px; margin-top: 10px; }
.loy-bar { background: linear-gradient(90deg,#6C47FF,#A855F7); border-radius: 99px; height: 4px; }
.loy-rdm { margin-top: 12px; background: rgba(255,255,255,.06); border-radius: 10px; padding: 10px; }
.loy-rdm-l { font-size: 10px; color: rgba(255,255,255,.4); }
.loy-rdm-v { font-size: 18px; font-weight: 700; color: #22C55E; margin-top: 2px; }
.loy-earn { font-size: 11px; color: rgba(255,255,255,.4); margin-top: 8px; }

/* Checkout card */
.co-card { background: #fff; border: 1px solid #EFEFEF; border-radius: 16px; overflow: hidden; margin: 6px 0; }
.co-hdr { padding: 14px; border-bottom: 1px solid #EFEFEF; }
.co-hdr-t { font-size: 15px; font-weight: 700; color: #000; }
.co-hdr-s { font-size: 11px; color: #8E8E8E; margin-top: 2px; }
.co-sec { padding: 10px 14px; border-bottom: 1px solid #F5F5F5; }
.co-sec-t { font-size: 10px; font-weight: 700; color: #8E8E8E; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
.co-total { font-size: 22px; font-weight: 700; color: #000; }
.co-saved { font-size: 12px; color: #22C55E; font-weight: 600; margin-top: 2px; }

/* Success card */
.suc-card { background: linear-gradient(135deg,#F0FDF4,#DCFCE7);
    border: 1px solid #22C55E; border-radius: 16px; padding: 18px; margin: 6px 0; }
.suc-row { display: flex; justify-content: space-between; padding: 6px 0;
    border-bottom: 1px solid rgba(34,197,94,.15); font-size: 12px; }
.suc-l { color: #6B7280; }
.suc-v { color: #000; font-weight: 600; }

/* Buttons */
.stButton > button {
    background: #0095F6 !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; padding: 11px 20px !important;
    font-family: -apple-system,BlinkMacSystemFont,sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    width: 100% !important; min-height: 44px !important;
    cursor: pointer !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:disabled { background: #E0E0E0 !important; color: #999 !important; }

/* Open pill on DM list */
.open-pill > div > button {
    background: transparent !important;
    border: 1.5px solid #DBDBDB !important;
    border-radius: 20px !important;
    color: #000 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 5px 14px !important;
    min-height: unset !important;
    height: auto !important;
    width: auto !important;
}

/* Invisible tap buttons on DM rows */
.tap-btn > div > button {
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: transparent !important;
    font-size: 1px !important; opacity: 0 !important;
    position: relative !important; margin-top: -72px !important;
    height: 72px !important; z-index: 10 !important;
    border-radius: 0 !important; padding: 0 !important;
}

/* Inputs */
[data-testid="stTextInput"] input {
    background: #FAFAFA !important; border: 1.5px solid #DBDBDB !important;
    border-radius: 10px !important; color: #000 !important;
    padding: 10px 14px !important; font-size: 15px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #0095F6 !important;
    box-shadow: 0 0 0 2px rgba(0,149,246,0.15) !important;
    background: #fff !important;
}
[data-testid="stTextInput"] label { font-size: 13px !important; color: #555 !important; }
[data-testid="stSelectbox"] > div > div { background: #FAFAFA !important; border: 1.5px solid #DBDBDB !important; border-radius: 10px !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; background: #fff !important;
    border-bottom: 1px solid #F2F2F2 !important; align-items: center !important; padding: 0 !important; }
[data-testid="stHorizontalBlock"] > div { background: #fff !important; padding: 0 !important; }
hr { border-color: #EFEFEF !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_product_card(pid):
    p = CATALOG[pid]
    coup = f'<div class="p-card-coup">🏷️ Code: <b>{p["coupon"]}</b></div>' if p.get("coupon") else ""
    low = '<div style="font-size:10px;color:#FF3B30;margin-top:2px;font-weight:600">⚠️ Only a few left</div>' if p["stock"] == "low_stock" else ""
    st.markdown(f"""
    <div class="p-card">
      <div class="p-card-img">
        <span>{p["emoji"]}</span>
        <div class="p-card-disc">{p["discount"]}% OFF</div>
        <div class="p-card-net">✓ In Network</div>
      </div>
      <div class="p-card-body">
        <div class="p-card-brand">{p["brand"]}</div>
        <div class="p-card-name">{p["name"]}</div>
        <div class="p-card-var">{p["variant"]}</div>
        <div class="p-card-prices">
          <span class="p-card-price">₹{p["best_price"]:,}</span>
          <span class="p-card-mrp">₹{p["mrp"]:,}</span>
        </div>
        <div class="p-card-plat">via {p["platform"]} · KwikAI</div>
        {coup}{low}
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_carousel(pids, label="You may also like"):
    st.markdown(f'<div style="font-size:11px;font-weight:700;color:#8E8E8E;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">{label}</div>', unsafe_allow_html=True)
    for pid in pids:
        p = CATALOG[pid]
        coup = f'<span style="font-size:9px;color:#FF9500">🏷️ {p["coupon"]}</span>' if p.get("coupon") else ""
        st.markdown(f"""
        <div class="c-card">
          <div class="c-em">{p["emoji"]}</div>
          <div style="flex:1;min-width:0">
            <div class="c-brand">{p["brand"]}</div>
            <div class="c-name">{p["name"]}</div>
            <div style="display:flex;align-items:center;margin-top:3px">
              <span class="c-price">₹{p["best_price"]:,}</span>
              <span class="c-mrp">₹{p["mrp"]:,}</span>
              <span class="c-disc">{p["discount"]}% OFF</span>
            </div>
            {coup}
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_skeleton():
    st.markdown("""
    <div class="sk-card"><div class="sk sk-img"></div>
    <div class="sk-body"><div class="sk sk-line" style="width:50%"></div>
    <div class="sk sk-line" style="width:75%"></div>
    <div class="sk sk-line" style="width:40%"></div></div></div>
    <div class="sk-card" style="margin-top:6px"><div class="sk-body">
    <div class="sk sk-line" style="width:70%"></div>
    <div class="sk sk-line" style="width:45%"></div></div></div>
    """, unsafe_allow_html=True)

def render_price_card(pid):
    p = CATALOG[pid]
    coup = f'<div class="coup-box">🏷️ Apply code <b style="margin-left:4px">{p["coupon"]}</b> at checkout</div>' if p.get("coupon") else ""
    st.markdown(f"""
    <div class="pr-card">
      <div class="pr-hdr">
        <div class="pr-hdr-t">{p["emoji"]} {p["name"]}</div>
        <div class="pr-hdr-s">Best price found · {p["platform"]}</div>
      </div>
      <div class="pr-body">
        <div class="pr-row"><span class="pr-lbl">MRP</span><span class="pr-val-s">₹{p["mrp"]:,}</span></div>
        <div class="pr-row"><span class="pr-lbl">Merchant discount ({p["discount"]}%)</span><span class="pr-val-g">−₹{p["mrp"]-p["best_price"]:,}</span></div>
        <div class="pr-row"><span class="pr-lbl">Cashback after purchase</span><span class="pr-val-o">+₹{p["cashback"]:,} LR</span></div>
        <div class="pr-final">₹{p["best_price"]:,}</div>
        <div class="pr-final-s">Best available · {p["platform"]} via KwikAI</div>
        {coup}
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_loyalty_card(ld):
    pts = SHOPPER["points"]
    pct = min(100, int(pts / 10000 * 100))
    st.markdown(f"""
    <div class="loy-card">
      <div class="loy-tier">★ {SHOPPER["tier"]} MEMBER</div>
      <div class="loy-pts">{pts:,} <span style="font-size:14px;font-weight:400;color:rgba(255,255,255,.4)">LR</span></div>
      <div class="loy-pts-s">Available loyalty points</div>
      <div class="loy-bar-bg"><div class="loy-bar" style="width:{pct}%"></div></div>
      <div class="loy-rdm">
        <div class="loy-rdm-l">Redeemable on this order</div>
        <div class="loy-rdm-v">−₹{ld["discount_rs"]:,.0f}</div>
        <div style="font-size:10px;color:rgba(255,255,255,.35);margin-top:2px">{ld["redeemable_pts"]:,} pts × ₹{ld["lr_rate"]}/LR</div>
      </div>
      <div class="loy-earn">+{ld["points_earned"]:,} LR earned on this order</div>
    </div>
    """, unsafe_allow_html=True)

def render_checkout_card(pid, ld):
    p = CATALOG[pid]
    final = p["best_price"] - ld["discount_rs"]
    saved = p["mrp"] - final
    st.markdown(f"""
    <div class="co-card">
      <div class="co-hdr">
        <div class="co-hdr-t">Your personalised cart ✦</div>
        <div class="co-hdr-s">Identity pre-filled · Rewards applied · Best price locked</div>
      </div>
      <div class="co-sec"><div class="co-sec-t">Delivering to</div>
        <div style="font-size:13px;color:#000">📍 {SHOPPER["addresses"][0]}</div></div>
      <div class="co-sec"><div class="co-sec-t">Payment</div>
        <div style="font-size:13px;color:#000">💳 {SHOPPER["payment"][0]}</div></div>
      <div class="co-sec">
        <div class="co-sec-t">Order summary</div>
        <div class="pr-row"><span class="pr-lbl">{p["name"]}</span><span class="pr-val">₹{p["mrp"]:,}</span></div>
        <div class="pr-row"><span class="pr-lbl">Merchant deal</span><span class="pr-val-g">−₹{p["mrp"]-p["best_price"]:,}</span></div>
        <div class="pr-row"><span class="pr-lbl">Loyalty points</span><span class="pr-val-g">−₹{ld["discount_rs"]:,.0f}</span></div>
        <div class="pr-row"><span class="pr-lbl">Cashback earned</span><span class="pr-val-o">+₹{p["cashback"]:,} LR</span></div>
      </div>
      <div style="padding:12px 14px">
        <div class="co-total">₹{final:,.0f}</div>
        <div class="co-saved">You save ₹{saved:,.0f} total 🎉</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_success_card(pid, ld, order_id, delivery):
    p = CATALOG[pid]
    st.markdown(f"""
    <div class="suc-card">
      <div style="text-align:center;margin-bottom:12px">
        <div style="font-size:40px">✅</div>
        <div style="font-size:17px;font-weight:700;color:#000;margin-top:6px">Order Confirmed!</div>
        <div style="font-size:12px;color:#16A34A;font-weight:600;margin-top:2px">{p["brand"]} order is on its way</div>
      </div>
      <div class="suc-row"><span class="suc-l">Order ID</span><span class="suc-v">KWK{order_id}</span></div>
      <div class="suc-row"><span class="suc-l">Product</span><span class="suc-v">{p["name"]}</span></div>
      <div class="suc-row"><span class="suc-l">Delivering to</span><span class="suc-v">Home, Bengaluru</span></div>
      <div class="suc-row"><span class="suc-l">Est. delivery</span><span class="suc-v">{delivery}</span></div>
      <div class="suc-row"><span class="suc-l">Points earned</span><span class="suc-v" style="color:#22C55E">+{ld["points_earned"]:,} LR</span></div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_messages():
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        mtype = msg.get("type", "text")
        data = msg.get("data")
        t = msg.get("time", "")

        if role == "banner":
            st.markdown(f'<div class="banner-pill">🔗 {content}</div>', unsafe_allow_html=True)

        elif role == "them":
            st.markdown(f'<div class="bubble-them">{content}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)

        elif role == "me":
            st.markdown(f'<div style="text-align:right"><div class="bubble-me">{content}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-time right">{t}</div>', unsafe_allow_html=True)

        elif role == "agent":
            if mtype == "text":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#0095F6;margin-bottom:2px">✦ CurateAI</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F8F9FF;border:1px solid #E8EEFF;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;line-height:1.45;color:#000;max-width:88%;margin-bottom:4px">{content}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)
            elif mtype == "product_exact":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#0095F6;margin-bottom:2px">✦ CurateAI — Found it!</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F8F9FF;border:1px solid #E8EEFF;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;color:#000;max-width:88%;margin-bottom:6px">{content}</div>', unsafe_allow_html=True)
                render_product_card(data)
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)
            elif mtype == "product_carousel":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#0095F6;margin-bottom:2px">✦ CurateAI — Similar picks</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F8F9FF;border:1px solid #E8EEFF;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;color:#000;max-width:88%;margin-bottom:6px">{content}</div>', unsafe_allow_html=True)
                render_carousel(data["pids"], data.get("label","You may also like"))
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)
            elif mtype == "price_card":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#0095F6;margin-bottom:2px">✦ CurateAI — Best Price</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F8F9FF;border:1px solid #E8EEFF;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;color:#000;max-width:88%;margin-bottom:6px">{content}</div>', unsafe_allow_html=True)
                render_price_card(data["pid"])
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)
            elif mtype == "loyalty_card":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#0095F6;margin-bottom:2px">✦ CurateAI — Your Rewards</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F8F9FF;border:1px solid #E8EEFF;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;color:#000;max-width:88%;margin-bottom:6px">{content}</div>', unsafe_allow_html=True)
                render_loyalty_card(data)
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)
            elif mtype == "checkout_card":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#0095F6;margin-bottom:2px">✦ CurateAI — Your Cart</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F8F9FF;border:1px solid #E8EEFF;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;color:#000;max-width:88%;margin-bottom:6px">{content}</div>', unsafe_allow_html=True)
                render_checkout_card(data["pid"], data["ld"])
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)
            elif mtype == "success_card":
                st.markdown(f'<div style="font-size:10px;font-weight:600;color:#22C55E;margin-bottom:2px">✦ CurateAI — Order Confirmed</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#F0FDF4;border:1px solid #DCFCE7;border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:14px;color:#000;max-width:88%;margin-bottom:6px">{content}</div>', unsafe_allow_html=True)
                render_success_card(data["pid"], data["ld"], data["order_id"], data["delivery"])
                st.markdown(f'<div class="msg-time">{t}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: DM LIST
# ══════════════════════════════════════════════════════════════════════════════
def screen_dm_list():
    st.markdown("""
    <div style="background:#fff;padding:14px 16px 0;display:flex;align-items:center;justify-content:space-between">
      <div style="display:flex;align-items:center;gap:5px">
        <span style="font-size:17px;font-weight:700;color:#000">singh_amarjyot</span>
        <span style="font-size:12px;color:#000">&#9660;</span>
      </div>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 000-1.41l-2.34-2.34a1 1 0 00-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="#000"/>
      </svg>
    </div>
    <div style="background:#fff;display:flex;border-bottom:1px solid #EFEFEF;margin-top:10px">
      <div style="flex:1;text-align:center;padding:10px 0;font-size:14px;font-weight:700;color:#000;border-bottom:2px solid #000">Primary</div>
      <div style="flex:1;text-align:center;padding:10px 0;font-size:14px;color:#8E8E8E">Agents</div>
      <div style="flex:1;text-align:center;padding:10px 0;font-size:14px;color:#8E8E8E">Requests <span style="background:#0095F6;color:#fff;font-size:10px;font-weight:700;padding:1px 6px;border-radius:10px">2</span></div>
    </div>
    <div style="background:#fff;padding:8px 16px 6px">
      <div style="background:#EFEFEF;border-radius:10px;padding:8px 14px;font-size:14px;color:#8E8E8E;display:flex;align-items:center;gap:6px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="7" stroke="#8E8E8E" stroke-width="2.2"/><path d="M16.5 16.5L21 21" stroke="#8E8E8E" stroke-width="2.2" stroke-linecap="round"/></svg>
        Search
      </div>
    </div>
    """, unsafe_allow_html=True)

    ROWS = [
        {"key":"@curate",        "name":"CurateAI",       "av":"✦",  "color":"linear-gradient(135deg,#1a1a2e,#2d1b69)", "verified":True,  "agent":True,  "unread":0, "time":"",    "preview":"Hey! Ready to help you shop smarter"},
        {"key":"@sonambajwa",    "name":"Sonam Bajwa",    "av":"SB", "color":"#E91E8C", "verified":False, "agent":False, "unread":2, "time":"2m",  "preview":"Hey! Check out this ethnic look 🔥"},
        {"key":"@diljitdosanjh", "name":"Diljit Dosanjh", "av":"DD", "color":"#FF6B35", "verified":False, "agent":False, "unread":0, "time":"45m", "preview":"Bro check this jacket 🧥"},
        {"key":"@hm_india",      "name":"H&M India",      "av":"HM", "color":"#E50010", "verified":True,  "agent":False, "unread":1, "time":"1h",  "preview":"New drop just landed 🛍️"},
        {"key":"@virat.kohli",   "name":"Virat Kohli",    "av":"VK", "color":"#0066CC", "verified":False, "agent":False, "unread":0, "time":"1m",  "preview":"These earbuds are fire 🔥"},
        {"key":"@boat.nirvana",  "name":"boAt",           "av":"bA", "color":"#FF0000", "verified":True,  "agent":False, "unread":0, "time":"3h",  "preview":"Bestseller back in stock ⚡"},
        {"key":"@pumaindia",     "name":"Puma India",     "av":"PM", "color":"#1a1a1a", "verified":True,  "agent":False, "unread":0, "time":"2h",  "preview":"New season kicks 👟"},
    ]
    FRIENDS = {"@sonambajwa","@diljitdosanjh","@virat.kohli"}

    for r in ROWS:
        unread = r["unread"]
        nw = "700" if unread > 0 else "500"
        pc = "#262626" if unread > 0 else "#8E8E8E"
        pw = "600" if unread > 0 else "400"

        online = ""
        if r["key"] in FRIENDS:
            online = '<div style="position:absolute;bottom:1px;right:1px;width:13px;height:13px;border-radius:50%;background:#22C55E;border:2px solid #fff"></div>'
        vtick = ""
        if r["verified"] and not r["agent"]:
            vtick = '<svg width="13" height="13" viewBox="0 0 24 24" style="vertical-align:middle;margin-left:3px"><path d="M9 12l2 2 4-4m5 2a9 9 0 11-18 0 9 9 0 0118 0z" fill="#0095F6"/></svg>'
        agent_badge = '<span style="background:#0095F6;color:#fff;font-size:9px;font-weight:700;padding:2px 6px;border-radius:10px;margin-left:5px;vertical-align:middle">AI Agent</span>' if r["agent"] else ""
        badge = f'<span style="background:#0095F6;color:#fff;font-size:10px;font-weight:700;min-width:18px;height:18px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;padding:0 3px">{unread}</span>' if unread > 0 else ""
        av_size = "22px" if r["agent"] else "15px"

        c1, c2 = st.columns([7, 3])
        with c1:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0 10px 16px;background:#fff;min-height:72px">'
                f'<div style="position:relative;flex-shrink:0">'
                f'<div style="width:54px;height:54px;border-radius:50%;background:{r["color"]};display:flex;align-items:center;justify-content:center;font-size:{av_size};font-weight:700;color:#fff">{r["av"]}</div>'
                f'{online}</div>'
                f'<div style="flex:1;min-width:0">'
                f'<div style="font-size:14px;font-weight:{nw};color:#000">{r["name"]}{vtick}{agent_badge}</div>'
                f'<div style="font-size:13px;color:{pc};font-weight:{pw};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{r["preview"]}</div>'
                f'</div>'
                f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;flex-shrink:0;padding-right:8px">'
                f'<span style="font-size:12px;color:#8E8E8E">{r["time"]}</span>{badge}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with c2:
            st.markdown('<div class="open-pill">', unsafe_allow_html=True)
            if st.button("Open", key=f"dm_{r['key']}"):
                reset_journey()
                if r["key"] == "@curate":
                    st.session_state.screen = "curate_chat"
                    st.session_state.active_sender = None
                else:
                    st.session_state.active_sender = r["key"]
                    st.session_state.screen = "sender_chat"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="height:70px"></div>
    <div style="position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:430px;max-width:100vw;
        background:#fff;border-top:1px solid #EFEFEF;padding:10px 0 20px;
        display:flex;justify-content:space-around;align-items:center;z-index:200">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" opacity="0.4"><path d="M3 12L12 3l9 9M5 10v9a1 1 0 001 1h4v-5h4v5h4a1 1 0 001-1v-9" stroke="#000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" opacity="0.4"><rect x="2" y="2" width="9" height="9" rx="1.5" stroke="#000" stroke-width="1.8"/><rect x="13" y="2" width="9" height="9" rx="1.5" stroke="#000" stroke-width="1.8"/><rect x="2" y="13" width="9" height="9" rx="1.5" stroke="#000" stroke-width="1.8"/><rect x="13" y="13" width="9" height="9" rx="1.5" stroke="#000" stroke-width="1.8"/></svg>
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" opacity="0.4"><path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z" stroke="#000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" opacity="0.4"><circle cx="11" cy="11" r="8" stroke="#000" stroke-width="1.8"/><path d="M21 21l-4.35-4.35" stroke="#000" stroke-width="1.8" stroke-linecap="round"/></svg>
      <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);border:2px solid #000"></div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def screen_login():
    sk = st.session_state.get("active_sender")
    sender_name = DM_SENDERS[sk]["name"] if sk and sk in DM_SENDERS else "your friend"
    step = st.session_state.get("login_step", "mobile")

    # Activation banner only — header already rendered by caller
    st.markdown("""
    <div style="display:flex;justify-content:center;padding:10px 16px 4px;background:#fff">
      <div style="background:#F0F0F5;border-radius:20px;padding:6px 14px;font-size:12px;color:#555">
        🔗 Product detected &nbsp;|&nbsp; <span style="color:#6C47FF;font-weight:600">CurateAI activated ✦</span>
      </div>
    </div>
    <div style="height:6px;background:#fff"></div>
    """, unsafe_allow_html=True)

    if step == "mobile":
        st.markdown("### 👋 Hey! I'm **CurateAI**")
        st.markdown("Your personal shopping concierge. Login once to unlock **best prices, loyalty rewards & instant checkout.**")
        st.markdown("*🔒 Only you can see this conversation — not any friend or brand.*")
        st.markdown("---")
        st.markdown("**📞 Mobile Number** *(auto-detected from Instagram)*")
        c1, c2 = st.columns([1, 4])
        with c1:
            st.text_input("cc", value="+91", disabled=True, label_visibility="collapsed")
        with c2:
            st.text_input("num", value="7014363367", label_visibility="collapsed", key="mobile_val")
        st.caption("✓ Auto-detected from your Instagram account")
        st.markdown(" ")
        if st.button("Send OTP", key="send_otp_btn", use_container_width=True):
            st.session_state.login_step = "otp"
            st.rerun()
        st.caption("🔒 100% Secure | End to End Encrypted Chat")

    elif step == "otp":
        st.markdown("### OTP sent to **7014363367**")
        st.markdown("Enter any 6 digits to continue *(demo)*")
        st.markdown("---")
        otp = st.text_input("OTP", placeholder="Enter 6-digit OTP", max_chars=6, key="otp_input", label_visibility="collapsed")
        filled = len(otp) if otp else 0
        boxes = ""
        for i in range(6):
            if i < filled:
                boxes += f'<span style="display:inline-flex;width:42px;height:48px;border-radius:10px;background:#0095F6;color:#fff;font-size:18px;font-weight:700;align-items:center;justify-content:center;margin:0 3px">{otp[i]}</span>'
            else:
                boxes += '<span style="display:inline-flex;width:42px;height:48px;border-radius:10px;background:#F0F0F0;margin:0 3px"></span>'
        st.markdown(f'<div style="display:flex;justify-content:center;margin:8px 0">{boxes}</div>', unsafe_allow_html=True)
        st.markdown(" ")
        if filled == 6:
            if st.button("✓ Verify & Continue", key="verify_btn", use_container_width=True):
                st.session_state.login_step = "success"
                st.session_state.logged_in = True
                st.rerun()
        else:
            st.button("Verify & Continue", key="verify_disabled", use_container_width=True, disabled=True)
        st.caption("🔒 100% Secure | End to End Encrypted Chat")

    elif step == "success":
        st.markdown("## ✅ Account created!")
        st.markdown(f"Your profile, addresses & preferences are all set.")
        st.markdown("---")
        # Set context from sender before going to shop
        sk = st.session_state.get("active_sender")
        if sk and sk in DM_SENDERS:
            s = DM_SENDERS[sk]
            product_context = f"I found the product shared by **{sender_name}**. Let me surface the best deals 🎯"
        else:
            product_context = f"Let me show you picks based on your style — {', '.join(SHOPPER['purchase_history'])} 🎯"
        st.markdown(product_context)
        st.markdown(" ")
        if st.button("✦  Show Me the Products", key="show_products_btn", use_container_width=True):
            # Set trigger context
            if sk and sk in DM_SENDERS:
                s = DM_SENDERS[sk]
                st.session_state.trigger = s["demo_trigger"]
                st.session_state.matched_product = s["demo_product"]
                st.session_state.similars = s["similars"] if s["similars"] else PROFILE_RECS
            else:
                st.session_state.trigger = "profile"
                st.session_state.matched_product = None
                st.session_state.similars = PROFILE_RECS
            st.session_state.login_step = "mobile"
            st.session_state.screen = "shop"
            add_msg("me", "Show me the products!")
            st.rerun()
        st.caption("🔒 100% Secure | End to End Encrypted Chat")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: SENDER CHAT
# ══════════════════════════════════════════════════════════════════════════════
def screen_sender_chat():
    sk = st.session_state.active_sender
    s = DM_SENDERS[sk]

    # Header
    st.markdown(f"""
    <div class="ig-hdr">
      <span style="font-size:20px;color:#000">←</span>
      <div class="ig-av" style="background:{s["color"]}">{s["avatar"]}</div>
      <div>
        <div class="ig-name">{s["name"]}</div>
        <div class="ig-sub" style="color:#22C55E">Active now</div>
      </div>
      <div style="margin-left:auto;color:#000;font-size:18px">📞 &nbsp; 🎥</div>
    </div>
    """, unsafe_allow_html=True)

    # Seed prefilled messages ONCE per sender — flag prevents re-seeding on rerun
    seeded_key = f"seeded_{sk}"
    if not st.session_state.get(seeded_key, False):
        st.session_state.messages = []
        for _role, _msg in s["prefilled"]:
            st.session_state.messages.append({"role": _role, "content": _msg, "type": "text", "data": None, "time": ts()})
        st.session_state.messages.append({"role": "banner", "content": s["banner_msg"], "type": "banner", "data": None, "time": ts()})
        st.session_state[seeded_key] = True

    scr = st.session_state.screen

    # Route to login if needed
    if scr == "login":
        screen_login()
        return

    # Render all messages ONCE
    render_chat_messages()

    # Stage routing — stages only render CTAs, not messages
    if scr == "sender_chat":
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("✦ Start Shopping with CurateAI", key="start_shop_btn", use_container_width=True):
            st.session_state.trigger = s["demo_trigger"]
            st.session_state.matched_product = s["demo_product"]
            st.session_state.similars = s["similars"] if s["similars"] else PROFILE_RECS
            if st.session_state.logged_in:
                add_msg("me", "Show me the products!")
                st.session_state.screen = "shop"
            else:
                st.session_state.screen = "login"
            st.rerun()
    elif scr == "shop":
        _stage_shop()
    elif scr == "price":
        _stage_price()
    elif scr == "loyalty":
        _stage_loyalty()
    elif scr == "checkout":
        _stage_checkout()
    elif scr == "order_confirm":
        _stage_order_confirm()
    elif scr in ["done"]:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("← Back to Messages", key="back_dms", use_container_width=True):
            st.session_state.screen = "dm_list"
            reset_journey()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: CURATE DIRECT CHAT
# ══════════════════════════════════════════════════════════════════════════════
def screen_curate_chat():
    on = st.session_state.get("assistant_on", True)
    st.markdown(f"""
    <div class="ig-hdr">
      <div class="ig-av" style="background:linear-gradient(135deg,#6C47FF,#A855F7);border-radius:10px">✦</div>
      <div>
        <div class="ig-name">CurateAI</div>
        <div class="ig-sub">AI shopping concierge</div>
      </div>
      <div style="margin-left:auto">
        <span style="background:{'#22C55E' if on else '#C7C7C7'};color:#fff;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px">
          {'ON ✦' if on else 'OFF'}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("Toggle", key="toggle_btn"):
            st.session_state.assistant_on = not on
            st.rerun()

    scr = st.session_state.screen

    if scr == "login":
        screen_login()
        return

    if not st.session_state.messages:
        st.markdown("""
        <div style="padding:40px 20px;text-align:center;background:#fff">
          <div style="font-size:48px">✦</div>
          <div style="font-size:20px;font-weight:700;color:#000;margin-top:10px">CurateAI</div>
          <div style="font-size:13px;color:#8E8E8E;margin-top:6px;line-height:1.65">Share a product photo, link,<br>or describe what you're looking for</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render messages ONCE here
        render_chat_messages()

    if scr == "curate_chat":
        st.markdown("---")
        mode = st.radio("", ["💬 Text", "📷 Photo", "🔗 Link"], horizontal=True, key="input_mode", label_visibility="collapsed")
        if mode == "💬 Text":
            txt = st.text_input("", placeholder="e.g. I want a streetwear hoodie, earth tones...", key="ctxt", label_visibility="collapsed")
            if st.button("Search ✦", key="srch_txt", use_container_width=True):
                if txt:
                    add_msg("me", txt)
                    st.session_state.trigger = "profile"
                    st.session_state.matched_product = None
                    st.session_state.similars = PROFILE_RECS
                    if st.session_state.logged_in:
                        st.session_state.screen = "shop"
                    else:
                        st.session_state.screen = "login"
                    st.rerun()
        elif mode == "📷 Photo":
            up = st.file_uploader("", type=["jpg","jpeg","png","webp"], key="cphoto", label_visibility="collapsed")
            if up and st.button("Analyse ✦", key="srch_photo", use_container_width=True):
                add_msg("me", "📷 [Shared a product photo]")
                st.session_state.trigger = "exact_match"
                st.session_state.matched_product = "F001"
                st.session_state.similars = PROFILE_RECS
                if st.session_state.logged_in:
                    st.session_state.screen = "shop"
                else:
                    st.session_state.screen = "login"
                st.rerun()
        elif mode == "🔗 Link":
            lnk = st.text_input("", placeholder="Paste product link...", key="clnk", label_visibility="collapsed")
            if st.button("Check ✦", key="srch_link", use_container_width=True):
                if lnk:
                    add_msg("me", f"🔗 {lnk[:40]}...")
                    st.session_state.trigger = "exact_match"
                    st.session_state.matched_product = "G001"
                    st.session_state.similars = PROFILE_RECS
                    if st.session_state.logged_in:
                        st.session_state.screen = "shop"
                    else:
                        st.session_state.screen = "login"
                    st.rerun()
    elif scr == "shop":
        _stage_shop()
    elif scr == "price":
        _stage_price()
    elif scr == "loyalty":
        _stage_loyalty()
    elif scr == "checkout":
        _stage_checkout()
    elif scr == "order_confirm":
        _stage_order_confirm()
    elif scr == "done":
        if st.button("🛍️ Shop something else", key="shop_more", use_container_width=True):
            st.session_state.screen = "curate_chat"
            reset_journey()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE HANDLERS
# ══════════════════════════════════════════════════════════════════════════════
def _stage_shop():
    trigger = st.session_state.trigger
    matched = st.session_state.matched_product
    similars = st.session_state.similars or PROFILE_RECS

    if not st.session_state.shop_done:
        with st.spinner(""):
            render_skeleton()
            time.sleep(1)
            if trigger == "exact_match" and matched:
                p = CATALOG[matched]
                msg = ask_llm(
                    f"{PERSONA} Found exact product: {p['name']} by {p['brand']} at ₹{p['best_price']} on {p['platform']}. Tell {SHOPPER['first_name']} in 1 warm sentence.",
                    f"Found it, {SHOPPER['first_name']}! Here's the {p['name']} by {p['brand']} — exactly what was shared, at ₹{p['best_price']}."
                )
                add_msg("agent", msg, "product_exact", matched)
            else:
                label = "You may also like" if trigger in ["not_in_network"] else "Picked for you"
                msg = ask_llm(
                    f"{PERSONA} Showing {len(similars)} product recommendations for {SHOPPER['first_name']} who loves {SHOPPER['style_profile']}. 1 warm sentence.",
                    f"These picks match your style perfectly, {SHOPPER['first_name']} — sorted by best discount available."
                )
                add_msg("agent", msg, "product_carousel", {"pids": similars, "label": label})
            st.session_state.shop_done = True
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if trigger == "exact_match":
        st.markdown('<div style="font-size:12px;color:#8E8E8E;margin-bottom:6px;padding:0 4px">Is this the same product?</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✓ Yes — Get Best Price", key="yes_exact"):
                st.session_state.selected_pid = matched
                add_msg("me", "Yes! Get me the best price.")
                st.session_state.screen = "price"
                st.rerun()
        with c2:
            if st.button("✗ Not quite", key="no_exact"):
                add_msg("me", "Not quite what I was looking for")
                add_msg("agent", f"My bad, {SHOPPER['first_name']}! Tell me more — colour, style, or occasion?")
                st.session_state.screen = "curate_chat" if not st.session_state.active_sender else "sender_chat"
                st.session_state.shop_done = False
                st.rerun()
    else:
        st.markdown('<div style="font-size:12px;color:#8E8E8E;margin-bottom:6px;padding:0 4px">Like these picks? Select one to continue</div>', unsafe_allow_html=True)
        opts = {f"{CATALOG[p]['name']} — {CATALOG[p]['brand']} (₹{CATALOG[p]['best_price']:,})": p for p in similars}
        chosen = st.selectbox("", list(opts.keys()), key="car_sel", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✓ Get Best Price", key="yes_car"):
                pid = opts[chosen]
                st.session_state.selected_pid = pid
                add_msg("me", f"I like the {CATALOG[pid]['name']} — get me the best price!")
                st.session_state.screen = "price"
                st.rerun()
        with c2:
            if st.button("✗ Show more", key="no_car"):
                add_msg("me", "Not quite right")
                add_msg("agent", f"Let me dig deeper, {SHOPPER['first_name']}! Tell me more about what you had in mind.")
                st.session_state.screen = "curate_chat" if not st.session_state.active_sender else "sender_chat"
                st.session_state.shop_done = False
                st.rerun()

def _stage_price():
    pid = st.session_state.selected_pid
    if not st.session_state.price_done:
        with st.spinner("Scanning merchant network..."):
            p = CATALOG[pid]
            msg = ask_llm(
                f"{PERSONA} Best price for {p['name']}: ₹{p['best_price']} on {p['platform']} ({p['discount']}% off ₹{p['mrp']}). Cashback ₹{p['cashback']} LR. Coupon: {p.get('coupon','none')}. 1-2 sentences.",
                f"Scanned the network — best deal is ₹{p['best_price']} on {p['platform']} ({p['discount']}% off MRP). You'll also earn ₹{p['cashback']} LR cashback."
            )
        add_msg("agent", msg, "price_card", {"pid": pid})
        st.session_state.price_done = True
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Apply My Loyalty Points →", key="apply_loy_btn", use_container_width=True):
        add_msg("me", "Apply my loyalty points!")
        st.session_state.screen = "loyalty"
        st.rerun()

def _stage_loyalty():
    pid = st.session_state.selected_pid
    if not st.session_state.loyalty_done:
        p = CATALOG[pid]
        ld = calc_loyalty(p["best_price"], SHOPPER["points"])
        st.session_state.loyalty_data = ld
        with st.spinner("Loading your rewards..."):
            msg = ask_llm(
                f"{PERSONA} {SHOPPER['first_name']} has {SHOPPER['points']:,} LR ({SHOPPER['tier']}). Redeeming {ld['redeemable_pts']:,} pts = ₹{ld['discount_rs']:.0f} off. Earning {ld['points_earned']} pts. 1-2 celebratory sentences.",
                f"Your {SHOPPER['tier']} rewards are working for you, {SHOPPER['first_name']}! Redeeming {ld['redeemable_pts']:,} points saves you ₹{ld['discount_rs']:.0f} — applied instantly, no redirect needed."
            )
        add_msg("agent", msg, "loyalty_card", ld)
        st.session_state.loyalty_done = True
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Proceed to Checkout →", key="to_checkout_btn", use_container_width=True):
        add_msg("me", "Let's checkout!")
        st.session_state.screen = "checkout"
        st.rerun()

def _stage_checkout():
    pid = st.session_state.selected_pid
    if not st.session_state.checkout_done:
        p = CATALOG[pid]
        ld = st.session_state.loyalty_data or calc_loyalty(p["best_price"], SHOPPER["points"])
        final = p["best_price"] - ld["discount_rs"]
        with st.spinner("Building your cart..."):
            msg = ask_llm(
                f"{PERSONA} Cart ready for {SHOPPER['first_name']}: {p['name']} at ₹{final:.0f} (saved ₹{p['mrp']-final:.0f}). Identity pre-filled, rewards applied. 1-2 sentences.",
                f"Your cart is ready, {SHOPPER['first_name']} — ₹{final:.0f} all in, with every deal applied. One tap and it's yours."
            )
        add_msg("agent", msg, "checkout_card", {"pid": pid, "ld": ld})
        st.session_state.checkout_done = True
        st.rerun()
    # CTA outside render_chat_messages to avoid duplicate key
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("✓ Order Placed — Confirm", key="confirm_order_btn", use_container_width=True):
        st.session_state.screen = "order_confirm"
        st.rerun()


def _stage_order_confirm():
    pid = st.session_state.selected_pid
    ld = st.session_state.loyalty_data or {}
    add_msg("me", "Order placed! ✓")
    order_id = random.randint(100000, 999999)
    msg = ask_llm(
        f"{PERSONA} Order confirmed for {SHOPPER['first_name']}! {CATALOG[pid]['name']} on its way. Earned {ld.get('points_earned',0)} LR. 1 celebratory sentence.",
        f"Order confirmed! Your {CATALOG[pid]['name']} is on its way, {SHOPPER['first_name']} — and you just earned {ld.get('points_earned',0)} LR points. 🎉"
    )
    add_msg("agent", msg, "success_card", {"pid": pid, "ld": ld, "order_id": order_id, "delivery": "Apr 9–11, 2026"})
    st.session_state.screen = "done"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
scr = st.session_state.screen

if scr not in ["dm_list"]:
    if st.button("← Back", key="global_back"):
        back_map = {
            "sender_chat": "dm_list",
            "curate_chat": "dm_list",
            "login": "sender_chat" if st.session_state.active_sender else "curate_chat",
            "shop": "sender_chat" if st.session_state.active_sender else "curate_chat",
            "price": "shop",
            "loyalty": "price",
            "checkout": "loyalty",
            "order_confirm": "checkout",
            "done": "dm_list",
        }
        dest = back_map.get(scr, "dm_list")
        if dest == "dm_list":
            reset_journey()
            st.session_state.active_sender = None
        st.session_state.screen = dest
        st.rerun()

if scr == "dm_list":
    screen_dm_list()
elif scr in ["login"]:
    if st.session_state.active_sender:
        screen_sender_chat()
    else:
        screen_curate_chat()
elif scr == "sender_chat":
    screen_sender_chat()
elif scr == "curate_chat":
    screen_curate_chat()
elif scr in ["shop","price","loyalty","checkout","order_confirm","done"]:
    if st.session_state.active_sender:
        screen_sender_chat()
    else:
        screen_curate_chat()
