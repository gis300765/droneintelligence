from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parent.parent
output=root/'dist'
output.mkdir(exist_ok=True)
with ZipFile(output/'droneintelligence-web.zip','w',ZIP_DEFLATED) as archive:
    for path in sorted((root/'web').rglob('*')):
        if path.is_file():archive.write(path,path.relative_to(root/'web'))
print(output/'droneintelligence-web.zip')
