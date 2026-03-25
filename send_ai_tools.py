import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json
import os

# ============================================================
# CONFIGURATION
# ============================================================
SENDER_EMAIL = "verozanoot@gmail.com"
SENDER_APP_PASSWORD = "aogy ssgi dtqy kqxv"  # Gmail App Password
RECEIVER_EMAIL = "verozanoot@gmail.com"
NUM_TOOLS = 10

# ============================================================
# FETCH AI TOOLS FROM FREE APIs
# ============================================================
def fetch_ai_tools():
    tools = []
    
    # Source 1: ProductHunt via public API (no key needed)
    try:
        today = datetime.now()
        url = "https://www.producthunt.com/frontend/graphql"
        query = """
        {
          posts(order: VOTES, topic: "artificial-intelligence", first: 15) {
            edges {
              node {
                name
                tagline
                url
                votesCount
                website
              }
            }
          }
        }
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            posts = data.get("data", {}).get("posts", {}).get("edges", [])
            for post in posts[:NUM_TOOLS]:
                node = post["node"]
                tools.append({
                    "name": node.get("name", "Unknown"),
                    "description": node.get("tagline", "No description"),
                    "url": node.get("website") or node.get("url", "#"),
                    "votes": node.get("votesCount", 0),
                    "source": "Product Hunt"
                })
    except Exception as e:
        print(f"ProductHunt error: {e}")

    # Source 2: Fallback - Hacker News AI stories
    if len(tools) < NUM_TOOLS:
        try:
            hn_url = "https://hn.algolia.com/api/v1/search?query=AI+tool&tags=story&hitsPerPage=20"
            resp = requests.get(hn_url, timeout=10)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                for hit in hits:
                    if len(tools) >= NUM_TOOLS:
                        break
                    title = hit.get("title", "")
                    if any(kw in title.lower() for kw in ["ai", "gpt", "llm", "model", "tool", "assistant"]):
                        tools.append({
                            "name": title[:60],
                            "description": f"From Hacker News — {hit.get('points', 0)} points",
                            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                            "votes": hit.get("points", 0),
                            "source": "Hacker News"
                        })
        except Exception as e:
            print(f"HackerNews error: {e}")

    # Fallback static list if APIs fail
    if len(tools) < 5:
        fallback = [
            {"name": "Claude", "description": "Anthropic ka powerful AI assistant", "url": "https://claude.ai", "votes": 999, "source": "Anthropic"},
            {"name": "ChatGPT", "description": "OpenAI ka conversational AI", "url": "https://chatgpt.com", "votes": 999, "source": "OpenAI"},
            {"name": "Gemini", "description": "Google ka multimodal AI", "url": "https://gemini.google.com", "votes": 999, "source": "Google"},
            {"name": "Perplexity", "description": "AI-powered search engine", "url": "https://perplexity.ai", "votes": 850, "source": "Perplexity"},
            {"name": "Midjourney", "description": "AI image generation tool", "url": "https://midjourney.com", "votes": 900, "source": "Midjourney"},
        ]
        tools.extend(fallback)

    return tools[:NUM_TOOLS]


# ============================================================
# BUILD BEAUTIFUL HTML EMAIL
# ============================================================
def build_html_email(tools):
    today_str = datetime.now().strftime("%A, %d %B %Y")
    
    tool_cards = ""
    for i, tool in enumerate(tools, 1):
        emoji = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"][i-1]
        tool_cards += f"""
        <div style="background:#ffffff; border:1px solid #e8e8e8; border-radius:12px;
                    padding:20px; margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <div style="display:flex; align-items:center; margin-bottom:8px;">
            <span style="font-size:22px; margin-right:10px;">{emoji}</span>
            <a href="{tool['url']}" style="font-size:18px; font-weight:700;
               color:#2D3748; text-decoration:none;">{tool['name']}</a>
            <span style="margin-left:auto; font-size:11px; color:#A0AEC0;
                  background:#F7FAFC; padding:3px 8px; border-radius:20px;">
              {tool['source']}
            </span>
          </div>
          <p style="color:#718096; font-size:14px; margin:0 0 12px 0;">
            {tool['description']}
          </p>
          <a href="{tool['url']}"
             style="display:inline-block; background:linear-gradient(135deg,#667eea,#764ba2);
                    color:white; padding:8px 18px; border-radius:8px;
                    text-decoration:none; font-size:13px; font-weight:600;">
            🔗 Try Now
          </a>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:0; background:#F0F4F8; font-family:'Segoe UI',Arial,sans-serif;">

      <div style="max-width:620px; margin:30px auto; background:#F0F4F8; padding:20px;">

        <!-- HEADER -->
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                    border-radius:16px; padding:32px; text-align:center; margin-bottom:24px;">
          <div style="font-size:48px; margin-bottom:8px;">🤖</div>
          <h1 style="color:white; margin:0; font-size:26px; font-weight:800;">
            Daily AI Tools Digest
          </h1>
          <p style="color:rgba(255,255,255,0.85); margin:8px 0 0; font-size:15px;">
            {today_str}
          </p>
          <div style="background:rgba(255,255,255,0.2); border-radius:20px;
                      padding:6px 16px; display:inline-block; margin-top:12px;">
            <span style="color:white; font-size:13px;">⚡ Top {len(tools)} AI Tools Today</span>
          </div>
        </div>

        <!-- TOOLS LIST -->
        <div style="margin-bottom:24px;">
          {tool_cards}
        </div>

        <!-- FOOTER -->
        <div style="text-align:center; padding:20px; color:#A0AEC0; font-size:12px;">
          <p style="margin:0;">🤖 Yeh email automatically generate hui hai</p>
          <p style="margin:6px 0 0;">Har raat 10 PM Pakistan Time • Daily AI Tools Bot</p>
        </div>

      </div>
    </body>
    </html>
    """
    return html


# ============================================================
# SEND EMAIL
# ============================================================
def send_email(html_content, tools_count):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 Aaj ke Top {tools_count} AI Tools — {datetime.now().strftime('%d %b %Y')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    # Plain text fallback
    plain = f"Aaj ke Top {tools_count} AI Tools — {datetime.now().strftime('%d %b %Y')}\nHTML email support enable karein behtar experience ke liye."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"✅ Email successfully sent to {RECEIVER_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Email send karne mein error: {e}")
        return False


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("🔍 AI Tools fetch ho rahi hain...")
    tools = fetch_ai_tools()
    print(f"✅ {len(tools)} tools mili hain")
    
    print("📧 Email build ho rahi hai...")
    html = build_html_email(tools)
    
    print("📤 Email bhej raha hun...")
    send_email(html, len(tools))
