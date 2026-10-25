from pathlib import Path
import io, json, base64, importlib.util, tempfile, threading, os
from flask import Flask, request, jsonify, send_from_directory, Response
from PIL import Image
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.enums import ColorInterp
import numpy as np
from rasterio.vrt import WarpedVRT
from rasterio.transform import from_bounds
import math
import requests
from pyodm import Node

ROOT=Path(__file__).resolve().parent.parent
WEB_ROOT=ROOT/"web"
(ROOT/'models').mkdir(exist_ok=True)
app=Flask(__name__,static_folder=None)
app.config['MAX_CONTENT_LENGTH']=8*1024*1024*1024
model_lock=threading.Lock()
models={}
@app.before_request
def local_only():
    if request.host.split(':')[0] not in ('127.0.0.1','localhost'):
        return jsonify(error='Acceso local únicamente'),403
    origin=request.headers.get('Origin')
    if request.method!='GET' and origin not in (None,'null','http://127.0.0.1:8765','http://localhost:8765'):
        return jsonify(error='Origen no autorizado'),403
@app.after_request
def cors(response):
    if request.headers.get('Origin')=='null':
        response.headers['Access-Control-Allow-Origin']='null'
    response.headers['X-Content-Type-Options']='nosniff'
    return response
@app.errorhandler(Exception)
def error(e):
    return jsonify(error=str(e)),getattr(e,'code',400) or 400
@app.get('/')
def index(): return send_from_directory(WEB_ROOT,'index.html')
@app.get('/app')
@app.get('/app/')
def platform():return send_from_directory(WEB_ROOT/'app','index.html')
@app.get('/config.js')
def config():return send_from_directory(WEB_ROOT,'config.js')
@app.get('/landing')
@app.get('/landing.html')
def landing():return send_from_directory(WEB_ROOT,'index.html')
@app.get('/landing-assets/<path:filename>')
def landing_asset(filename):return send_from_directory(WEB_ROOT/'landing-assets',filename)
@app.get('/api/health')
def health():
    return jsonify(ok=True,geotiff=True,yolo=bool(importlib.util.find_spec('ultralytics')),models=[p.name for p in (ROOT/'models').glob('*.pt')])
def real_library():
    manifest=ROOT/'data'/'library.json'
    items=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    for item in items:
        local_source=ROOT/'data'/'source'/Path(item['meta']['source_file']).name
        if local_source.is_file():item['meta']['source_path']=str(local_source)
    return items
@app.get('/api/library')
def library():
    result=real_library()
    for item in result:item['meta'].pop('source_path',None)
    return jsonify(result)
@app.get('/api/library/<ident>/preview.png')
def library_preview(ident):
    if not any(p['source_id']==ident for p in real_library()):return jsonify(error='Raster no registrado'),404
    return send_from_directory(ROOT/'data',ident+'.png')
@app.get('/api/rasters/<ident>/tile/<int:z>/<int:x>/<int:y>.png')
def raster_tile(ident,z,x,y):
    entry=next((p for p in real_library() if p['source_id']==ident),None)
    if not entry:return jsonify(error='Raster no registrado'),404
    if not 0<=z<=23 or not 0<=x<2**z or not 0<=y<2**z:return jsonify(error='Tesela inválida'),400
    half=20037508.342789244;size=2*half/2**z
    west=-half+x*size;north=half-y*size
    transform=from_bounds(west,north-size,west+size,north,256,256)
    with rasterio.open(entry['meta']['source_path']) as src:
        with WarpedVRT(src,crs='EPSG:3857',transform=transform,width=256,height=256,resampling=Resampling.bilinear,add_alpha=True) as vrt:
            rgba=np.moveaxis(vrt.read([1,2,3,4]),0,-1).astype('uint8')
    buf=io.BytesIO();Image.fromarray(rgba).save(buf,format='PNG')
    return Response(buf.getvalue(),mimetype='image/png',headers={'Cache-Control':'private, max-age=3600'})
