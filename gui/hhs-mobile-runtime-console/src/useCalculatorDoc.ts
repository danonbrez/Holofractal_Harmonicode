import { useMemo, useState } from 'react';
import {
  ExprDocument,
  backspaceDocument,
  clearDocument,
  diagnosticsForDocument,
  documentFromText,
  insertIntoDocument,
  moveCursor,
  renderDocument,
} from './calculatorExpressionModel';

export function useCalculatorDoc(initialText: string) {
  const [doc, setDoc] = useState<ExprDocument>(() => documentFromText(initialText));
  const text = useMemo(() => renderDocument(doc), [doc]);
  const diagnostics = useMemo(() => diagnosticsForDocument(doc), [doc]);
  const diagnosticNodeIds = useMemo(() => new Set(diagnostics.flatMap((d) => d.nodeIds)), [diagnostics]);

  function insert(raw?: string) {
    if (!raw) return;
    if (raw === 'CLEAR') return setDoc(clearDocument());
    if (raw === 'BACK') return setDoc((prev) => backspaceDocument(prev));
    if (raw === 'LEFT') return setDoc((prev) => moveCursor(prev, -1));
    if (raw === 'RIGHT') return setDoc((prev) => moveCursor(prev, 1));
    setDoc((prev) => insertIntoDocument(prev, raw));
  }

  function reset(nextText: string) {
    setDoc(documentFromText(nextText));
  }

  return { doc, setDoc, text, diagnostics, diagnosticNodeIds, insert, reset };
}
