"""Reproducible two-card availability correction over immutable old evidence."""
import copy
from date_schema import load,put,validate_timeline,validate_release

def apply_correction(root):
    evidence=load(root/'tools/tgt-dk-availability-evidence.json')
    old=evidence['previousDate'];new=evidence['adoptedDate']
    for cid,dbf in evidence['ids'].items():
        path=root/'data'/f'{cid}.json';sidecar=root/'metadata'/f'{cid}.json'
        timeline=load(path);meta=load(sidecar)
        assert meta['originalSource']['card']['dbfId']==dbf
        assert next(iter(timeline)) in (old,new), 'Unexpected availability baseline; review correction before proceeding'
        if next(iter(timeline))==old:
            timeline={new if day==old else day:state for day,state in timeline.items()}
        release={'date':new,'status':evidence['releaseStatus'],'beforeDate':evidence['beforeDate']}
        validate_release(release);validate_timeline(timeline)
        meta['release']=release
        meta['availabilityCorrection']={
            'source':'tools/tgt-dk-availability-evidence.json',
            'previousDate':old,'adoptedDate':new,'status':'estimated',
            'meaning':evidence['meaning'],'confidence':copy.deepcopy(evidence['confidence']),
            'classUnlock':evidence['classUnlock'],
            'sourceRevision':evidence['sourceRevision'],
        }
        put(path,timeline);put(sidecar,meta)
