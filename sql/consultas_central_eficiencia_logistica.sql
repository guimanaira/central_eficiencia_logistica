-- Banco de dados: Central de Controle de Eficiência Logística
-- Objetivo: identificar etapas, turnos e motivos que mais geram atraso na operação.

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
);

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
);

-- 1. Taxa de atraso por etapa logística
SELECT
    etapa_critica AS etapa,
    COUNT(*) AS total_pedidos,
    SUM(CASE WHEN status_pedido = 'Atrasado' THEN 1 ELSE 0 END) AS pedidos_atrasados,
    ROUND(100.0 * SUM(CASE WHEN status_pedido = 'Atrasado' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_atraso_pct,
    ROUND(AVG(CASE WHEN status_pedido = 'Atrasado' THEN tempo_atraso_min END), 2) AS media_atraso_min
FROM pedidos
GROUP BY etapa_critica
ORDER BY taxa_atraso_pct DESC, pedidos_atrasados DESC;

-- 2. Volume de pedidos por turno e taxa de atraso
SELECT
    turno,
    COUNT(*) AS volume_pedidos,
    SUM(CASE WHEN status_pedido = 'Atrasado' THEN 1 ELSE 0 END) AS pedidos_atrasados,
    ROUND(100.0 * SUM(CASE WHEN status_pedido = 'Atrasado' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_atraso_pct
FROM pedidos
GROUP BY turno
ORDER BY volume_pedidos DESC;

-- 3. Percentual de SLA por dia
SELECT
    DATE(data_pedido) AS data_pedido,
    COUNT(*) AS total_pedidos,
    SUM(CASE WHEN sla_cumprido = 'Sim' THEN 1 ELSE 0 END) AS sla_cumprido,
    ROUND(100.0 * SUM(CASE WHEN sla_cumprido = 'Sim' THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_pct
FROM pedidos
GROUP BY DATE(data_pedido)
ORDER BY data_pedido;

-- 4. Retrabalho e inconsistências no total de pedidos
SELECT
    ROUND(100.0 * SUM(CASE WHEN retrabalho = 'Sim' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_retrabalho,
    ROUND(100.0 * SUM(CASE WHEN inconsistencias = 'Sim' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_inconsistencia
FROM pedidos;

-- 5. Participação de cada motivo no total de atrasos
SELECT
    motivo_atraso AS motivo,
    COUNT(*) AS pedidos_atrasados,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS participacao_pct
FROM pedidos
WHERE status_pedido = 'Atrasado'
GROUP BY motivo_atraso
ORDER BY pedidos_atrasados DESC;

-- 6. Top 10 combinações de etapa e motivo de atraso
SELECT
    etapa_critica AS etapa,
    motivo_atraso AS motivo,
    COUNT(*) AS ocorrencias,
    ROUND(AVG(tempo_atraso_min), 2) AS media_atraso_min
FROM pedidos
WHERE status_pedido = 'Atrasado'
GROUP BY etapa_critica, motivo_atraso
ORDER BY ocorrencias DESC, media_atraso_min DESC
LIMIT 10;

-- 7. Categorização de ocorrências por etapa e severidade
SELECT
    etapa_logistica,
    severidade,
    COUNT(*) AS qtd_ocorrencias,
    ROUND(AVG(tempo_atraso_min), 2) AS media_minutos
FROM ocorrencias
GROUP BY etapa_logistica, severidade
ORDER BY qtd_ocorrencias DESC;

-- 8. Top 3 ofensores da operação (visão executiva)
WITH ofensores AS (
    SELECT
        etapa_critica AS etapa,
        motivo_atraso AS motivo,
        COUNT(*) AS pedidos_atrasados,
        ROUND(AVG(tempo_atraso_min), 2) AS media_atraso_min
    FROM pedidos
    WHERE status_pedido = 'Atrasado'
    GROUP BY etapa_critica, motivo_atraso
)
SELECT *
FROM ofensores
ORDER BY pedidos_atrasados DESC, media_atraso_min DESC
LIMIT 3;
