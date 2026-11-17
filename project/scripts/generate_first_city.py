#!/usr/bin/env python3
"""Regenerate the district-based FRLG walking demo. Generated assets are committed.
Pillow is required only for regeneration. No original source tilesets are modified.
"""
from pathlib import Path
from collections import Counter, deque
import json, struct
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
W, H = 106, 96
PRIMARY = ROOT / 'data/tilesets/primary/general_frlg'
OUT = ROOT / 'data/tilesets/secondary/prototype_city_frlg'

def read_palette(path):
    return tuple(tuple(map(int, s.split())) for s in path.read_text().splitlines()[3:19])

def read_tiles(path):
    im = Image.open(path)
    return [bytes(im.crop((x,y,x+8,y+8)).get_flattened_data()) for y in range(0,im.height,8) for x in range(0,im.width,8)]

class Bank:
    """Pack only used metatiles, preserving pixel indices, palettes, flips and layers."""
    def __init__(self):
        self.sources = {}
        self.palettes = [read_palette(PRIMARY/'palettes'/f'{n:02d}.pal') for n in range(7)]
        self.primary_tiles = read_tiles(PRIMARY/'tiles.png')
        self.tiles = []
        self.tile_ids = {t:i for i,t in enumerate(read_tiles(PRIMARY/'tiles.png'))}
        self.metas, self.attributes, self.cache = [], [], {}
    def source(self, name):
        if name not in self.sources:
            p=ROOT/'data/tilesets/secondary'/name
            self.sources[name]=(read_tiles(p/'tiles.png'),list(struct.iter_unpack('<8H',(p/'metatiles.bin').read_bytes())),list(struct.unpack('<%dI'%((p/'metatile_attributes.bin').stat().st_size//4),(p/'metatile_attributes.bin').read_bytes())),p)
        return self.sources[name]
    def palette(self, name, n):
        if n < 7:return n
        pal=read_palette(self.source(name)[3]/'palettes'/f'{n:02d}.pal')
        if pal not in self.palettes:
            self.palettes.append(pal)
        assert len(self.palettes)<=13, f'Too many palettes: {len(self.palettes)}; source {name} palette {n}'
        return self.palettes.index(pal)
    def tile(self, data):
        if data not in self.tile_ids:
            self.tile_ids[data]=640+len(self.tiles);self.tiles.append(data)
        return self.tile_ids[data]
    def meta(self, name, n):
        if n<640:return n
        key=(name,n)
        if key in self.cache:return self.cache[key]
        tiles,metas,attrs,_=self.source(name)
        words=[]
        for word in metas[n-640]:
            idx=word&1023;pal=word>>12
            if name in ['pewter_city_frlg','pallet_town_frlg'] and pal>=7:
                # Adapt museum/house colors to the shared FRLG building palettes.
                dest=({8:1,11:2}.get(pal,2) if name=='pallet_town_frlg' else {8:3,9:3,10:2,11:1}.get(pal,2))
                old=read_palette(self.source(name)[3]/'palettes'/f'{pal:02d}.pal')
                target=self.palettes[dest]
                remap=[0]+[min(range(1,16),key=lambda n:sum((a-b)**2 for a,b in zip(rgb,target[n]))) for rgb in old[1:]]
                pixels=tiles[idx-640] if idx>=640 else self.primary_tiles[idx]
                idx=self.tile(bytes(remap[v] for v in pixels));pal=dest
            else:
                if idx>=640:idx=self.tile(tiles[idx-640])
                pal=self.palette(name,pal)
            words.append(idx|(word&0xC00)|(pal<<12))
        result=640+len(self.metas);self.metas.append(words);self.attributes.append(attrs[n-640]);self.cache[key]=result
        return result
    def transformed(self,n,operation):
        words=list(self.metas[n-640] if n>=640 else struct.unpack_from('<8H',(PRIMARY/'metatiles.bin').read_bytes(),n*16))
        attr=self.attributes[n-640] if n>=640 else struct.unpack_from('<I',(PRIMARY/'metatile_attributes.bin').read_bytes(),n*4)[0]
        grass=list(struct.unpack_from('<8H',(PRIMARY/'metatiles.bin').read_bytes(),16))
        if operation=='clear_upper':
            for i in [0,1,4,5]:words[i]=grass[i]
        elif operation=='flip_y':words=[words[i]^0x800 for i in [2,3,0,1,6,7,4,5]]
        result=640+len(self.metas);self.metas.append(words);self.attributes.append(attr);return result
    def label(self,text):
        im=Image.new('P',(48,16),1);d=ImageDraw.Draw(im);font=ImageFont.load_default(size=9)
        d.rectangle((0,0,47,15),outline=7);box=d.textbbox((0,0),text,font=font)
        d.text(((48-box[2]+box[0])//2,2),text,fill=7,font=font)
        result=[]
        for x in range(3):
            words=[]
            for y in range(2):
                for i in range(2):words.append(self.tile(bytes(im.crop((x*16+i*8,y*8,x*16+i*8+8,y*8+8)).get_flattened_data()))|0x2000)
            result.append(640+len(self.metas));self.metas.append(words+words);self.attributes.append(0)
        return result
    def save(self):
        assert len(self.tiles)<=384, f'Too many secondary tiles: {len(self.tiles)}'
        assert len(self.metas)<=384, f'Too many secondary metatiles: {len(self.metas)}'
        OUT.mkdir(parents=True,exist_ok=True);(OUT/'palettes').mkdir(exist_ok=True)
        im=Image.new('P',(128,((len(self.tiles)+15)//16)*8));im.putpalette([c for rgb in self.palettes[0] for c in rgb]+[0]*(768-48))
        for i,t in enumerate(self.tiles):
            tile=Image.frombytes('P',(8,8),t);im.paste(tile,((i%16)*8,(i//16)*8))
        im.save(OUT/'tiles.png')
        (OUT/'metatiles.bin').write_bytes(b''.join(struct.pack('<8H',*m) for m in self.metas))
        (OUT/'metatile_attributes.bin').write_bytes(struct.pack('<%dI'%len(self.attributes),*self.attributes))
        for n in range(16):
            p=self.palettes[n] if n<len(self.palettes) else self.palettes[0]
            (OUT/'palettes'/f'{n:02d}.pal').write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,rgb)) for rgb in p)+'\n')
        return {'secondary_tiles':len(self.tiles),'secondary_metatiles':len(self.metas),'secondary_palettes':len(self.palettes)-7}

bank=Bank()
map_cache={}
def patch(city,tileset,x,y,w,h):
    if city not in map_cache:
        layouts=json.loads((ROOT/'data/layouts/layouts.json').read_text())['layouts']
        l=next(l for l in layouts if l['name']==city+'_Layout')
        raw=(ROOT/l['blockdata_filepath']).read_bytes();map_cache[city]=(l['width'],struct.unpack('<%dH'%(len(raw)//2),raw))
    width,vals=map_cache[city]
    return [[bank.meta(tileset,vals[(y+j)*width+x+i]&1023) for i in range(w)] for j in range(h)]
def c(n,solid=False):return n|0x3000|(0x400 if solid else 0)
grid=[[c(1) for _ in range(W)] for _ in range(H)]
occupied={}
def fill(x,y,w,h,n,solid=False):
    for yy in range(y,y+h):
        for xx in range(x,x+w):grid[yy][xx]=c(n,solid)
def stamp(x,y,mat,solid=True):
    for j,row in enumerate(mat):
        for i,n in enumerate(row):grid[y+j][x+i]=c(n,solid)
# Verified complete FRLG conifer. Previous prototype incorrectly used row 22/23.
TREE=[[14,15],[30,31],[38,39]]
def tree(x,y):stamp(x,y,TREE)
def flowerbed(x,y,w,h):
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            if (xx-x+yy-y)%2==0:grid[yy][xx]=c(4,True)
# Actual stone path, sampled from the broad pavement in Pewter City.
STONE=patch('PewterCity','pewter_city_frlg',10,9,2,2)
def pave(x,y,w,h):
    for yy in range(y,y+h):
        for xx in range(x,x+w):grid[yy][xx]=c(STONE[yy%2][xx%2])
manifest={'prototype':True,'version':'0.2','name':'Ciudad de prueba; nombre pendiente','width':W,'height':H,'spawn':[54,48],'buildings':[],'landmarks':[],'districts':{'residencial':[5,5,44,40],'comercial':[59,5,43,39],'negocios':[5,54,40,31],'parque_central':[48,53,31,22],'gimnasio_sur':[44,78,32,15]},'promenade':[52,3,4,90]}
# Consistent perimeter, no overlapping or half-tree pieces.
fill(0,0,W,3,1,True);fill(0,H-3,W,3,1,True);fill(0,0,4,H,1,True);fill(W-4,0,4,H,1,True)
for x in range(0,W-1,2):tree(x,0);tree(x,H-3)
for y in range(3,H-3,3):tree(0,y);tree(2,y);tree(W-4,y);tree(W-2,y)
# Main avenues: narrow paths through lawns, not a completely paved background.
pave(4,46,W-8,4);pave(52,3,4,87)
pave(47,49,4,40)
# Residential roads and short lanes linking each front door.
pave(6,14,43,3);pave(6,24,43,3);pave(6,34,43,3);pave(6,43,43,3)
pave(5,14,3,32);pave(46,14,3,32);pave(6,45,48,3)
# Commercial boulevards and connections to the common avenue.
pave(59,18,43,3);pave(59,31,43,3);pave(59,42,43,3)
pave(58,18,3,30);pave(99,18,3,28);pave(59,44,43,4)
# Add buildings with exact, independently verifiable footprints.
def building(kind,zone,x,y,mat,label=None,door=None):
    h,w=len(mat),len(mat[0]);assert x>=4 and y>=3 and x+w<=W-4 and y+h<=H-3
    for yy in range(y,y+h):
        for xx in range(x,x+w):assert (xx,yy) not in occupied,(kind,occupied.get((xx,yy)));occupied[xx,yy]=kind
    stamp(x,y,mat,True)
    if label:
        for i,n in enumerate(bank.label(label)):grid[y+h-3][x+(w-3)//2+i]=c(n,True)
    dx=x+w//2 if door is None else x+door
    pave(dx-1,y+h,3,2)
    b={'kind':kind,'zone':zone,'x':x,'y':y,'width':w,'height':h,'approach':[dx,y+h]};manifest['buildings'].append(b)
    return b
apt=patch('CeladonCity','celadon_city_frlg',4,4,5,8)
window_bottom=apt[-1][2]
condo_door=patch('CeladonCity','celadon_city_frlg',30,11,1,1)[0][0]
apt[-1][2]=condo_door
for x in [9,24,39]:building('departamentos','residencial',x,5,apt)
house=patch('PalletTown','pallet_town_frlg',5,3,5,5)
for x in [8,19,30,41]:building('casa','residencial',x,18,house,door=1)
for x in [8,19,30]:building('casa','residencial',x,28,house,door=1)
# Shops retain the distinctive original architecture.
mall=patch('CeladonCity','celadon_city_frlg',9,5,9,10)
building('centro_comercial','comercial',60,6,mall,door=2)
tower=[[row[0],row[1],row[2],row[2],row[2],row[3],row[4]] for row in apt]
tower[-1]=[apt[-1][0],apt[-1][1],window_bottom,condo_door,window_bottom,apt[-1][3],apt[-1][4]]
building('hotel','comercial',74,6,tower,label='HOTEL')
museum=patch('PewterCity','pewter_city_frlg',12,0,16,8)
museum[0]=[bank.transformed(n,'clear_upper') if i<11 else 1 for i,n in enumerate(museum[0])]
building('museo','comercial',86,6,museum,door=5)
pave(90,14,3,5);pave(76,14,3,5)
casino=patch('CeladonCity','celadon_city_frlg',31,17,10,5)
building('casino','comercial',84,25,casino,door=3)
center=patch('SaffronCity','saffron_city_frlg',22,34,5,5)
mart=patch('SaffronCity','saffron_city_frlg',38,18,4,4)
building('centro_pokemon','comercial',61,25,center)
building('tienda_azul','comercial',71,26,mart)
police=patch('PewterCity','pewter_city_frlg',32,8,5,4)
building('policia','comercial',93,37,police,label='POLICIA')
# Offices surround their own plaza: two north, one west and two south.
for x,y in [(8,55),(33,55),(6,66),(8,77),(33,77)]:building('oficina','negocios',x,y,apt)
pave(14,65,21,10);pave(18,62,4,24);pave(28,62,4,24);pave(5,86,44,3)
pave(12,63,26,3);pave(36,63,16,3);pave(11,75,28,2);pave(8,74,8,3)
fountain=patch('CeladonCity','celadon_city_frlg',12,18,3,4)
fill(22,66,7,8,1)
flowerbed(22,66,2,1);flowerbed(27,66,2,1);flowerbed(22,73,2,1);flowerbed(27,73,2,1)
stamp(24,68,fountain);manifest['landmarks'].append({'kind':'fuente_negocios','rect':[24,68,3,4],'approach':[25,72]})
# Central park with a formal flower ring, fountain and intersecting stone paths.
pave(49,53,31,3);pave(49,73,31,3);pave(77,53,3,23)
pave(55,62,24,3);pave(62,55,3,20)
fill(60,57,7,8,1)
pave(59,56,9,1);pave(59,65,9,1);pave(59,56,1,10);pave(67,56,1,10)
stamp(62,59,fountain);manifest['landmarks'].append({'kind':'fuente_central','rect':[62,59,3,4],'approach':[63,65]})
flowerbed(58,57,3,2);flowerbed(67,57,3,2);flowerbed(58,67,3,2);flowerbed(67,67,3,2)
for x,y in [(57,54),(70,54),(57,70),(70,70)]:tree(x,y)
# Quiet residential park and lake, separate from the central civic park.
pave(9,39,24,2);flowerbed(11,38,5,1);flowerbed(23,41,5,1)
for x,y in [(8,37),(28,37)]:tree(x,y)
# Lake bank is copied from a complete original lake; stretch its straight sides.
# No improvised metatile mirroring: primary corner/side pieces are taken in order.
# Use the known closed rectangular Celadon pool, including its original lower bank.
pool=patch('CeladonCity','celadon_city_frlg',24,21,6,3)
lake_w,lake_h=11,7
expanded=[]
for y in range(lake_h):
    row=pool[0 if y==0 or y==lake_h-1 else 1]
    if y==lake_h-1:row=[bank.transformed(n,'flip_y') for n in row]
    expanded.append([row[0] if x==0 else row[-1] if x==lake_w-1 else row[1] for x in range(lake_w)])
stamp(36,28,expanded);manifest['landmarks'].append({'kind':'lago_residencial','rect':[36,28,lake_w,lake_h],'approach':[40,36]})
# Southern gym: grove and a continuous promenade up to the north of the map.
pave(48,77,12,3);pave(48,77,3,16);pave(58,77,3,16);pave(48,92,13,1)
gym=patch('SaffronCity','saffron_city_frlg',43,8,7,5)
building('gimnasio','sur',51,85,gym)
pave(53,90,3,3)
for x in [44,46,62,64,66]:
    for y in [78,81,84,87,90]:tree(x,y)
# Restore the ceremonial approach through the tree line.
pave(52,77,4,8)
# Southeastern woodland balances the built-up blocks without adding empty pavement.
for y in range(52,91,3):
    for x in range(83,101,2):tree(x,y)
# Flower borders and planted junctions. No flowers are stamped onto the paving.
for x,y in [(8,4),(23,4),(38,4),(70,22),(77,22),(97,22),(17,53),(37,53),(57,40),(79,38),(60,90)]:
    if (x,y) not in occupied and grid[y][x]&1023==1:grid[y][x]=c(4,True)
# Validate traversability and exact requested counts before writing anything.
counts=Counter(b['kind'] for b in manifest['buildings'])
assert counts==Counter({'departamentos':3,'casa':7,'oficina':5,'hotel':1,'centro_comercial':1,'museo':1,'casino':1,'centro_pokemon':1,'tienda_azul':1,'policia':1,'gimnasio':1}),counts
spawn=tuple(manifest['spawn']);q=deque([spawn]);seen={spawn}
while q:
    x,y=q.popleft()
    for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
        xx,yy=p
        if 0<=xx<W and 0<=yy<H and p not in seen and not grid[yy][xx]&0xC00:seen.add(p);q.append(p)
for b in manifest['buildings']:assert tuple(b['approach']) in seen,('Unreachable',b)
paved_ids={n for row in STONE for n in row}
paved_seen={spawn};paved_queue=deque([spawn])
while paved_queue:
    x,y=paved_queue.popleft()
    for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
        if 0<=xx<W and 0<=yy<H and (xx,yy) not in paved_seen and not grid[yy][xx]&0xC00 and grid[yy][xx]&1023 in paved_ids:
            paved_seen.add((xx,yy));paved_queue.append((xx,yy))
for b in manifest['buildings']:assert tuple(b['approach']) in paved_seen,('Missing paved connection',b)
manifest['paving_metatiles']=sorted(paved_ids)
manifest['connected_paving_tiles']=len(paved_seen)
for point in manifest['landmarks']:assert tuple(point['approach']) in seen,('Unreachable landmark',point)
assert all(x not in [0,W-1] and y not in [0,H-1] for x,y in seen)
# Paths never overwrite a building footprint, and all complete buildings are solid.
for x,y in occupied:assert grid[y][x]&0xC00,('Paving overlaps a facade',x,y)
manifest['resources']=bank.save();manifest['walkable_connected_tiles']=len(seen)
layout=ROOT/'data/layouts/PrototypeCity_Frlg'
(layout/'map.bin').write_bytes(struct.pack('<%dH'%(W*H),*(v for row in grid for v in row)))
(layout/'border.bin').write_bytes(struct.pack('<4H',*(c(v,True) for v in [30,31,38,39])))
(ROOT/'project/prototypes/first_city.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'size':[W,H],'buildings':dict(counts),'resources':manifest['resources'],'reachable_tiles':len(seen)},indent=2))
