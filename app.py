import streamlit as st
import anthropic
import base64
import json
import time
from PIL import Image
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopDM – AI Commerce Agent",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Mock data layer ───────────────────────────────────────────────────────────
MOCK_SHOPPERS = {
    "@priya.styles": {
        "name": "Priya Sharma",
        "tier": "Gold",
        "points": 3420,
        "cashback_pct": 8,
        "avatar": "PS",
        "history": ["Zara", "H&M", "Mango", "The Label Life"],
    },
    "@rahul.buys": {
        "name": "Rahul Mehta",
        "tier": "Silver",
        "points": 1180,
        "cashback_pct": 5,
        "avatar": "RM",
        "history": ["Myntra", "Bewakoof", "Campus Sutra"],
    },
    "@sneha_k": {
        "name": "Sneha Kapoor",
        "tier": "Platinum",
        "points": 8750,
        "cashback_pct": 12,
        "avatar": "SK",
        "history": ["Nykaa Fashion", "Pernia's Pop-Up", "Aza", "Libas"],
    },
}

MOCK_CATALOG = [
    {"id": "P001", "name": "Floral Wrap Midi Dress", "brand": "The Label Life", "price_mrp": 3299, "price_best": 2149, "platform": "Myntra", "coupon": "STYLE20", "discount_pct": 35, "cashback": 180, "image_emoji": "👗"},
    {"id": "P002", "name": "Linen Co-ord Set – Sage", "brand": "Mango", "price_mrp": 4500, "price_best": 3150, "platform": "Ajio", "coupon": "AJIO30", "discount_pct": 30, "cashback": 250, "image_emoji": "👚"},
    {"id": "P003", "name": "Strappy Block Heel Sandals", "brand": "Steve Madden", "price_mrp": 5990, "price_best": 3594, "platform": "Nykaa Fashion", "coupon": "NYKAA40", "discount_pct": 40, "cashback": 300, "image_emoji": "👡"},
    {"id": "P004", "name": "Rattan Shoulder Bag", "brand": "Zara", "price_mrp": 2799, "price_best": 1959, "platform": "Zara.in", "coupon": None, "discount_pct": 30, "cashback": 150, "image_emoji": "👜"},
    {"id": "P005", "name": "Gold Layered Necklace Set", "brand": "Zaveri Pearls", "price_mrp": 999, "price_best": 599, "platform": "Myntra", "coupon": "BLING40", "discount_pct": 40, "cashback": 50, "image_emoji": "📿"},
]

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0a !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0a0a 0%, #111118 100%) !important;
}

/* Hide default streamlit elements */
#MainMenu, footer, header, [data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 480px !important; margin: 0 auto; }

