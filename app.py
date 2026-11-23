import os, json, sqlite3, csv, io, hmac, hashlib, secrets
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, render_template_string, Response, redirect, url_for, abort

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12000
DB = os.environ.get("DB_PATH", "/opt/render/project/src/netflix_test_responses.sqlite3")
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
DEVICE_COOKIE = "tt_netflix_attempt_finished_v2"
ONE_YEAR = 365 * 24 * 60 * 60

def signed_completion_cookie():
    token = secrets.token_urlsafe(24)
    mac = hmac.new(ADMIN_PASSWORD.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
    return token + "." + mac

def has_completed_cookie():
    cookie = request.cookies.get(DEVICE_COOKIE, "")
    if not ADMIN_PASSWORD or len(cookie) > 150 or "." not in cookie:
        return False
    token, received = cookie.rsplit(".", 1)
    expected = hmac.new(ADMIN_PASSWORD.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
    return bool(token) and hmac.compare_digest(received, expected)

def completion_page(title, message):
    return render_template_string(TEMPLATE_HEAD + """
    <main><section class="hero"><div class="brand">Türk Telekom ◆</div>
    <div class="small">Personel bilgi testi</div><h1>{{ title }}</h1><p>{{ message }}</p></section>
    <p class="info">Her personel ve tarayıcı için bir katılım hakkı bulunmaktadır.
    Yardım gerektiğinde yöneticinize başvurabilirsiniz.</p></main>
    </body></html>""", title=title, message=message)

@app.get("/completed")
def completed():
    return completion_page("Katılım hakkınız kullanıldı.", "Bu cihazın bu tarayıcısından test yalnızca bir kez tamamlanabilir.")
KEYS = ["C","A","B","B","C","B","A","C","B","B"]
QUESTIONS = [
 ("Netflix Hediyeli İnternet + Tivibu kampanyası aşağıdaki müşteri gruplarından hangisine yönelik değildir?", ["Yeni bireysel ev interneti aboneliği başlatan müşterilere", "İnternet ve Tivibu IPTV hizmetlerini birlikte alan yeni bireysel müşterilere", "Kurumsal internet aboneliği açtıran işletmelere", "18 ay taahhütle yeni bireysel ev interneti müşterisi olanlara"]),
 ("Kampanyada internet ve Tivibu taahhüdü ile Netflix faydasının toplam süresi sırasıyla kaç aydır?", ["İnternet ve Tivibu 18 ay, Netflix 12 ay", "İnternet ve Tivibu 12 ay, Netflix 18 ay", "İnternet ve Tivibu 18 ay, Netflix 18 ay", "İnternet ve Tivibu 12 ay, Netflix 12 ay"]),
 ("Netflix hediyeli kampanyalarda internet (DSL) aboneliği zorunlu mudur?", ["Evet, her Netflix kampanyasında DSL aboneliği zorunludur", "Hayır. DSL + Tivibu ile veya yalnızca Tivibu Süper Paket üzerinden yararlanılabilir", "Hayır, yalnızca DSL aboneliği yeterlidir", "Evet, Tivibu olmadan yalnızca DSL aboneliğiyle yararlanılır"]),
 ("Kampanya kapsamında Netflix kaç ay ücretsiz sunulmaktadır?", ["3 ay", "6 ay", "12 ay", "18 ay"]),
 ("Netflix üyeliğinin 7–12. aylarındaki ücretlendirme nasıl yapılır?", ["Ücretsiz devam eder", "Her ay güncel fiyat uygulanır", "Kampanyaya katılım tarihindeki fiyatla sabit ücretlendirilir", "Netflix üyeliği iptal edilir"]),
 ("Netflix üyeliğinin 13. ayından itibaren hangi fiyat uygulanır?", ["İlk 6 ayın fiyatı", "O tarihteki güncel Netflix fiyatı", "%50 indirimli fiyat", "Ücret alınmaz"]),
 ("Netflix avantajı açısından İnternet + Tivibu kampanyası ile yalnızca Tivibu kampanyasının paket koşulları nasıl farklılaşır?", ["İnternet + Tivibu kampanyasında tüm Tivibu paketleri; yalnızca Tivibu kampanyasında sadece Süper Paket geçerlidir", "Her iki kampanyada sadece Süper Paket geçerlidir", "İnternet + Tivibu kampanyasında sadece Süper Paket; yalnızca Tivibu kampanyasında tüm paketler geçerlidir", "Her iki kampanyada tüm Tivibu paketleri geçerlidir"]),
 ("Kampanya kapsamında hangi Netflix paketleri seçilebilir?", ["Yalnızca Temel", "Yalnızca Premium", "Temel, Standart veya Premium", "Yalnızca Standart"]),
 ("Müşteri Netflix üyeliğini nasıl aktif hale getirir?", ["Türk Telekom bayisine tekrar gelerek", "İnternet ve Tivibu aktivasyonundan sonra gönderilen SMS üzerinden mevcut hesabını bağlayarak veya yeni üyelik açarak", "Netflix müşteri hizmetlerini arayarak", "Üyelik hiçbir işlem gerekmeden otomatik açılır"]),
 ("Müşteri, “Netflix 18 ay boyunca ücretsiz mi?” diye sorarsa doğru yanıt hangisidir?", ["Evet, 18 ay boyunca ücretsizdir", "İlk 6 ay ücretsizdir. 7–12. aylar arasında sabit ücret, 13. aydan itibaren güncel Netflix fiyatı uygulanır", "İlk 12 ay ücretsizdir", "Sadece ilk ay ücretsizdir"])
]
CSS = """
:root{color-scheme:light;font-family:Inter,system-ui,-apple-system,'Segoe UI',Arial,sans-serif;color:#0b2450}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,#f4fbff,#e9f0ff 55%,#faffff);min-height:100vh}
main{max-width:780px;margin:0 auto;padding:22px 18px 70px}
.hero{background:linear-gradient(130deg,#071e4d,#064b9b 70%,#13c5d5);color:white;border-radius:24px;padding:28px 26px;box-shadow:0 12px 34px #1f59aa25}
.brand{font-weight:850;letter-spacing:-.7px;font-size:20px}.small{font-size:12px;opacity:.78;letter-spacing:1.3px;text-transform:uppercase}
h1{font-size:clamp(27px,5vw,40px);line-height:1.1;margin:22px 0 14px;letter-spacing:-1px}
.hero p{line-height:1.5;color:#dbedff;margin:0}.pill{background:#12dde5;color:#002551;border-radius:99px;padding:9px 14px;display:inline-block;font-weight:850;margin-top:18px}
.info{margin:20px 0;color:#456080;line-height:1.6;font-size:14px}
.card{background:white;border:1px solid #e3edf9;border-radius:18px;margin:16px 0;padding:23px;box-shadow:0 5px 20px #1d468010}
label.field{display:block;font-weight:750;font-size:14px;margin:15px 0 5px}
input[type=text]{width:100%;padding:13px;border-radius:12px;border:1px solid #c5d9eb;font:inherit;outline-color:#17bed3}
h3{font-size:17px;margin:0 0 14px;line-height:1.45}.index{color:#11abbc;font-weight:900}
.answer{display:flex;gap:12px;align-items:flex-start;padding:13px;margin:8px 0;border:1px solid #dce9f8;border-radius:12px;cursor:pointer;line-height:1.4}
.answer:hover{background:#f3fbff}.answer:has(input:checked){background:#e6faff;border-color:#00a3ce;box-shadow:0 0 0 1px #00a3ce}
input[type=radio]{accent-color:#0589c9;margin-top:4px;transform:scale(1.2)}
.btn{display:block;width:100%;background:linear-gradient(100deg,#0475c5,#04c6d7);color:white;font:inherit;font-weight:850;border:0;padding:17px;border-radius:14px;cursor:pointer;margin-top:25px}
.progress{height:6px;border-radius:8px;background:#dbeaf8;overflow:hidden;margin-top:16px}.bar{height:100%;width:0;background:#11d8dc;transition:width .2s}
footer{text-align:center;margin-top:25px;font-size:12px;color:#7891a8}
table{width:100%;border-collapse:collapse;background:white;font-size:13px}th,td{border-bottom:1px solid #e4edf7;padding:10px 8px;text-align:left}th{background:#dff7ff}
a{color:#0076be}.stats{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.stat{background:white;border-radius:12px;padding:17px;flex:1;min-width:130px}.stat b{font-size:28px;display:block}
@media(max-width:580px){main{padding:12px 12px 50px}.hero{padding:24px 20px}.card{padding:19px 15px}.answer{padding:12px 10px}table{font-size:11px}}
"""
TEMPLATE_HEAD = "<!doctype html><html lang='tr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow'><title>Netflix Kampanya Bilgi Testi</title><style>"+CSS+"</style></head><body>"
class PostgresConnection:
    def __init__(self, raw):
        self.raw = raw

    def execute(self, statement, values=()):
        sql = "BEGIN" if statement.strip().upper() == "BEGIN IMMEDIATE" else statement.replace("?", "%s")
        return self.raw.execute(sql, values)

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()


def db():
    if DATABASE_URL:
        raw = psycopg.connect(DATABASE_URL, connect_timeout=8, row_factory=dict_row)
        raw.execute("""CREATE TABLE IF NOT EXISTS responses (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            branch TEXT NOT NULL,
            answers TEXT NOT NULL,
            score INTEGER NOT NULL,
            submitted_at TEXT NOT NULL,
            UNIQUE(name, branch))""")
        raw.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_person_branch_norm
                       ON responses(lower(name), lower(branch))""")
        raw.commit()
        return PostgresConnection(raw)
    # Historic local data may only survive within its original temporary server instance.
    con = sqlite3.connect(DB, timeout=25)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        branch TEXT NOT NULL,
        answers TEXT NOT NULL,
        score INTEGER NOT NULL,
        submitted_at TEXT NOT NULL,
        UNIQUE(name, branch))""")
    con.commit()
    return con


def storage_not_ready():
    return render_template_string(TEMPLATE_HEAD + """
    <main><section class="hero"><div class="brand">Türk Telekom ◆</div>
    <div class="small">Netflix Kampanyası Bilgi Testi</div>
    <h1>Test geçici olarak kapalı.</h1>
    <p>Yanıtların güvenle saklanabilmesi için kalıcı veritabanı bağlantısı henüz tamamlanmadı.
    Bu nedenle şu anda yeni sınav gönderimi kabul edilmiyor.</p></section>
    <p class="info">Önceden testi tamamladıysanız yeniden giriş yapmayın.
    Sınav sorumlusu sonuçlar ve yeni katılım hakkında bilgilendirme yapacaktır.</p></main>
    </body></html>""")


@app.after_request
def headers(resp):
    resp.headers['X-Content-Type-Options']='nosniff'
    resp.headers['X-Frame-Options']='DENY'
    resp.headers['Referrer-Policy']='no-referrer'
    resp.headers['Cache-Control']='no-store'
    return resp

@app.get("/")
def home():
    if not DATABASE_URL:
        return storage_not_ready()
    if has_completed_cookie():
        return redirect("/completed")
    content = """
    <script>try {if(localStorage.getItem("tt_netflix_attempt_finished_v2")==="yes"){location.replace("/completed");}} catch(e){}</script>
    <main><section class="hero"><div class="brand">Türk Telekom <span style="color:#16f2f2">◆</span></div>
    <div class="small">Personel bilgi ve yetkinlik testi</div>
    <h1>Netflix Hediyeli<br>İnternet + Tivibu<br>Kampanyası</h1>
    <p>Kampanyayı ne kadar iyi tanıyorsunuz? 10 soruluk bilgi testini tamamlayın.</p>
    <span class="pill">10 SORU · 100 PUAN</span></section>
    <div class="info">Lütfen adınızı, soyadınızı ve bayi adını girin. Her soruda tek seçenek işaretleyin. Bu test tek katılımlıktır: Gönderdikten sonra aynı tarayıcıda yeniden açılmaz, aynı ad-soyad ve bayiyle ikinci gönderim kabul edilmez. Yanıtınız yöneticinizin değerlendirmesi için kaydedilecektir.</div>
    <form action="/submit" method="post" id="test">
       <section class="card"><h3>Personel Bilgileri</h3>
       <label class="field" for="name">Ad Soyad</label><input id="name" type="text" name="name" maxlength="120" autocomplete="name" placeholder="Adınız ve soyadınız" required>
       <label class="field" for="branch">Bayi Adı / Kodu</label><input id="branch" type="text" name="branch" maxlength="120" placeholder="Bayi adı veya kodu" required>
       <input type="text" name="website" style="display:none" tabindex="-1" autocomplete="off"></section>
       {% for q in questions %}
       <section class="card"><h3><span class="index">{{ loop.index | string | e }}.</span> {{q[0]}}</h3>
       {% set idx = loop.index0 %}
       {% for choice in q[1] %}
       <label class="answer"><input type="radio" name="q{{idx}}" value="{{'ABCD'[loop.index0]}}" required><span><strong>{{'ABCD'[loop.index0]}})</strong> {{choice}}</span></label>
       {% endfor %}</section>
       {% endfor %}
       <button class="btn">Cevaplarımı Gönder</button>
       <div class="progress"><div class="bar" id="bar"></div></div>
    </form>
    <footer>Bu test, paylaşılan kampanya özetindeki bilgilere göre hazırlanmıştır.<br>Kampanya koşullarının güncelliği ayrıca doğrulanmalıdır.</footer></main>
    <script>const radios=document.querySelectorAll('input[type=radio]');radios.forEach(el=>el.addEventListener('change',()=>{const n=new Set([...radios].filter(x=>x.checked).map(x=>x.name)).size;document.getElementById('bar').style.width=(n*10)+'%'}));</script>
    """
    return render_template_string(TEMPLATE_HEAD+content+"</body></html>",questions=QUESTIONS)

@app.post("/submit")
def submit():
    if not DATABASE_URL:
        return storage_not_ready(), 503
    if has_completed_cookie():
        return redirect("/completed")
    if request.form.get("website"):
        return redirect("/")
    name=" ".join(request.form.get("name","").strip().split())
    branch=" ".join(request.form.get("branch","").strip().split())
    if not 3<=len(name)<=120 or not 2<=len(branch)<=120:
        abort(400)
    answers=[request.form.get("q"+str(i),"") for i in range(10)]
    if any(a not in "ABCD" or len(a)!=1 for a in answers):
        abort(400)
    score=sum(a==b for a,b in zip(answers,KEYS))*10
    con=db()
    try:
        con.execute("BEGIN IMMEDIATE")
        existing=con.execute("""SELECT 1 FROM responses
                                WHERE lower(name)=lower(?) AND lower(branch)=lower(?)
                                LIMIT 1""",(name,branch)).fetchone()
        if existing:
            con.rollback()
            return completion_page("Bu personel testi daha önce tamamlamış.", "Aynı ad-soyad ve bayi için ikinci katılım kabul edilmiyor.")
        con.execute("""INSERT INTO responses (name,branch,answers,score,submitted_at)
                       VALUES (?,?,?,?,?)""",
                    (name,branch,json.dumps(answers,ensure_ascii=False),score,datetime.now(timezone.utc).isoformat()))
        con.commit()
    except (sqlite3.IntegrityError, psycopg.errors.UniqueViolation):
        con.rollback()
        return completion_page("Bu personel testi daha önce tamamlamış.", "Aynı personel ve bayi için ikinci katılım kabul edilmiyor.")
    finally:
        con.close()
    page=render_template_string(TEMPLATE_HEAD+"""
    <main><section class="hero"><div class="brand">Türk Telekom ◆</div><h1>Cevaplarınız alındı. ✓</h1>
    <p>Katılımınız için teşekkürler. Yanıtlarınız değerlendirildikten sonra sonuçlar yöneticiniz tarafından incelenecektir.</p>
    <p style="color:#daf6fa;margin-top:16px">Testiniz tamamlandı. Aynı tarayıcıdan tekrar katılım yapılamaz.</p>
    </section></main>
    <script>try{localStorage.setItem("tt_netflix_attempt_finished_v2","yes")}catch(e){}</script>
    </body></html>""")
    response=Response(page)
    response.set_cookie(DEVICE_COOKIE,signed_completion_cookie(),max_age=ONE_YEAR,secure=True,httponly=True,samesite="Lax",path="/")
    return response

def admin_only(fn):
    @wraps(fn)
    def check(*a,**kw):
        auth=request.authorization
        if not ADMIN_PASSWORD or not auth or not hmac.compare_digest(auth.username or "","yonetici") or not hmac.compare_digest(auth.password or "",ADMIN_PASSWORD):
            return Response("Yönetici girişi gerekli",401,{"WWW-Authenticate":'Basic realm="Personel Testi - Yonetici"'})
        return fn(*a,**kw)
    return check

@app.get("/admin")
@admin_only
def admin():
    if not DATABASE_URL:
        return storage_not_ready()
    con=db()
    rows=[dict(x) for x in con.execute("SELECT * FROM responses ORDER BY branch,name")]
    con.close()
    count=len(rows); avg=round(sum(r['score'] for r in rows)/count,1) if count else 0
    grouped={}
    freq=[0]*10
    for r in rows:
        grouped.setdefault(r["branch"],[]).append(r["score"])
        for i,a in enumerate(json.loads(r["answers"])):
            if a==KEYS[i]:freq[i]+=1
    stats=sorted([(k,len(v),round(sum(v)/len(v),1)) for k,v in grouped.items()])
    body="""<main><section class='hero'><div class='small'>Yönetici paneli</div><h1>Personel Bilgi Testi<br>Sonuçları</h1><p>Yanıtlar yönetici erişimine özeldir.</p></section>
    <div class='stats'><div class='stat'><b>{{count}}</b>Personel</div><div class='stat'><b>{{avg}}</b>Ortalama puan</div><div class='stat'><b>{{groups|length}}</b>Bayi</div></div>
    <p><a href='/admin/export.csv'>↓ Tüm sonuçları Excel için CSV olarak indir</a></p>
    <section class='card' style='overflow:auto'><h3>Personel Bazında</h3><table><thead><tr><th>Bayi</th><th>Personel</th><th>Puan</th><th>Tarih (UTC)</th></tr></thead><tbody>
    {% for r in rows %}<tr><td>{{r.branch}}</td><td>{{r.name}}</td><td><strong>{{r.score}}</strong></td><td>{{r.submitted_at[:16]}}</td></tr>{%endfor%}</tbody></table></section>
    <section class='card'><h3>Bayi Bazında</h3><table><tr><th>Bayi</th><th>Katılım</th><th>Ortalama</th></tr>
    {%for g in groups%}<tr><td>{{g[0]}}</td><td>{{g[1]}}</td><td>{{g[2]}}</td></tr>{%endfor%}</table></section>
    <section class='card'><h3>Soru Bazında Doğru Yanıt Oranı</h3><table><tr><th>Soru</th><th>Doğru</th></tr>
    {%for f in freq%}<tr><td>{{loop.index}}. soru</td><td>{{(100*f/count)|round(1) if count else 0}}%</td></tr>{%endfor%}</table></section>
    <footer>Veriler güvenli süreklilik için ayrıca yedeklenmelidir.</footer></main></body></html>"""
    return render_template_string(TEMPLATE_HEAD+body,rows=rows,groups=stats,freq=freq,count=count,avg=avg)

def csv_cell(x):
    s=str(x)
    return "'"+s if s and s[0] in "=+-@" else s

@app.get("/admin/export.csv")
@admin_only
def export():
    if not DATABASE_URL:
        return storage_not_ready(), 503
    con=db()
    rows=con.execute("SELECT name,branch,answers,score,submitted_at FROM responses ORDER BY branch,name").fetchall()
    con.close()
    f=io.StringIO()
    w=csv.writer(f)
    w.writerow(["Ad Soyad","Bayi","Puan","Tarih (UTC)"]+["Soru "+str(i+1) for i in range(10)])
    for r in rows:
        w.writerow([csv_cell(r["name"]),csv_cell(r["branch"]),r["score"],r["submitted_at"]]+json.loads(r["answers"]))
    return Response("\ufeff"+f.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=netflix_personel_sonuclari.csv"})

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
