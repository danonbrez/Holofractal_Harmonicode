"use strict";
/* Node regression loader for standalone browser/UMD render modules.
 * hhs_gui/package.json owns ESM semantics for the GUI; do not change that
 * package boundary or modify browser-embedded source for test execution.
 * Evaluate the unmodified UMD source in this Node realm with CJS bindings
 * so ArrayBuffer, typed arrays, and native packet validators retain identity.
 */
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
function loadRenderingUMD(relativeFile) {
  if(typeof relativeFile!=="string"||!/^hhs_[a-z0-9_]+\.js$/.test(relativeFile))
    throw Error("P220_UMD_RENDER_MODULE_PATH_INVALID");
  const file=path.resolve(__dirname,"../../hhs_gui/rendering",relativeFile);
  const source=fs.readFileSync(file,"utf8");
  const mod={exports:{}};
  const wrapper=vm.runInThisContext("(function(module,exports,require){\n"+source+"\n})",
    {filename:file});
  wrapper(mod,mod.exports,require);
  if(!mod.exports||typeof mod.exports!=="object"||Object.keys(mod.exports).length===0)
    throw Error("P220_UMD_RENDER_EXPORT_MISSING");
  return mod.exports;
}
module.exports={loadRenderingUMD};
