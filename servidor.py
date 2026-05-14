"""
SISTEMA ELEC — Servidor Cloud (Railway)
HTML embutido diretamente — sem dependência de arquivos externos
"""
import os, json, threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGISTROS_FILE = DATA_DIR / "registros.json"
PECAS_FILE     = DATA_DIR / "pecas.json"
LAUDOS_FILE    = DATA_DIR / "laudos.json"

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN",   "8647040791:AAGq1YP0BLSlscZ0hKqN68LvHaHPoFvbLns")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8704528010")

# ── HTML EMBUTIDO ────────────────────────────
INDEX_HTML   = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ELEC — Sistema de Gestão</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0f0f13;
  --surface: #17171d;
  --card: #1e1e26;
  --border: rgba(255,255,255,0.07);
  --text: #f0f0f5;
  --muted: #6b6b80;
  --azul: #4d9fff;
  --verde: #3ddc84;
  --amarelo: #ffb84d;
  --roxo: #a06bff;
  --vermelho: #ff5c5c;
  --notro: #4d9fff;
  --juvo: #3ddc84;
  --aciona: #a06bff;
  --mondial: #ffb84d;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--text); font-family:'Space Grotesk',sans-serif; min-height:100vh; padding:20px; }

.topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; }
.topbar h1 { font-size:18px; font-weight:600; }
.status-pill { display:flex; align-items:center; gap:8px; background:var(--card); border:1px solid var(--border); border-radius:100px; padding:8px 16px; font-size:12px; color:var(--verde); }
.status-dot { width:7px; height:7px; border-radius:50%; background:var(--verde); box-shadow:0 0 8px var(--verde); animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px; }
.metric { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:20px; }
.metric-label { font-size:12px; color:var(--muted); margin-bottom:8px; }
.metric-value { font-size:32px; font-weight:700; line-height:1; }
.metric-value.azul { color:var(--azul); }
.metric-value.verde { color:var(--verde); }
.metric-value.amarelo { color:var(--amarelo); }
.metric-value.roxo { color:var(--roxo); }

.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:20px; }

.panel { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:20px; }
.panel-title { font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:16px; font-family:'Space Mono',monospace; }

/* OS LIST */
.os-item { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px solid var(--border); }
.os-item:last-child { border-bottom:none; }
.os-icon { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0; }
.os-icon.eletrica { background:rgba(77,159,255,0.15); }
.os-icon.branca    { background:rgba(61,220,132,0.15); }
.os-icon.encanador { background:rgba(160,107,255,0.15); }
.os-info { flex:1; min-width:0; }
.os-tipo { font-size:14px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.os-sub { font-size:11px; color:var(--muted); margin-top:2px; font-family:'Space Mono',monospace; }
.os-badge { font-size:10px; font-weight:700; padding:4px 10px; border-radius:20px; white-space:nowrap; flex-shrink:0; }
.badge-aceito      { background:rgba(77,159,255,0.15); color:var(--azul); }
.badge-andamento   { background:rgba(255,184,77,0.15); color:var(--amarelo); }
.badge-concluido   { background:rgba(61,220,132,0.15); color:var(--verde); }
.badge-recusado    { background:rgba(255,92,92,0.15); color:var(--vermelho); }

/* TÉCNICOS */
.tec-item { display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--border); }
.tec-item:last-child { border-bottom:none; }
.tec-avatar { width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:14px; flex-shrink:0; }
.av-c { background:rgba(77,159,255,0.2); color:var(--azul); }
.av-l { background:rgba(160,107,255,0.2); color:var(--roxo); }
.tec-info { flex:1; }
.tec-nome { font-size:14px; font-weight:600; }
.tec-tipo { font-size:11px; color:var(--muted); margin-top:1px; }
.tec-os { font-size:20px; font-weight:700; color:var(--azul); }
.tec-os-label { font-size:9px; color:var(--muted); font-family:'Space Mono',monospace; text-align:right; }

/* PORTAIS */
.portal-row { display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid var(--border); }
.portal-row:last-child { border-bottom:none; }
.portal-nome { font-size:13px; font-weight:500; width:90px; flex-shrink:0; }
.portal-bar-wrap { flex:1; height:5px; background:var(--border); border-radius:3px; overflow:hidden; }
.portal-bar { height:100%; border-radius:3px; transition:width .6s; }
.portal-count { font-size:13px; font-weight:700; font-family:'Space Mono',monospace; min-width:20px; text-align:right; }

