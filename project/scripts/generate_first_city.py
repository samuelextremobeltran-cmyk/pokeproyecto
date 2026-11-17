#!/usr/bin/env python3
"""Build the non-canon walking prototype from FRLG assets. Requires Pillow only to regenerate."""
from pathlib import Path
import json,struct
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
W,H=72,64
source=ROOT/'data/layouts/SaffronCity_Frlg/map.bin'
raw=source.read_bytes();original=list(struct.unpack('<%dH'%(len(raw)//2),raw))
def sample(x,y,w,h):return [[original[(y+j)*66+x+i] for i in range(w)] for j in range(h)]
def cell(n,blocked=False):return (n&1023)|0x3000|(0x400 if blocked else 0)
grid=[[cell(745) for x in range(W)] for y in range(H)]
def fill(x,y,w,h,n,blocked=False):
 for j in range(y,y+h):
  for i in range(x,x+w):grid[j][i]=cell(n,blocked)
def stamp(x,y,patch,blocked=None):
 for j,row in enumerate(patch):
  for i,v in enumerate(row):grid[y+j][x+i]=cell(v, bool(v&0xC00) if blocked is None else blocked)
def tree(x,y):stamp(x,y,[[14,15],[22,23],[30,31]],True)
# The city is enclosed: there are no links to the original region.
fill(0,0,W,H,1)
fill(4,4,W-8,H-8,745)
# Block the full rim even where the tree pattern has a gap at its edge.
fill(0,0,W,4,1,True);fill(0,H-4,W,4,1,True)
fill(0,0,4,H,1,True);fill(W-4,0,4,H,1,True)
for y in range(0,H-2,3):
 for x in range(0,W,2):
  if x<4 or x>=W-4 or y<3 or y>=H-4:tree(x,y)
# Raised flower islands divide the wide avenues.
for x in [21,44]:
 fill(x,7,3,13,1)
 for y in [8,11,14,17]:grid[y][x+1]=cell(4,True)
# Primary buildings: exactly 3 offices + 2 apartment complexes + 1 hotel + 3 services.
manifest={'prototype':True,'name':'Ciudad de prueba (nombre pendiente)','width':W,'height':H,'spawn':[27,34],'buildings':[],'park':[7,27,39,15]}
def building(kind,x,y,patch,label=None):
 stamp(x,y,patch,True)
 h=len(patch);w=len(patch[0]);manifest['buildings'].append({'kind':kind,'x':x,'y':y,'width':w,'height':h,'label':label,'approach':[x+w//2,y+h]})
 return w,h
tower=sample(29,16,9,15)
for i,x in enumerate([8,31,54],1):building('edificio',x,6,tower,f'OF.{i}')
# Two separately located residential compounds, each with two joined blocks.
apartments=sample(19,25,10,6)
building('departamentos',7,49,apartments,'APT.A')
building('departamentos',28,49,apartments,'APT.B')
# Hotel uses a shorter version of the same FRLG tower, not a third apartment compound.
hotel=tower[:6]+tower[10:]
building('hotel',53,46,hotel,'HOTEL')
building('gimnasio',54,27,sample(43,8,7,5))
building('centro_pokemon',50,36,sample(22,34,5,5))
building('tienda_azul',61,37,sample(38,18,4,4))
# Park: lawns, a four-way path, a pond and seating areas.
fill(7,27,39,15,1)
fill(7,33,39,3,217)
for x in range(7,46):grid[33][x]=cell(209);grid[35][x]=cell(225)
fill(25,27,3,15,217)
for y in range(27,42):grid[y][25]=cell(216);grid[y][27]=cell(218)
fill(25,33,3,3,217)
# Small ornamental pond with blocked banks: no Surf or interactions in this version.
for yy in range(28,32):
 for xx in range(11,20):grid[yy][xx]=cell(430,True)
for xx in range(11,20):
 grid[28][xx]=cell(421 if xx==11 else 423 if xx==19 else 422,True)
 grid[31][xx]=cell(437 if xx==11 else 439 if xx==19 else 438,True)
for yy in [29,30]:grid[yy][11]=cell(429,True);grid[yy][19]=cell(431,True)
for x,y in [(8,28),(21,28),(30,28),(42,28),(8,38),(21,38),(30,38),(42,38)]:tree(x,y)
for x in range(10,44,4):grid[40][x]=cell(4,True)
for x,y in [(31,31),(39,31),(12,37),(18,37)]:
 # Existing FRLG bench artwork.
 stamp(x,y,[[781,782]],True)
# Decorative lawns along the residential promenade.
for x in [7,28]:
 fill(x,57,10,2,1)
 for k in [1,4,7]:grid[57][x+k]=cell(4,True)
# Labels are rasterized into extra tiles; all architectural graphics remain FRLG assets.
secondary=ROOT/'data/tilesets/secondary/prototype_city_frlg';secondary.mkdir(parents=True,exist_ok=True)
saffron=ROOT/'data/tilesets/secondary/saffron_city_frlg'
im=Image.open(saffron/'tiles.png')
tiles=[im.crop((x,y,x+8,y+8)) for y in range(0,im.height,8) for x in range(0,im.width,8)]
metas=bytearray((saffron/'metatiles.bin').read_bytes());attrs=bytearray((saffron/'metatile_attributes.bin').read_bytes())
# Reflect the existing top bank to produce a clean bottom bank without new artwork.
primary=ROOT/'data/tilesets/primary/general_frlg'
primary_metas=(primary/'metatiles.bin').read_bytes()
primary_attrs=(primary/'metatile_attributes.bin').read_bytes()
pond_bottom=[]
for source_id in [421,422,423]:
 ids=list(struct.unpack_from('<8H',primary_metas,source_id*16))
 reflected=[ids[i]^0x800 for i in [2,3,0,1,6,7,4,5]]
 pond_bottom.append(640+len(metas)//16)
 metas.extend(struct.pack('<8H',*reflected));attrs.extend(primary_attrs[source_id*4:source_id*4+4])
for xx in range(11,20):grid[31][xx]=cell(pond_bottom[0] if xx==11 else pond_bottom[2] if xx==19 else pond_bottom[1],True)
font=ImageFont.load_default(size=10)
for b in manifest['buildings']:
 if not b['label']:continue
 sign=Image.new('P',(48,16),1);d=ImageDraw.Draw(sign)
 d.rectangle((0,0,47,15),outline=7,width=1);d.line((1,14,46,14),fill=4)
 text=b['label'];box=d.textbbox((0,0),text,font=font);tx=(48-(box[2]-box[0]))//2
 d.text((tx,1),text,font=font,fill=7,stroke_width=0)
 # Use primary palette 2: light background and blue-gray lettering.
 for col in range(3):
  ids=[]
  for ty in range(2):
   for tx2 in range(2):
    tile=sign.crop((col*16+tx2*8,ty*8,col*16+tx2*8+8,ty*8+8))
    ids.append((640+len(tiles))|(2<<12));tiles.append(tile)
  meta_id=640+len(metas)//16
  metas.extend(struct.pack('<8H',*(ids+ids)));attrs.extend(struct.pack('<I',0))
  # Mounted just above the lobby entrance, not a text interaction.
  grid[b['y']+b['height']-3][b['x']+3+col]=cell(meta_id,True)
assert len(tiles)<=384,'Secondary tile limit exceeded'
out=Image.new('P',(128,((len(tiles)+15)//16)*8));out.putpalette(im.getpalette())
for i,t in enumerate(tiles):out.paste(t,((i%16)*8,(i//16)*8))
out.save(secondary/'tiles.png');(secondary/'metatiles.bin').write_bytes(metas);(secondary/'metatile_attributes.bin').write_bytes(attrs)
layout=ROOT/'data/layouts/PrototypeCity_Frlg';layout.mkdir(parents=True,exist_ok=True)
(layout/'map.bin').write_bytes(struct.pack('<%dH'%(W*H),*(v for row in grid for v in row)))
(layout/'border.bin').write_bytes(struct.pack('<4H',*(cell(v,True) for v in [20,21,28,29])))
(ROOT/'project/prototypes/first_city.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print(f'Generated {W}x{H} city, {len(manifest["buildings"])} buildings, {len(tiles)} secondary tiles.')
