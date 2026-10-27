import zipfile, sys, shutil, hashlib
from pathlib import Path
dest = Path(sys.argv[1]) / "data" / "microdata"
U = Path("/mnt/user-data/uploads"); A = Path("/mnt/user-data/attachments/bfd8486f-afae-5f86-94d0-3b0175c610fd")
plan = [(U/"Dados__2_.zip", "CSV/PENSE2024_MICRODADOS.csv", "PENSE_2024"),
        (U/"Dados__4_.zip", "Dados/CSV/PENSE2019_MICRODADOS.csv", "PENSE_2019"),
        (U/"PeNSE_2015_AMOSTRA1__1_.zip", "arquivos csv/PENSE_AMOSTRA1_ALUNOESCOLA.CSV", "PENSE_2015_A1"),
        (U/"PeNSE_2015_AMOSTRA2_1.zip", "arquivos csv/PENSE_AMOSTRA2_ALUNO.CSV", "PENSE_2015_A2"),
        (U/"1793054645171_PENSE_2012_microdados.zip", "pense2012Estudantes.txt", "PENSE_2012"),
        (A/"3cb19858-1793054645170_PENSE_2009_microdados.zip", "Base_Pense_Completa_2009.txt", "PENSE_2009")]
for zp, member, ed in plan:
    z = zipfile.ZipFile(zp)
    info = next(i for i in z.infolist() if i.filename.endswith(member) or i.filename.split("/")[-1] == member)
    out = dest / ed / member.split("/")[-1]; out.parent.mkdir(parents=True, exist_ok=True)
    with z.open(info) as src, out.open("wb") as dst: shutil.copyfileobj(src, dst)
    print(ed, out.name, out.stat().st_size, hashlib.sha256(out.read_bytes()).hexdigest()[:16])
