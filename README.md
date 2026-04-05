# CurateAI — AI-Powered Instagram Commerce Agent

> A conversational AI shopping concierge embedded inside Instagram DMs. Discover products, get the best price, apply loyalty rewards, and checkout — without leaving the chat.

---

## 🚀 Run Locally in 3 Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Anthropic API key (optional — fallbacks work without it)
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 3. Launch the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

> **No API key?** The app runs fully on hardcoded fallback responses. All 7 chat flows, login, products, loyalty, and checkout work without any API credits.

---

## 📋 Requirements

- Python 3.9+
- pip

Dependencies (`requirements.txt`):
```
streamlit
anthropic
python-dotenv
pillow
jupyter
```

---

## 🗂️ Project Structure

```
curateai-shopdm/
│
├── app.py                  # Main Streamlit application (all screens + logic)
├── requirements.txt        # Python dependencies
├── .env                    # API key (not committed — see .gitignore)
├── .gitignore
├── README.md
└── shopdm_walkthrough.ipynb  # Jupyter notebook — 5-moment narrated walkthrough
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  DM List → Sender Chat → Login → Shop → Price →        │
│  Loyalty → Checkout → Order Success                     │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │       Session State          │
          │  screen, messages, trigger,  │
          │  matched_product, similars,  │
          │  loyalty_data, shopper       │
          └──────────────┬──────────────┘
                         │
         ┌───────────────▼───────────────┐
         │         Pure Python Logic      │
         │  • Login & OTP (no API)        │
         │  • Mock catalog lookups        │
         │  • Loyalty calculation         │
         │  • Prefilled chat seeding      │
         │  • Screen routing              │
         └───────────────┬───────────────┘
                         │ (only 5 moments)
         ┌───────────────▼───────────────┐
         │      Anthropic Claude API      │
         │   claude-opus-4-5              │
         │  • Shop the Look message       │
         │  • Best Price narrative        │
         │  • Loyalty Apply message       │
         │  • Checkout closing message    │
         │  • Order success message       │
         └───────────────────────────────┘
```

### Key Design Decisions

| Decision | Reason |
|----------|--------|
| LLM called only for 5 moments | Minimise latency and API cost — everything else is deterministic |
| All LLM calls have hardcoded fallbacks | App works without API key for demo |
| Session state for all data | Single-page Streamlit app — no database needed |
| Mock catalog + shopper data | No live APIs required to run the demo |
| Seeded prefilled chats | Each of the 7 DM contacts has realistic prefilled conversation history |

---

## 👤 Mock Shopper Profile

```
Handle:     @singh_amarjyot
Name:       Amarjyot Singh
Tier:       Platinum
Points:     8,240 LR
Cashback:   12%
History:    Roadster, H&M, boAt
Addresses:  Home & Office — Bengaluru, Karnataka
Payment:    UPI GPay · HDFC Millennia
```

---

## 💬 7 DM Chat Flows

| Sender | Type | Trigger | Product Shown |
|--------|------|---------|---------------|
| Sonam Bajwa | Friend | Fashion photo — NOT in network | F001, F003, F005 carousel |
| Diljit Dosanjh | Friend | Streetwear link — exact match | F001 H&M Hoodie |
| Virat Kohli | Friend | Earbuds photo — exact match | G001 boAt Airdopes |
| H&M India | Brand (in network) | Product post — exact match | F001 H&M Hoodie |
| boAt | Brand (in network) | Product post — exact match | G001 boAt Airdopes |
| Puma India | Brand (NOT in network) | Running shoes — alternatives | F004, F005 carousel |
| CurateAI Direct | — | Text / Photo / Link input | Profile-based recommendations |

---

## 🤖 LLM Prompts — All 5 Moments

### Agent Persona (System Context)
Applied to every LLM call:
```
You are CurateAI, a warm personal shopping concierge inside Instagram DM.
Be warm, concise (1-2 sentences), natural. Use first name.
```

---

### Moment 1 — Shop the Look (Exact Match)
**Trigger:** Product found in merchant network

```
{PERSONA}
Found exact product: {product_name} by {brand} at ₹{best_price} on {platform}.
Tell {first_name} in 1 warm sentence.
```

