import { useEffect, useState } from 'react';

export function useHHSStream() {
  const [state, setState] = useState<any>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/hhs`);

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setState(data);
      } catch {}
    };

    return () => ws.close();
  }, []);

  return state;
}
