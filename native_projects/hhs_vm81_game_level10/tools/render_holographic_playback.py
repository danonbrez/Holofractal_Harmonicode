#!/usr/bin/env python3
import argparse, hashlib, json, shutil, subprocess
from fractions import Fraction
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CONTRACT='HHS-VM81-MP4-HOLOGRAPHIC-PLAYBACK-OVERLAY-V1'
CLASSES=['VM81_MP4_HOLOGRAPHIC_OVERLAY_GENERATED','VM81_MP4_HOLOGRAPHIC_PLAYBACK_ROUNDTRIP_VERIFIED','VM81_HOLOGRAPHIC_DEPTH_LIGHTING_COMPOSITE_VERIFIED']
VIDEO=(640,576)

def run(c): return subprocess.run(c,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True).stdout
def tool(n):
    p=shutil.which(n)
    if not p: raise RuntimeError(f'missing required tool: {n}')
    return p
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clamp(v): return max(0,min(255,v))
def font(s):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(p).exists(): return ImageFont.truetype(p,s)
    return ImageFont.load_default()
def screen(a,b): return 255-(((255-a)*(255-b)+127)//255)
def composite(a,b):
    a=a.convert('RGB'); b=b.convert('RGB'); ap=a.load(); bp=b.load(); out=Image.new('RGB',a.size); op=out.load()
    for y in range(a.height):
        for x in range(a.width):
            ar,ag,ab=ap[x,y]; br,bg,bb=bp[x,y]; op[x,y]=(screen(ar,br),screen(ag,bg),screen(ab,bb))
    return out

def masks(base):
    rgb=base.convert('RGB'); px=rgb.load(); sem=Image.new('L',rgb.size); sp=sem.load()
    gray=rgb.convert('L'); gp=gray.load(); edge=Image.new('L',rgb.size); ep=edge.load()
    total=sx=sy=0
    for y in range(rgb.height):
        for x in range(rgb.width):
            r,g,b=px[x,y]; hi=max(r,g,b); sat=hi-min(r,g,b)
            if hi>=168 and sat>=64 and y>10:
                v=min(255,96+sat); sp[x,y]=v
                if v>=128: total+=v; sx+=x*v; sy+=y*v
            if x and y:
                v=abs(gp[x,y]-gp[x-1,y])+abs(gp[x,y]-gp[x,y-1])
                if v>28: ep[x,y]=min(255,v*2)
    return sem,edge,(sx//total,sy//total) if total else (rgb.width//2,rgb.height//2)

def light(dst,mask,color,scale):
    dp=dst.load(); mp=mask.load(); cr,cg,cb=color
    for y in range(dst.height):
        for x in range(dst.width):
            q=(mp[x,y]*scale)//255
            if q:
                r,g,b=dp[x,y]; dp[x,y]=(clamp(r+cr*q//255),clamp(g+cg*q//255),clamp(b+cb*q//255))

def overlay(base,i):
    base=base.convert('RGB'); w,h=base.size; out=Image.new('RGB',base.size); d=ImageDraw.Draw(out)
    for y in range(h):
        scan=(y+i)%6==0
        for x in range(w):
            if (3*x+5*y+2*i)%53<=1: d.point((x,y),fill=(0,10+y%10,18+i%12))
            if (7*x-2*y+3*i)%71<=1 and y<126: d.point((x,y),fill=(10+i%8,0,22+x%12))
            if scan and ((x+i)&3):
                r,g,b=out.getpixel((x,y)); d.point((x,y),fill=(r,clamp(g+5),clamp(b+9)))
    sem,edges,(cx,cy)=masks(base); light(out,sem.filter(ImageFilter.MaxFilter(13)),(16,42,70),120); light(out,sem.filter(ImageFilter.MaxFilter(5)),(22,92,120),180)
    ep=edges.load(); op=out.load()
    for y in range(h):
        for x in range(w):
            v=ep[x,y]
            if not v: continue
            q=min(80,v//4)
            if x+1<w:
                r,g,b=op[x+1,y]; op[x+1,y]=(r,clamp(g+q),clamp(b+2*q))
            if x:
                r,g,b=op[x-1,y]; op[x-1,y]=(clamp(r+2*q),g,clamp(b+q))
    d=ImageDraw.Draw(out); pulse=i%36
    for n in range(5):
        rx=18+14*n+pulse//4; ry=max(6,rx//3); d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(8+8*n,44+10*n,74+13*n))
    cw=20+i%24; d.polygon([(cx-cw,0),(cx+cw,0),(cx+5,cy),(cx-5,cy)],fill=(4,12,22))
    for n in range(3):
        rx=24+18*n+(2*i)%14; ry=max(8,rx//4); d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(18+9*n,76+13*n,110+16*n))
    horizon=88+(i//12)%4
    for off in range(-96,97,24): d.line((w//2,horizon,w//2+off,h-1),fill=(5,28,44))
    for y in range(horizon,h,9): d.line((0,y,w-1,y),fill=(4,20,34))
    return out

def probe(path,count,fps,size):
    j=json.loads(run([tool('ffprobe'),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_read_frames,duration:format=duration,size','-of','json',str(path)])); s=j['streams'][0]; f=j['format']
    r={'codec':s.get('codec_name'),'pixel_format':s.get('pix_fmt'),'width':int(s.get('width',0)),'height':int(s.get('height',0)),'r_frame_rate':s.get('r_frame_rate','0/0'),'frame_count':int(s.get('nb_read_frames',0)),'duration_seconds':float(s.get('duration') or f.get('duration') or 0),'size_bytes':int(f.get('size',0))}
    if r['codec']!='h264' or (r['width'],r['height'])!=size or r['frame_count']!=count or Fraction(r['r_frame_rate'])!=Fraction(fps,1) or abs(r['duration_seconds']-count/fps)>1/fps+.02 or r['size_bytes']<=1024: raise RuntimeError(f'video verification failed: {path}')
    return r

def panel(im,label,scale=4):
    im=im.convert('RGB').resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST); p=Image.new('RGB',(im.width,im.height+34),(4,6,16)); p.paste(im,(0,34)); ImageDraw.Draw(p).text((8,8),label,font=font(14),fill=(238,244,255)); return p
def sheet(items,target,cols=2):
    ps=[]
    for path,label,scale,box in items:
        with Image.open(path) as im: im=im.convert('RGB').crop(box) if box else im.convert('RGB'); ps.append(panel(im,label,scale))
    w=max(p.width for p in ps); h=max(p.height for p in ps); rows=(len(ps)+cols-1)//cols; out=Image.new('RGB',(w*cols,h*rows),(4,6,16))
    for n,p in enumerate(ps): out.paste(p,((n%cols)*w,(n//cols)*h))
    out.save(target); return target

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); inp=a.input.resolve(); out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    trace=json.loads((inp/'texture-capture-trace.json').read_text())
    if trace.get('capture_classification')!='VM81_GOVERNED_TEXTURE_LAYER_FRAME_STREAM_CAPTURED' or trace.get('state_projection_non_mutating')!='VERIFIED' or trace.get('replay')!='MATCH': raise RuntimeError('source texture evidence is not closed')
    count=int(trace['frame_count']); fps=int(trace['ticks_per_second']); bases=sorted(inp.glob('frame_*.ppm'))
    if len(bases)!=count or any(p.name!=f'frame_{i:06d}.ppm' for i,p in enumerate(bases)): raise RuntimeError('noncanonical source frame sequence')
    canon=out/'canonical-overlay-frames'; decoded=out/'decoded-playback-frames'; comps=out/'composite-frames'; screens=out/'screenshots'
    for d in (canon,decoded,comps,screens): shutil.rmtree(d,ignore_errors=True); d.mkdir(parents=True)
    cp=[]; nonblack=0
    for i,p in enumerate(bases):
        with Image.open(p) as im: ov=overlay(im,i)
        raw=ov.tobytes(); nonblack+=sum(1 for k in range(0,len(raw),3) if raw[k] or raw[k+1] or raw[k+2]); q=canon/f'frame_{i:06d}.png'; ov.save(q); cp.append(q)
    if nonblack<=count*100: raise RuntimeError('blank holographic overlay')
    overlay_mp4=out/'vm81-holographic-overlay.mp4'; run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(canon/'frame_%06d.png'),'-c:v','libx264rgb','-preset','medium','-crf','0','-pix_fmt','rgb24','-movflags','+faststart',str(overlay_mp4)]); oi=probe(overlay_mp4,count,fps,(160,144))
    run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(overlay_mp4),'-vsync','0',str(decoded/'frame_%06d.png')]); dp=sorted(decoded.glob('frame_*.png'))
    if len(dp)!=count: raise RuntimeError('decoded frame count mismatch')
    c1=hashlib.sha256(); c2=hashlib.sha256(); outp=[]
    for i,(x,y,b) in enumerate(zip(cp,dp,bases)):
        with Image.open(x) as a1,Image.open(y) as a2:
            r1=a1.convert('RGB').tobytes(); r2=a2.convert('RGB').tobytes(); c1.update(r1); c2.update(r2)
            if r1!=r2: raise RuntimeError('MP4 playback was not pixel-exact')
        with Image.open(b) as bi,Image.open(y) as oi2: co=composite(bi,oi2)
        q=comps/f'frame_{i:06d}.png'; co.save(q); outp.append(q)
    if c1.hexdigest()!=c2.hexdigest(): raise RuntimeError('playback chain mismatch')
    movie=out/'vm81-platformer-holographic-playback.mp4'; run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(comps/'frame_%06d.png'),'-vf',f'scale={VIDEO[0]}:{VIDEO[1]}:flags=neighbor','-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]); mi=probe(movie,count,fps,VIDEO)
    specs=[('title','title_frame','01-title.png','TITLE / HOLOGRAPHIC DEPTH FIELD'),('checkpoint_one','checkpoint_one_frame','02-checkpoint-one.png','CHECKPOINT 1 / SEMANTIC LIGHT'),('checkpoint_two','checkpoint_two_frame','03-checkpoint-two.png','CHECKPOINT 2 / PARALLAX HOLOGRAM'),('victory','victory_frame','04-victory.png','VICTORY / GOAL VOLUMETRIC LIGHT')]; shots={}; items=[]
    for key,field,name,label in specs:
        p=outp[int(trace[field])]; q=screens/name; sheet([(p,label,4,None)],q,1); shots[key]=q; items.append((p,label,4,None))
    overview=sheet(items,screens/'00-holographic-playback-overview.png',2); shots['overview']=overview; sel=int(trace['checkpoint_one_frame'])
    stages=sheet([(bases[sel],'AUTHORITATIVE TEXTURE FRAME',4,None),(cp[sel],'CANONICAL HOLOGRAM FRAME',4,None),(dp[sel],'MP4 PLAYBACK FRAME',4,None),(outp[sel],'SCREEN-LIGHT COMPOSITE',4,None)],screens/'05-mp4-holographic-overlay-stages.png',2)
    details=sheet([(bases[int(trace['title_frame'])],'BASE PHASE CURVATURE',5,(0,8,160,86)),(dp[sel],'HOLOGRAPHIC DEPTH PLANES',5,(0,8,160,86)),(outp[int(trace['victory_frame'])],'SEMANTIC LIGHT + MATERIAL',5,(64,64,144,140)),(outp[int(trace['victory_frame'])],'PERSPECTIVE FLOOR VOLUME',5,(0,82,160,144))],screens/'06-holographic-depth-lighting-details.png',2)
    receipt={'contract':CONTRACT,'terminal_classifications':CLASSES,'status':'VERIFIED','source_contract':trace.get('contract'),'source_capture_classification':trace.get('capture_classification'),'authoritative_state':trace.get('authoritative_state'),'mutation_authority':trace.get('mutation_authority'),'base_projection_authority':trace.get('projection_authority'),'holographic_overlay_authority':'render_holographic_playback.py','overlay_transport':'H.264 RGB MP4 decoded before composition','composition_rule':'integer per-channel screen blend; black overlay pixels are identity','logical_resolution':'160x144','composite_video_resolution':f'{VIDEO[0]}x{VIDEO[1]}','frame_count':count,'ticks_per_second':fps,'selected_frames':{k:int(trace[f]) for k,f,_,_ in specs},'holographic_effects':['phase-interference scan field','semantic luminance bloom','chromatic edge phase echo','elliptical hologram rings','volumetric light cone','perspective guide-plane depth volume'],'overlay_nonblack_pixel_writes':nonblack,'canonical_overlay_pixel_chain_sha256':c1.hexdigest(),'decoded_playback_pixel_chain_sha256':c2.hexdigest(),'mp4_playback_pixel_exact':'VERIFIED','source_texture_frame_chain_hash72':trace.get('frame_stream_hash72'),'source_texture_frame_chain_hash216':trace.get('frame_stream_hash216'),'source_final_hash72':trace.get('final_hash72'),'source_final_hash216':trace.get('final_hash216'),'source_state_projection_non_mutating':trace.get('state_projection_non_mutating'),'source_inherited_gradient_reproducible':trace.get('inherited_gradient_reproducible'),'overlay_mp4':{'path':overlay_mp4.name,'sha256':sha(overlay_mp4),**oi},'composite_mp4':{'path':movie.name,'sha256':sha(movie),**mi},'screenshots':{k:{'path':str(p.relative_to(out)),'sha256':sha(p)} for k,p in shots.items()},'stage_sheet':{'path':str(stages.relative_to(out)),'sha256':sha(stages)},'detail_sheet':{'path':str(details.relative_to(out)),'sha256':sha(details)},'phase':trace.get('phase'),'opcode_coverage':trace.get('opcode_coverage'),'checkpoints_reached':int(trace.get('checkpoints_reached',0)),'replay':trace.get('replay'),'base_texture_frames_unchanged':'VERIFIED','vm81_state_mutation':'NONE'}
    (out/'holographic-playback-evidence.json').write_text(json.dumps(receipt,indent=2)+'\n'); print(json.dumps(receipt,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