@app.post('/api/ortho')
def ortho():
    upload=request.files['image']
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'input.tif';upload.save(path)
        with rasterio.open(path) as src:
            if not src.crs: raise ValueError('El TIFF no contiene CRS. Exporta un GeoTIFF con sistema de referencia.')
            if src.count<3: raise ValueError('Se necesita un ortomosaico RGB de tres bandas. Los productos multiespectrales requieren un flujo específico.')
            transform,w,h=calculate_default_transform(src.crs,'EPSG:4326',src.width,src.height,*src.bounds)
            scale=min(1,2048/max(w,h));dw=max(1,int(w*scale));dh=max(1,int(h*scale))
            transform=transform*transform.scale(w/dw,h/dh)
            channels=[]
            for band in range(1,4):
                dst=np.zeros((dh,dw),dtype='float32')
                reproject(rasterio.band(src,band),dst,src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs='EPSG:4326',resampling=Resampling.bilinear,dst_nodata=np.nan)
                if src.dtypes[band-1]!='uint8':
                    valid=dst[np.isfinite(dst)]
                    if len(valid):
                        low,high=np.percentile(valid,[2,98]);dst=(dst-low)*255/max(high-low,1e-8)
                channels.append(np.nan_to_num(np.clip(dst,0,255)).astype('uint8'))
            rgb=np.stack(channels,axis=-1)
            alpha=np.zeros((dh,dw),dtype='uint8')
            reproject(src.dataset_mask(),alpha,src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs='EPSG:4326',resampling=Resampling.nearest)
            out=io.BytesIO();Image.fromarray(np.dstack([rgb,alpha])).save(out,format='PNG')
            west,south,east,north=rasterio.transform.array_bounds(dh,dw,transform)
            if west < -180 or east > 180 or south < -85 or north >85 or east-west>5 or north-south>5:
                raise ValueError('Extensión fuera del visor local: usa un ortomosaico de escala local, sin cruzar el antimeridiano.')
            return jsonify(image='data:image/png;base64,'+base64.b64encode(out.getvalue()).decode(),bounds=[west,south,east,north],source_crs=str(src.crs),source_width=src.width,source_height=src.height,resolution=list(src.res),display_width=dw,display_height=dh)
@app.post('/api/detect')
def detect():
    if not importlib.util.find_spec('ultralytics'):raise ValueError('YOLO no está instalado. Ejecuta instalar-yolo.cmd')
    from ultralytics import YOLO
    name=request.form['model']
    if Path(name).name!=name or not name.endswith('.pt') or not (ROOT/'models'/name).is_file():raise ValueError('Modelo no encontrado en models/')
    confidence=float(request.form.get('confidence',.25))
    if not .05<=confidence<=1:raise ValueError('Confianza fuera de rango')
    im=Image.open(request.files['image'].stream).convert('RGB')
    if im.width*im.height>50000000:raise ValueError('Imagen demasiado grande para inferencia directa')
    with model_lock:
        if name not in models:models[name]=YOLO(str(ROOT/'models'/name))
        results=models[name].predict(im,conf=confidence,verbose=False)
        boxes=[dict(xyxy=b.xyxy[0].tolist(),confidence=float(b.conf[0]),class_id=int(b.cls[0]),label=results[0].names[int(b.cls[0])]) for b in results[0].boxes]
    return jsonify(width=im.width,height=im.height,model=name,boxes=boxes)
def port():
    p=int(request.values.get('port',3000))
    if not 1<=p<=65535 or p==8765:raise ValueError('Puerto NodeODM inválido')
    return p
@app.get('/api/odm/info')
def odm_info():
    response=requests.get(f'http://127.0.0.1:{port()}/info',timeout=3)
    response.raise_for_status()
    return jsonify(response.json())
@app.post('/api/odm/task')
def odm_new():
    p=port();files=request.files.getlist('images')
    if len(files)<3:raise ValueError('Se necesitan tres fotos como mínimo')
    with tempfile.TemporaryDirectory() as td:
        paths=[]
        for i,f in enumerate(files):
            suffix=Path(f.filename or '').suffix.lower()
            if suffix not in ('.jpg','.jpeg','.png','.tif','.tiff','.txt'):raise ValueError('Formato no admitido: '+suffix)
            if suffix=='.txt' and f.filename!='gcp_list.txt':raise ValueError('Solo se admite gcp_list.txt como archivo de control')
            path=Path(td)/('gcp_list.txt' if suffix=='.txt' else str(i)+suffix);f.save(path);paths.append(str(path))
        task=Node('127.0.0.1',p).create_task(paths,{'orthophoto-resolution':5},name='Aerolab drone flight')
        return jsonify(uuid=task.uuid)
@app.get('/api/odm/task/<uuid>')
def odm_status(uuid):
    info=Node('127.0.0.1',port()).get_task(uuid).info()
    return jsonify(uuid=uuid,status=int(info.status),progress=info.progress,last_error=info.last_error)
@app.get('/api/odm/download/<uuid>')
def odm_download(uuid):
    r=requests.get(f'http://127.0.0.1:{port()}/task/{uuid}/download/orthophoto.tif',stream=True,timeout=60);r.raise_for_status()
    return Response(r.iter_content(1024*1024),content_type='image/tiff',headers={'Content-Disposition':'attachment; filename=ortomosaico.tif'})
if __name__=='__main__':
    print('DRONEINTELLIGENCE LOCAL: http://127.0.0.1:8765',flush=True)
    app.run(host='127.0.0.1',port=int(os.environ.get('PORT','8765')),threaded=True,debug=False)
