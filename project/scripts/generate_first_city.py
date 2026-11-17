#!/usr/bin/env python3
"""Regenerate the district-based FRLG walking demo. Generated assets are committed.
Pillow is required only for regeneration. No original source tilesets are modified.
"""
from pathlib import Path
from collections import Counter, deque
import json, struct
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
W, H = 118, 92
assert (W+15)*(H+14) <= 14336, "City exceeds map buffer including camera margin"
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
manifest={'prototype':True,'version':'0.3','name':'Ciudad de prueba; nombre pendiente','width':W,'height':H,'spawn':[65,45],'buildings':[],'landmarks':[],'districts':{'negocios':[4,3,36,33],'comercial':[49,3,64,39],'policia':[45,32,9,10],'lago_parque':[4,38,38,22],'gimnasio_suroeste':[4,62,54,26],'parque_este':[74,49,39,12],'residencial':[70,65,44,23]},'promenade':[64,13,4,76],'layout_reference':'Sam, plano dibujado adjunto del 17 de noviembre de 2026'}
# Perimeter, kept separate from the paths so no half-trees are erased.
fill(0,0,W,3,1,True);fill(0,H-3,W,3,1,True);fill(0,0,4,H,1,True);fill(W-4,0,4,H,1,True)
for x in range(0,W-1,2):tree(x,0);tree(x,H-3)
for y in range(3,H-3,3):tree(0,y);tree(2,y);tree(W-4,y);tree(W-2,y)
# The hand-drawn plan's spine: central north-south avenue, east commercial crossroad.
pave(64,13,4,76);pave(54,43,60,4)
pave(37,15,77,3);pave(37,15,3,20)
pave(49,31,65,2);pave(97,15,3,28)
# North-west business loop around E2's park.
pave(4,21,36,2);pave(8,33,32,3);pave(19,11,3,24)
pave(8,21,3,14);pave(31,21,3,14)
pave(38,33,3,16);pave(38,46,29,3)
# Lake park paths join the police crossing and the central avenue.
pave(4,37,38,2);pave(4,55,38,2);pave(4,37,2,20);pave(39,35,3,22)
pave(39,48,28,2)
# Commercial side streets between the Pokemon Center, mall, shop and museum.
pave(59,17,3,26);pave(78,17,3,26);pave(99,17,3,26)
pave(49,42,65,2)
# South-eastern residential perimeter; a park sits between the two house rows.
pave(70,62,44,3);pave(70,70,44,3);pave(70,87,44,2)
pave(70,62,3,27);pave(112,62,2,27);pave(76,81,38,1)
pave(64,63,9,3);pave(64,87,9,2)
# Keep the known, complete facades and graphics from the previous verified version.
def building(kind,zone,x,y,mat,label=None,door=None,reference=None):
    h,w=len(mat),len(mat[0]);assert x>=4 and y>=3 and x+w<=W-4 and y+h<=H-3
    for yy in range(y,y+h):
        for xx in range(x,x+w):assert (xx,yy) not in occupied,(kind,occupied.get((xx,yy)));occupied[xx,yy]=kind
    stamp(x,y,mat,True)
    if label:
        for i,n in enumerate(bank.label(label)):grid[y+h-3][x+(w-3)//2+i]=c(n,True)
    dx=x+w//2 if door is None else x+door
    pave(dx-1,y+h,3,min(2,H-3-y-h))
    b={'kind':kind,'zone':zone,'x':x,'y':y,'width':w,'height':h,'approach':[dx,y+h]}
    if reference:b['reference']=reference
    manifest['buildings'].append(b);return b
apt=patch('CeladonCity','celadon_city_frlg',4,4,5,8)
window_bottom=apt[-1][2]
condo_door=patch('CeladonCity','celadon_city_frlg',30,11,1,1)[0][0]
apt[-1][2]=condo_door
# E1 and E3 are tall side blocks; E2 is above the park, E5/E4 below it.
tall=apt[:6]+[apt[5]]*4+apt[6:]
for ref,x,y,mat in [('E1',5,7,tall),('E2',18,3,apt),('E3',31,7,tall),('E5',11,24,apt),('E4',27,24,apt)]:
    building('oficina','negocios',x,y,mat,reference=ref)
# Small business park directly below E2, with the retained first fountain.
fountain=patch('CeladonCity','celadon_city_frlg',12,18,3,4)
pave(14,12,15,2);pave(14,22,15,2);pave(14,12,2,12);pave(27,12,2,12)
fill(16,14,11,8,1)
stamp(19,16,fountain);flowerbed(17,14,2,1);flowerbed(24,14,2,1);flowerbed(17,20,2,1);flowerbed(24,20,2,1)
manifest['landmarks'].append({'kind':'fuente_negocios','rect':[19,16,3,4],'approach':[20,20]})
# Commercial layout follows the drawing: hotel/casino above, Center/mall/shop below.
tower=[[row[0],row[1],row[2],row[2],row[2],row[3],row[4]] for row in apt]
tower[-1]=[apt[-1][0],apt[-1][1],window_bottom,condo_door,window_bottom,apt[-1][3],apt[-1][4]]
building('hotel','comercial',54,4,tower,label='HOTEL');pave(56,12,3,5)
casino=patch('CeladonCity','celadon_city_frlg',31,17,10,5)
building('casino','comercial',85,4,casino,door=3);pave(87,9,3,8)
center=patch('SaffronCity','saffron_city_frlg',22,34,5,5)
mart=patch('SaffronCity','saffron_city_frlg',38,18,4,4)
building('centro_pokemon','comercial',51,22,center);pave(52,27,3,6)
mall=patch('CeladonCity','celadon_city_frlg',9,5,9,10)
building('centro_comercial','comercial',68,19,mall,door=2);pave(69,29,3,4)
building('tienda_azul','comercial',91,22,mart);pave(92,26,3,7)
museum=patch('PewterCity','pewter_city_frlg',12,0,16,8)
museum[0]=[bank.transformed(n,'clear_upper') if i<11 else 1 for i,n in enumerate(museum[0])]
building('museo','comercial',67,34,museum,door=5)
# Police station at the central crossing, between the lake and commercial block.
police=patch('PewterCity','pewter_city_frlg',32,8,5,4)
police=police[:3]+[police[2]]*3+police[3:]
building('policia','centro',46,33,police,label='POLICIA');pave(47,40,3,9)
# Western lake surrounded by a park. Closed banks retain the previous validated art.
pool=patch('CeladonCity','celadon_city_frlg',24,21,6,3)
lake_w,lake_h=27,12
expanded=[]
for y in range(lake_h):
    row=pool[0 if y==0 or y==lake_h-1 else 1]
    if y==lake_h-1:row=[bank.transformed(n,'flip_y') for n in row]
    expanded.append([row[0] if x==0 else row[-1] if x==lake_w-1 else row[1] for x in range(lake_w)])
stamp(7,40,expanded)
manifest['landmarks'].append({'kind':'lago_oeste','rect':[7,40,lake_w,lake_h],'approach':[20,53]})
flowerbed(8,58,8,1);flowerbed(25,58,8,1)
for x,y in [(7,36),(31,36),(34,51)]:tree(x,y)
# Large eastern park below the museum and above the residential quarter.
pave(73,49,41,2);pave(73,60,41,2);pave(73,49,2,13);pave(112,49,2,13)
pave(88,50,3,12);pave(74,55,39,2)
fill(86,52,7,7,1);stamp(88,53,fountain)
manifest['landmarks'].append({'kind':'fuente_parque_este','rect':[88,53,3,4],'approach':[89,58]})
flowerbed(81,52,3,2);flowerbed(95,52,3,2);flowerbed(81,58,3,1);flowerbed(95,58,3,1)
for x,y in [(76,51),(105,51),(76,57),(105,57)]:tree(x,y)
pave(66,49,9,2)
# Residential area: four houses above the park, three below, apartments on its sides.
house=patch('PalletTown','pallet_town_frlg',5,3,5,5)
for x in [73,83,93,103]:building('casa','residencial',x,65,house,door=1)
for x in [78,86,94]:building('casa','residencial',x,82,house,door=1)
for x in [71,100,108]:building('departamentos','residencial',x,74,apt)
pave(99,82,15,2)
# The third apartment is placed beside the eastern block; seven houses remain unchanged.
pave(77,73,22,1);pave(77,80,22,1);pave(77,73,1,8);pave(98,73,1,8)
flowerbed(80,75,4,1);flowerbed(91,78,4,1)
for x,y in [(80,76),(93,74)]:tree(x,y)
# South-west gym in a wooded enclosure with the L-shaped exit path in Sam's plan.
for x in range(4,58,2):tree(x,62)
for y in range(65,86,3):tree(4,y);tree(6,y)
for x in range(8,40,2):tree(x,83)
for y in range(65,80,3):tree(54,y);tree(56,y)
gym=patch('SaffronCity','saffron_city_frlg',43,8,7,5)
building('gimnasio','suroeste',13,72,gym)
pave(15,77,3,3);pave(15,78,29,3);pave(41,78,3,7);pave(41,83,26,2)
flowerbed(12,67,5,1);flowerbed(27,69,6,1)
# Plant the unbuilt margins without blocking or erasing any path.
for x,y in [(43,5),(45,17),(105,5),(108,23),(9,60),(47,60),(69,57),(112,33),(5,28)]:
    if grid[y][x]&1023==1 and all((xx,yy) not in occupied and grid[yy][xx]&1023==1 for yy in range(y,y+3) for xx in range(x,x+2)):tree(x,y)
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
