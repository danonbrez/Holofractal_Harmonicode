#!/usr/bin/env python3
"""Verify the native VM81 texture stream and produce modality-matched media."""
from __future__ import annotations

import argparse, hashlib, json, shutil, subprocess
from fractions import Fraction
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageStat

CONTRACT="HHS-VM81-GOVERNED-TEXTURE-LAYERS-V1"
CAPTURE="VM81_GOVERNED_TEXTURE_LAYER_FRAME_STREAM_CAPTURED"
LAYERS="VM81_GOVERNED_TEXTURE_LAYER_COMPARISON_CAPTURED"
CLASSIFICATION="VM81_GOVERNED_TEXTURE_LAYER_PRESENTATION_VERIFIED"
LOGICAL=(160,144); VIDEO=(640,576)
FONT_PATHS=(Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'),Path('/usr/share/fonts/dejavu/DejaVuSansMono.ttf'))

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()

def tool(name:str)->str:
    p=shutil.which(name)
    if not p: raise RuntimeError(f'missing executable: {name}')
    return p

def run(args:list[str])->str:
    return subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout

def font(size:int):
    for p in FONT_PATHS:
        if p.is_file(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def load_json(path:Path): return json.loads(path.read_text(encoding='utf-8'))

def labelled(path:Path,label:str,scale:int=4)->Image.Image:
    with Image.open(path) as im:
        base=im.convert('RGB').resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
    canvas=Image.new('RGB',(base.width,base.height+34),(8,12,28)); canvas.paste(base,(0,34))
    ImageDraw.Draw(canvas).text((10,8),label,font=font(16),fill=(238,244,255))
    return canvas

def inspect_frames(paths:list[Path]):
    hashes=set(); min_colors=1<<30; max_colors=0; min_std=1e9
    for p in paths:
        with Image.open(p) as im:
            rgb=im.convert('RGB'); rgb.load()
            if rgb.size!=LOGICAL: raise RuntimeError(f'bad frame size: {p} {rgb.size}')
            colors=len(rgb.getcolors(maxcolors=LOGICAL[0]*LOGICAL[1]) or [])
            std=sum(ImageStat.Stat(rgb).stddev)/3
            if colors<128 or std<14: raise RuntimeError(f'flat texture frame: {p}')
            min_colors=min(min_colors,colors); max_colors=max(max_colors,colors); min_std=min(min_std,std)
        hashes.add(sha(p))
    if len(hashes)!=len(paths): raise RuntimeError('texture frame stream is not unique')
    return {'unique_frames':len(hashes),'minimum_rgb_colors':min_colors,'maximum_rgb_colors':max_colors,'minimum_channel_stddev':round(min_std,4)}

def adjacent_energy(im:Image.Image,box):
    rgb=im.convert('RGB').crop(box); px=rgb.load(); total=count=0
    for y in range(0,rgb.height-1,2):
        for x in range(0,rgb.width-1,2):
            a=px[x,y]
            for b in (px[x+1,y],px[x,y+1]): total+=sum(abs(i-j) for i,j in zip(a,b)); count+=3
    return total/max(1,count)

def structure(path:Path):
    with Image.open(path) as im:
        rgb=im.convert('RGB'); top=ImageStat.Stat(rgb.crop((0,12,160,42))).mean; low=ImageStat.Stat(rgb.crop((0,72,160,102))).mean
        distance=sum(abs(a-b) for a,b in zip(top,low)); bg=adjacent_energy(rgb,(0,12,160,104)); terrain=adjacent_energy(rgb,(0,112,160,144))
    if distance<22 or bg<2 or terrain<5: raise RuntimeError('texture structure thresholds failed')
    return {'top_mean_rgb':[round(x,3) for x in top],'lower_mean_rgb':[round(x,3) for x in low],'absolute_rgb_distance':round(distance,3),'background_adjacent_energy':round(bg,4),'terrain_adjacent_energy':round(terrain,4)}

def screenshots(paths:list[Path],trace:dict,out:Path):
    d=out/'screenshots'; d.mkdir(parents=True,exist_ok=True)
    specs=[('title',trace['title_frame'],'01-title.png','TITLE / TEXTURE FIELD'),('checkpoint_one',trace['checkpoint_one_frame'],'02-checkpoint-one.png','CHECKPOINT 1 / MATERIAL + SIGNATURE'),('checkpoint_two',trace['checkpoint_two_frame'],'03-checkpoint-two.png','CHECKPOINT 2 / PARALLAX DEPTH'),('victory',trace['victory_frame'],'04-victory.png','VICTORY / GOAL ATTRACTOR')]
    outputs={}; panels=[]
    for key,index,name,label in specs:
        panel=labelled(paths[int(index)],label); target=d/name; panel.save(target); outputs[key]=target; panels.append(panel)
    w=max(x.width for x in panels); h=max(x.height for x in panels); sheet=Image.new('RGB',(w*2,h*2),(4,6,16))
    for i,p in enumerate(panels): sheet.paste(p,((i%2)*w,(i//2)*h))
    overview=d/'00-texture-layer-overview.png'; sheet.save(overview); outputs['overview']=overview
    for p in panels:p.close()
    return outputs

def layer_sheet(input_dir:Path,out:Path):
    manifest=load_json(input_dir/'layers/layer-manifest.json')
    if manifest.get('classification')!=LAYERS: raise RuntimeError('missing texture layer classification')
    paths=sorted((input_dir/'layers').glob('[0-9][0-9]-*.ppm'))
    if len(paths)!=8 or len({sha(p) for p in paths})!=8: raise RuntimeError('texture layer comparison mismatch')
    layers=manifest.get('layers',[])
    if len(layers)!=8: raise RuntimeError('native layer manifest count mismatch')
    required={'INTERFERENCE_TEXTURE_FIELD':'field_writes','PARALLAX_MIDGROUND':'midground_writes','TERRAIN_MATERIALS':'material_writes','SEMANTIC_ENERGY_SIGNATURES':'semantic_writes','PLAYER_MATERIAL_AND_TRAIL':'player_writes'}
    for item in layers:
        field=required.get(item.get('name'))
        if field and int(item.get(field,0))<=0: raise RuntimeError(f'empty texture layer: {item.get("name")}')
    labels=['LEGACY GRADIENT','INTERFERENCE FIELD','PARALLAX MIDGROUND','TERRAIN MATERIALS','SEMANTIC ENERGY','PLAYER MATERIAL','STRUCTURAL COMPOSITE','FULL COHESION']
    panels=[labelled(p,l,3) for p,l in zip(paths,labels)]; w=max(p.width for p in panels); h=max(p.height for p in panels)
    sheet=Image.new('RGB',(w*4,h*2),(4,6,16))
    for i,p in enumerate(panels): sheet.paste(p,((i%4)*w,(i//4)*h))
    target=out/'screenshots/05-governed-texture-layers.png'; sheet.save(target)
    for p in panels:p.close()
    return target,{'source_frame':int(manifest['source_frame']),'source_state_hash216':manifest['source_state_hash216'],'native_layers':layers,'ppm_sha256':[sha(p) for p in paths]}

def detail_sheet(paths:list[Path],trace:dict,out:Path):
    specs=[(trace['title_frame'],(0,12,160,80),'INTERFERENCE + MIDGROUND'),(trace['checkpoint_one_frame'],(0,92,160,144),'TERRAIN + HAZARD MATERIAL'),(trace['checkpoint_one_frame'],(72,72,132,132),'CHECKPOINT SIGNATURE'),(trace['victory_frame'],(80,72,160,136),'PLAYER + GOAL ATTRACTOR')]
    panels=[]
    for index,box,label in specs:
        with Image.open(paths[int(index)]) as im: crop=im.convert('RGB').crop(box)
        scaled=crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST); panel=Image.new('RGB',(scaled.width,scaled.height+30),(8,12,28)); panel.paste(scaled,(0,30)); ImageDraw.Draw(panel).text((8,7),label,font=font(14),fill=(238,244,255)); panels.append(panel)
    w=max(p.width for p in panels); h=max(p.height for p in panels); sheet=Image.new('RGB',(w*2,h*2),(4,6,16))
    for i,p in enumerate(panels): sheet.paste(p,((i%2)*w,(i//2)*h))
    target=out/'screenshots/06-texture-detail-crops.png'; sheet.save(target)
    for p in panels:p.close()
    return target

def video(input_dir:Path,target:Path,fps:int,count:int):
    run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(input_dir/'frame_%06d.ppm'),'-vf',f'scale={VIDEO[0]}:{VIDEO[1]}:flags=neighbor','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',str(target)])
    probe=json.loads(run([tool('ffprobe'),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration:format=duration,size','-of','json',str(target)])); stream=probe['streams'][0]; fmt=probe['format']
    info={'codec':stream.get('codec_name'),'width':int(stream.get('width',0)),'height':int(stream.get('height',0)),'r_frame_rate':stream.get('r_frame_rate','0/0'),'avg_frame_rate':stream.get('avg_frame_rate','0/0'),'frame_count':int(stream.get('nb_read_frames',0)),'duration_seconds':float(stream.get('duration') or fmt.get('duration') or 0),'size_bytes':int(fmt.get('size',0))}
    if info['codec']!='h264' or (info['width'],info['height'])!=VIDEO or info['frame_count']!=count or Fraction(info['r_frame_rate'])!=Fraction(fps,1) or abs(info['duration_seconds']-count/fps)>1/fps+0.02 or info['size_bytes']<=1024: raise RuntimeError('texture video verification failed')
    return info

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); inp=a.input.resolve(); out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    trace=load_json(inp/'texture-capture-trace.json')
    if trace.get('contract')!=CONTRACT or trace.get('capture_classification')!=CAPTURE or trace.get('state_projection_non_mutating')!='VERIFIED' or trace.get('inherited_gradient_reproducible')!='VERIFIED' or trace.get('replay')!='MATCH' or trace.get('opcode_coverage')!='19/19': raise RuntimeError('invalid native texture trace')
    for key in ('field','midground','materials','semantic','player'):
        if int(trace.get('texture_write_totals',{}).get(key,0))<=0: raise RuntimeError(f'zero texture writes: {key}')
    paths=sorted(inp.glob('frame_*.ppm')); count=int(trace['frame_count'])
    if len(paths)!=count or any(p.name!=f'frame_{i:06d}.ppm' for i,p in enumerate(paths)): raise RuntimeError('noncanonical texture frame sequence')
    frame_metrics=inspect_frames(paths); structure_metrics=structure(paths[int(trace['checkpoint_one_frame'])]); shots=screenshots(paths,trace,out); layers_path,layers_data=layer_sheet(inp,out); details=detail_sheet(paths,trace,out); movie=out/'vm81-platformer-governed-textures.mp4'; movie_info=video(inp,movie,int(trace['ticks_per_second']),count)
    receipt={'contract':CONTRACT,'terminal_classification':CLASSIFICATION,'status':'VERIFIED','source_capture_classification':trace['capture_classification'],'authoritative_state':trace['authoritative_state'],'mutation_authority':trace['mutation_authority'],'projection_authority':trace['projection_authority'],'logical_resolution':trace['logical_resolution'],'video_resolution':f'{VIDEO[0]}x{VIDEO[1]}','frame_count':count,'ticks_per_second':int(trace['ticks_per_second']),'selected_frames':{'title':int(trace['title_frame']),'checkpoint_one':int(trace['checkpoint_one_frame']),'checkpoint_two':int(trace['checkpoint_two_frame']),'victory':int(trace['victory_frame'])},'texture_system':{'inherited_sprite_flags':int(trace['inherited_sprite_flags']),'texture_flags':int(trace['texture_flags']),'layers':trace['texture_layers'],'write_totals':trace['texture_write_totals'],'frame_metrics':frame_metrics,'structure_metrics':structure_metrics,'layer_comparison':layers_data},'screenshots':{k:{'path':str(p.relative_to(out)),'sha256':sha(p)} for k,p in shots.items()},'texture_layer_sheet':{'path':str(layers_path.relative_to(out)),'sha256':sha(layers_path)},'texture_detail_sheet':{'path':str(details.relative_to(out)),'sha256':sha(details)},'mp4':{'path':str(movie.relative_to(out)),'sha256':sha(movie),**movie_info},'inherited_gradient_reproducible':trace['inherited_gradient_reproducible'],'inherited_sprite_projection':'UNCHANGED','state_projection_non_mutating':trace['state_projection_non_mutating'],'phase':trace['phase'],'opcode_coverage':trace['opcode_coverage'],'checkpoints_reached':int(trace['checkpoints_reached']),'replay':trace['replay'],'frame_stream_hash72':trace['frame_stream_hash72'],'frame_stream_hash216':trace['frame_stream_hash216'],'final_hash72':trace['final_hash72'],'final_hash216':trace['final_hash216']}
    (out/'texture-modality-evidence.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
