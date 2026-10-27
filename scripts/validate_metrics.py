from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "central_eficiencia_logistica.sqlite"


def import_csv_to_sqlite():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS pedidos")
    cur.execute("DROP TABLE IF EXISTS ocorrencias")

    cur.execute(
        """
        CREATE TABLE pedidos (
            pedido_id INTEGER,
            data_pedido TEXT,
            data_programada TEXT,
            data_real TEXT,
            turno TEXT,
            canal TEXT,
            etapa_critica TEXT,
            status_pedido TEXT,
            motivo_atraso TEXT,
            tempo_atraso_min INTEGER,
            sla_cumprido TEXT,
            retrabalho TEXT,
            inconsistencias TEXT
        )
        """
    )

    with (DATA_DIR / "pedidos.csv").open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["pedido_id"]),
                r["data_pedido"],
                r["data_programada"],
                r["data_real"],
                r["turno"],
                r["canal"],
                r["etapa_critica"],
                r["status_pedido"],
                r["motivo_atraso"],
                int(r["tempo_atraso_min"]),
                r["sla_cumprido"],
                r["retrabalho"],
                r["inconsistencia"],
            )
            for r in reader
        ]

    cur.executemany(
        "INSERT INTO pedidos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )

    cur.execute(
        """
        CREATE TABLE ocorrencias (
            ocorrencia_id INTEGER,
            pedido_id INTEGER,
            etapa_logistica TEXT,
            data_ocorrencia TEXT,
            turno TEXT,
            motivo TEXT,
            retrabalho TEXT,
            severidade TEXT,
            tempo_atraso_min INTEGER
        )
        """
    )

    with (DATA_DIR / "ocorrencias.csv").open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["ocorrencia_id"]),
                int(r["pedido_id"]),
                r["etapa_logistica"],
                r["data_ocorrencia"],
                r["turno"],
                r["motivo"],
                r["retrabalho"],
                r["severidade"],
                int(r["tempo_atraso_min"]),
            )
            for r in reader
        ]

    cur.executemany(
        "INSERT INTO ocorrencias VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )

    conn.commit()
    conn.close()


def fetch_all(query: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    result = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in result]


def build_summary():
    metrics = {}
    metrics["volume_total_pedidos"] = fetch_all("SELECT COUNT(*) AS total FROM pedidos")[0]["total"]
    metrics["pedidos_atrasados"] = fetch_all("SELECT COUNT(*) AS total FROM pedidos WHERE status_pedido = 'Atrasado'")[0]["total"]
    metrics["taxa_atraso_geral"] = round(metrics["pedidos_atrasados"] / metrics["volume_total_pedidos"] * 100, 2)
    metrics["sla_cumprido"] = fetch_all("SELECT COUNT(*) AS total FROM pedidos WHERE sla_cumprido = 'Sim'")[0]["total"]
    metrics["sla_pct"] = round(metrics["sla_cumprido"] / metrics["volume_total_pedidos"] * 100, 2)
    metrics["taxa_retrabalho"] = fetch_all("SELECT ROUND(100.0 * SUM(CASE WHEN retrabalho='Sim' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct FROM pedidos")[0]["pct"]
    metrics["taxa_inconsistencia"] = fetch_all("SELECT ROUND(100.0 * SUM(CASE WHEN inconsistencias='Sim' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct FROM pedidos")[0]["pct"]
    metrics["atraso_por_etapa"] = fetch_all(
        """
        SELECT etapa_critica AS etapa,
               COUNT(*) AS total_pedidos,
               SUM(CASE WHEN status_pedido='Atrasado' THEN 1 ELSE 0 END) AS pedidos_atrasados,
               ROUND(100.0 * SUM(CASE WHEN status_pedido='Atrasado' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_atraso_pct,
               ROUND(AVG(CASE WHEN status_pedido='Atrasado' THEN tempo_atraso_min END), 2) AS media_minutos
        FROM pedidos
        GROUP BY etapa_critica
        ORDER BY taxa_atraso_pct DESC, pedidos_atrasados DESC
        """
    )
    metrics["top_motivos"] = fetch_all(
        """
        SELECT motivo_atraso AS motivo,
               COUNT(*) AS pedidos_atrasados,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS participacao_pct
        FROM pedidos
        WHERE status_pedido='Atrasado'
        GROUP BY motivo_atraso
        ORDER BY pedidos_atrasados DESC
        LIMIT 10
        """
    )
    metrics["top_ofensores"] = fetch_all(
        """
        SELECT etapa_critica AS etapa,
               motivo_atraso AS motivo,
               COUNT(*) AS ocorrencias,
               ROUND(AVG(tempo_atraso_min), 2) AS media_minutos
        FROM pedidos
        WHERE status_pedido='Atrasado'
        GROUP BY etapa_critica, motivo_atraso
        ORDER BY ocorrencias DESC, media_minutos DESC
        LIMIT 10
        """
    )
    return metrics


if __name__ == "__main__":
    import_csv_to_sqlite()
    summary = build_summary()
    (DATA_DIR / "metricas_resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "database": str(DB_PATH),
        "volume_total_pedidos": summary["volume_total_pedidos"],
        "pedidos_atrasados": summary["pedidos_atrasados"],
        "taxa_atraso_geral": summary["taxa_atraso_geral"],
        "sla_pct": summary["sla_pct"],
        "taxa_retrabalho": summary["taxa_retrabalho"],
        "taxa_inconsistencia": summary["taxa_inconsistencia"],
        "top_etapa": summary["atraso_por_etapa"][0],
        "top_motivo": summary["top_motivos"][0]
    }, ensure_ascii=False, indent=2))
