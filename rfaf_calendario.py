#!/usr/bin/env python3
"""
Extrae el calendario de A.D. MARIANISTAS C.D. de la RFAF (PNFG)
y genera un feed .ics suscribible + un JSON.

Uso:
    python rfaf_calendario.py            # descarga de la web
    python rfaf_calendario.py fichero.html   # parsea un HTML local
"""

import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

# --- Configuración -----------------------------------------------------------

EQUIPO = "A.D. MARIANISTAS C.D."

BASE = "https://www.rfaf.es/pnfg/NPcd/NFG_VisCalendario_Vis"
PARAMS = {
    "cod_primaria": "1000120",
    "codgrupo": "48795840",
    "codcompeticion": "48795719",
    "codtemporada": "22",
    "CodJornada": "1",
    "CDetalle": "1",          # <-- versión extendida: incluye el campo
}

# Sin hora oficial todavía. (A) = mañana, (T) = tarde.
HORA_MANANA, HORA_TARDE, HORA_DESCONOCIDA = "11:00", "17:00", "12:00"
DURACION_MIN = 105  # 90' + descanso

OUT = Path(__file__).parent


# --- Utilidades --------------------------------------------------------------

def normaliza(texto: str) -> str:
    """Limpia nbsp, espacios repetidos y acentos para comparar nombres.

    Los nombres del PNFG vienen sucios: 'TRASMALLO F.C .C.D.',
    espacios iniciales, &nbsp; al final. Comparar en crudo falla en silencio.
    """
    t = texto.replace("\xa0", " ")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\s+", " ", t)
    return t.strip().upper()


CLAVE_EQUIPO = normaliza(EQUIPO)


# --- Descarga ----------------------------------------------------------------

def descargar() -> str:
    import requests

    r = requests.get(
        BASE,
        params=PARAMS,
        headers={"User-Agent": "CalendarioPersonal/1.0 (uso personal)"},
        timeout=30,
    )
    r.raise_for_status()
    r.encoding = "ISO-8859-15"   # declarado en el <meta> de la página
    return r.text


# --- Parseo ------------------------------------------------------------------

RE_JORNADA = re.compile(r"Jornada\s+(\d+)")
RE_FECHA = re.compile(r"\((\d{2})-(\d{2})-(\d{4})\)")
RE_TURNO = re.compile(r"\((A|T)\)\s*$")


def parsea(html: str) -> list[dict]:
    # html.parser tolera el <span> sin cerrar del <h5 class="card-title">
    soup = BeautifulSoup(html, "html.parser")
    partidos = []

    for card in soup.select("div.card-body"):
        titulo = card.find("h5", class_="card-title")
        if not titulo:
            continue

        texto_titulo = titulo.get_text(" ", strip=True)
        m_jor, m_fec = RE_JORNADA.search(texto_titulo), RE_FECHA.search(texto_titulo)
        if not (m_jor and m_fec):
            continue

        jornada = int(m_jor.group(1))
        dia, mes, anio = m_fec.groups()

        for fila in card.select("div.row"):
            equipos = fila.select("div.col-sm-7 span.font_responsive")
            if len(equipos) != 2:
                continue

            local = re.sub(r"\s+", " ", equipos[0].get_text().replace("\xa0", " ")).strip()
            visitante = re.sub(r"\s+", " ", equipos[1].get_text().replace("\xa0", " ")).strip()

            if CLAVE_EQUIPO not in (normaliza(local), normaliza(visitante)):
                continue

            detalle = fila.select_one("div.col-sm-5")
            campo, turno = None, None
            if detalle:
                # El campo es el texto entre el icono de mapa y el <br>
                bruto = detalle.get_text("\n", strip=True).split("\n")[0]
                bruto = bruto.replace("\xa0", " ").strip()
                m_turno = RE_TURNO.search(bruto)
                if m_turno:
                    turno = m_turno.group(1)
                    bruto = bruto[: m_turno.start()].strip()
                campo = re.sub(r"\s+", " ", bruto)

            partidos.append({
                "jornada": jornada,
                "fecha": f"{anio}-{mes}-{dia}",
                "local": local,
                "visitante": visitante,
                "en_casa": normaliza(local) == CLAVE_EQUIPO,
                "rival": visitante if normaliza(local) == CLAVE_EQUIPO else local,
                "campo": campo,
                "turno": turno,          # 'A' mañana, 'T' tarde, None desconocido
                "hora_confirmada": False,  # la RFAF aún no publica horas
            })

    partidos.sort(key=lambda p: p["jornada"])
    return partidos


