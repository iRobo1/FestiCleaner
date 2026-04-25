/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * Hostname (or IP) of the Arduino UNO Q running the FestiCleaner app.
   * When set, LivePanel embeds the on-board video stream from
   * http://<host>:4912/embed instead of falling back to ASCII telemetry.
   *
   * Example: VITE_BOARD_HOST=festicleaner.local
   */
  readonly VITE_BOARD_HOST?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
