/**
 * Compatibility export.
 *
 * The canonical RuntimeShell lives under runtime_os/core.
 * This file remains only so older imports continue to resolve during
 * release consolidation.
 */

export {
    RuntimeShell
} from "../../runtime_os/core/RuntimeShell"

export type {
    RuntimeShellProps
} from "../../runtime_os/core/RuntimeShell"