/* BOTTOM BUTTONS */
.bottom-btns { display:flex; gap:10px; }
.btt { flex:1; padding:13px; background:var(--card); border:1px solid var(--border); border-radius:12px; color:var(--text); font-family:'Space Grotesk',sans-serif; font-size:13px; font-weight:600; cursor:pointer; transition:background .2s; }
.btt:hover { background:#2a2a35; }
.btt.primary { background:var(--azul); color:#000; border-color:var(--azul); }
.btt.primary:hover { background:#6db3ff; }

/* TABS */
.tabs { display:flex; gap:4px; margin-bottom:20px; }
.tab { padding:8px 16px; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; color:var(--muted); border:1px solid transparent; }
.tab.ativa { background:var(--card); color:var(--text); border-color:var(--border); }

.empty { text-align:center; padding:30px; color:var(--muted); font-size:13px; }

/* MODAL */
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.7); z-index:100; display:none; align-items:center; justify-content:center; }
.modal-overlay.aberto { display:flex; }
.modal { background:var(--card); border:1px solid var(--border); border-radius:18px; padding:28px; width:100%; max-width:440px; }
.modal h2 { font-size:18px; margin-bottom:16px; }
.campo { margin-bottom:14px; }
.campo label { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; display:block; margin-bottom:6px; }
.campo input, .campo select { width:100%; padding:11px 14px; background:var(--surface); border:1px solid var(--border); border-radius:10px; color:var(--text); font-family:'Space Grotesk',sans-serif; font-size:14px; outline:none; }
.campo input:focus, .campo select:focus { border-color:var(--azul); }
.modal-btns { display:flex; gap:10px; margin-top:20px; }
</style>
</head>
<body>

<div class="topbar">
  <h1>ELEC Empreendimentos — Sistema de Gestão</h1>
  <div class="status-pill">
    <div class="status-dot"></div>
    <span>Agente monitorando portais</span>
    <span style="color:var(--muted);font-family:'Space Mono',monospace" id="hora-top">--:--</span>
  </div>
</div>

<div class="tabs">
  <div class="tab ativa" onclick="mostrarAba('hoje')">📊 Hoje</div>
  <div class="tab" onclick="mostrarAba('historico')">📋 Ordens de Serviço</div>
  <div class="tab" onclick="mostrarAba('tecnicos')">👷 Técnicos</div>
  <div class="tab" onclick="mostrarAba('pecas')">🔩 Estoque de Peças</div>
</div>

<!-- ABA HOJE -->
<div id="aba-hoje">
  <div class="metrics">
    <div class="metric">
      <div class="metric-label">Serviços hoje</div>
      <div class="metric-value azul" id="m-hoje">0</div>
    </div>
    <div class="metric">
      <div class="metric-label">OS aceitas</div>
      <div class="metric-value verde" id="m-aceitas">0</div>
    </div>
    <div class="metric">
      <div class="metric-label">Em andamento</div>
      <div class="metric-value amarelo" id="m-andamento">0</div>
    </div>
    <div class="metric">
      <div class="metric-label">Recusadas</div>
      <div class="metric-value" style="color:var(--vermelho)" id="m-recusadas">0</div>
    </div>
  </div>

  <div class="grid2">
    <div class="panel">
      <div class="panel-title">Ordens de Serviço — Hoje</div>
      <div id="lista-os"><div class="empty">Carregando...</div></div>
    </div>
    <div>
      <div class="panel" style="margin-bottom:12px">
        <div class="panel-title">Técnicos</div>
        <div class="tec-item">
          <div class="tec-avatar av-c">CA</div>
          <div class="tec-info">
            <div class="tec-nome">Carlos Augusto</div>
            <div class="tec-tipo">Elétrica · Encanador</div>
          </div>
          <div style="text-align:right">
            <div class="tec-os" id="os-carlos">0</div>
            <div class="tec-os-label">OS hoje</div>
          </div>
        </div>
        <div class="tec-item">
          <div class="tec-avatar av-l">LG</div>
          <div class="tec-info">
            <div class="tec-nome">Leandro Goulart</div>
            <div class="tec-tipo">Linha branca</div>
          </div>
          <div style="text-align:right">
            <div class="tec-os" id="os-leandro" style="color:var(--roxo)">0</div>
            <div class="tec-os-label">OS hoje</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">Por Portal</div>
        <div class="portal-row">
          <span class="portal-nome" style="color:var(--notro)">Notro</span>
          <div class="portal-bar-wrap"><div class="portal-bar" id="bar-notro" style="background:var(--notro);width:0%"></div></div>
          <span class="portal-count" id="cnt-notro">0</span>
        </div>
        <div class="portal-row">
          <span class="portal-nome" style="color:var(--juvo)">Juvo</span>
          <div class="portal-bar-wrap"><div class="portal-bar" id="bar-juvo" style="background:var(--juvo);width:0%"></div></div>
          <span class="portal-count" id="cnt-juvo">0</span>
        </div>
        <div class="portal-row">
          <span class="portal-nome" style="color:var(--aciona)">Aciona Fácil</span>
          <div class="portal-bar-wrap"><div class="portal-bar" id="bar-aciona" style="background:var(--aciona);width:0%"></div></div>
          <span class="portal-count" id="cnt-aciona">0</span>
        </div>
        <div class="portal-row">
          <span class="portal-nome" style="color:var(--mondial)">Mondial</span>
          <div class="portal-bar-wrap"><div class="portal-bar" id="bar-mondial" style="background:var(--mondial);width:0%"></div></div>
          <span class="portal-count" id="cnt-mondial">0</span>
        </div>
      </div>
    </div>
  </div>

  <div class="bottom-btns">
    <button class="btt primary" onclick="abrirModal()">+ Nova OS manual</button>
    <button class="btt" onclick="mostrarAba('historico')">Histórico completo</button>
    <button class="btt" onclick="exportar()">⬇ Exportar Excel</button>
  </div>
</div>

<!-- ABA HISTÓRICO -->
<div id="aba-historico" style="display:none">
  <div class="panel">
    <div class="panel-title">Pesquisa de Ordens de Serviço</div>
    <div style="margin-bottom:14px">
      <input id="busca-os" oninput="carregarHistorico()" placeholder="🔍  Buscar por tipo, funcionário, endereço..." 
        style="width:100%;padding:11px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;color:var(--text);font-family:'Space Grotesk',sans-serif;font-size:14px;outline:none">
    </div>
    <div style="display:flex;gap:10px;margin-bottom:16px">
      <select id="filtro-portal" onchange="carregarHistorico()" style="background:var(--surface);color:var(--text);border:1px solid var(--border);padding:8px 12px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-size:13px">
        <option value="">Todos os portais</option>
        <option value="NOTRO">Notro</option>
        <option value="TEMPO SLZ">Juvo</option>
      </select>
      <select id="filtro-status" onchange="carregarHistorico()" style="background:var(--surface);color:var(--text);border:1px solid var(--border);padding:8px 12px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-size:13px">
        <option value="">Todos os status</option>
        <option value="ACEITO">Aceito</option>
        <option value="RECUSADO">Recusado</option>
      </select>
    </div>
    <table style="width:100%;border-collapse:collapse" id="tabela-historico">
      <thead>
        <tr style="border-bottom:1px solid var(--border)">
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Data</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Portal</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Tipo</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Funcionário</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Status</th>
        </tr>
      </thead>
      <tbody id="tbody-historico"><tr><td colspan="5" class="empty">Carregando...</td></tr></tbody>
    </table>
  </div>
</div>

<!-- ABA TÉCNICOS -->
<div id="aba-tecnicos" style="display:none">
  <div class="grid2">
    <div class="panel">
      <div class="panel-title" style="color:var(--azul)">⚡ Carlos Augusto · PTI2314</div>
      <div style="text-align:center;padding:16px 0">
        <div style="width:64px;height:64px;border-radius:50%;background:rgba(77,159,255,0.2);display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;color:var(--azul);margin:0 auto 10px">CA</div>
        <div style="font-size:24px;font-weight:700" id="tec-carlos-total">0</div>
        <div style="font-size:11px;color:var(--muted);font-family:'Space Mono',monospace">OS total</div>
      </div>
      <div id="tec-carlos-lista"></div>
    </div>
    <div class="panel">
      <div class="panel-title" style="color:var(--roxo)">🔧 Leandro Goulart · QXM9I81</div>
      <div style="text-align:center;padding:16px 0">
        <div style="width:64px;height:64px;border-radius:50%;background:rgba(160,107,255,0.2);display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;color:var(--roxo);margin:0 auto 10px">LG</div>
        <div style="font-size:24px;font-weight:700" id="tec-leandro-total">0</div>
        <div style="font-size:11px;color:var(--muted);font-family:'Space Mono',monospace">OS total</div>
      </div>
      <div id="tec-leandro-lista"></div>
    </div>
  </div>
</div>

<!-- MODAL NOVA OS -->
<div class="modal-overlay" id="modal-os">
  <div class="modal">
    <h2>+ Nova OS Manual</h2>
    <div class="campo"><label>Portal</label>
      <select id="nova-portal">
        <option>NOTRO</option><option>TEMPO SLZ</option><option>ACIONA FACIL</option><option>MONDIAL</option>
      </select></div>
    <div class="campo"><label>Tipo de serviço</label>
      <input id="nova-tipo" placeholder="Ex: Eletricista, Encanador..."></div>
    <div class="campo"><label>Funcionário</label>
      <select id="nova-func">
        <option value="CARLOS AUGUSTO PEREIRA FILHO">Carlos Augusto</option>
        <option value="LEANDRO GOULART DE JESUS SOUZA">Leandro Goulart</option>
      </select></div>
    <div class="campo"><label>Endereço</label>
      <input id="nova-end" placeholder="Endereço do cliente"></div>
    <div class="modal-btns">
      <button class="btt" onclick="fecharModal()">Cancelar</button>
      <button class="btt primary" onclick="salvarOS()">Salvar OS</button>
    </div>
  </div>
</div>

<!-- MODAL DETALHE OS -->
<div class="modal-overlay" id="modal-detalhe">
  <div class="modal" style="max-width:560px;max-height:85vh;overflow-y:auto">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2 id="det-titulo">Detalhe da OS</h2>
      <button onclick="fecharDetalhe()" style="background:none;border:none;color:var(--muted);font-size:22px;cursor:pointer">✕</button>
    </div>
    <!-- DADOS PÚBLICOS -->
    <div style="font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;font-family:'Space Mono',monospace">Dados da OS</div>
    <div id="det-publico" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px"></div>
    <!-- DADOS INTERNOS -->
    <div style="background:rgba(255,184,77,0.08);border:1px solid rgba(255,184,77,0.2);border-radius:12px;padding:16px;margin-bottom:16px">
      <div style="font-size:11px;font-weight:700;color:var(--amarelo);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'Space Mono',monospace">🔒 Dados Internos — não aparecem no PDF do cliente</div>
      <div id="det-interno" style="display:grid;grid-template-columns:1fr 1fr;gap:10px"></div>
    </div>
    <!-- FOTOS -->
    <div id="det-fotos" style="display:none">
      <div style="font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;font-family:'Space Mono',monospace">Fotos</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">
        <div><div style="font-size:11px;color:var(--muted);margin-bottom:6px">Antes</div><img id="foto-antes" style="width:100%;border-radius:10px;border:1px solid var(--border)"></div>
        <div><div style="font-size:11px;color:var(--muted);margin-bottom:6px">Depois</div><img id="foto-depois" style="width:100%;border-radius:10px;border:1px solid var(--border)"></div>
      </div>
    </div>
  </div>
</div>

<!-- ABA PEÇAS -->
<div id="aba-pecas" style="display:none">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
    <div>
      <input id="busca-peca" oninput="filtrarPecas()" placeholder="🔍  Buscar peça..." 
        style="padding:10px 16px;background:var(--card);border:1px solid var(--border);border-radius:10px;color:var(--text);font-family:'Space Grotesk',sans-serif;font-size:14px;outline:none;width:280px">
    </div>
    <button class="btt primary" onclick="abrirModalPeca()" style="width:auto;padding:10px 20px">+ Cadastrar Peça</button>
  </div>
  <div class="panel">
    <div class="panel-title">Estoque de Peças e Materiais</div>
    <table style="width:100%;border-collapse:collapse" id="tabela-pecas">
      <thead>
        <tr style="border-bottom:1px solid var(--border)">
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Nome</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Marca</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Modelo</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Tipo</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Valor</th>
          <th style="text-align:left;padding:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Space Mono',monospace">Estoque</th>
          <th style="padding:8px"></th>
        </tr>
      </thead>
      <tbody id="tbody-pecas"><tr><td colspan="7" class="empty">Carregando...</td></tr></tbody>
    </table>
  </div>
</div>

<!-- MODAL NOVA PEÇA -->
<div class="modal-overlay" id="modal-peca">
  <div class="modal" style="max-width:460px">
    <h2>+ Cadastrar Peça</h2>
    <div class="campo"><label>Nome da peça *</label><input id="p-nome" placeholder="Ex: Resistência, Termostato..."></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="campo"><label>Marca</label><input id="p-marca" placeholder="Ex: Brastemp, LG..."></div>
      <div class="campo"><label>Modelo</label><input id="p-modelo" placeholder="Ex: W10871761..."></div>
    </div>
    <div class="campo"><label>Tipo de peça</label>
      <select id="p-tipo">
        <option value="">Selecione...</option>
        <option>Resistência</option><option>Termostato</option><option>Motor</option>
        <option>Compressor</option><option>Placa eletrônica</option><option>Sensor</option>
        <option>Capacitor</option><option>Disjuntor</option><option>Fio/Cabo</option>
        <option>Mangueira</option><option>Bomba d'água</option><option>Válvula</option>
        <option>Filtro</option><option>Outro</option>
      </select>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="campo"><label>Valor (R$) *</label><input id="p-valor" type="number" step="0.01" placeholder="0,00"></div>
      <div class="campo"><label>Qtd em estoque</label><input id="p-estoque" type="number" placeholder="0"></div>
    </div>
    <div class="modal-btns">
      <button class="btt" onclick="fecharModalPeca()">Cancelar</button>
      <button class="btt primary" onclick="cadastrarPeca()">Cadastrar</button>
    </div>
  </div>
</div>

<script>
const COLUNAS = ["DATA","HORA","PORTAL","TIPO SERVIÇO","ENDEREÇO","FUNCIONÁRIO","VEÍCULO","STATUS","OBS"];

function iconeServico(tipo) {
  const t = (tipo||"").toLowerCase();
  if (t.includes("eletric")) return {ico:"⚡", cls:"eletrica"};
  if (t.includes("encanad")||t.includes("hidraul")) return {ico:"🔧", cls:"encanador"};
  if (t.includes("geladeira")||t.includes("freezer")||t.includes("maquina")||t.includes("ar cond")||t.includes("higieniza")||t.includes("fogao")||t.includes("fogão")||t.includes("microondas")) return {ico:"❄️", cls:"branca"};
  return {ico:"🔩", cls:"eletrica"};
}

function badgeStatus(s) {
  const m = {ACEITO:"badge-aceito",RECUSADO:"badge-recusado","EM ANDAMENTO":"badge-andamento",CONCLUIDO:"badge-concluido"};
  return m[s] || "badge-aceito";
}

function portalClass(p) {
  const m = {NOTRO:"notro","TEMPO SLZ":"juvo","ACIONA FACIL":"aciona",MONDIAL:"mondial"};
  return m[(p||"").toUpperCase()] || "azul";
}

async function fetchDados() {
  try { const r = await fetch("/listar"); return await r.json(); } catch { return {}; }
}

async function carregarPainel() {
  const dados = await fetchDados();
  const hoje = new Date().toLocaleDateString("pt-BR");
  let total=0, aceitas=0, andamento=0, recusadas=0;
  let carlos=0, leandro=0;
  let portais = {NOTRO:0,"TEMPO SLZ":0,"ACIONA FACIL":0,MONDIAL:0};
  let os_hoje = [];

  for (const [aba, linhas] of Object.entries(dados)) {
    for (const l of linhas) {
      if (l.DATA !== hoje) continue;
      total++;
      if (l.STATUS==="ACEITO") aceitas++;
      if (l.STATUS==="RECUSADO") recusadas++;
      if (l.STATUS==="EM ANDAMENTO") andamento++;
      if ((l["FUNCIONÁRIO"]||"").includes("CARLOS")) carlos++;
      if ((l["FUNCIONÁRIO"]||"").includes("LEANDRO")) leandro++;
      const p = (aba==="TEMPO SLZ") ? "TEMPO SLZ" : (l.PORTAL||aba).toUpperCase();
      if (portais[p] !== undefined) portais[p]++;
      os_hoje.push({...l, aba});
    }
  }

  document.getElementById("m-hoje").textContent = total;
  document.getElementById("m-aceitas").textContent = aceitas;
  document.getElementById("m-andamento").textContent = andamento;
  document.getElementById("m-recusadas").textContent = recusadas;
  document.getElementById("os-carlos").textContent = carlos;
  document.getElementById("os-leandro").textContent = leandro;

  const maxP = Math.max(...Object.values(portais), 1);
  for (const [p, cnt] of Object.entries(portais)) {
    const key = p==="TEMPO SLZ"?"juvo": p.toLowerCase().replace(" ","");
    const el = document.getElementById("cnt-"+key);
    const bar = document.getElementById("bar-"+key);
    if (el) el.textContent = cnt;
    if (bar) bar.style.width = (cnt/maxP*100)+"%";
  }

  const lista = document.getElementById("lista-os");
  if (!os_hoje.length) {
    lista.innerHTML = '<div class="empty">📭 Sem serviços hoje ainda</div>';
    return;
  }
  lista.innerHTML = os_hoje.slice(-8).reverse().map(l => {
    const {ico,cls} = iconeServico(l["TIPO SERVIÇO"]);
    const func = (l["FUNCIONÁRIO"]||"—").split(" ").slice(0,2).join(" ");
    return `<div class="os-item">
      <div class="os-icon ${cls}">${ico}</div>
      <div class="os-info">
        <div class="os-tipo">${l["TIPO SERVIÇO"]||"—"}</div>
        <div class="os-sub">${l.PORTAL||l.aba} · ${func} · ${l.HORA||""}</div>
      </div>
      <span class="os-badge ${badgeStatus(l.STATUS)}">${l.STATUS||""}</span>
    </div>`;
  }).join("");
}

async function carregarHistorico() {
  const dados = await fetchDados();
  const filtroPortal = document.getElementById("filtro-portal").value;
  const filtroStatus = document.getElementById("filtro-status").value;
  const busca = (document.getElementById("busca-os")?.value||"").toLowerCase();
  let rows = [];
  for (const [aba, linhas] of Object.entries(dados)) {
    if (filtroPortal && aba !== filtroPortal) continue;
    linhas.forEach(l => {
      if (filtroStatus && l.STATUS !== filtroStatus) return;
      if (busca) {
        const texto = [l["TIPO SERVIÇO"],l["FUNCIONÁRIO"],l["ENDEREÇO"],l.OBS,l.PORTAL].join(" ").toLowerCase();
        if (!texto.includes(busca)) return;
      }
      rows.push({...l, aba});
    });
  }
  rows = rows.reverse();
  const tbody = document.getElementById("tbody-historico");
  if (!rows.length) { tbody.innerHTML = '<tr><td colspan="5" class="empty">Nenhum registro encontrado</td></tr>'; return; }
  tbody.innerHTML = rows.slice(0,100).map(l => {
    const func = (l["FUNCIONÁRIO"]||"—").split(" ").slice(0,2).join(" ");
    return `<tr style="border-bottom:1px solid var(--border);cursor:pointer" onclick='abrirDetalheOS(${JSON.stringify(l)})' onmouseover="this.style.background='rgba(255,255,255,0.03)'" onmouseout="this.style.background=''">
      <td style="padding:10px 8px;font-size:11px;font-family:'Space Mono',monospace;color:var(--muted)">${l.DATA||""}<br>${l.HORA||""}</td>
      <td style="padding:10px 8px"><span style="color:var(--${portalClass(l.aba)});font-size:12px;font-weight:600">${l.aba}</span></td>
      <td style="padding:10px 8px;font-size:13px;max-width:180px">${(l["TIPO SERVIÇO"]||"—").substring(0,40)}</td>
      <td style="padding:10px 8px;font-size:12px;color:var(--muted)">${func}</td>
      <td style="padding:10px 8px"><span class="os-badge ${badgeStatus(l.STATUS)}">${l.STATUS||""}</span></td>
    </tr>`;
  }).join("");
}

async function carregarTecnicos() {
  const dados = await fetchDados();
  let carlos=[], leandro=[];
  for (const [aba, linhas] of Object.entries(dados)) {
    for (const l of linhas) {
      if ((l["FUNCIONÁRIO"]||"").includes("CARLOS")) carlos.push({...l,aba});
      if ((l["FUNCIONÁRIO"]||"").includes("LEANDRO")) leandro.push({...l,aba});
    }
  }
  document.getElementById("tec-carlos-total").textContent = carlos.length;
  document.getElementById("tec-leandro-total").textContent = leandro.length;

  function renderTec(lista, elId) {
    const el = document.getElementById(elId);
    const porPortal = {};
    lista.forEach(l => { porPortal[l.aba] = (porPortal[l.aba]||0)+1; });
    el.innerHTML = Object.entries(porPortal).map(([p,c]) =>
      `<div class="portal-row"><span class="portal-nome" style="color:var(--${portalClass(p)})">${p}</span><span style="font-size:13px;font-weight:700;font-family:'Space Mono',monospace">${c}</span></div>`
    ).join("") || '<div class="empty">Nenhum serviço</div>';
  }
  renderTec(carlos, "tec-carlos-lista");
  renderTec(leandro, "tec-leandro-lista");
}

// ── TABS ──────────────────────────────────
function mostrarAba(id) {
  ["hoje","historico","tecnicos"].forEach(a => {
    document.getElementById("aba-"+a).style.display = a===id?"block":"none";
  });
  document.querySelectorAll(".tab").forEach((t,i) => {
    const ids = ["hoje","historico","tecnicos"];
    t.classList.toggle("ativa", ids[i]===id);
  });
  if (id==="historico") carregarHistorico();
  if (id==="tecnicos")  carregarTecnicos();
}

// ── MODAL ────────────────────────────────
function abrirModal() { document.getElementById("modal-os").classList.add("aberto"); }
function fecharModal() { document.getElementById("modal-os").classList.remove("aberto"); }

async function salvarOS() {
  const dados = {
    portal:       document.getElementById("nova-portal").value,
    tipo_servico: document.getElementById("nova-tipo").value,
    funcionario:  document.getElementById("nova-func").value,
    endereco:     document.getElementById("nova-end").value,
    status: "ACEITO",
  };
  const aba = dados.portal === "TEMPO SLZ" ? "salvar_juvo" : "salvar_notro";
  await fetch("/"+aba, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(dados)});
  fecharModal();
  carregarPainel();
}

