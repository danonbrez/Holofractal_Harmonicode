import React from 'react';
import { RuntimeAnomalies } from '../runtimeData';

export function AlertBanner({ anomalies }: { anomalies?: RuntimeAnomalies }) {
  const status = anomalies?.status ?? 'CLEAR';
  const color = status === 'CRITICAL' ? '#f44' : status === 'WARN' ? '#ff4' : '#4f4';
  return (
    <div style={{ padding: '8px 10px', background: status === 'CLEAR' ? '#031' : status === 'WARN' ? '#332800' : '#300', color, borderBottom: `1px solid ${color}`, fontSize: 12 }}>
      ALERT STATE: {status} · critical={anomalies?.critical ?? 0} warn={anomalies?.warn ?? 0}
    </div>
  );
}

export default function AlertPanel({ anomalies }: { anomalies?: RuntimeAnomalies }) {
  const alerts = anomalies?.alerts ?? [];
  return (
    <div style={{ padding: 10, fontSize: 11, borderTop: '1px solid #133' }}>
      <div>Anomaly Timeline</div>
      {alerts.length === 0 ? (
        <div style={{ color: '#9f9', marginTop: 6 }}>CLEAR · no active alerts</div>
      ) : alerts.map((a) => {
        const color = a.severity === 'CRITICAL' ? '#f66' : a.severity === 'WARN' ? '#ff6' : '#9cf';
        return (
          <div key={a.alert_hash72} style={{ borderBottom: '1px solid #222', padding: '6px 0', color }}>
            <div>{a.severity} · {a.code}</div>
            <div style={{ opacity: 0.85 }}>{a.message}</div>
            <div style={{ opacity: 0.55 }}>{a.alert_hash72}</div>
          </div>
        );
      })}
    </div>
  );
}