**Fallback:**
```
Found it, {first_name}! Here's the {product_name} by {brand} — 
exactly what was shared, at ₹{best_price}.
```

---

### Moment 2 — Shop the Look (Carousel / Not in Network)
**Trigger:** Product not in network — showing alternatives

```
{PERSONA}
Showing {count} product recommendations for {first_name} who loves {style_profile}.
1 warm sentence.
```

**Fallback:**
```
These picks match your style perfectly, {first_name} — 
sorted by best discount available.
```

---

### Moment 3 — Best Price
**Trigger:** User taps "Get Best Price"

```
{PERSONA}
Best price for {product_name}: ₹{best_price} on {platform} ({discount}% off ₹{mrp}).
Cashback ₹{cashback} LR. Coupon: {coupon}.
1-2 sentences.
```

**Fallback:**
```
Scanned the network — best deal is ₹{best_price} on {platform} ({discount}% off MRP).
You'll also earn ₹{cashback} LR cashback.
```

---

### Moment 4 — Loyalty Apply
**Trigger:** User taps "Apply My Loyalty Points"

```
{PERSONA}
{first_name} has {points} LR ({tier} member).
Redeeming {redeemable_pts} pts = ₹{discount_rs} off.
Earning {points_earned} pts on this order.
1-2 celebratory sentences.
```

**Fallback:**
```
Your {tier} rewards are working for you, {first_name}!
Redeeming {redeemable_pts} points saves you ₹{discount_rs} — 
applied instantly, no redirect needed.
```

---

### Moment 5 — Checkout & Order Success
**Trigger:** Cart ready + Order confirmed

**Checkout prompt:**
```
{PERSONA}
Cart ready for {first_name}: {product_name} at ₹{final_price}
(saved ₹{total_saved}). Identity pre-filled, rewards applied.
1-2 sentences, VIP concierge tone.
```

**Order success prompt:**
```
{PERSONA}
Order confirmed for {first_name}! {product_name} is on its way.
Earned {points_earned} LR. 1 celebratory sentence.
```

**Fallback (checkout):**
```
Your cart is ready, {first_name} — ₹{final_price} all in,
with every deal applied. One tap and it's yours.
```

**Fallback (success):**
```
Order confirmed! Your {product_name} is on its way, {first_name} — 
and you just earned {points_earned} LR points. 🎉
```

---

## 🧮 Loyalty Reward Logic

### Redemption (Spend)
| Cart Value | Redeemable % | Rate |
|-----------|-------------|------|
| Up to ₹1,000 | 10% of cart | 1 LR = ₹0.50 |
| ₹1,000–₹2,000 | 7.5% of cart | 1 LR = ₹0.35 |
| ₹2,000–₹5,000 | 5% of cart | 1 LR = ₹0.30 |
| Above ₹5,000 | 3.5% of cart | 1 LR = ₹0.25 |

### Earning
| Cart Value | Earn % | Rate |
|-----------|--------|------|
| Up to ₹1,000 | 7.5% | ₹1 = 0.20 LR |
| ₹1,000–₹2,000 | 5% | ₹1 = 0.35 LR |
| ₹2,000–₹5,000 | 3.5% | ₹1 = 0.40 LR |
| Above ₹5,000 | 2.5% | ₹1 = 0.50 LR |

---

## ⚙️ Out of Scope (Demo Constraints)

| Item | Note |
|------|------|
| Real Instagram API | Simulated UI — no Meta OAuth |
| Live OTP via SMS | Any 6 digits verify in demo |
| Real merchant catalog | Hardcoded mock products |
| Live price scraping | Prices fixed in mock data |
| Actual KwikAI payment | Checkout link is simulated |
| Multi-language | English only |

---

## 👨‍💻 Built By

**Amarjyot Singh** — Product & AI Automation Lead  
GitHub: [@SINGHAMARJYOT](https://github.com/SINGHAMARJYOT)  
Assignment for: AI Commerce Agent Product Role  
Model: Claude claude-opus-4-5 (Anthropic)

---

*Built with Streamlit · Anthropic Claude · Python*
