/**
 * =========================================================
 * RuntimeWorkspacePersistence
 * =========================================================
 *
 * Canonical Runtime OS persistence authority.
 *
 * Responsibilities:
 *
 * - window persistence
 * - viewport persistence
 * - overlay persistence
 * - replay persistence
 * - graph camera persistence
 * - workspace continuity
 *
 * Initial backend:
 *
 *     localStorage
 *
 * Future:
 *
 *     IndexedDB
 *     receipt snapshots
 *     runtime replay restoration
 */

// =========================================================
// Types
// =========================================================

export interface PersistedRuntimeWindow {

    id: string

    x: number

    y: number

    width: number

    height: number

    minimized: boolean

    maximized: boolean

    focused: boolean
}

// ---------------------------------------------------------

export interface PersistedViewportState {

    cameraX: number

    cameraY: number

    cameraZ: number

    targetX: number

    targetY: number

    targetZ: number

    zoom: number
}

// ---------------------------------------------------------

export interface PersistedRuntimeWorkspace {

    version: number

    updatedAt: number

    windows:
        PersistedRuntimeWindow[]

    overlays: {

        replayTimeline: boolean

        receiptInspector: boolean

        sidebarVisible: boolean
    }

    viewport:
        PersistedViewportState

    selectedReceiptId?:
        string

    replayPosition?:
        number
}

// =========================================================
// Constants
// =========================================================

const STORAGE_KEY =
    "HHS_RUNTIME_WORKSPACE"

const STORAGE_VERSION = 1

// =========================================================
// RuntimeWorkspacePersistence
// =========================================================

export class RuntimeWorkspacePersistence {

    // =====================================================
    // Save
    // =====================================================

    public save(

        workspace:
            PersistedRuntimeWorkspace

    ): void {

        try {

            const payload = {

                ...workspace,

                version:
                    STORAGE_VERSION,

                updatedAt:
                    Date.now()
            }

            localStorage.setItem(

                STORAGE_KEY,

                JSON.stringify(
                    payload
                )
            )

            console.log(

                "[RuntimeWorkspacePersistence] save"
            )

        } catch (error) {

            console.error(

                "[RuntimeWorkspacePersistence] save failure",

                error
            )
        }
    }

    // =====================================================
    // Load
    // =====================================================

    public load():
        PersistedRuntimeWorkspace
        | null {

        try {

            const raw =
                localStorage.getItem(
                    STORAGE_KEY
                )

            if (!raw) {

                return null
            }

            const parsed =
                JSON.parse(raw)

            // ---------------------------------------------
            // Version Guard
            // ---------------------------------------------

            if (

                parsed.version
                !== STORAGE_VERSION

            ) {

                console.warn(

                    "[RuntimeWorkspacePersistence] version mismatch"
                )

                return null
            }

            return parsed

        } catch (error) {

            console.error(

                "[RuntimeWorkspacePersistence] load failure",

                error
            )

            return null
        }
    }

    // =====================================================
    // Clear
    // =====================================================

    public clear():
        void {

        try {

            localStorage.removeItem(
                STORAGE_KEY
            )

            console.log(

                "[RuntimeWorkspacePersistence] cleared"
            )

        } catch (error) {

            console.error(

                "[RuntimeWorkspacePersistence] clear failure",

                error
            )
        }
    }

    // =====================================================
    // Exists
    // =====================================================

    public exists():
        boolean {

        return !!localStorage.getItem(
            STORAGE_KEY
        )
    }

    // =====================================================
    // Snapshot Helpers
    // =====================================================

    public defaultWorkspace():
        PersistedRuntimeWorkspace {

        return {

            version:
                STORAGE_VERSION,

            updatedAt:
                Date.now(),

            windows: [],

            overlays: {

                replayTimeline:
                    false,

                receiptInspector:
                    false,

                sidebarVisible:
                    true
            },

            viewport: {

                cameraX: 0,

                cameraY: 0,

                cameraZ: 12,

                targetX: 0,

                targetY: 0,

                targetZ: 0,

                zoom: 1
            },

            replayPosition: 0
        }
    }

    // =====================================================
    // Metrics
    // =====================================================

    public metrics() {

        const exists =
            this.exists()

        return {

            exists,

            storageKey:
                STORAGE_KEY,

            storageVersion:
                STORAGE_VERSION
        }
    }
}

// =========================================================
// Global Persistence Authority
// =========================================================

export const runtimeWorkspacePersistence =
    new RuntimeWorkspacePersistence()