/* ── Top nav bar ── */
.ig-nav {
    position: sticky; top: 0; z-index: 100;
    background: rgba(10,10,10,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 14px 20px;
    display: flex; align-items: center; gap: 14px;
}
.ig-nav-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: white; flex-shrink: 0;
}
.ig-nav-info { flex: 1; }
.ig-nav-name { font-size: 14px; font-weight: 600; color: #fff; }
.ig-nav-status { font-size: 11px; color: #22c55e; margin-top: 1px; }
.ig-nav-badge {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; font-size: 10px; font-weight: 700;
    padding: 3px 8px; border-radius: 20px; letter-spacing: 0.5px;
}

/* ── Thread container ── */
.dm-thread {
    padding: 20px 16px;
    min-height: 60vh;
    display: flex; flex-direction: column; gap: 12px;
}

/* ── Message bubbles ── */
.msg-row { display: flex; align-items: flex-end; gap: 8px; }
.msg-row.user { flex-direction: row-reverse; }

.bubble {
    max-width: 78%;
    padding: 11px 15px;
    border-radius: 20px;
    font-size: 14px; line-height: 1.5; color: #f1f1f1;
    position: relative;
}
.bubble.user {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-bottom-right-radius: 4px;
}
.bubble.agent {
    background: #1e1e2e;
    border: 1px solid rgba(255,255,255,0.08);
    border-bottom-left-radius: 4px;
}
.bubble-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #f09433, #dc2743, #bc1888);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: white; flex-shrink: 0;
}
.msg-time { font-size: 10px; color: #555; margin-top: 3px; text-align: right; }

/* ── Product cards ── */
.product-grid { display: flex; flex-direction: column; gap: 10px; margin-top: 6px; }
.product-card {
    background: #16161f;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 14px;
    display: flex; gap: 14px; align-items: center;
    transition: border-color 0.2s;
}
.product-card.best-deal {
    border-color: rgba(99, 102, 241, 0.5);
    background: linear-gradient(135deg, #16161f 0%, #1a1a2e 100%);
}
.product-emoji { font-size: 32px; background: #0d0d17; border-radius: 10px; width: 54px; height: 54px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.product-info { flex: 1; }
.product-name { font-size: 13px; font-weight: 600; color: #f1f1f1; margin-bottom: 2px; }
.product-brand { font-size: 11px; color: #666; margin-bottom: 6px; }
.product-price-row { display: flex; align-items: center; gap: 8px; }
.product-price { font-size: 15px; font-weight: 700; color: #fff; }
.product-mrp { font-size: 11px; color: #555; text-decoration: line-through; }
.product-badge { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px; }
.badge-deal { background: rgba(34,197,94,0.15); color: #22c55e; }
.badge-best { background: rgba(99,102,241,0.2); color: #a5b4fc; }
.coupon-tag { font-size: 10px; margin-top: 5px; color: #f59e0b; }

/* ── Loyalty card ── */
.loyalty-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 18px; padding: 18px;
    margin-top: 6px;
}
.loyalty-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.loyalty-tier { font-size: 11px; font-weight: 700; letter-spacing: 1px; }
.tier-gold { color: #f59e0b; }
.tier-silver { color: #94a3b8; }
.tier-platinum { color: #a5b4fc; }
.loyalty-points { font-size: 28px; font-weight: 700; color: #fff; }
.loyalty-label { font-size: 11px; color: #666; margin-top: 2px; }
.loyalty-bar-bg { background: rgba(255,255,255,0.08); border-radius: 99px; height: 6px; margin-top: 14px; }
.loyalty-bar-fill { background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 99px; height: 6px; }
.loyalty-value { font-size: 20px; font-weight: 700; color: #22c55e; margin-top: 10px; }

/* ── Checkout card ── */
.checkout-card {
    background: linear-gradient(135deg, #0f1629, #131629);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 20px; padding: 20px;
    margin-top: 6px;
}
.checkout-title { font-family: 'DM Serif Display', serif; font-size: 18px; color: #fff; margin-bottom: 16px; }
.checkout-line { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 13px; }
.checkout-line:last-of-type { border-bottom: none; }
.checkout-label { color: #777; }
.checkout-value { color: #f1f1f1; font-weight: 500; }
.checkout-total { font-size: 20px; font-weight: 700; color: #fff; margin-top: 12px; }
.checkout-savings { font-size: 12px; color: #22c55e; margin-top: 4px; }
.checkout-link {
    display: block; width: 100%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white !important; text-align: center;
    padding: 14px; border-radius: 14px; margin-top: 16px;
    font-size: 15px; font-weight: 700; text-decoration: none;
    letter-spacing: 0.3px;
    box-shadow: 0 8px 24px rgba(99,102,241,0.35);
}
.checkout-prefill { font-size: 10px; color: #555; margin-top: 10px; text-align: center; }

/* ── Step indicator ── */
.step-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px; padding: 4px 12px;
    font-size: 11px; font-weight: 600; color: #818cf8;
    margin-bottom: 4px; letter-spacing: 0.3px;
}
.step-dot { width: 6px; height: 6px; border-radius: 50%; background: #6366f1; }

/* ── Input area ── */
.input-area {
    position: sticky; bottom: 0;
    background: rgba(10,10,10,0.9);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255,255,255,0.07);
    padding: 12px 16px;
}

/* Streamlit widget overrides */
[data-testid="stTextInput"] input {
    background: #1e1e2e !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 24px !important;
    color: #f1f1f1 !important;
    padding: 10px 18px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
[data-testid="stTextInput"] label { color: #666 !important; font-size: 12px !important; }

.stButton button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 24px !important;
    padding: 10px 22px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

[data-testid="stFileUploader"] {
    background: #1e1e2e !important;
    border: 1px dashed rgba(99,102,241,0.3) !important;
    border-radius: 14px !important;
    padding: 10px !important;
}
[data-testid="stFileUploader"] label { color: #818cf8 !important; font-size: 13px !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1e1e2e !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #f1f1f1 !important;
}
[data-testid="stSelectbox"] label { color: #666 !important; font-size: 12px !important; }

/* Spinner */
[data-testid="stSpinner"] { color: #6366f1 !important; }

/* Divider */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* typing indicator */
@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
}
.typing-dot { display: inline-block; width: 6px; height: 6px; background: #666; border-radius: 50%; margin: 0 2px; animation: blink 1.4s infinite ease-in-out; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "stage": "login",          # login | otp | shopping | price | loyalty | checkout | done
        "messages": [],            # list of {role, content, type, data}
        "shopper": None,
        "selected_products": None,
        "best_product": None,
        "checkout_link": None,
        "otp_sent": False,
        "handle": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

client = anthropic.Anthropic()

# ── Helpers ───────────────────────────────────────────────────────────────────
def now_time():
    return time.strftime("%I:%M %p")

def add_message(role, content, msg_type="text", data=None):
    st.session_state.messages.append({
        "role": role, "content": content,
        "type": msg_type, "data": data,
        "time": now_time()
    })

def ask_claude(system_prompt, user_content, image_b64=None, image_type="image/jpeg"):
    """Call Claude API — optionally with an image."""
    messages_payload = []
    if image_b64:
        messages_payload.append({
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": image_type, "data": image_b64}},
                {"type": "text", "text": user_content}
            ]
        })
    else:
        messages_payload.append({"role": "user", "content": user_content})

    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        system=system_prompt,
        messages=messages_payload
    )
    return resp.content[0].text

def encode_image(uploaded_file):
    bytes_data = uploaded_file.read()
    return base64.standard_b64encode(bytes_data).decode("utf-8"), uploaded_file.type

# ── Render thread ─────────────────────────────────────────────────────────────
def render_nav():
    shopper = st.session_state.shopper
    if shopper:
        name = shopper["name"]
        av = shopper["avatar"]
        tier = shopper["tier"]
        tier_color = {"Gold": "#f59e0b", "Silver": "#94a3b8", "Platinum": "#a5b4fc"}.get(tier, "#fff")
    else:
        name = "ShopDM Agent"
        av = "AI"
        tier_color = "#6366f1"

    st.markdown(f"""
    <div class="ig-nav">
        <div class="ig-nav-avatar">{av}</div>
        <div class="ig-nav-info">
            <div class="ig-nav-name">{name if shopper else "ShopDM"}</div>
            <div class="ig-nav-status">{"● Active now" if shopper else "AI Commerce Agent"}</div>
        </div>
        <div class="ig-nav-badge">AI AGENT</div>
    </div>
    """, unsafe_allow_html=True)

def render_bubble(msg):
    role = msg["role"]
    content = msg["content"]
    msg_type = msg["type"]
    data = msg.get("data")
    t = msg.get("time", "")

    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
            <div>
                <div class="bubble user">{content}</div>
                <div class="msg-time">{t}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # agent message
        if msg_type == "products":
            _render_product_bubbles(content, data, t)
        elif msg_type == "loyalty":
            _render_loyalty_bubble(content, data, t)
        elif msg_type == "checkout":
            _render_checkout_bubble(content, data, t)
        else:
            step_pill = ""
            if data and data.get("step"):
                step_pill = f'<div class="step-pill"><span class="step-dot"></span>{data["step"]}</div><br>'
            st.markdown(f"""
            <div class="msg-row">
                <div class="bubble-avatar">S</div>
                <div>
                    {step_pill}
                    <div class="bubble agent">{content}</div>
                    <div class="msg-time">{t}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def _render_product_bubbles(intro_text, products, t):
    cards_html = ""
    for i, p in enumerate(products):
        best_class = "best-deal" if i == 0 else ""
        best_badge = '<span class="product-badge badge-best">BEST DEAL</span>' if i == 0 else ""
        coupon_html = f'<div class="coupon-tag">🏷️ Use code <b>{p["coupon"]}</b> at checkout</div>' if p.get("coupon") else ""
        cards_html += f"""
        <div class="product-card {best_class}">
            <div class="product-emoji">{p["image_emoji"]}</div>
            <div class="product-info">
                <div class="product-name">{p["name"]}</div>
                <div class="product-brand">{p["brand"]} · {p["platform"]}</div>
                <div class="product-price-row">
                    <span class="product-price">₹{p["price_best"]:,}</span>
                    <span class="product-mrp">₹{p["price_mrp"]:,}</span>
                    <span class="product-badge badge-deal">{p["discount_pct"]}% OFF</span>
                    {best_badge}
                </div>
                {coupon_html}
            </div>
        </div>
        """

    st.markdown(f"""
    <div class="msg-row">
        <div class="bubble-avatar">S</div>
        <div style="max-width:85%">
            <div class="step-pill"><span class="step-dot"></span>SHOP THE LOOK</div><br>
            <div class="bubble agent">{intro_text}</div>
            <div class="product-grid" style="margin-top:10px">{cards_html}</div>
            <div class="msg-time">{t}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_loyalty_bubble(intro_text, data, t):
    s = st.session_state.shopper
    tier = s["tier"]
    tier_class = f"tier-{tier.lower()}"
    tier_max = {"Gold": 5000, "Silver": 3000, "Platinum": 10000}.get(tier, 5000)
    fill_pct = min(100, int(s["points"] / tier_max * 100))
    val = data.get("redemption_value", 0)

    st.markdown(f"""
    <div class="msg-row">
        <div class="bubble-avatar">S</div>
        <div style="max-width:88%">
            <div class="step-pill"><span class="step-dot"></span>LOYALTY APPLY</div><br>
            <div class="bubble agent">{intro_text}</div>
            <div class="loyalty-card" style="margin-top:10px">
                <div class="loyalty-header">
                    <div>
                        <div class="loyalty-tier {tier_class}">★ {tier.upper()} MEMBER</div>
                        <div class="loyalty-points">{s["points"]:,} pts</div>
                        <div class="loyalty-label">Available reward balance</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:11px;color:#555">Cashback rate</div>
                        <div style="font-size:20px;font-weight:700;color:#f59e0b">{s["cashback_pct"]}%</div>
                    </div>
                </div>
                <div class="loyalty-bar-bg"><div class="loyalty-bar-fill" style="width:{fill_pct}%"></div></div>
                <div style="font-size:10px;color:#555;margin-top:4px">{fill_pct}% toward next tier</div>
                <div class="loyalty-value">💰 Redeem → save ₹{val:,} instantly</div>
            </div>
            <div class="msg-time">{t}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_checkout_bubble(intro_text, data, t):
    st.markdown(f"""
    <div class="msg-row">
        <div class="bubble-avatar">S</div>
        <div style="max-width:90%">
            <div class="step-pill"><span class="step-dot"></span>CHECKOUT</div><br>
            <div class="bubble agent">{intro_text}</div>
            <div class="checkout-card" style="margin-top:10px">
                <div class="checkout-title">Your personalised cart ✦</div>
                <div class="checkout-line"><span class="checkout-label">Product</span><span class="checkout-value">{data["product"]}</span></div>
                <div class="checkout-line"><span class="checkout-label">Platform</span><span class="checkout-value">{data["platform"]}</span></div>
                <div class="checkout-line"><span class="checkout-label">MRP</span><span class="checkout-value">₹{data["mrp"]:,}</span></div>
                <div class="checkout-line"><span class="checkout-label">Deal price</span><span class="checkout-value">₹{data["deal_price"]:,}</span></div>
                <div class="checkout-line"><span class="checkout-label">Coupon ({data["coupon"]})</span><span class="checkout-value" style="color:#22c55e">–₹{data["coupon_saving"]:,}</span></div>
                <div class="checkout-line"><span class="checkout-label">Loyalty points</span><span class="checkout-value" style="color:#22c55e">–₹{data["loyalty_saving"]:,}</span></div>
                <div class="checkout-line"><span class="checkout-label">Cashback earned</span><span class="checkout-value" style="color:#f59e0b">+₹{data["cashback_earned"]:,}</span></div>
                <div style="border-top:1px solid rgba(255,255,255,0.1);margin-top:10px;padding-top:12px">
                    <div class="checkout-total">You pay ₹{data["final_price"]:,}</div>
                    <div class="checkout-savings">You saved ₹{data["total_saving"]:,} on this order 🎉</div>
                </div>
                <a class="checkout-link" href="#" onclick="return false;">Tap to Checkout →</a>
                <div class="checkout-prefill">🔒 Identity pre-filled · Rewards applied · Best price locked</div>
            </div>
            <div class="msg-time">{t}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_thread():
    st.markdown('<div class="dm-thread">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        render_bubble(msg)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Stage handlers ────────────────────────────────────────────────────────────
def handle_login():
    st.markdown("""
    <div style="padding:16px 16px 8px">
        <div style="font-size:12px;color:#555;margin-bottom:12px;text-align:center">Enter your Instagram handle to begin</div>
    </div>
    """, unsafe_allow_html=True)

    handle = st.selectbox(
        "Your Instagram handle",
        options=["", "@priya.styles", "@rahul.buys", "@sneha_k"],
        format_func=lambda x: x if x else "— select handle —",
        key="handle_select"
    )

    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("Send OTP →", disabled=not handle):
            st.session_state.handle = handle
            add_message("user", f"Hi! I'm {handle}", data={"step": "LOGIN"})
            with st.spinner(""):
                time.sleep(0.8)
            add_message("agent",
                f"Hey! 👋 I've sent a 4-digit OTP to the number linked with <b>{handle}</b>. Enter it below to continue.",
                data={"step": "IDENTITY CHECK"}
            )
            st.session_state.stage = "otp"
            st.session_state.otp_sent = True
            st.rerun()

def handle_otp():
    otp = st.text_input("Enter OTP", placeholder="e.g. 8421", max_chars=4, key="otp_input")
    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("Verify ✓", disabled=len(otp) != 4):
            handle = st.session_state.handle
            shopper = MOCK_SHOPPERS.get(handle)
            if not shopper:
                st.error("Handle not found in demo data.")
                return

            add_message("user", f"OTP: {otp}")
            st.session_state.shopper = shopper

            greeting = ask_claude(
                "You are ShopDM, a warm and knowledgeable AI shopping concierge living inside an Instagram DM thread. "
                "You are NOT a chatbot. You are elegant, concise, and helpful like a personal stylist who knows the shopper well. "
                "Keep responses under 80 words. Use emojis sparingly — only when natural.",
                f"The shopper {shopper['name']} just verified their identity. They are a {shopper['tier']} member with "
                f"{shopper['points']} reward points and {shopper['cashback_pct']}% cashback rate. "
                f"They've shopped at: {', '.join(shopper['history'])}. "
                "Welcome them back warmly, mention their tier and points briefly, and invite them to share what they want to shop today."
            )
            add_message("agent", greeting.replace("\n", "<br>"), data={"step": "IDENTITY VERIFIED"})
            st.session_state.stage = "shopping"
            st.rerun()

def handle_shopping():
    st.markdown('<div style="padding:8px 16px 4px"><div style="font-size:11px;color:#555">Describe a style or upload a photo</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        user_text = st.text_input("Message", placeholder="e.g. I love this boho summer look...", key="shop_text", label_visibility="collapsed")
    with col2:
        uploaded = st.file_uploader("📷", type=["jpg", "jpeg", "png", "webp"], key="shop_image", label_visibility="collapsed")

    if st.button("Find the Look 🔍"):
        if not user_text and not uploaded:
            st.warning("Type a description or upload an image.")
            return

        display_msg = user_text if user_text else "📷 [Shared an image]"
        add_message("user", display_msg)

        with st.spinner("Identifying the look..."):
            if uploaded:
                img_b64, img_type = encode_image(uploaded)
                analysis = ask_claude(
                    "You are a fashion AI that identifies clothing items and styles from images. "
                    "Be specific about garments, colours, silhouettes, and occasion. Keep it under 60 words.",
                    "Identify the key fashion pieces and overall aesthetic in this image.",
                    image_b64=img_b64, image_type=img_type
                )
                style_description = analysis
            else:
                style_description = user_text

            intro = ask_claude(
                "You are ShopDM, an elegant AI shopping concierge in an Instagram DM. "
                "You've identified the shopper's style. Introduce the product recommendations in 1-2 warm sentences. No bullet points.",
                f"The shopper is looking for: {style_description}. "
                "Introduce that you've found 5 great shoppable pieces across the merchant network."
            )

        add_message("agent", intro.replace("\n", "<br>"), msg_type="products", data=MOCK_CATALOG)
        st.session_state.selected_products = MOCK_CATALOG
        st.session_state.best_product = MOCK_CATALOG[0]
        st.session_state.stage = "price"
        st.rerun()

def handle_price():
    if st.button("Check Best Price 💰"):
        p = st.session_state.best_product
        add_message("user", "What's the best price I can get?")

        with st.spinner("Scanning the network..."):
            price_msg = ask_claude(
                "You are ShopDM, an AI commerce concierge. Explain the best price finding result in 2-3 sentences. Sound confident and helpful. Mention the platform and the deal.",
                f"You checked prices across the merchant network for '{p['name']}' by {p['brand']}. "
                f"Best price is ₹{p['price_best']} on {p['platform']} (MRP ₹{p['price_mrp']}, {p['discount_pct']}% off). "
                f"Coupon code: {p.get('coupon', 'none')}. Cashback: ₹{p['cashback']}. "
                "Tell the shopper clearly and naturally."
            )

        add_message("agent", price_msg.replace("\n", "<br>"), data={"step": "BEST PRICE"})
        st.session_state.stage = "loyalty"
        st.rerun()

def handle_loyalty():
    if st.button("Apply My Rewards 🎁"):
        s = st.session_state.shopper
        p = st.session_state.best_product
        add_message("user", "Can I use my reward points too?")

        # Calculate redemption (100 points = ₹1, cap at 20% of deal price)
        max_redemption = int(p["price_best"] * 0.20)
        points_value = int(s["points"] / 100)
        redemption_val = min(points_value, max_redemption)

        with st.spinner("Loading your rewards..."):
            loyalty_intro = ask_claude(
                "You are ShopDM. Explain the loyalty redemption naturally in 1-2 sentences. Sound warm.",
                f"The shopper has {s['points']} points = ₹{points_value} value. "
                f"They can redeem up to ₹{redemption_val} on this order (20% cap). "
                f"Their tier is {s['tier']} with {s['cashback_pct']}% cashback. Mention the savings."
            )

        add_message("agent", loyalty_intro.replace("\n", "<br>"),
                    msg_type="loyalty", data={"redemption_value": redemption_val})
        st.session_state["redemption_val"] = redemption_val
        st.session_state.stage = "checkout"
        st.rerun()

def handle_checkout():
    if st.button("Generate My Checkout Link ⚡"):
        s = st.session_state.shopper
        p = st.session_state.best_product
        rdv = st.session_state.get("redemption_val", 0)
        add_message("user", "Generate my checkout link please!")

        # Compute final numbers
        coupon_saving = int(p["price_best"] * 0.05) if p.get("coupon") else 0
        final_price = p["price_best"] - coupon_saving - rdv
        cashback_earned = int(final_price * s["cashback_pct"] / 100)
        total_saving = p["price_mrp"] - final_price

        checkout_data = {
            "product": p["name"],
            "platform": p["platform"],
            "mrp": p["price_mrp"],
            "deal_price": p["price_best"],
            "coupon": p.get("coupon", "NONE"),
            "coupon_saving": coupon_saving,
            "loyalty_saving": rdv,
            "cashback_earned": cashback_earned,
            "final_price": max(final_price, 0),
            "total_saving": total_saving,
        }

        with st.spinner("Building your cart..."):
            checkout_msg = ask_claude(
                "You are ShopDM. Write a short, exciting closing message (2 sentences) as you hand the shopper their personalised checkout link. Sound like a concierge handing over a VIP ticket.",
                f"The shopper is paying ₹{final_price} for {p['name']} — saving ₹{total_saving} total. "
                f"Rewards applied, best price locked, identity pre-filled. Make it feel special."
            )

        add_message("agent", checkout_msg.replace("\n", "<br>"), msg_type="checkout", data=checkout_data)
        st.session_state.stage = "done"
        st.rerun()

def handle_done():
    if st.button("🔄 Start a new session"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Main render ───────────────────────────────────────────────────────────────
render_nav()
render_thread()

st.markdown("<hr style='margin:0'>", unsafe_allow_html=True)
st.markdown('<div class="input-area">', unsafe_allow_html=True)

stage = st.session_state.stage
if stage == "login":
    handle_login()
elif stage == "otp":
    handle_otp()
elif stage == "shopping":
    handle_shopping()
elif stage == "price":
    handle_price()
elif stage == "loyalty":
    handle_loyalty()
elif stage == "checkout":
    handle_checkout()
elif stage == "done":
    handle_done()

st.markdown('</div>', unsafe_allow_html=True)