"""
SISTEMA ELEC — Servidor Cloud (Railway)
"""
import os, json, threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

BASE = os.path.dirname(os.path.abspath(__file__))
app  = Flask(__name__)
CORS(app)

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGISTROS_FILE = DATA_DIR / "registros.json"
PECAS_FILE     = DATA_DIR / "pecas.json"
LAUDOS_FILE    = DATA_DIR / "laudos.json"

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN",   "8647040791:AAGq1YP0BLSlscZ0hKqN68LvHaHPoFvbLns")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8704528010")

def ler(path):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except: pass
    return []

def salvar(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def enviar_telegram(msg):
    try:
        import urllib.request as u
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        req = u.Request(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        data=payload, headers={"Content-Type":"application/json"})
        u.urlopen(req, timeout=10)
    except: pass

# ── PÁGINAS ───────────────────────────────────
@app.route("/")
def index():
    try:
        path = os.path.join(BASE, "index.html")
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return f"Erro: {e} | BASE={BASE}", 500

@app.route("/tecnico")
def tecnico():
    try:
        path = os.path.join(BASE, "tecnico.html")
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return f"Erro: {e} | BASE={BASE}", 500

# ── API REGISTRAR ────────────────────────────
@app.route("/api/registrar", methods=["POST"])
def registrar():
    try:
        d = request.get_json()
        registros = ler(REGISTROS_FILE)
        agora = datetime.now()

        tipo_raw = d.get("tipo_servico", d.get("tipo", ""))
        if "→" in tipo_raw: tipo_raw = tipo_raw.split("→")[0].strip()
        if "\n" in tipo_raw: tipo_raw = tipo_raw.split("\n")[0].strip()

        registro = {
            "id":          str(agora.timestamp()).replace(".",""),
            "data":        agora.strftime("%d/%m/%Y"),
            "hora":        agora.strftime("%H:%M:%S"),
            "portal":      d.get("portal",""),
            "tipo_servico": tipo_raw,
            "endereco":    d.get("endereco",""),
            "funcionario": d.get("funcionario",""),
            "veiculo":     d.get("veiculo",""),
            "status":      d.get("status","ACEITO"),
            "obs":         d.get("obs",""),
            "cliente":     d.get("cliente",""),
            "numero":      d.get("numero","") or d.get("obs",""),
        }
        registros.append(registro)
        salvar(REGISTROS_FILE, registros)
        print(f"  [+] {registro['portal']} | {tipo_raw} | {registro['funcionario']} | {registro['cliente']}")

        status    = registro["status"]
        emoji     = "✅" if status == "ACEITO" else "❌"
        cliente   = registro.get("cliente","") or "—"
        func      = (registro["funcionario"].split()[0].title()
                     if registro["funcionario"] else "—")
        msg = (f"{emoji} {registro['portal']} — {status}\n"
               f"Tipo: {tipo_raw}\n"
               f"Cliente: {cliente}\n"
               f"Funcionário: {func}\n"
               f"Veículo: {registro['veiculo']}\n"
               f"Hora: {registro['hora']}")
        threading.Thread(target=enviar_telegram, args=(msg,), daemon=True).start()
        return jsonify({"ok": True})
    except Exception as e:
        print(f"  ERRO registrar: {e}")
        return jsonify({"ok": False, "erro": str(e)}), 500

@app.route("/api/nova_os", methods=["POST","OPTIONS"])
def nova_os():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})
    return registrar()

@app.route("/salvar_notro", methods=["POST"])
def salvar_notro():
    return registrar()

@app.route("/salvar_juvo", methods=["POST"])
def salvar_juvo():
    return registrar()

# ── LISTAR ────────────────────────────────────
@app.route("/listar")
def listar_route():
    try:
        registros = ler(REGISTROS_FILE)
        res = {"NOTRO":[], "TEMPO SLZ":[], "ACIONA FACIL":[], "MONDIAL":[]}
        for r in registros:
            aba = r.get("portal","NOTRO")
            if aba not in res: res[aba] = []
            res[aba].append({
                "DATA":        r.get("data",""),
                "HORA":        r.get("hora",""),
                "PORTAL":      r.get("portal",""),
                "TIPO SERVIÇO":r.get("tipo_servico",""),
                "ENDEREÇO":    r.get("endereco",""),
                "FUNCIONÁRIO": r.get("funcionario",""),
                "VEÍCULO":     r.get("veiculo",""),
                "STATUS":      r.get("status",""),
                "OBS":         r.get("obs",""),
                "CLIENTE":     r.get("cliente",""),
            })
        return jsonify(res)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ── APP TÉCNICO ───────────────────────────────