// ── EXPORTAR ─────────────────────────────
function exportar() {
  window.open("/listar");
}

// ── RELÓGIO ──────────────────────────────
setInterval(() => {
  document.getElementById("hora-top").textContent = new Date().toLocaleTimeString("pt-BR");
}, 1000);

// ── DETALHE OS ───────────────────────────
let todosLaudos = [];

async function carregarLaudos() {
  try { const r = await fetch("/api/laudos"); const d = await r.json(); todosLaudos = d.laudos || []; } catch { todosLaudos = []; }
}

function abrirDetalheOS(os) {
  const laudo = todosLaudos.find(l => l.os_numero === os.OBS || l.os_numero === (os["TIPO SERVIÇO"]||"").substring(0,20));
  document.getElementById("det-titulo").textContent = "OS — " + (os["TIPO SERVIÇO"]||"Serviço");

  const pub = [
    ["Portal", os.PORTAL || os.aba || "—"],
    ["Data", (os.DATA||"") + " " + (os.HORA||"")],
    ["Funcionário", (os["FUNCIONÁRIO"]||"—").split(" ").slice(0,2).join(" ")],
    ["Veículo", os["VEÍCULO"]||"—"],
    ["Endereço", os["ENDEREÇO"]||"—"],
    ["Status", os.STATUS||"—"],
  ];
  document.getElementById("det-publico").innerHTML = pub.map(([k,v]) =>
    `<div style="background:var(--surface);border-radius:10px;padding:12px">
      <div style="font-size:10px;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px">${k}</div>
      <div style="font-size:13px;font-weight:600">${v}</div>
    </div>`).join("");

  let interno = [
    ["Marca", laudo?.interno?.marca || "—"],
    ["Modelo", laudo?.interno?.modelo || "—"],
    ["Peças utilizadas", laudo?.interno?.obs_tecnica?.includes("peça") ? "Ver observações" : "—"],
    ["Retorno necessário", laudo?.interno?.retorno || "—"],
    ["Obs. técnicas", laudo?.interno?.obs_tecnica || "—"],
    ["Problema relatado", laudo?.problema || "—"],
  ];
  document.getElementById("det-interno").innerHTML = interno.map(([k,v]) =>
    `<div style="background:rgba(0,0,0,0.2);border-radius:10px;padding:12px">
      <div style="font-size:10px;color:var(--amarelo);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px">${k}</div>
      <div style="font-size:13px;font-weight:500">${v}</div>
    </div>`).join("");

  // Fotos
  const fotos = laudo?.interno?.fotos;
  if (fotos?.antes || fotos?.depois) {
    document.getElementById("det-fotos").style.display = "block";
    if (fotos.antes)  document.getElementById("foto-antes").src  = fotos.antes;
    if (fotos.depois) document.getElementById("foto-depois").src = fotos.depois;
  } else {
    document.getElementById("det-fotos").style.display = "none";
  }

  document.getElementById("modal-detalhe").classList.add("aberto");
}

