import { RuntimeDesktop } from "./runtime_os/core/RuntimeDesktop";
import { RuntimeWindowManager } from "./runtime_os/core/RuntimeWindowManager";

import { RuntimeCalculator } from "./runtime_apps/calculator/RuntimeCalculator";
import { RuntimeBreadboard } from "./runtime_apps/breadboard/RuntimeBreadboard";

export default function App() {
  return (
    <RuntimeDesktop>
      <RuntimeWindowManager>
        <RuntimeCalculator />
        <RuntimeBreadboard />
      </RuntimeWindowManager>
    </RuntimeDesktop>
  );
}
import { RuntimeShell } from "../runtime_os/core/RuntimeShell";

export default function App() {
  return <RuntimeShell />;
}