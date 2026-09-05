"""Check generated synthetic examples; requires pypdf. Run after compilation."""
from pathlib import Path
import re
from pypdf import PdfReader

root = Path(__file__).resolve().parent.parent
for name, category, level in [
    ('compliance-example', 'professional', '博士'),
    ('academic-doctor', 'academic', '博士'),
    ('academic-master', 'academic', '硕士'),
    ('professional-master', 'professional', '硕士'),
]:
    reader = PdfReader(root / (name + '.pdf'))
    pages = [re.sub(r'\s+', '', p.extract_text()) for p in reader.pages]
    professional = category == 'professional'
    assert len(pages) == 8, (name, 'unexpected cover or statement page break', len(pages))
    assert ('专业学位论文' if professional else '学术学位论文') in pages[0]
    assert ('类别' if professional else '学科') in pages[1]
    assert ('专业学位' + level if professional else '工程' + level) in pages[1]
    assert '行业导师' in pages[1]
    assert ('ProfessionalDegreeAppliedfor' if professional else 'AcademicDegreeAppliedfor') in pages[2]
    assert ('ProfessionalDegreeCategory' if professional else 'Speciality') in pages[2]
    assert 'Degree-Conferring-Institution' in pages[2], (name, 'English cover split')
    assert 'IndustrySupervisor' in pages[2]
    assert '学术研究工作或专业实践工作' in pages[-1]
    assert '保密学位论文' in pages[-1] and '导师签名' in pages[-1]
    assert '嗨！thesis' not in ''.join(pages)
    log = (root / (name + '.log')).read_text(encoding='utf-8', errors='replace')
    assert not re.search(r'^!|undefined|Overfull', log, re.MULTILINE), name
    assert 'textheight=637.34172pt' in log and 'textwidth=426.79134pt' in log
    print(name + ': PASS (covers, degree labels, geometry, declaration, log)')
