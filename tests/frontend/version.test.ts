import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { APP_VERSION } from '../../src/lib/version';

// The updater compares the installed version with the release feed. One number in three files.
describe('app version', () => {
  it('is the same in package.json, Cargo.toml and tauri.conf.json', () => {
    const cargo = readFileSync(resolve('src-tauri/Cargo.toml'), 'utf8').match(/^version = "([^"]+)"/m)?.[1];
    const tauri = JSON.parse(readFileSync(resolve('src-tauri/tauri.conf.json'), 'utf8')).version;
    expect(cargo).toBe(APP_VERSION);
    expect(tauri).toBe(APP_VERSION);
  });

  it('ships an updater feed address and verifies installs only with a configured key', () => {
    const updater = JSON.parse(readFileSync(resolve('src-tauri/tauri.conf.json'), 'utf8')).plugins.updater;
    expect(updater.endpoints).toEqual(['https://github.com/kim0040/PomiTranslate/releases/latest/download/latest.json']);
    expect(typeof updater.pubkey).toBe('string');
  });
});
