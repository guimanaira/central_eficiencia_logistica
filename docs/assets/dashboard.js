const metrics = {
  totalOrders: 1800,
  delayedOrders: 758,
  delayRate: 42.11,
  sla: 57.89,
  retrabalho: 18.44,
  inconsistencias: 12.33,
  topStages: [
    { stage: 'Separação', value: 82, tone: 'primary' },
    { stage: 'Carregamento', value: 71, tone: 'warning' },
    { stage: 'Recebimento', value: 63, tone: 'danger' },
    { stage: 'Conferência', value: 58, tone: 'primary' },
    { stage: 'Expedição', value: 46, tone: 'warning' }
  ],
  topReasons: [
    { label: 'Falta de operador', percent: 88, tone: 'danger' },
    { label: 'Pedido incompleto', percent: 72, tone: 'warning' },
    { label: 'Conferência pendente', percent: 68, tone: 'primary' },
    { label: 'Falha de WMS', percent: 53, tone: 'warning' },
    { label: 'Separação incorreta', percent: 48, tone: 'primary' }
  ],
  offenders: [
    { stage: 'Separação', reason: 'Falta de operador', volume: '137', impact: '18.1%' },
    { stage: 'Carregamento', reason: 'Falha de WMS', volume: '123', impact: '16.2%' },
    { stage: 'Recebimento', reason: 'Pedido incompleto', volume: '109', impact: '14.4%' }
  ]
};

function renderMetricCard(id, value, label, trend) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `
    <div class="kpi-label">${label}</div>
    <div class="kpi-value">${value}</div>
    <div class="kpi-trend">${trend}</div>
  `;
}

function renderBars() {
  const container = document.getElementById('barChart');
  if (!container) return;

  container.innerHTML = metrics.topStages.map(item => `
    <div class="bar-group">
      <div class="bar ${item.tone === 'warning' ? 'warning' : item.tone === 'danger' ? 'danger' : ''}" style="height:${item.value}%"></div>
      <div class="bar-label">${item.stage}</div>
    </div>
  `).join('');
}

function renderProgressList() {
  const list = document.getElementById('reasonList');
  if (!list) return;

  list.innerHTML = metrics.topReasons.map(item => `
    <div class="progress-item">
      <div class="progress-top">
        <span>${item.label}</span>
        <strong>${item.percent}%</strong>
      </div>
      <div class="progress-track">
        <div class="progress-bar ${item.tone === 'warning' ? 'warning' : item.tone === 'danger' ? 'danger' : ''}" style="width:${item.percent}%"></div>
      </div>
    </div>
  `).join('');
}

function renderOffenderTable() {
  const tbody = document.getElementById('offenderBody');
  if (!tbody) return;

  tbody.innerHTML = metrics.offenders.map((row) => `
    <tr>
      <td>${row.stage}</td>
      <td>${row.reason}</td>
      <td>${row.volume}</td>
      <td>${row.impact}</td>
    </tr>
  `).join('');
}

renderMetricCard('metricOrders', metrics.totalOrders.toLocaleString('pt-BR'), 'Pedidos', 'Base mensal');
renderMetricCard('metricDelayed', `${metrics.delayedOrders.toLocaleString('pt-BR')}`, 'Atrasados', `${metrics.delayRate}% da operação`);
renderMetricCard('metricSla', `${metrics.sla}%`, 'SLA', 'Meta do mês');
renderMetricCard('metricRetrabalho', `${metrics.retrabalho}%`, 'Retrabalho', 'Indicador crítico');

renderBars();
renderProgressList();
renderOffenderTable();