@app.route("/api/os_tecnico")
def os_tecnico():
    try:
        tec   = request.args.get("tecnico","").upper()
        hoje  = datetime.now().strftime("%d/%m/%Y")
        lista = []
        for i, r in enumerate(ler(REGISTROS_FILE)):
            func = r.get("funcionario","").upper()
            if tec and tec not in func: continue
            if r.get("status") not in ["ACEITO","EM ANDAMENTO"]: continue
            if r.get("data","") != hoje: continue
            tipo = r.get("tipo_servico","")
            if "→" in tipo: tipo = tipo.split("→")[0].strip()
            if not tipo or len(tipo) < 2: tipo = "Serviço"
            lista.append({
                "id":           r.get("id", str(i)),
                "numero":       r.get("numero","") or r.get("obs","") or f"OS-{i+1}",
                "portal":       r.get("portal",""),
                "tipo_servico": tipo,
                "endereco":     r.get("endereco",""),
                "cliente":      r.get("cliente",""),
                "status":       "NOVA" if r.get("status")=="ACEITO" else "DESLOCAMENTO",
                "hora":         r.get("hora",""),
                "funcionario":  r.get("funcionario",""),
                "veiculo":      r.get("veiculo",""),
            })
        return jsonify({"ok": True, "os": lista})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e), "os": []}), 500

@app.route("/api/atualizar_os", methods=["POST"])
def atualizar_os():
    try:
        d = request.get_json()
        print(f"  [OS] {d.get('id')} → {d.get('status')}")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500

# ── LAUDO ─────────────────────────────────────
@app.route("/api/laudo", methods=["POST"])
def salvar_laudo():
    try:
        d      = request.get_json()
        laudos = ler(LAUDOS_FILE)
        laudos.append({**d, "salvo_em": datetime.now().isoformat()})
        salvar(LAUDOS_FILE, laudos)
        msg = (f"✅ SERVIÇO FINALIZADO\n"
               f"OS: {d.get('os_numero','')}\n"
               f"Técnico: {d.get('tecnico','').title()}\n"
               f"Cliente: {d.get('nome_cliente','')}\n"
               f"Resolvido: {d.get('resolvido','')}")
        threading.Thread(target=enviar_telegram, args=(msg,), daemon=True).start()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500

@app.route("/api/laudos")
def listar_laudos():
    return jsonify({"ok": True, "laudos": ler(LAUDOS_FILE)})

# ── PEÇAS ─────────────────────────────────────
@app.route("/api/pecas", methods=["GET"])
def listar_pecas():
    return jsonify({"ok": True, "pecas": ler(PECAS_FILE)})

@app.route("/api/pecas", methods=["POST"])
def adicionar_peca():
    try:
        d     = request.get_json()
        pecas = ler(PECAS_FILE)
        peca  = {
            "id":      str(datetime.now().timestamp()).replace(".",""),
            "nome":    d.get("nome",""),
            "marca":   d.get("marca",""),
            "modelo":  d.get("modelo",""),
            "tipo":    d.get("tipo",""),
            "valor":   d.get("valor",""),
            "estoque": d.get("estoque",0),
            "criado":  datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        pecas.append(peca)
        salvar(PECAS_FILE, pecas)
        return jsonify({"ok": True, "peca": peca})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500

@app.route("/api/pecas/<pid>", methods=["DELETE"])
def remover_peca(pid):
    try:
        pecas = [p for p in ler(PECAS_FILE) if p["id"] != pid]
        salvar(PECAS_FILE, pecas)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500

# ── STATUS ────────────────────────────────────
@app.route("/api/status")
def status():
    return jsonify({"ok": True, "registros": len(ler(REGISTROS_FILE))})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"⚡ SISTEMA ELEC — Cloud — porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