function fecharDetalhe() { document.getElementById("modal-detalhe").classList.remove("aberto"); }

// ── PEÇAS ─────────────────────────────────
let todasPecas = [];

async function carregarPecasTab() {
  try { const r = await fetch("/api/pecas"); const d = await r.json(); todasPecas = d.pecas || []; }
  catch { todasPecas = []; }
  renderPecas(todasPecas);
}

function filtrarPecas() {
  const q = document.getElementById("busca-peca").value.toLowerCase();
  renderPecas(todasPecas.filter(p =>
    (p.nome||"").toLowerCase().includes(q) ||
    (p.marca||"").toLowerCase().includes(q) ||
    (p.modelo||"").toLowerCase().includes(q) ||
    (p.tipo||"").toLowerCase().includes(q)
  ));
}

function renderPecas(lista) {
  const tbody = document.getElementById("tbody-pecas");
  if (!lista.length) { tbody.innerHTML = '<tr><td colspan="7" class="empty">Nenhuma peça cadastrada</td></tr>'; return; }
  tbody.innerHTML = lista.map(p => `<tr style="border-bottom:1px solid var(--border)">
    <td style="padding:12px 8px;font-size:14px;font-weight:600">${p.nome||"—"}</td>
    <td style="padding:12px 8px;font-size:13px;color:var(--muted)">${p.marca||"—"}</td>
    <td style="padding:12px 8px;font-size:13px;color:var(--muted);font-family:'Space Mono',monospace">${p.modelo||"—"}</td>
    <td style="padding:12px 8px"><span style="background:rgba(77,159,255,0.15);color:var(--azul);font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px">${p.tipo||"—"}</span></td>
    <td style="padding:12px 8px;font-size:14px;font-weight:700;color:var(--verde)">R$ ${parseFloat(p.valor||0).toFixed(2)}</td>
    <td style="padding:12px 8px;font-size:14px;font-weight:600;text-align:center">${p.estoque||0}</td>
    <td style="padding:12px 8px;text-align:right">
      <button onclick="removerPeca('${p.id}')" style="background:rgba(255,92,92,0.1);color:var(--vermelho);border:none;border-radius:8px;padding:6px 12px;cursor:pointer;font-size:12px">🗑 Remover</button>
    </td>
  </tr>`).join("");
}

function abrirModalPeca() { document.getElementById("modal-peca").classList.add("aberto"); }
function fecharModalPeca() { document.getElementById("modal-peca").classList.remove("aberto"); }

async function cadastrarPeca() {
  const nome = document.getElementById("p-nome").value.trim();
  const valor = document.getElementById("p-valor").value;
  if (!nome || !valor) { alert("Informe nome e valor da peça"); return; }
  await fetch("/api/pecas", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
      nome, marca: document.getElementById("p-marca").value,
      modelo: document.getElementById("p-modelo").value,
      tipo: document.getElementById("p-tipo").value,
      valor, estoque: parseInt(document.getElementById("p-estoque").value)||0
    })
  });
  fecharModalPeca();
  ["p-nome","p-marca","p-modelo","p-valor","p-estoque"].forEach(id => document.getElementById(id).value="");
  document.getElementById("p-tipo").value = "";
  carregarPecasTab();
}

async function removerPeca(id) {
  if (!confirm("Remover esta peça?")) return;
  await fetch("/api/pecas/"+id, {method:"DELETE"});
  carregarPecasTab();
}

// ── BUSCA OS ─────────────────────────────
// já integrada em carregarHistorico via #busca-os

// ── TABS (atualizado) ────────────────────
function mostrarAba(id) {
  ["hoje","historico","tecnicos","pecas"].forEach(a => {
    const el = document.getElementById("aba-"+a);
    if (el) el.style.display = a===id?"block":"none";
  });
  document.querySelectorAll(".tab").forEach((t,i) => {
    const ids = ["hoje","historico","tecnicos","pecas"];
    t.classList.toggle("ativa", ids[i]===id);
  });
  if (id==="historico") { carregarLaudos(); carregarHistorico(); }
  if (id==="tecnicos")  carregarTecnicos();
  if (id==="pecas")     carregarPecasTab();
}

// ── INIT ─────────────────────────────────
carregarPainel();
carregarLaudos();
setInterval(carregarPainel, 30000);

