"""
AGENTE NOTRO LOCAL — roda no seu PC
Envia dados para o sistema na nuvem (Railway)
"""
import asyncio, json, urllib.request as _u
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# ⚠️ COLOQUE AQUI A URL DO SEU SISTEMA NO RAILWAY
URL_CLOUD = "https://SEU-SISTEMA.railway.app"

URL_NOTRO  = "https://hub.notro.io/#/solicitacoes"
PERFIL     = Path("C:/agente_servicos/perfil_notro")

TELEGRAM_TOKEN   = "8647040791:AAGq1YP0BLSlscZ0hKqN68LvHaHPoFvbLns"
TELEGRAM_CHAT_ID = "8704528010"

LINHA_BASICA = ["eletric","elétric","encanad","hidraul","chuveiro","instalacao","instalação","tecnico","técnico"]
LINHA_BRANCA = ["geladeira","freezer","maquina de lavar","ar condicionado","higieniza","fogao","fogão","microondas","lava louça"]
RECUSAR_LISTA = ["desentupimento","vigilante","limpeza","pintura","jardinagem","chaveiro"]

CARLOS_NOME  = "CARLOS AUGUSTO PEREIRA FILHO"
CARLOS_PLACA = "PTI2314"
LEANDRO_NOME  = "LEANDRO GOULART DE JESUS SOUZA"
LEANDRO_PLACA = "QXM9I81"

processados = set()

def decidir(texto):
    t = texto.lower()
    for p in RECUSAR_LISTA:
        if p in t: return "RECUSAR", None, p
    for p in LINHA_BRANCA:
        if p in t: return "ACEITAR", "branca", p
    for p in LINHA_BASICA:
        if p in t: return "ACEITAR", "basica", p
    return "RECUSAR", None, "tipo desconhecido"

def enviar_nuvem(dados):
    try:
        payload = json.dumps(dados).encode()
        req = _u.Request(f"{URL_CLOUD}/api/registrar", data=payload,
                         headers={"Content-Type":"application/json"})
        _u.urlopen(req, timeout=10)
        print(f"  ☁️  Enviado para nuvem!")
    except Exception as e:
        print(f"  ⚠️ Erro ao enviar para nuvem: {e}")

def enviar_telegram(msg):
    try:
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        req = _u.Request(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                         data=payload, headers={"Content-Type":"application/json"})
        _u.urlopen(req, timeout=10)
    except: pass

async def aceitar_modal(page, func, placa):
    try:
        await page.wait_for_selector("text=Aceite de Serviço", timeout=5000)
        await page.wait_for_timeout(800)
        drops = await page.locator("mat-select,[class*='select']").all()
        if drops: await drops[0].click(); await page.wait_for_timeout(600)
        for op in await page.locator("mat-option,[role='option']").all():
            if await op.is_visible() and func.split()[0] in await op.inner_text():
                await op.click(); await page.wait_for_timeout(500); break
        if len(drops) > 1: await drops[1].click(); await page.wait_for_timeout(600)
        for op in await page.locator("mat-option,[role='option']").all():
            if await op.is_visible() and placa in await op.inner_text():
                await op.click(); await page.wait_for_timeout(500); break
        btn = page.locator("button:has-text('CONFIRMAR'),button:has-text('Confirmar')").first
        if await btn.count(): await btn.click(); await page.wait_for_timeout(2000)
        return True
    except Exception as e:
        print(f"    ⚠️ Modal: {e}"); return False

async def verificar(page):
    try:
        await page.reload(wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(2000)
        corpo = await page.locator("body").inner_text()
        cards = await page.locator("mat-card,.mat-card,[class*='solicitacao']").all()
        servicos = 0
        for card in cards:
            try:
                if not await card.is_visible(): continue
                texto = (await card.inner_text()).strip()
                if len(texto) < 15: continue
                if not ("Expira em" in texto or "aguardando aceite" in texto.lower()): continue
                item_id = texto[:80].replace("\n","_")
                if item_id in processados: continue
                decisao, tipo, motivo = decidir(texto)
                func  = LEANDRO_NOME  if tipo == "branca" else CARLOS_NOME
                placa = LEANDRO_PLACA if tipo == "branca" else CARLOS_PLACA
                resumo = texto[:60].replace("\n"," ")
                print(f"  [{decisao}] {resumo[:50]} | {motivo}")
                hora = datetime.now().strftime("%H:%M:%S")
                servicos += 1
                if decisao == "ACEITAR":
                    btn = card.locator("button[color='primary'],button:last-child").first
                    if await btn.count():
                        await btn.click(); await page.wait_for_timeout(1500)
                        ok = await aceitar_modal(page, func, placa)
                        if ok:
                            enviar_nuvem({"portal":"NOTRO","tipo_servico":resumo,"funcionario":func,"veiculo":placa,"status":"ACEITO","obs":""})
                            enviar_telegram(f"✅ NOTRO — ACEITO\nTipo: {resumo}\nFuncionário: {func}\nVeículo: {placa}\nHora: {hora}")
                else:
                    btn_r = card.locator("button[color='warn'],button:first-child").first
                    if await btn_r.count():
                        await btn_r.click(); await page.wait_for_timeout(1000)
                        conf = page.locator("button:has-text('CONFIRMAR')").first
                        if await conf.count(): await conf.click()
                processados.add(item_id)
            except: pass
        if servicos == 0: print("  Sem serviços novos.")
    except Exception as e:
        print(f"  ⚠️ Erro: {e}")

async def main():
    print("=" * 50)
    print("  ⚡ AGENTE NOTRO LOCAL")
    print(f"  ☁️  Cloud: {URL_CLOUD}")
    print("=" * 50)
    PERFIL.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(user_data_dir=str(PERFIL), headless=False, args=["--start-maximized"])
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(URL_NOTRO, timeout=30000)
        await page.wait_for_timeout(3000)
        for _ in range(120):
            if "Novos serviços" in await page.locator("body").inner_text(): break
            print("  ⏳ Aguardando login...")
            await asyncio.sleep(5)
        print("  ✅ Logado! Monitorando a cada 30s.\n")
        ciclo = 0
        while True:
            ciclo += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ciclo #{ciclo}")
            await verificar(page)
            await asyncio.sleep(30)

asyncio.run(main())