# --- Generación del .ics -----------------------------------------------------

def esc(texto: str) -> str:
    """Escapado obligatorio en RFC 5545. Los campos llevan comas a menudo."""
    return (texto.replace("\\", "\\\\")
                 .replace(",", "\\,")
                 .replace(";", "\\;")
                 .replace("\n", "\\n"))


def plegar(linea: str) -> list[str]:
    """RFC 5545: máximo 75 octetos por línea; continuación con espacio."""
    datos = linea.encode("utf-8")
    if len(datos) <= 73:
        return [linea]
    trozos, actual = [], b""
    for char in linea:
        b = char.encode("utf-8")
        if len(actual) + len(b) > 73:
            trozos.append(actual.decode("utf-8"))
            actual = b" " + b
        else:
            actual += b
    trozos.append(actual.decode("utf-8"))
    return trozos


def genera_ics(partidos: list[dict]) -> str:
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//calendario-rfaf-personal//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(EQUIPO)}",
        "X-WR-TIMEZONE:Europe/Madrid",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for p in partidos:
        hora = {"A": HORA_MANANA, "T": HORA_TARDE}.get(p["turno"], HORA_DESCONOCIDA)
        inicio = datetime.fromisoformat(f"{p['fecha']}T{hora}")
        fin = inicio + timedelta(minutes=DURACION_MIN)
        fmt = "%Y%m%dT%H%M%S"

        señal = "🏠" if p["en_casa"] else "✈️"
        turno_txt = {"A": "mañana", "T": "tarde"}.get(p["turno"], "sin turno")
        desc = (f"Jornada {p['jornada']} · {turno_txt}\\n"
                f"⚠️ Hora estimada: la RFAF no ha publicado horarios todavía.")

        evento = [
            "BEGIN:VEVENT",
            # UID estable por jornada -> actualiza en vez de duplicar
            f"UID:rfaf-48795840-j{p['jornada']:02d}@calendario-personal",
            f"DTSTAMP:{sello}",
            f"DTSTART;TZID=Europe/Madrid:{inicio.strftime(fmt)}",
            f"DTEND;TZID=Europe/Madrid:{fin.strftime(fmt)}",
            f"SUMMARY:{señal} {esc(p['local'])} - {esc(p['visitante'])}",
            f"DESCRIPTION:{desc}",
            "STATUS:TENTATIVE",   # honesto: la hora no está confirmada
            "TRANSP:TRANSPARENT",
        ]
        if p["campo"]:
            evento.append(f"LOCATION:{esc(p['campo'])}")
        evento.append("END:VEVENT")
        lineas += evento

    lineas.append("END:VCALENDAR")

    salida = []
    for l in lineas:
        salida.extend(plegar(l))
    return "\r\n".join(salida) + "\r\n"


# --- Main --------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        html = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    else:
        html = descargar()

    partidos = parsea(html)
    if not partidos:
        print(f"⚠️  No se encontró ningún partido de {EQUIPO}. "
              "¿Ha cambiado el nombre o el HTML?", file=sys.stderr)
        return 1

    (OUT / "marianistas.ics").write_text(genera_ics(partidos), encoding="utf-8")
    (OUT / "marianistas.json").write_text(
        json.dumps(partidos, ensure_ascii=False, indent=2), encoding="utf-8")

    casa = sum(p["en_casa"] for p in partidos)
    print(f"✅ {len(partidos)} partidos ({casa} en casa, {len(partidos)-casa} fuera)")
    for p in partidos:
        marca = "🏠" if p["en_casa"] else "✈️"
        print(f"  J{p['jornada']:>2}  {p['fecha']}  {marca} vs {p['rival']:<34} "
              f"[{p['turno'] or '?'}]  {p['campo'] or '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
