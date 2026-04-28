export type AudioEncodeRequest = {
  expression: string;
  items: { id: string; text: string; kind: string; phaseIndex: number }[];
};

export type AudioEncodeResponse = {
  manifest: any;
};

export async function encodeAudioPhase(req: AudioEncodeRequest): Promise<AudioEncodeResponse> {
  const res = await fetch('/api/audio/encode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`audio encode failed: ${res.status}`);
  return res.json();
}
