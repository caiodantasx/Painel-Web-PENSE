from __future__ import annotations
import argparse, hashlib, json, logging, re, zipfile, unicodedata
from pathlib import Path
from collections import Counter
import pandas as pd

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'data'/'raw'; OUT=ROOT/'data'/'processed'; REPORTS=ROOT/'reports'; LOGS=ROOT/'logs'
for p in (OUT,REPORTS,LOGS): p.mkdir(parents=True,exist_ok=True)
logging.basicConfig(filename=LOGS/'pipeline.log',level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

SUPPORTED={'.xlsx','.xlsm','.xls','.ods','.csv'}
TERRITORIES={'Brasil':'BR','Norte':'N','Nordeste':'NE','Sudeste':'SE','Sul':'S','Centro-Oeste':'CO',
'Rondônia':'11','Acre':'12','Amazonas':'13','Roraima':'14','Pará':'15','Amapá':'16','Tocantins':'17',
'Maranhão':'21','Piauí':'22','Ceará':'23','Rio Grande do Norte':'24','Paraíba':'25','Pernambuco':'26',
'Alagoas':'27','Sergipe':'28','Bahia':'29','Minas Gerais':'31','Espírito Santo':'32','Rio de Janeiro':'33',
'São Paulo':'35','Paraná':'41','Santa Catarina':'42','Rio Grande do Sul':'43','Mato Grosso do Sul':'50',
'Mato Grosso':'51','Goiás':'52','Distrito Federal':'53'}
def clean(v):
    if pd.isna(v): return ''
    return re.sub(r'\s+',' ',str(v).replace('\n',' ').replace('\r',' ')).strip()
def slug(v):
    s=unicodedata.normalize('NFKD',clean(v)).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def number(v):
    if pd.isna(v): return None
    if isinstance(v,(int,float)) and not isinstance(v,bool): return float(v)
    s=clean(v).replace('%','').replace(' ','')
    if not s or s.lower() in {'-','—','…','...','x','na','n/a'}: return None
    if ',' in s and '.' in s: s=s.replace('.','').replace(',','.')
    elif ',' in s: s=s.replace(',','.')
    try: return float(s)
    except: return None
def expand_archives():
    for p in list(RAW.rglob('*.zip')):
        target=p.parent/'extracted'/re.sub(r'[^A-Za-z0-9_.-]+','_',p.stem)
        marker=target/'.extracted'
        if marker.exists(): continue
        target.mkdir(parents=True,exist_ok=True)
        try:
            with zipfile.ZipFile(p) as z:
                for item in z.infolist():
                    # prevent zip-slip
                    dest=(target/item.filename).resolve()
                    if target.resolve() not in dest.parents and dest != target.resolve(): continue
                    if not item.is_dir(): dest.parent.mkdir(parents=True,exist_ok=True)
                z.extractall(target)
            marker.write_text('ok',encoding='utf-8')
        except Exception as e: logging.exception('Falha extraindo %s: %s',p,e)
def input_files():
    return sorted(p for p in RAW.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED and 'extracted' not in p.parts or False)
def get_files():
    # Exclude files inside ZIP extraction folders if identical source also exists elsewhere; retain one copy by SHA-256.
    candidates=[p for p in RAW.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED and p.name!='.extracted']
    unique={}
    for p in candidates:
        try: h=hashlib.sha256(p.read_bytes()).hexdigest()
        except: continue
        unique.setdefault(h,p)
    return sorted(unique.values())
def read_workbook(path):
    ext=path.suffix.lower()
    if ext=='.csv': return {'CSV':pd.read_csv(path,header=None,dtype=object,encoding_errors='replace')}
    if ext=='.ods': return pd.read_excel(path,sheet_name=None,header=None,engine='odf',dtype=object)
    if ext=='.xls': return pd.read_excel(path,sheet_name=None,header=None,engine='xlrd',dtype=object)
    return pd.read_excel(path,sheet_name=None,header=None,dtype=object)
def detect_year(path, sheet, df):
    text=path.name+' '+sheet+' '+' '.join(clean(v) for v in df.head(10).to_numpy().flatten() if clean(v))
    years=re.findall(r'(?<!\d)(20(?:0\d|1\d|2\d))(?!\d)',text)
    # explicit years from names/titles only; otherwise leave unknown instead of guessing
    return int(years[0]) if years else None
def table_code(path,sheet):
    txt=path.stem+' '+sheet
    m=re.search(r'(?<!\d)(\d{1,2}\.\d{1,2}\.\d{1,2})(?!\d)',txt)
    if m:return m.group(1)
    m=re.search(r'(?<!\d)(\d{1,2}\.\d{1,2})(?!\d)',txt)
    return m.group(1) if m else ''
def title_candidate(df):
    rows=[]
    for i in range(min(12,len(df))):
        vals=[clean(v) for v in df.iloc[i].tolist() if clean(v)]
        if vals: rows.append(' | '.join(vals))
    return max(rows,key=len)[:500] if rows else ''
def row_fingerprint(cells):
    return hashlib.sha1('|'.join(slug(c) for c in cells if c).encode()).hexdigest()[:12]
def run_inventory():
    sheets=[]; cells=[]; issues=[]; row_records=[]
    files=get_files()
    for path in files:
        try: workbook=read_workbook(path)
        except Exception as e:
            issues.append({'severity':'ERROR','issue_type':'read_failure','file':str(path.relative_to(ROOT)),'sheet':'','row':'','detail':str(e)})
            continue
        for sheet,df in workbook.items():
            code=table_code(path,str(sheet)); year=detect_year(path,str(sheet),df)
            title=title_candidate(df)
            sheets.append({'file':str(path.relative_to(ROOT)),'file_name':path.name,'extension':path.suffix.lower(),
                'sheet':str(sheet),'table_code':code,'year_detected':year,'rows':len(df),'columns':len(df.columns),
                'title_candidate':title,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            for ri,row in df.iterrows():
                vals=[clean(v) for v in row.tolist()]
                nonempty=[v for v in vals if v]
                if not nonempty: continue
                terr=next((v for v in vals[:5] if v in TERRITORIES), '')
                row_records.append({'file':path.name,'sheet':str(sheet),'table_code':code,'year_detected':year,
                    'row_excel':int(ri)+1,'row_fingerprint':row_fingerprint(vals),'territory_candidate':terr,
                    'row_text':' | '.join(nonempty)[:1500],'nonempty_cells':len(nonempty)})
                for ci,v in enumerate(row.tolist()):
                    raw=clean(v)
                    if raw=='' : continue
                    # collect a header hint from preceding rows; not treated as definitive schema
                    headers=[]
                    for hr in range(max(0,int(ri)-5),int(ri)):
                        hv=clean(df.iloc[hr,ci])
                        if hv: headers.append(hv)
                    cells.append({'file':path.name,'sheet':str(sheet),'table_code':code,'year_detected':year,
                        'row_excel':int(ri)+1,'column_excel':ci+1,'territory_candidate':terr,
                        'raw_value':raw,'numeric_value':number(raw),'header_context':' | '.join(headers[-3:]),
                        'row_fingerprint':row_fingerprint(vals)})
            # likely anomalies: duplicate-looking rows and numeric range issues, not substantive outliers
            for ri,row in df.iterrows():
                vals=[clean(v) for v in row.tolist()]
                nums=[number(v) for v in row.tolist()]
                nums=[n for n in nums if n is not None]
                if len(nums)>=3 and any(n<0 or n>100 for n in nums):
                    issues.append({'severity':'REVIEW','issue_type':'numeric_outside_0_100','file':path.name,'sheet':str(sheet),'row':int(ri)+1,
                        'detail':'Há números fora de 0–100; pode ser contagem, código ou outra unidade. Validar unidade/cabeçalho.'})
    pd.DataFrame(sheets).to_csv(OUT/'catalogo_abas.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(row_records).to_csv(OUT/'linhas_origem.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(cells).to_csv(OUT/'celulas_normalizadas.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(issues,columns=['severity','issue_type','file','sheet','row','detail']).to_csv(OUT/'anomalias.csv',index=False,encoding='utf-8-sig')
    return pd.DataFrame(sheets),pd.DataFrame(row_records),pd.DataFrame(cells),pd.DataFrame(issues)
def build_comparison_catalog(sheet_df):
    if sheet_df.empty:return
    # Similar table codes across years are candidate matches, not proof of statistical comparability.
    g=sheet_df.groupby('table_code',dropna=False)
    records=[]
    for code,grp in g:
        if not code: continue
        records.append({'table_code':code,'files':' | '.join(sorted(grp.file_name.unique())),
            'sheets':' | '.join(sorted(grp.sheet.unique())),'years_detected':' | '.join(map(str,sorted(set(y for y in grp.year_detected.dropna().astype(int))))),
            'variants':len(grp),'row_counts':' | '.join(map(str,grp.rows.tolist())),
            'column_counts':' | '.join(map(str,grp.columns.tolist())),
            'comparability_status':'PENDENTE_VALIDACAO',
            'review_required':'Enunciado, população, denominador, unidade, categorias, idade, dependência, território e IC'})
    pd.DataFrame(records).to_csv(OUT/'catalogo_comparabilidade.csv',index=False,encoding='utf-8-sig')
def build_historical():
    # No mean is computed from raw cells. This creates a safe template; values enter only after mapping/validation.
    path=ROOT/'config'/'mapeamento_validado.csv'
    if not path.exists():
        pd.DataFrame(columns=['source_file','source_sheet','table_code','year','indicator_id','indicator_label','territory','territory_code','age_group','administration','category','estimate_column','ci_low_column','ci_high_column','unit','denominator','series_id','comparable','validation_note']).to_csv(path,index=False,encoding='utf-8-sig')
    mapping=pd.read_csv(path,dtype=str).fillna('')
    canonical=ROOT/'data'/'processed'/'base_analitica.csv'
    if mapping.empty:
        pd.DataFrame(columns=['year','series_id','indicator_id','territory','estimate','ci_low','ci_high','source_file','source_sheet']).to_csv(canonical,index=False,encoding='utf-8-sig')
        pd.DataFrame(columns=['series_id','territory','n_years','first_year','last_year','mean_estimate','min_estimate','max_estimate','years','status','interpretation_note']).to_csv(OUT/'serie_historica.csv',index=False,encoding='utf-8-sig')
        return
    # Mapped column names refer to Excel columns like A, B, C. Extracted row-level mapping is deliberately explicit.
    # Full canonicalization requires per-table adapter code; do not infer from raw cells.
    pd.DataFrame(columns=['year','series_id','indicator_id','territory','estimate','ci_low','ci_high','source_file','source_sheet']).to_csv(canonical,index=False,encoding='utf-8-sig')
    pd.DataFrame(columns=['series_id','territory','n_years','first_year','last_year','mean_estimate','min_estimate','max_estimate','years','status','interpretation_note']).to_csv(OUT/'serie_historica.csv',index=False,encoding='utf-8-sig')
def main():
    expand_archives()
    sheets,rows,cells,issues=run_inventory()
    build_comparison_catalog(sheets)
    build_historical()
    print(f"Arquivos/abas catalogados: {len(sheets)} abas em {sheets.file_name.nunique() if not sheets.empty else 0} arquivos.")
    print(f"Linhas preservadas: {len(rows):,}; células não vazias: {len(cells):,}; alertas: {len(issues):,}.")
    print("Saídas: data/processed/catalogo_abas.csv, linhas_origem.csv, celulas_normalizadas.csv, catalogo_comparabilidade.csv, anomalias.csv.")
    print("Série histórica permanece bloqueada até configurar mapeamento validado por indicador/tabela.")
if __name__=='__main__': main()
