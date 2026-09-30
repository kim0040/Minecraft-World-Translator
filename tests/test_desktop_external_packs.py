"""Desktop explicit external ZIP plans and restore with synthetic, manual-only text."""
from __future__ import annotations
import json,sys,tempfile,zipfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tests.test_desktop_parity import _request, _settings_set, _synthetic_world, _files_under
from tests.test_resource_pack_preflight import _resource_pack
from mwt import desktop_entry
from mwt.safety import ExternalTargetError
from mwt.desktop_resource_packs import normalize_external_pack_paths


def workflow(root: Path) -> None:
    world = _synthetic_world(root/'world-fixture')
    pack = root/'external-packs'/'selected.zip'
    original_pack = _resource_pack(pack)
    original_world = _files_under(world)
    data = root/'data'
    _settings_set(data, worldDir=str(world), resourcePackEnabled=True, externalResourcePackPaths=[str(pack)],
                  resourcePackOptions={'source_lang_files':['en_us.json'],'target_lang_file':'ko_kr.json','skip_if_target_exists':False})
    settings=_request(data,'settings.get',{'credentialOwner':'rust'})['payload']['settings']
    assert settings['external_resource_pack_paths']==[str(pack)]
    scan=_request(data,'scan.start',{'worldDir':str(world),'credentialOwner':'rust'})['payload']
    assert scan['status']=='completed',scan
    sources={item['source']:item['id'] for item in scan['candidates']}
    assert set(sources)=={'Hello sign','Hello pack'},sources
    assert next(row for row in scan['coverage'] if row['id']=='external_resource_pack')['scanned']
    assert pack.read_bytes()==original_pack and _files_under(world)==original_world
    with patch('mwt.secrets.load_api_key',side_effect=AssertionError('manual external pack must not read keychain')):
        result=_request(data,'translate.start',{'worldDir':str(world),'credentialOwner':'rust',
            'fingerprint':scan['fingerprint'],'scanPlanId':scan['scanPlanId'],
            'candidateOverrides':{sources['Hello sign']:'표지판 번역',sources['Hello pack']:'팩 번역'}})['payload']
    assert result['status']=='completed',result
    assert result['providerRequests']==0
    translated_pack=pack.read_bytes()
    assert translated_pack!=original_pack
    with zipfile.ZipFile(pack) as archive:
        assert json.loads(archive.read('assets/demo/lang/ko_kr.json'))=={'demo.greeting':'팩 번역'}
    backups=_request(data,'backups.list',{'worldDir':str(world)})['payload']['backups']
    selected=next(row for row in backups if row['backupSetId']==result['backupSetId'])
    assert selected['externalTargets']==[str(pack)]
    _settings_set(data,externalResourcePackPaths=[])
    with TestCase().assertRaises(ExternalTargetError):
        _request(data,'restore.start',{'worldDir':str(world),'backupSetId':result['backupSetId']})
    assert pack.read_bytes()==translated_pack
    _settings_set(data,externalResourcePackPaths=[str(pack)])
    restored=_request(data,'restore.start',{'worldDir':str(world),'backupSetId':result['backupSetId']})['payload']
    assert restored['status']=='restored'
    assert pack.read_bytes()==original_pack and _files_under(world)==original_world
    recovery=_request(data,'backups.list',{'worldDir':str(world)})['payload']['backups']
    assert next(row for row in recovery if row['backupSetId']==restored['recoverySetId'])['externalTargets']==[str(pack)]


def invalidation(root: Path) -> None:
    world=_synthetic_world(root/'world-fixture'); data=root/'data'; pack=root/'packs'/'selected.zip'
    _resource_pack(pack)
    _settings_set(data,worldDir=str(world),resourcePackEnabled=True,externalResourcePackPaths=[str(pack)])
    scan=_request(data,'scan.start',{'worldDir':str(world),'credentialOwner':'rust'})['payload']
    original_world=_files_under(world)
    with zipfile.ZipFile(pack,'a') as archive:archive.comment=b'changed after review'
    changed_pack=pack.read_bytes()
    result=_request(data,'translate.start',{'worldDir':str(world),'credentialOwner':'rust',
        'fingerprint':scan['fingerprint'],'scanPlanId':scan['scanPlanId']})
    assert result['type']=='response.error' and result['error']['code']=='PLAN_INVALIDATED',result
    assert _files_under(world)==original_world and pack.read_bytes()==changed_pack
    pack.unlink();(data/'jobs').mkdir(exist_ok=True)
    boot=_request(data,'app.bootstrap',{'worldDir':str(world),'credentialOwner':'rust'})['payload']
    assert boot['settings']['external_resource_pack_paths']==[str(pack)]
    assert not boot['resume']['available']



def changed_during_scan(root: Path) -> None:
    world = _synthetic_world(root / 'world-fixture')
    data = root / 'data'
    pack = root / 'packs' / 'selected.zip'
    _resource_pack(pack)
    _settings_set(data, worldDir=str(world), resourcePackEnabled=True, externalResourcePackPaths=[str(pack)])
    original_world = _files_under(world)
    run = desktop_entry._run_translator
    def change_after_collect(*args, **kwargs):
        report = run(*args, **kwargs)
        with zipfile.ZipFile(pack, 'a') as archive:
            archive.comment = b'changed while scan was running'
        return report
    with patch.object(desktop_entry, '_run_translator', side_effect=change_after_collect):
        result = _request(data, 'scan.start', {'worldDir': str(world), 'credentialOwner': 'rust'})
    assert result['type'] == 'response.error' and result['error']['code'] == 'PLAN_INVALIDATED', result
    assert json.loads((data / 'reports' / 'scan-report.json').read_text())['status'] == 'invalidated'
    assert not list((data / 'scan-plans').glob('*.json'))
    assert _files_under(world) == original_world


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='pomi-desktop-external-') as temporary:
        root=Path(temporary)
        workflow(root/'workflow');invalidation(root/'invalidate');changed_during_scan(root/'midscan')
    assert normalize_external_pack_paths([])==[]
    for invalid in [['relative.zip'],['/tmp/not-a-zip.dat'],['/tmp/a.zip']*17,{'path':'/tmp/a.zip'}]:
        try:normalize_external_pack_paths(invalid)
        except ValueError:pass
        else:raise AssertionError('invalid external selection accepted')
    print('PASS desktop external ZIP scan/manual run/invalidation/explicit restore/byte-identical recovery')

if __name__=='__main__':main()
