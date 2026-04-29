@@
   const [busy, setBusy] = useState(false);
   const [error, setError] = useState<string | null>(null);
   const [page, setPage] = useState<'main' | 'more' | 'hhs'>('main');
+  const [selectedBranchHash, setSelectedBranchHash] = useState<string | null>(null);
@@
   const autocorrectionSuggestions = result?.autocorrections?.suggestions ?? [];
   const branchFrontier = result?.correctionBranchFrontier;
   const symbolicCandidates = result?.symbolic_substitution?.candidates ?? [];
-  const selectedBranch = branchFrontier?.branches?.find?.((b: any) => b.branch_hash72 === branchFrontier?.selected_branch_hash72) ?? branchFrontier?.branches?.[0];
+  const selectedBranch = branchFrontier?.branches?.find?.((b: any) => b.branch_hash72 === (selectedBranchHash ?? branchFrontier?.selected_branch_hash72)) ?? branchFrontier?.branches?.[0];
@@
-      {branchFrontier?.branches?.length ? <div style={{ marginTop: 8, background: '#050b14', border: '1px solid #08c', borderRadius: 6, padding: 8, fontSize: 11 }}><div style={{ color: '#72d6ff', fontWeight: 700 }}>Branch Frontier</div>{branchFrontier.branches.slice(0, 6).map((b: any) => <div key={b.branch_hash72} style={{ marginTop: 4, color: b.branch_hash72 === branchFrontier.selected_branch_hash72 ? '#ffff66' : '#dff' }}>{b.correction_kind} · score {b.total_score} · path [{b.projected_phases?.join(' → ')}]</div>)}</div> : null}
+      {branchFrontier?.branches?.length ? <div style={{ marginTop: 8, background: '#050b14', border: '1px solid #08c', borderRadius: 6, padding: 8, fontSize: 11 }}><div style={{ color: '#72d6ff', fontWeight: 700 }}>Branch Frontier</div>{branchFrontier.branches.slice(0, 6).map((b: any) => { const active = b.branch_hash72 === selectedBranch?.branch_hash72; return <div key={b.branch_hash72} style={{ marginTop: 6, color: active ? '#ffff66' : '#dff', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: 5 }}><div>{b.correction_kind} · score {b.total_score} · path [{b.projected_phases?.join(' → ')}]</div><button onClick={() => setSelectedBranchHash(b.branch_hash72)} style={{ marginTop: 3, background: active ? '#ffff66' : '#09324a', color: active ? '#111' : '#dff', border: 0, borderRadius: 4, padding: '2px 7px', fontWeight: 700 }}>{active ? 'SELECTED' : 'SELECT'}</button></div>; })}</div> : null}