document.getElementById("modal-os").addEventListener("click", e => {
  if (e.target === document.getElementById("modal-os")) fecharModal();
});
document.getElementById("modal-detalhe").addEventListener("click", e => {
  if (e.target === document.getElementById("modal-detalhe")) fecharDetalhe();
});
document.getElementById("modal-peca").addEventListener("click", e => {
  if (e.target === document.getElementById("modal-peca")) fecharModalPeca();
});
</script>
</body>
</html>
"""
TECNICO_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>ELEC — App Técnico</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --azul: #0057FF;
  --azul-escuro: #003FCC;
  --verde: #00C853;
  --vermelho: #FF3D00;
  --amarelo: #FFB300;
  --cinza: #F5F6FA;
  --texto: #1A1A2E;
  --muted: #8890A4;
  --branco: #FFFFFF;
  --borda: #E8EAF0;
  --sombra: 0 2px 16px rgba(0,87,255,0.10);
}
* { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
body { font-family:'DM Sans',sans-serif; background:var(--cinza); color:var(--texto); min-height:100vh; }

/* TELAS */
.tela { display:none; min-height:100vh; flex-direction:column; }
.tela.ativa { display:flex; }

/* ── LOGIN ─────────────────────────────────── */
#tela-login {
  background: linear-gradient(160deg, #0057FF 0%, #003FCC 60%, #001A80 100%);
  align-items:center; justify-content:center; padding:32px 24px;
}
.login-logo { text-align:center; margin-bottom:40px; }
.login-logo .icon { width:72px; height:72px; background:rgba(255,255,255,.15); border-radius:20px;
  display:flex; align-items:center; justify-content:center; font-size:36px; margin:0 auto 12px; }
.login-logo h1 { color:#fff; font-size:28px; font-weight:700; }
.login-logo p { color:rgba(255,255,255,.6); font-size:14px; margin-top:4px; }
.login-card { background:#fff; border-radius:24px; padding:28px 24px; width:100%; max-width:380px; box-shadow:0 20px 60px rgba(0,0,0,.2); }
.login-card h2 { font-size:18px; font-weight:700; margin-bottom:6px; }
.login-card p { font-size:13px; color:var(--muted); margin-bottom:24px; }
.campo { margin-bottom:16px; }
.campo label { font-size:12px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; display:block; margin-bottom:6px; }
.campo input, .campo select, .campo textarea {
  width:100%; padding:13px 16px; border:1.5px solid var(--borda); border-radius:12px;
  font-family:'DM Sans',sans-serif; font-size:15px; color:var(--texto); background:#fff;
  transition:border-color .2s; outline:none; -webkit-appearance:none;
}
.campo input:focus, .campo select:focus { border-color:var(--azul); }
.btn { width:100%; padding:15px; border-radius:14px; font-family:'DM Sans',sans-serif;
  font-size:16px; font-weight:700; border:none; cursor:pointer; transition:all .2s; }
.btn-azul { background:var(--azul); color:#fff; }
.btn-azul:active { background:var(--azul-escuro); transform:scale(.98); }
.btn-verde { background:var(--verde); color:#fff; }
.btn-vermelho { background:var(--vermelho); color:#fff; }
.btn-outline { background:transparent; color:var(--azul); border:2px solid var(--azul); }
.btn-cinza { background:var(--borda); color:var(--muted); }

/* ── HEADER ─────────────────────────────────── */
.header {
  background:var(--azul); color:#fff; padding:16px 20px;
  display:flex; align-items:center; justify-content:space-between;
  position:sticky; top:0; z-index:100;
}
.header-back { width:36px; height:36px; background:rgba(255,255,255,.15); border-radius:10px;
  display:flex; align-items:center; justify-content:center; font-size:18px; cursor:pointer; }
.header-info h2 { font-size:16px; font-weight:700; }
.header-info p { font-size:12px; opacity:.7; margin-top:1px; }
.header-avatar { width:36px; height:36px; border-radius:50%; background:rgba(255,255,255,.2);
  display:flex; align-items:center; justify-content:center; font-weight:700; font-size:15px; }

/* ── LISTA DE OS ─────────────────────────────── */
.lista-header { padding:20px 20px 12px; }
.lista-header h2 { font-size:20px; font-weight:700; }
.lista-header p { font-size:13px; color:var(--muted); margin-top:3px; }
.lista-os { padding:0 16px 100px; }
.os-card {
  background:#fff; border-radius:18px; padding:18px; margin-bottom:12px;
  box-shadow:var(--sombra); cursor:pointer; transition:transform .15s;
  border-left:4px solid transparent;
}
.os-card:active { transform:scale(.98); }
.os-card.nova { border-left-color:var(--azul); }
.os-card.deslocamento { border-left-color:var(--amarelo); }
.os-card.execucao { border-left-color:var(--verde); }
.os-card.concluida { border-left-color:var(--muted); opacity:.7; }
.os-card-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }
.os-num { font-size:11px; font-weight:600; color:var(--muted); font-family:'DM Mono',monospace; }
.os-badge { font-size:10px; font-weight:700; padding:4px 10px; border-radius:20px; }
.badge-nova { background:#EBF0FF; color:var(--azul); }
.badge-deslocamento { background:#FFF8E1; color:#F57F17; }
.badge-execucao { background:#E8F5E9; color:#2E7D32; }
.badge-concluida { background:#F5F5F5; color:var(--muted); }
.os-tipo { font-size:16px; font-weight:700; margin-bottom:6px; }
.os-info { font-size:13px; color:var(--muted); display:flex; gap:12px; flex-wrap:wrap; }
.os-info span { display:flex; align-items:center; gap:4px; }

/* ── DETALHE DA OS ─────────────────────────────── */
.detalhe-cards { padding:16px; display:flex; flex-direction:column; gap:12px; flex:1; }
.info-card { background:#fff; border-radius:18px; overflow:hidden; box-shadow:var(--sombra); }
.info-card-btn { width:100%; padding:18px 20px; display:flex; align-items:center; justify-content:space-between;
  background:#fff; border:none; cursor:pointer; font-family:'DM Sans',sans-serif; text-align:left; }
.info-card-btn .label { font-size:13px; color:var(--muted); font-weight:500; }
.info-card-btn .valor { font-size:15px; font-weight:700; color:var(--texto); margin-top:2px; }
.info-card-btn .chevron { font-size:20px; color:var(--muted); }
.status-bar { padding:10px 20px; font-size:12px; font-weight:700; letter-spacing:.5px; text-align:center; }
.status-nova { background:#EBF0FF; color:var(--azul); }
.status-deslocamento { background:#FFF8E1; color:#F57F17; }
.status-execucao { background:#E8F5E9; color:#2E7D32; }
.status-concluida { background:#F5F5F5; color:var(--muted); }
.acoes-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:16px; }
.acao-btn { background:#fff; border-radius:14px; padding:16px 8px; display:flex; flex-direction:column;
  align-items:center; gap:8px; cursor:pointer; box-shadow:var(--sombra); transition:transform .15s; border:none;
  font-family:'DM Sans',sans-serif; }
.acao-btn:active { transform:scale(.95); }
.acao-icon { font-size:24px; }
.acao-label { font-size:11px; font-weight:600; color:var(--muted); text-align:center; }
.botoes-detalhe { padding:16px; display:flex; gap:10px; position:sticky; bottom:0; background:var(--cinza); }
.botoes-detalhe .btn { flex:1; padding:16px; font-size:14px; }

/* ── LAUDO DIGITAL ─────────────────────────────── */
.laudo-tabs { display:flex; background:#fff; border-bottom:1px solid var(--borda); position:sticky; top:56px; z-index:50; }
.laudo-tab { flex:1; padding:14px 4px; font-size:11px; font-weight:600; color:var(--muted);
  border:none; background:none; cursor:pointer; border-bottom:2px solid transparent;
  font-family:'DM Sans',sans-serif; display:flex; flex-direction:column; align-items:center; gap:4px; }
.laudo-tab.ativa { color:var(--azul); border-bottom-color:var(--azul); }
.laudo-tab .tab-icon { font-size:18px; }
.laudo-content { flex:1; overflow-y:auto; padding:16px 16px 100px; }
.foto-slot { background:var(--cinza); border:2px dashed var(--borda); border-radius:16px;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  height:160px; cursor:pointer; transition:border-color .2s; position:relative; overflow:hidden; }
.foto-slot:hover { border-color:var(--azul); }
.foto-slot img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; border-radius:14px; }
.foto-slot .foto-label { font-size:13px; color:var(--muted); margin-top:8px; font-weight:500; }
.foto-slot .foto-icon { font-size:32px; }
.foto-slot .foto-remover { position:absolute; top:8px; right:8px; width:28px; height:28px; background:rgba(0,0,0,.5);
  border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:14px; z-index:2; cursor:pointer; }
.secao { margin-bottom:24px; }
.secao-titulo { font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; margin-bottom:12px; }
.opcoes-lista { display:flex; flex-direction:column; gap:8px; }
.opcao-item { padding:14px 16px; background:#fff; border-radius:12px; border:1.5px solid var(--borda);
  font-size:14px; font-weight:500; cursor:pointer; transition:all .15s; }
.opcao-item.selecionada { border-color:var(--azul); background:#EBF0FF; color:var(--azul); font-weight:700; }
.slider-opcao { display:flex; align-items:center; justify-content:space-between; background:#fff;
  border-radius:16px; padding:20px 24px; box-shadow:var(--sombra); margin-bottom:16px; }
.slider-opcao .seta { width:40px; height:40px; background:var(--cinza); border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-size:20px; cursor:pointer; color:var(--muted); }
.slider-opcao .valor-slider { font-size:32px; font-weight:700; color:var(--texto); }
.assinatura-canvas { width:100%; height:180px; background:#fff; border:1.5px solid var(--borda);
  border-radius:16px; touch-action:none; display:block; cursor:crosshair; }
.laudo-bottom { position:sticky; bottom:0; background:var(--cinza); padding:12px 16px; }

/* ── MOTIVO FINALIZAÇÃO ─────────────────────────────── */
.motivo-lista { padding:16px; display:flex; flex-direction:column; gap:10px; flex:1; }
.motivo-item { padding:18px 20px; background:#fff; border-radius:16px; border:2px solid var(--borda);
  font-size:14px; font-weight:600; cursor:pointer; transition:all .15s; box-shadow:var(--sombra); }
.motivo-item.selecionado { border-color:var(--azul); background:#EBF0FF; color:var(--azul); }
.motivo-item:active { transform:scale(.98); }

/* ── MODAL ─────────────────────────────── */
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:200; display:none; align-items:flex-end; }
.modal-overlay.aberto { display:flex; }
.modal-sheet { background:#fff; border-radius:24px 24px 0 0; padding:24px 20px 40px; width:100%; max-height:80vh; overflow-y:auto; }
.modal-handle { width:40px; height:4px; background:var(--borda); border-radius:2px; margin:0 auto 20px; }
.modal-titulo { font-size:18px; font-weight:700; margin-bottom:6px; }
.modal-sub { font-size:13px; color:var(--muted); margin-bottom:20px; }
.modal-lista { display:flex; flex-direction:column; gap:8px; }
.modal-opcao { padding:14px 16px; background:var(--cinza); border-radius:12px; font-size:14px; font-weight:500; cursor:pointer; }
.modal-opcao:active { background:var(--borda); }
.modal-opcao.selecionada { background:#EBF0FF; color:var(--azul); font-weight:700; }

/* ── TOAST ─────────────────────────────── */
.toast { position:fixed; bottom:100px; left:50%; transform:translateX(-50%); background:var(--texto);
  color:#fff; padding:12px 24px; border-radius:100px; font-size:14px; font-weight:600; z-index:999;
  opacity:0; transition:opacity .3s; pointer-events:none; white-space:nowrap; }
.toast.visivel { opacity:1; }

/* ── EMPTY STATE ─────────────────────────────── */
.empty { text-align:center; padding:60px 20px; color:var(--muted); }
.empty .icon { font-size:48px; margin-bottom:12px; }
.empty h3 { font-size:16px; font-weight:700; color:var(--texto); margin-bottom:6px; }
.empty p { font-size:13px; line-height:1.6; }

/* ── CARREGANDO ─────────────────────────────── */
.loading { display:flex; align-items:center; justify-content:center; padding:60px 20px; }
.spinner { width:32px; height:32px; border:3px solid var(--borda); border-top-color:var(--azul);
  border-radius:50%; animation:spin .8s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
</style>
</head>
<body>

<!-- ── TELA LOGIN ── -->
<div class="tela ativa" id="tela-login">
  <div class="login-logo">
    <div class="icon">⚡</div>
    <h1>ELEC</h1>
    <p>Sistema de Serviços</p>
  </div>
  <div class="login-card">
    <h2>Entrar</h2>
    <p>Acesse sua conta para ver suas ordens de serviço</p>
    <div class="campo">
      <label>Seu nome</label>
      <select id="login-tecnico">
        <option value="">Selecione...</option>
        <option value="carlos">Carlos Augusto</option>
        <option value="leandro">Leandro Goulart</option>
      </select>
    </div>
    <div class="campo">
      <label>Senha</label>
      <input type="password" id="login-senha" placeholder="Digite sua senha">
    </div>
    <button class="btn btn-azul" onclick="fazerLogin()">Entrar</button>
  </div>
</div>

<!-- ── TELA LISTA OS ── -->
<div class="tela" id="tela-lista">
  <div class="header">
    <div class="header-info">
      <h2 id="lista-nome">Técnico</h2>
      <p id="lista-data"></p>
    </div>
    <div class="header-avatar" id="lista-avatar">C</div>
  </div>
  <div class="lista-header">
    <h2>Meus Serviços</h2>
    <p id="lista-subtitulo">Carregando...</p>
  </div>
  <div class="lista-os" id="lista-os">
    <div class="loading"><div class="spinner"></div></div>
  </div>
</div>

<!-- ── TELA DETALHE OS ── -->
<div class="tela" id="tela-detalhe">
  <div class="header">
    <div class="header-back" onclick="voltarLista()">←</div>
    <div class="header-info">
      <h2 id="det-num">OS #...</h2>
      <p id="det-portal">Portal</p>
    </div>
    <div style="width:36px"></div>
  </div>
  <div class="detalhe-cards">
    <div class="info-card">
      <button class="info-card-btn" onclick="abrirMapa()">
        <div><div class="label">📍 Endereço</div><div class="valor" id="det-endereco">—</div></div>
        <div class="chevron">›</div>
      </button>
    </div>
    <div class="info-card">
      <button class="info-card-btn">
        <div><div class="label">👤 Cliente</div><div class="valor" id="det-cliente">—</div></div>
      </button>
    </div>
    <div class="info-card">
      <button class="info-card-btn">
        <div>
          <div class="label" id="det-tipo-label">🔧 Serviço</div>
          <div class="valor" id="det-tipo">—</div>
        </div>
      </button>
      <div class="status-bar" id="det-status-bar">NOVA</div>
    </div>
  </div>
  <div class="acoes-grid">
    <button class="acao-btn" onclick="abrirObservacoes()">
      <div class="acao-icon">📋</div><div class="acao-label">Observações</div>
    </button>
    <button class="acao-btn" onclick="abrirAtraso()">
      <div class="acao-icon">⏳</div><div class="acao-label">Atraso</div>
    </button>
    <button class="acao-btn" onclick="irParaLaudo()">
      <div class="acao-icon">📊</div><div class="acao-label">Laudo digital</div>
    </button>
  </div>
  <div class="botoes-detalhe" id="botoes-detalhe">
    <!-- botões dinâmicos por status -->
  </div>
</div>

<!-- ── TELA LAUDO DIGITAL ── -->
<div class="tela" id="tela-laudo">
  <div class="header">
    <div class="header-back" onclick="voltarDetalhe()">←</div>
    <div class="header-info">
      <h2>Laudo Digital</h2>
      <p id="laudo-os-num">OS #...</p>
    </div>
    <div style="width:36px"></div>
  </div>
  <div class="laudo-tabs">
    <button class="laudo-tab ativa" onclick="mudarTab('fotos')" id="tab-fotos">
      <div class="tab-icon">📷</div>Fotos
    </button>
    <button class="laudo-tab" onclick="mudarTab('questionario')" id="tab-questionario">
      <div class="tab-icon">📝</div>Questionário
    </button>
    <button class="laudo-tab" onclick="mudarTab('observacao')" id="tab-observacao">
      <div class="tab-icon">💬</div>Observação
    </button>
    <button class="laudo-tab" onclick="mudarTab('assinatura')" id="tab-assinatura">
      <div class="tab-icon">✍️</div>Assinatura
    </button>
  </div>

  <!-- FOTOS -->
  <div class="laudo-content" id="content-fotos">
    <div class="secao">
      <div class="secao-titulo">Foto Antes *</div>
      <div class="foto-slot" id="slot-antes" onclick="tirarFoto('antes')">
        <div class="foto-icon">📷</div>
        <div class="foto-label">Toque para adicionar</div>
      </div>
    </div>
    <div class="secao">
      <div class="secao-titulo">Foto Depois *</div>
      <div class="foto-slot" id="slot-depois" onclick="tirarFoto('depois')">
        <div class="foto-icon">📷</div>
        <div class="foto-label">Toque para adicionar</div>
      </div>
    </div>
    <div class="secao">
      <div class="secao-titulo">Peças (opcional)</div>
      <div class="foto-slot" id="slot-pecas" onclick="tirarFoto('pecas')">
        <div class="foto-icon">🔧</div>
        <div class="foto-label">Foto das peças utilizadas</div>
      </div>
    </div>
    <input type="file" id="input-foto" accept="image/*" capture="environment" style="display:none" onchange="processarFoto(event)">
  </div>

  <!-- QUESTIONÁRIO -->
  <div class="laudo-content" id="content-questionario" style="display:none">
    <div class="secao">
      <div class="secao-titulo">O problema foi resolvido? *</div>
      <div class="slider-opcao">
        <div class="seta" onclick="alternarOpcao('resolvido')">‹</div>
        <div class="valor-slider" id="val-resolvido">SIM</div>
        <div class="seta" onclick="alternarOpcao('resolvido')">›</div>
      </div>
    </div>
    <div class="secao" id="secao-retorno">
      <div class="secao-titulo">Haverá necessidade de retorno? *</div>
      <div class="slider-opcao">
        <div class="seta" onclick="alternarOpcao('retorno')">‹</div>
        <div class="valor-slider" id="val-retorno">NÃO</div>
        <div class="seta" onclick="alternarOpcao('retorno')">›</div>
      </div>
    </div>
    <div class="secao">
      <div class="secao-titulo">Confirme o problema *</div>
      <div class="campo"><select id="sel-problema">
        <option value="">Selecione...</option>
        <option>NÃO LIGA</option><option>NÃO ESQUENTA</option><option>NÃO RESFRIA</option>
        <option>FAZENDO BARULHO</option><option>VAZANDO ÁGUA</option><option>NÃO CENTRIFUGA</option>
        <option>NÃO ENCHE DE ÁGUA</option><option>MANGUEIRA FURADA</option>
        <option>NÃO BATE</option><option>NÃO SOLTA ÁGUA</option><option>OUTROS</option>
      </select></div>
    </div>
    <div class="secao">
      <div class="secao-titulo">Informe a marca</div>
      <div class="campo"><select id="sel-marca">
        <option value="">Selecione a marca</option>
        <option>BRASTEMP</option><option>CONSUL</option><option>ELECTROLUX</option>
        <option>LG</option><option>SAMSUNG</option><option>PHILCO</option>
        <option>PANASONIC</option><option>MIDEA</option><option>SPRINGER</option>
        <option>CARRIER</option><option>OUTRA</option>
      </select></div>
    </div>
    <div class="secao">
      <div class="secao-titulo">Informe o modelo</div>
      <div class="campo"><input type="text" id="inp-modelo" placeholder="Digite o nome/modelo"></div>
    </div>
  </div>

  <!-- OBSERVAÇÃO -->
  <div class="laudo-content" id="content-observacao" style="display:none">
    <div class="secao">
      <div class="secao-titulo">Observações do técnico</div>
      <div class="campo">
        <textarea id="txt-observacao" rows="6" placeholder="Descreva detalhes do serviço, materiais utilizados, recomendações..."></textarea>
      </div>
    </div>
  </div>

  <!-- ASSINATURA -->
  <div class="laudo-content" id="content-assinatura" style="display:none">
    <div class="secao">
      <div class="secao-titulo">Assinatura do cliente *</div>
      <canvas class="assinatura-canvas" id="canvas-assinatura"></canvas>
      <button class="btn btn-cinza" style="margin-top:10px;padding:10px" onclick="limparAssinatura()">Limpar assinatura</button>
    </div>
    <div class="secao">
      <div class="secao-titulo">Nome do cliente *</div>
      <div class="campo"><input type="text" id="inp-nome-cliente" placeholder="Nome completo"></div>
    </div>
    <div class="secao">
      <div class="secao-titulo">Envio do laudo</div>
      <div style="display:flex;gap:12px;margin-bottom:12px">
        <button class="btn" id="btn-email" style="flex:1;padding:12px;background:var(--cinza);border:2px solid var(--borda);border-radius:12px;font-size:13px"
          onclick="toggleEnvio('email')">✉️ E-MAIL</button>
        <button class="btn" id="btn-sms" style="flex:1;padding:12px;background:var(--cinza);border:2px solid var(--borda);border-radius:12px;font-size:13px"
          onclick="toggleEnvio('sms')">💬 SMS</button>
      </div>
      <div class="campo"><input type="tel" id="inp-celular" placeholder="(XX) XXXXX-XXXX"></div>
    </div>
    <button class="btn btn-verde" onclick="finalizarLaudo()" style="margin-top:8px">FINALIZAR SERVIÇO</button>
  </div>
</div>

<!-- ── TELA MOTIVO FINALIZAÇÃO ── -->
<div class="tela" id="tela-motivo">
  <div class="header">
    <div class="header-back" onclick="voltarDetalhe()">←</div>
    <div class="header-info"><h2>Motivo finalização</h2><p id="motivo-os-num"></p></div>
    <div style="width:36px"></div>
  </div>
  <div class="motivo-lista" id="motivo-lista">
    <div class="motivo-item" onclick="selecionarMotivo(this,'SOLUCIONADO SEM NECESSIDADE DE PEÇAS')">SOLUCIONADO SEM NECESSIDADE DE PEÇAS</div>
    <div class="motivo-item" onclick="selecionarMotivo(this,'SOLUCIONADO COM PEÇAS FORNECIDAS PELO CLIENTE')">SOLUCIONADO COM PEÇAS FORNECIDAS PELO CLIENTE</div>
    <div class="motivo-item" onclick="selecionarMotivo(this,'SOLUCIONADO COM PEÇAS FORNECIDAS PELO PRESTADOR')">SOLUCIONADO COM PEÇAS FORNECIDAS PELO PRESTADOR</div>
    <div class="motivo-item" onclick="selecionarMotivo(this,'NECESSÁRIO PEÇAS PARA RESOLVER')">NECESSÁRIO PEÇAS PARA RESOLVER</div>
    <div class="motivo-item" onclick="selecionarMotivo(this,'CLIENTE AUSENTE')">CLIENTE AUSENTE</div>
    <div class="motivo-item" onclick="selecionarMotivo(this,'ENDEREÇO NÃO LOCALIZADO')">ENDEREÇO NÃO LOCALIZADO</div>
    <div class="motivo-item" onclick="selecionarMotivo(this,'OUTROS')">OUTROS</div>
  </div>
  <div style="padding:16px;position:sticky;bottom:0;background:var(--cinza)">
    <button class="btn btn-azul" onclick="confirmarMotivo()">CONCLUIR</button>
  </div>
</div>

<!-- ── MODAL OBSERVAÇÕES ── -->
<div class="modal-overlay" id="modal-obs">
  <div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-titulo">Observações</div>
    <div class="modal-sub">Registre situações durante o atendimento</div>
    <div class="modal-lista">
      <div class="modal-opcao" onclick="registrarObs('CHEGUEI NO LOCAL')">CHEGUEI NO LOCAL</div>
      <div class="modal-opcao" onclick="registrarObs('CLIENTE AUSENTE')">CLIENTE AUSENTE</div>
      <div class="modal-opcao" onclick="registrarObs('CLIENTE NÃO LOCALIZADO')">CLIENTE NÃO LOCALIZADO</div>
      <div class="modal-opcao" onclick="registrarObs('NECESSÁRIO PEÇAS')">NECESSÁRIO PEÇAS</div>
      <div class="modal-opcao" onclick="registrarObs('AGUARDANDO AUTORIZAÇÃO')">AGUARDANDO AUTORIZAÇÃO ENTRADA</div>
      <div class="modal-opcao" onclick="registrarObs('OUTROS')">OUTROS</div>
    </div>
    <button class="btn btn-cinza" style="margin-top:16px" onclick="fecharModal('modal-obs')">Cancelar</button>
  </div>
</div>

<!-- ── MODAL ATRASO ── -->
<div class="modal-overlay" id="modal-atraso">
  <div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-titulo">Registrar Atraso</div>
    <div class="modal-sub">Selecione o motivo do atraso</div>
    <div class="modal-lista">
      <div class="modal-opcao" onclick="registrarObs('TRÂNSITO')">🚗 Trânsito</div>
      <div class="modal-opcao" onclick="registrarObs('SERVIÇO ANTERIOR DEMOROU')">⏱️ Serviço anterior demorou</div>
      <div class="modal-opcao" onclick="registrarObs('PROBLEMA NO VEÍCULO')">🔧 Problema no veículo</div>
      <div class="modal-opcao" onclick="registrarObs('OUTROS')">📝 Outros</div>
    </div>
    <button class="btn btn-cinza" style="margin-top:16px" onclick="fecharModal('modal-atraso')">Cancelar</button>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ── ESTADO ──────────────────────────────────
const SENHAS = { carlos: "carlos123", leandro: "leandro123" };
let tecnico = null;
let osAtual = null;
let motivoSelecionado = null;
let fotoAtual = null;
let fotos = {};
let assinaturaCtx = null;
let desenhando = false;
let envioTipo = null;

// ── OS MOCKADAS (virão do servidor) ──────────
let listaOS = [];

// ── LOGIN ────────────────────────────────────
function fazerLogin() {
  const nome  = document.getElementById('login-tecnico').value;
  const senha = document.getElementById('login-senha').value;
  if (!nome) { mostrarToast('Selecione seu nome'); return; }
  if (senha !== SENHAS[nome]) { mostrarToast('Senha incorreta'); return; }
  tecnico = nome;
  mostrarTela('tela-lista');
  document.getElementById('lista-nome').textContent = nome === 'carlos' ? 'Carlos Augusto' : 'Leandro Goulart';
  document.getElementById('lista-data').textContent = new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'});
  document.getElementById('lista-avatar').textContent = nome === 'carlos' ? 'C' : 'L';
  carregarOS();
}

// ── CARREGAR OS DO SERVIDOR ──────────────────
async function carregarOS() {
  try {
    const r = await fetch('/api/os_tecnico?tecnico=' + (tecnico === 'carlos' ? 'CARLOS' : 'LEANDRO'));
    const data = await r.json();
    listaOS = data.os || [];
  } catch {
    listaOS = [];
  }
  renderizarLista();
}

function renderizarLista() {
  const el = document.getElementById('lista-os');
  const pendentes = listaOS.filter(o => o.status !== 'CONCLUIDA');
  const concluidas = listaOS.filter(o => o.status === 'CONCLUIDA');
  document.getElementById('lista-subtitulo').textContent =
    `${pendentes.length} pendente(s) · ${concluidas.length} concluída(s)`;

  if (listaOS.length === 0) {
    el.innerHTML = `<div class="empty"><div class="icon">📭</div><h3>Nenhuma OS hoje</h3><p>Suas ordens de serviço aparecerão aqui quando forem aceitas</p></div>`;
    return;
  }
  el.innerHTML = listaOS.map(os => `
    <div class="os-card ${classeStatus(os.status)}" onclick="abrirOS('${os.id}')">
      <div class="os-card-top">
        <div class="os-num">${os.numero || os.id}</div>
        <span class="os-badge badge-${os.status.toLowerCase()}">${labelStatus(os.status)}</span>
      </div>
      <div class="os-tipo">${os.tipo_servico || 'Serviço'}</div>
      <div class="os-info">
        <span>📍 ${(os.endereco||'—').substring(0,25)}</span>
        <span>🕐 ${os.hora || ''}</span>
      </div>
    </div>`).join('');
}

function classeStatus(s) {
  const m = {NOVA:'nova',DESLOCAMENTO:'deslocamento',EXECUCAO:'execucao',CONCLUIDA:'concluida'};
  return m[s] || 'nova';
}
function labelStatus(s) {
  const m = {NOVA:'NOVA',DESLOCAMENTO:'EM DESLOCAMENTO',EXECUCAO:'EM EXECUÇÃO',CONCLUIDA:'CONCLUÍDA'};
  return m[s] || s;
}

// ── ABRIR OS ────────────────────────────────
function abrirOS(id) {
  osAtual = listaOS.find(o => o.id === id);
  if (!osAtual) return;
  document.getElementById('det-num').textContent = 'OS ' + (osAtual.numero || osAtual.id);
  document.getElementById('det-portal').textContent = osAtual.portal || 'Portal';
  document.getElementById('det-endereco').textContent = osAtual.endereco || '—';
  document.getElementById('det-cliente').textContent = osAtual.cliente || '—';
  document.getElementById('det-tipo').textContent = osAtual.tipo_servico || '—';
  atualizarStatusBar(osAtual.status);
  renderizarBotoes(osAtual.status);
  mostrarTela('tela-detalhe');
}

function atualizarStatusBar(status) {
  const bar = document.getElementById('det-status-bar');
  bar.textContent = labelStatus(status);
  bar.className = 'status-bar status-' + classeStatus(status);
}

function renderizarBotoes(status) {
  const el = document.getElementById('botoes-detalhe');
  if (status === 'NOVA') {
    el.innerHTML = `<button class="btn btn-azul" onclick="avancarStatus('DESLOCAMENTO')">🚗 INICIAR DESLOCAMENTO</button>`;
  } else if (status === 'DESLOCAMENTO') {
    el.innerHTML = `
      <button class="btn btn-outline" onclick="abrirMapa()">NAVEGAR</button>
      <button class="btn btn-verde" onclick="avancarStatus('EXECUCAO')">EM EXECUÇÃO</button>`;
  } else if (status === 'EXECUCAO') {
    el.innerHTML = `<button class="btn btn-azul" onclick="abrirMotivo()">FINALIZAR</button>`;
  } else {
    el.innerHTML = `<button class="btn btn-cinza">✅ SERVIÇO CONCLUÍDO</button>`;
  }
}

// ── AVANÇAR STATUS ───────────────────────────
async function avancarStatus(novoStatus) {
  osAtual.status = novoStatus;
  atualizarStatusBar(novoStatus);
  renderizarBotoes(novoStatus);
  // Atualiza no servidor
  try {
    await fetch('/api/atualizar_os', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ id: osAtual.id, status: novoStatus, tecnico })
    });
  } catch {}
  const msgs = {DESLOCAMENTO:'Em deslocamento!', EXECUCAO:'Em execução!'};
  mostrarToast(msgs[novoStatus] || 'Status atualizado');
  // Atualiza na lista local
  const idx = listaOS.findIndex(o => o.id === osAtual.id);
  if (idx >= 0) listaOS[idx].status = novoStatus;
}

// ── LAUDO DIGITAL ────────────────────────────
function irParaLaudo() {
  document.getElementById('laudo-os-num').textContent = 'OS ' + (osAtual?.numero || osAtual?.id || '');
  mostrarTela('tela-laudo');
  mudarTab('fotos');
  iniciarAssinatura();
}

function mudarTab(tab) {
  ['fotos','questionario','observacao','assinatura'].forEach(t => {
    document.getElementById('content-' + t).style.display = t === tab ? 'block' : 'none';
    document.getElementById('tab-' + t).classList.toggle('ativa', t === tab);
  });
}

// Fotos
function tirarFoto(slot) {
  fotoAtual = slot;
  document.getElementById('input-foto').click();
}

function processarFoto(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    fotos[fotoAtual] = ev.target.result;
    const slot = document.getElementById('slot-' + fotoAtual);
    slot.innerHTML = `<img src="${ev.target.result}"><div class="foto-remover" onclick="removerFoto('${fotoAtual}');event.stopPropagation()">✕</div>`;
  };
  reader.readAsDataURL(file);
  e.target.value = '';
}

function removerFoto(slot) {
  delete fotos[slot];
  const icons = {antes:'📷',depois:'📷',pecas:'🔧'};
  const labels = {antes:'Toque para adicionar',depois:'Toque para adicionar',pecas:'Foto das peças utilizadas'};
  document.getElementById('slot-' + slot).innerHTML =
    `<div class="foto-icon">${icons[slot]}</div><div class="foto-label">${labels[slot]}</div>`;
}

// Questionário
const estadosResolvido = ['SIM','NÃO'];
const estadosRetorno   = ['NÃO','SIM'];
let idxResolvido = 0, idxRetorno = 0;
function alternarOpcao(tipo) {
  if (tipo === 'resolvido') {
    idxResolvido = (idxResolvido + 1) % estadosResolvido.length;
    document.getElementById('val-resolvido').textContent = estadosResolvido[idxResolvido];
  } else {
    idxRetorno = (idxRetorno + 1) % estadosRetorno.length;
    document.getElementById('val-retorno').textContent = estadosRetorno[idxRetorno];
  }
}

// Assinatura
function iniciarAssinatura() {
  const canvas = document.getElementById('canvas-assinatura');
  if (!canvas) return;
  canvas.width  = canvas.offsetWidth * window.devicePixelRatio;
  canvas.height = canvas.offsetHeight * window.devicePixelRatio;
  assinaturaCtx = canvas.getContext('2d');
  assinaturaCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
  assinaturaCtx.strokeStyle = '#1A1A2E';
  assinaturaCtx.lineWidth   = 2.5;
  assinaturaCtx.lineCap     = 'round';
  assinaturaCtx.lineJoin    = 'round';

  function pos(e) {
    const r = canvas.getBoundingClientRect();
    const t = e.touches ? e.touches[0] : e;
    return { x: t.clientX - r.left, y: t.clientY - r.top };
  }
  canvas.addEventListener('mousedown',  e => { desenhando=true; const p=pos(e); assinaturaCtx.beginPath(); assinaturaCtx.moveTo(p.x,p.y); });
  canvas.addEventListener('mousemove',  e => { if(!desenhando) return; const p=pos(e); assinaturaCtx.lineTo(p.x,p.y); assinaturaCtx.stroke(); });
  canvas.addEventListener('mouseup',    () => desenhando=false);
  canvas.addEventListener('touchstart', e => { e.preventDefault(); desenhando=true; const p=pos(e); assinaturaCtx.beginPath(); assinaturaCtx.moveTo(p.x,p.y); });
  canvas.addEventListener('touchmove',  e => { e.preventDefault(); if(!desenhando) return; const p=pos(e); assinaturaCtx.lineTo(p.x,p.y); assinaturaCtx.stroke(); });
  canvas.addEventListener('touchend',   e => { e.preventDefault(); desenhando=false; });
}

function limparAssinatura() {
  if (assinaturaCtx) {
    const canvas = document.getElementById('canvas-assinatura');
    assinaturaCtx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
  }
}

function toggleEnvio(tipo) {
  envioTipo = tipo;
  ['email','sms'].forEach(t => {
    const btn = document.getElementById('btn-' + t);
    btn.style.background = t === tipo ? '#EBF0FF' : 'var(--cinza)';
    btn.style.borderColor = t === tipo ? 'var(--azul)' : 'var(--borda)';
    btn.style.color = t === tipo ? 'var(--azul)' : 'var(--muted)';
  });
}

async function finalizarLaudo() {
  const nomeCliente = document.getElementById('inp-nome-cliente').value.trim();
  if (!nomeCliente) { mostrarToast('Informe o nome do cliente'); return; }
  if (!fotos.antes) { mostrarToast('Foto "Antes" é obrigatória'); return; }
  if (!fotos.depois) { mostrarToast('Foto "Depois" é obrigatória'); return; }

  const laudo = {
    os_id: osAtual?.id,
    os_numero: osAtual?.numero,
    tecnico,
    resolvido: estadosResolvido[idxResolvido],
    retorno: estadosRetorno[idxRetorno],
    problema: document.getElementById('sel-problema').value,
    marca: document.getElementById('sel-marca').value,
    modelo: document.getElementById('inp-modelo').value,
    observacao: document.getElementById('txt-observacao').value,
    nome_cliente: nomeCliente,
    celular: document.getElementById('inp-celular').value,
    envio: envioTipo,
    data_hora: new Date().toLocaleString('pt-BR'),
    assinatura: document.getElementById('canvas-assinatura').toDataURL(),
    fotos: { antes: fotos.antes || null, depois: fotos.depois || null, pecas: fotos.pecas || null }
  };

  try {
    await fetch('/api/laudo', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(laudo) });
  } catch {}

  // Finaliza a OS
  await avancarStatus('CONCLUIDA');
  mostrarToast('✅ Serviço finalizado com sucesso!');
  setTimeout(() => voltarLista(), 2000);
}

// ── MOTIVO FINALIZAÇÃO ───────────────────────
function abrirMotivo() {
  motivoSelecionado = null;
  document.querySelectorAll('.motivo-item').forEach(el => el.classList.remove('selecionado'));
  document.getElementById('motivo-os-num').textContent = 'OS ' + (osAtual?.numero || '');
  mostrarTela('tela-motivo');
}

function selecionarMotivo(el, motivo) {
  document.querySelectorAll('.motivo-item').forEach(e => e.classList.remove('selecionado'));
  el.classList.add('selecionado');
  motivoSelecionado = motivo;
}

function confirmarMotivo() {
  if (!motivoSelecionado) { mostrarToast('Selecione um motivo'); return; }
  if (motivoSelecionado.startsWith('SOLUCIONADO')) {
    voltarDetalhe();
    irParaLaudo();
  } else {
    avancarStatus('CONCLUIDA');
    mostrarToast('Serviço finalizado: ' + motivoSelecionado);
    setTimeout(() => voltarLista(), 1500);
  }
}

// ── MODAIS ───────────────────────────────────
function abrirObservacoes() { document.getElementById('modal-obs').classList.add('aberto'); }
function abrirAtraso() { document.getElementById('modal-atraso').classList.add('aberto'); }
function fecharModal(id) { document.getElementById(id).classList.remove('aberto'); }
function registrarObs(obs) {
  fecharModal('modal-obs'); fecharModal('modal-atraso');
  mostrarToast('Registrado: ' + obs);
}

// ── MAPA ─────────────────────────────────────
function abrirMapa() {
  const end = osAtual?.endereco || '';
  if (end) window.open('https://maps.google.com/?q=' + encodeURIComponent(end));
}

// ── NAVEGAÇÃO ────────────────────────────────
function mostrarTela(id) {
  document.querySelectorAll('.tela').forEach(t => t.classList.remove('ativa'));
  document.getElementById(id).classList.add('ativa');
  window.scrollTo(0, 0);
}
function voltarLista() {
  carregarOS();
  mostrarTela('tela-lista');
}
function voltarDetalhe() { mostrarTela('tela-detalhe'); }

// ── TOAST ────────────────────────────────────
function mostrarToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('visivel');
  setTimeout(() => t.classList.remove('visivel'), 2500);
}

// ── INICIAR ──────────────────────────────────
window.addEventListener('load', () => {
  document.getElementById('lista-data').textContent =
    new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'});
});
</script>
</body>
</html>
"""

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
    return Response(INDEX_HTML, mimetype="text/html; charset=utf-8")

