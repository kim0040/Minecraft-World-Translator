/**
 * The version shown before the shell answers (and in a browser preview). The packaged app reads
 * its real version from the shell; tests/frontend/version.test.ts keeps package.json, Cargo.toml
 * and tauri.conf.json on the same number so the updater compares the right one.
 */
import { version } from '../../package.json';

export const APP_VERSION: string = version;
