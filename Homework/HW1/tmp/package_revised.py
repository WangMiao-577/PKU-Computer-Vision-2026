"""Promote the visually verified report and atomically replace submission ZIP."""
from pathlib import Path
import hashlib
import shutil
import zipfile

root=Path(__file__).resolve().parents[1]
build=root/'tmp/pdfs/revised'
for name in ['report.pdf','report.aux','report.log','report.out']:
    shutil.copy2(build/name,root/name)

submission=root/'石禾言_2500013221_HW1'
paths=[Path(x) for x in ['report.pdf','gaussian_pyramid.py','campus.png','zebra.jpg',
     'figs/q2_overview.png','figs/q2_line_measurements.png','figs/q2_zoom.png',
     'figs/q3_comparison.png','out/comparison.png']]
for tag in ['gaussian_pyramid','direct_pyramid']:
    for i,name in enumerate(['original','half','quarter','eighth']):
        paths.append(Path(f'out/{tag}/level{i}_{name}.png'))
assert len(paths)==17
for p in paths:
    target=submission/p
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(root/p,target)

temporary=root/'tmp/revised_submission.zip'
with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in paths:
        z.write(submission/p,arcname=(Path(submission.name)/p).as_posix())

def digest(data):
    return hashlib.sha256(data).hexdigest()

with zipfile.ZipFile(temporary) as z:
    assert z.testzip() is None
    assert len(z.infolist())==17
    assert {n for n in z.namelist()}=={(Path(submission.name)/p).as_posix() for p in paths}
    for p in paths:
        assert '..' not in p.parts and not p.is_absolute()
        assert digest(z.read((Path(submission.name)/p).as_posix()))==digest((root/p).read_bytes()),p
        assert digest((submission/p).read_bytes())==digest((root/p).read_bytes()),p
assert digest((root/'report.pdf').read_bytes())!=digest((root/'tmp/pre_q2_revision/report.pdf').read_bytes())
final=root/'石禾言_2500013221_HW1.zip'
temporary.replace(final)
print(f'Updated ZIP: {final}')
print(f'{len(paths)} files, {final.stat().st_size / (1024*1024):.2f} MiB; CRC and all source/archive hashes verified.')
print('Current PDF SHA256:',digest((root/'report.pdf').read_bytes()))
print('Original PDF, source, images, and ZIP preserved under tmp/pre_q2_revision/.')