@app.route("/tecnico")
def tecnico():
    return Response(TECNICO_HTML, mimetype="text/html; charset=utf-8")

@app.route("/debug")
def debug():
    return jsonify({"ok": True, "msg": "servidor funcionando", "rotas": ["/", "/tecnico", "/api/status"]})

# ── API REGISTRAR ─────────────────────────────
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
            "id":           str(agora.timestamp()).replace(".",""),
            "data":         agora.strftime("%d/%m/%Y"),
            "hora":         agora.strftime("%H:%M:%S"),
            "portal":       d.get("portal",""),
            "tipo_servico": tipo_raw,
            "endereco":     d.get("endereco",""),
            "funcionario":  d.get("funcionario",""),
            "veiculo":      d.get("veiculo",""),
            "status":       d.get("status","ACEITO"),
            "obs":          d.get("obs",""),
            "cliente":      d.get("cliente",""),
            "numero":       d.get("numero","") or d.get("obs",""),
        }
        registros.append(registro)
        salvar(REGISTROS_FILE, registros)
        status  = registro["status"]
        emoji   = "✅" if status == "ACEITO" else "❌"
        cliente = registro.get("cliente","") or "—"
        func    = registro["funcionario"].split()[0].title() if registro["funcionario"] else "—"
        msg = (f"{emoji} {registro['portal']} — {status}\n"
               f"Tipo: {tipo_raw}\n"
               f"Cliente: {cliente}\n"
               f"Funcionário: {func}\n"
               f"Veículo: {registro['veiculo']}\n"
               f"Hora: {registro['hora']}")
        threading.Thread(target=enviar_telegram, args=(msg,), daemon=True).start()
        return jsonify({"ok": True})
    except Exception as e:
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

