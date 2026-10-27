from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

random.seed(42)

STAGES = [
    "Recebimento",
    "Separação",
    "Conferência",
    "Carregamento",
    "Expedição",
]

REASONS_BY_STAGE = {
    "Recebimento": [
        "Falta de operador",
        "Pedido incompleto",
        "Etiqueta divergente",
        "Atraso no recebimento",
    ],
    "Separação": [
        "Falta de operador",
        "Separação incorreta",
        "Falha de WMS",
        "Ajuste de estoque",
    ],
    "Conferência": [
        "Conferência pendente",
        "Pedido com divergência",
        "Falha de scanner",
        "Atraso de qualidade",
    ],
    "Carregamento": [
        "Falta de caminhão",
        "Falha de WMS",
        "Falha operacional",
        "Atraso de roteirização",
    ],
    "Expedição": [
        "Atraso de transporte",
        "Carregamento fora do horário",
        "Ponto de saída congestionado",
        "Falha de documentação",
    ],
}

TURNOS = ["Manhã", "Tarde", "Noite"]
CANAIS = ["Loja Própria", "Marketplace", "B2B", "Cross Dock"]


def pick_stage():
    weights = [0.18, 0.32, 0.22, 0.16, 0.12]
    return random.choices(STAGES, weights=weights, k=1)[0]


def pick_reason(stage):
    options = REASONS_BY_STAGE[stage]
    return random.choices(options, weights=[0.34, 0.24, 0.22, 0.20], k=1)[0]


def pick_turno(hour):
    if 6 <= hour < 14:
        return "Manhã"
    if 14 <= hour < 22:
        return "Tarde"
    return "Noite"


def build_order(order_id, start_date):
    created = start_date + timedelta(
        days=random.randint(0, 179),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    scheduled = created + timedelta(hours=random.randint(8, 18), minutes=random.randint(0, 59))

    stage = pick_stage()
    delay_minutes = 0
    status = "No prazo"
    motivo = "Sem atraso"
    sla_cumprido = True
    retrabalho = random.random() < 0.18
    inconsistencia = random.random() < 0.12

    if random.random() < 0.42:
        delay_minutes = random.randint(35, 420)
        status = "Atrasado"
        motivo = pick_reason(stage)
        sla_cumprido = False

    actual = scheduled + timedelta(minutes=delay_minutes)

    return {
        "pedido_id": order_id,
        "data_pedido": created.strftime("%Y-%m-%d %H:%M:%S"),
        "data_programada": scheduled.strftime("%Y-%m-%d %H:%M:%S"),
        "data_real": actual.strftime("%Y-%m-%d %H:%M:%S"),
        "turno": pick_turno(created.hour),
        "canal": random.choices(CANAIS, weights=[0.42, 0.35, 0.15, 0.08], k=1)[0],
        "etapa_critica": stage,
        "status_pedido": status,
        "motivo_atraso": motivo,
        "tempo_atraso_min": delay_minutes,
        "sla_cumprido": "Sim" if sla_cumprido else "Não",
        "retrabalho": "Sim" if retrabalho else "Não",
        "inconsistencia": "Sim" if inconsistencia else "Não",
    }


def build_occurrences(order_row, occurrence_id_start):
    rows = []
    if order_row["tempo_atraso_min"] == 0:
        return rows, occurrence_id_start

    impact_count = random.randint(1, 3)
    for idx in range(impact_count):
        stage = random.choices(STAGES, weights=[0.18, 0.32, 0.22, 0.16, 0.12], k=1)[0]
        reason = pick_reason(stage)
        ocorrencia_dt = datetime.strptime(order_row["data_programada"], "%Y-%m-%d %H:%M:%S") + timedelta(
            minutes=random.randint(15, 180)
        )
        rows.append(
            {
                "ocorrencia_id": occurrence_id_start + idx,
                "pedido_id": order_row["pedido_id"],
                "etapa_logistica": stage,
                "data_ocorrencia": ocorrencia_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "turno": pick_turno(ocorrencia_dt.hour),
                "motivo": reason,
                "retrabalho": "Sim" if random.random() < 0.35 else "Não",
                "severidade": random.choices(["Baixa", "Média", "Alta"], weights=[0.2, 0.5, 0.3], k=1)[0],
                "tempo_atraso_min": random.randint(10, max(30, order_row["tempo_atraso_min"] // 2)),
            }
        )
    return rows, occurrence_id_start + impact_count


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    orders = []
    start_date = datetime(2026, 1, 1, 6, 0, 0)
    for order_id in range(1, 1801):
        orders.append(build_order(order_id, start_date))

    with (DATA_DIR / "pedidos.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "pedido_id",
                "data_pedido",
                "data_programada",
                "data_real",
                "turno",
                "canal",
                "etapa_critica",
                "status_pedido",
                "motivo_atraso",
                "tempo_atraso_min",
                "sla_cumprido",
                "retrabalho",
                "inconsistencia",
            ],
        )
        writer.writeheader()
        writer.writerows(orders)

    ocorrencias = []
    next_id = 1
    for order in orders:
        rows, next_id = build_occurrences(order, next_id)
        ocorrencias.extend(rows)

    with (DATA_DIR / "ocorrencias.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "ocorrencia_id",
                "pedido_id",
                "etapa_logistica",
                "data_ocorrencia",
                "turno",
                "motivo",
                "retrabalho",
                "severidade",
                "tempo_atraso_min",
            ],
        )
        writer.writeheader()
        writer.writerows(ocorrencias)

    atrasados = sum(1 for o in orders if o["status_pedido"] == "Atrasado")
    sla_ok = sum(1 for o in orders if o["sla_cumprido"] == "Sim")
    print("Base gerada com sucesso!")
    print(f"Pedidos: {len(orders)}")
    print(f"Pedidos atrasados: {atrasados} ({atrasados / len(orders):.1%})")
    print(f"Cumprimento do SLA: {sla_ok} ({sla_ok / len(orders):.1%})")
    print(f"Arquivos: {DATA_DIR / 'pedidos.csv'} e {DATA_DIR / 'ocorrencias.csv'}")