@app.route("/listar")
def listar_route():
    try:
        registros = ler(REGISTROS_FILE)
        res = {"NOTRO":[], "TEMPO SLZ":[], "ACIONA FACIL":[], "MONDIAL":[]}
        for r in registros:
            aba = r.get("portal","NOTRO")
            if aba not in res: res[aba] = []
            res[aba].append({
                "DATA":         r.get("data",""),
                "HORA":         r.get("hora",""),
                "PORTAL":       r.get("portal",""),
                "TIPO SERVIÇO": r.get("tipo_servico",""),
                "ENDEREÇO":     r.get("endereco",""),
                "FUNCIONÁRIO":  r.get("funcionario",""),
                "VEÍCULO":      r.get("veiculo",""),
                "STATUS":       r.get("status",""),
                "OBS":          r.get("obs",""),
                "CLIENTE":      r.get("cliente",""),
            })
        return jsonify(res)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/os_tecnico")
def os_tecnico():
    try:
        tec  = request.args.get("tecnico","").upper()
        hoje = datetime.now().strftime("%d/%m/%Y")
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
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500

@app.route("/api/laudo", methods=["POST"])
def salvar_laudo():
    try:
        d = request.get_json()
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

@app.route("/api/pecas", methods=["GET"])
def listar_pecas():
    return jsonify({"ok": True, "pecas": ler(PECAS_FILE)})

@app.route("/api/pecas", methods=["POST"])
def adicionar_peca():
    try:
        d = request.get_json()
        pecas = ler(PECAS_FILE)
        peca = {
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

@app.route("/api/status")
def status():
    return jsonify({"ok": True, "registros": len(ler(REGISTROS_FILE))})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
