#!/usr/bin/env python3
"""Rich industrial warehouse for Gazebo Classic 11. Writes warehouse.world
next to this script. Driving aisle (|y|<=4.5) stays clear; the only in-path
obstacles are PEOPLE (YOLO-detectable). Everything else is side scenery so the
camera-only robot never collides with things it cannot see."""
import os

FX, FY = 84.0, 36.0
HX, HY = FX/2.0, FY/2.0
WALL_H, WALL_T = 5.0, 0.3

def smat(name):
    return ('<material><script><uri>file://media/materials/scripts/gazebo.material</uri>'
            '<name>%s</name></script></material>' % name)
def cmat(rgba):
    r,g,b,a = rgba.split()
    return ('<material><ambient>%s %s %s %s</ambient><diffuse>%s %s %s %s</diffuse>'
            '<specular>0.1 0.1 0.1 1</specular></material>' % (r,g,b,a,r,g,b,a))

def box(name,x,y,z,sx,sy,sz,mat,col=True):
    c = ('<collision name="c"><geometry><box><size>%s %s %s</size></box></geometry></collision>'%(sx,sy,sz)) if col else ''
    return ('<model name="%s"><static>true</static><pose>%s %s %s 0 0 0</pose><link name="link">%s'
            '<visual name="v"><geometry><box><size>%s %s %s</size></box></geometry>%s</visual></link></model>'
            %(name,x,y,z,c,sx,sy,sz,mat))

def cyl(name,x,y,z,rad,h,mat):
    return ('<model name="%s"><static>true</static><pose>%s %s %s 0 0 0</pose><link name="link">'
            '<collision name="c"><geometry><cylinder><radius>%s</radius><length>%s</length></cylinder></geometry></collision>'
            '<visual name="v"><geometry><cylinder><radius>%s</radius><length>%s</length></cylinder></geometry>%s</visual>'
            '</link></model>'%(name,x,y,z,rad,h,rad,h,mat))

def rack(name,cx,cy,length=4.0,depth=2.0,height=3.2,yaw=0.0):
    post=0.12; frame=cmat("0.10 0.25 0.75 1"); shelf=cmat("0.55 0.55 0.58 1"); pal=cmat("0.55 0.40 0.25 1")
    hx,hy=length/2.0,depth/2.0; L=[]
    for sx_ in (-hx+post,hx-post):
        for sy_ in (-hy+post,hy-post):
            L.append('<visual name="p%s_%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>%s %s %s</size></box></geometry>%s</visual>'
                     '<collision name="pc%s_%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>%s %s %s</size></box></geometry></collision>'
                     %(sx_,sy_,sx_,sy_,height/2,post,post,height,frame,sx_,sy_,sx_,sy_,height/2,post,post,height))
    for z in (0.6,1.5,2.4):
        L.append('<visual name="s%s"><pose>0 0 %s 0 0 0</pose><geometry><box><size>%s %s 0.06</size></box></geometry>%s</visual>'
                 '<collision name="sc%s"><pose>0 0 %s 0 0 0</pose><geometry><box><size>%s %s 0.06</size></box></geometry></collision>'
                 %(z,z,length,depth,shelf,z,z,length,depth))
    for i,(bx,z) in enumerate([(-1.1,0.95),(1.1,0.95),(0.0,1.85),(-1.0,2.75),(1.0,2.75)]):
        L.append('<visual name="b%s"><pose>%s 0 %s 0 0 0</pose><geometry><box><size>1.0 1.2 0.7</size></box></geometry>%s</visual>'%(i,bx,z,pal))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 %s</pose><link name="link">%s</link></model>'%(name,cx,cy,yaw,"".join(L))

def pallet(name,x,y):
    woodmat=cmat("0.50 0.36 0.22 1"); cb=cmat("0.62 0.47 0.30 1"); L=[]
    L.append('<visual name="pl"><pose>0 0 0.08 0 0 0</pose><geometry><box><size>1.2 1.0 0.16</size></box></geometry>%s</visual>'
             '<collision name="plc"><pose>0 0 0.08 0 0 0</pose><geometry><box><size>1.2 1.0 0.16</size></box></geometry></collision>'%woodmat)
    for i,(bx,by,bz) in enumerate([(-0.25,0,0.55),(0.30,0,0.55),(0,0,1.15)]):
        L.append('<visual name="c%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>0.55 0.8 0.55</size></box></geometry>%s</visual>'%(i,bx,by,bz,cb))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 0</pose><link name="link">%s</link></model>'%(name,x,y,"".join(L))

def forklift(name,x,y,yaw=0.0):
    body=cmat("0.95 0.55 0.05 1"); blk=cmat("0.1 0.1 0.1 1"); mast=cmat("0.3 0.3 0.32 1"); L=[]
    L.append('<visual name="bd"><pose>0 0 0.5 0 0 0</pose><geometry><box><size>1.6 1.0 0.8</size></box></geometry>%s</visual>'
             '<collision name="bdc"><pose>0 0 0.5 0 0 0</pose><geometry><box><size>1.6 1.0 0.8</size></box></geometry></collision>'%body)
    L.append('<visual name="cab"><pose>-0.2 0 1.3 0 0 0</pose><geometry><box><size>0.8 0.9 0.8</size></box></geometry>%s</visual>'%body)
    L.append('<visual name="mast"><pose>0.85 0 1.0 0 0 0</pose><geometry><box><size>0.12 0.9 2.0</size></box></geometry>%s</visual>'%mast)
    L.append('<visual name="forkL"><pose>1.2 -0.3 0.1 0 0 0</pose><geometry><box><size>0.9 0.12 0.08</size></box></geometry>%s</visual>'%blk)
    L.append('<visual name="forkR"><pose>1.2 0.3 0.1 0 0 0</pose><geometry><box><size>0.9 0.12 0.08</size></box></geometry>%s</visual>'%blk)
    for i,(wx,wy) in enumerate([(0.6,0.55),(0.6,-0.55),(-0.6,0.55),(-0.6,-0.55)]):
        L.append('<visual name="w%s"><pose>%s %s 0.25 1.5708 0 0</pose><geometry><cylinder><radius>0.25</radius><length>0.2</length></cylinder></geometry>%s</visual>'%(i,wx,wy,blk))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 %s</pose><link name="link">%s</link></model>'%(name,x,y,yaw,"".join(L))

def crate_stack(name,x,y):
    w=cmat("0.45 0.32 0.20 1"); L=[]
    for i,(bx,by,bz) in enumerate([(0,0,0.5),(0,0,1.5),(0.5,0.4,2.4)]):
        L.append('<visual name="cr%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>1.0 1.0 1.0</size></box></geometry>%s</visual>'
                 '<collision name="crc%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>1.0 1.0 1.0</size></box></geometry></collision>'
                 %(i,bx,by,bz,w,i,bx,by,bz))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 0</pose><link name="link">%s</link></model>'%(name,x,y,"".join(L))

def obstacle(name,x,y,color):
    # bright stacked crates placed IN the lane as object obstacles (YOLO-detectable)
    m=cmat(color); L=[]
    for i,(bz,sz) in enumerate([(0.45,0.9),(1.15,0.5)]):
        L.append('<visual name="o%s"><pose>0 0 %s 0 0 0</pose><geometry><box><size>0.9 0.9 %s</size></box></geometry>%s</visual>'
                 '<collision name="oc%s"><pose>0 0 %s 0 0 0</pose><geometry><box><size>0.9 0.9 %s</size></box></geometry></collision>'
                 %(i,bz,sz,m,i,bz,sz))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 0</pose><link name="link">%s</link></model>'%(name,x,y,"".join(L))

def person(name,x,y,yaw=0.0):
    return '<include><name>%s</name><uri>model://person_standing</uri><pose>%s %s 0 0 0 %s</pose></include>'%(name,x,y,yaw)

def pallet_jack(name,x,y,yaw=0.0):
    steel=cmat("0.85 0.35 0.05 1"); blk=cmat("0.08 0.08 0.08 1"); L=[]
    L.append('<visual name="body"><pose>0 0 0.12 0 0 0</pose><geometry><box><size>1.4 0.55 0.15</size></box></geometry>%s</visual>'
              '<collision name="bc"><pose>0 0 0.12 0 0 0</pose><geometry><box><size>1.4 0.55 0.15</size></box></geometry></collision>'%steel)
    L.append('<visual name="handle"><pose>-0.75 0 0.55 0 0.5 0</pose><geometry><box><size>0.06 0.5 0.9</size></box></geometry>%s</visual>'%blk)
    for i,(wx,wy) in enumerate([(0.55,0.2),(0.55,-0.2)]):
        L.append('<visual name="w%s"><pose>%s %s 0.06 1.5708 0 0</pose><geometry><cylinder><radius>0.06</radius><length>0.08</length></cylinder></geometry>%s</visual>'%(i,wx,wy,blk))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 %s</pose><link name="link">%s</link></model>'%(name,x,y,yaw,"".join(L))

def cone(name,x,y):
    return cyl(name,x,y,0.25,0.18,0.5,cmat("0.95 0.35 0.05 1"))

def box_pile(name,x,y):
    w=cmat("0.60 0.46 0.30 1"); L=[]
    for i,(bx,by,bz,s) in enumerate([(0,0,0.25,0.5),(0.2,0.15,0.65,0.35),(-0.15,-0.1,0.6,0.3)]):
        L.append('<visual name="b%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>%s %s %s</size></box></geometry>%s</visual>'
                 '<collision name="bc%s"><pose>%s %s %s 0 0 0</pose><geometry><box><size>%s %s %s</size></box></geometry></collision>'
                 %(i,bx,by,bz,s,s,s,w,i,bx,by,bz,s,s,s))
    return '<model name="%s"><static>true</static><pose>%s %s 0 0 0 0</pose><link name="link">%s</link></model>'%(name,x,y,"".join(L))

def cross_aisle_sign(name,x,y):
    return '<model name="%s"><static>true</static><pose>%s %s 1.8 0 0 0</pose><link name="link">' \
           '<visual name="v"><geometry><box><size>0.06 1.4 0.5</size></box></geometry>%s</visual></link></model>' \
           % (name,x,y,cmat("0.05 0.55 0.15 1"))

p=[]
# Floor + walls
p.append(box("floor",0,0,-0.05,FX,FY,0.1,smat("Gazebo/Grey"),col=False))
wm=smat("Gazebo/Grey")
p.append(box("wall_n",HX,0,WALL_H/2,WALL_T,FY,WALL_H,wm))
p.append(box("wall_s",-HX,0,WALL_H/2,WALL_T,FY,WALL_H,wm))
GAP = 6.0
BAY_DEPTH = 26.0
seg_len = (FX - GAP)/2.0
seg_off = GAP/2.0 + seg_len/2.0
p.append(box("wall_e_a", -seg_off, HY, WALL_H/2, seg_len, WALL_T, WALL_H, wm))
p.append(box("wall_e_b",  seg_off, HY, WALL_H/2, seg_len, WALL_T, WALL_H, wm))
p.append(box("wall_w_a", -seg_off,-HY, WALL_H/2, seg_len, WALL_T, WALL_H, wm))
p.append(box("wall_w_b",  seg_off,-HY, WALL_H/2, seg_len, WALL_T, WALL_H, wm))
# Side bays (real rooms) through the wall gaps -> actual LEFT / RIGHT paths
p.append(box("bay_e_floor", 0, HY+BAY_DEPTH/2, -0.05, GAP, BAY_DEPTH, 0.1, smat("Gazebo/Grey"), col=False))
p.append(box("bay_e_far",   0, HY+BAY_DEPTH,   WALL_H/2, GAP, WALL_T, WALL_H, wm))
p.append(box("bay_e_l",    -GAP/2, HY+BAY_DEPTH/2, WALL_H/2, WALL_T, BAY_DEPTH, WALL_H, wm))
p.append(box("bay_e_r",     GAP/2, HY+BAY_DEPTH/2, WALL_H/2, WALL_T, BAY_DEPTH, WALL_H, wm))
p.append(box("bay_w_floor", 0,-(HY+BAY_DEPTH/2), -0.05, GAP, BAY_DEPTH, 0.1, smat("Gazebo/Grey"), col=False))
p.append(box("bay_w_far",   0,-(HY+BAY_DEPTH),   WALL_H/2, GAP, WALL_T, WALL_H, wm))
p.append(box("bay_w_l",    -GAP/2,-(HY+BAY_DEPTH/2), WALL_H/2, WALL_T, BAY_DEPTH, WALL_H, wm))
p.append(box("bay_w_r",     GAP/2,-(HY+BAY_DEPTH/2), WALL_H/2, WALL_T, BAY_DEPTH, WALL_H, wm))

# ---- Outfit both side corridors like real aisles (flanking racks rotated
# 90 deg, inset from the corridor walls; three modules per side per bay) ----
for i,off in enumerate((5.0,13.0,21.0)):
    p.append(rack("bayL_rackL%d"%i, -1.9,  HY+off, depth=1.4, yaw=1.5708))
    p.append(rack("bayL_rackR%d"%i,  1.9,  HY+off, depth=1.4, yaw=1.5708))
    p.append(rack("bayR_rackL%d"%i, -1.9, -(HY+off), depth=1.4, yaw=1.5708))
    p.append(rack("bayR_rackR%d"%i,  1.9, -(HY+off), depth=1.4, yaw=1.5708))
# End-zone floor markers -> each side path clearly leads somewhere distinct
p.append(box("zoneB_pad", 0,  HY+BAY_DEPTH-2.0, 0.015, GAP-1.0, 3.0, 0.02, cmat("0.10 0.35 0.75 1"), col=False))
p.append(box("zoneC_pad", 0,-(HY+BAY_DEPTH-2.0), 0.015, GAP-1.0, 3.0, 0.02, cmat("0.85 0.35 0.05 1"), col=False))
# Extra lighting so both corridors are lit along their full length
p.append(f'<light name="bayL_light" type="point"><pose>0 {HY+BAY_DEPTH/2} 7 0 0 0</pose>'
         '<diffuse>0.7 0.7 0.7 1</diffuse><attenuation><range>40</range><linear>0.04</linear>'
         '<constant>0.3</constant></attenuation><cast_shadows>false</cast_shadows></light>')
p.append(f'<light name="bayR_light" type="point"><pose>0 -{HY+BAY_DEPTH/2} 7 0 0 0</pose>'
         '<diffuse>0.7 0.7 0.7 1</diffuse><attenuation><range>40</range><linear>0.04</linear>'
         '<constant>0.3</constant></attenuation><cast_shadows>false</cast_shadows></light>')
# Loading-dock doors on the north (goal-end) wall
for i,yy in enumerate([-9,-3,3,9]):
    p.append(box("dock%d"%i,HX-0.2,yy,1.6,0.1,4.0,3.2,cmat("0.20 0.22 0.28 1"),col=False))
# Inner racks y=+/-6 and outer racks y=+/-10
for i,sx in enumerate([-28,-20,-12,-4,4,12,20,28]):
    p.append(rack("rackLi%d"%i,sx,7.5)); p.append(rack("rackRi%d"%i,sx,-7.5))
for i,sx in enumerate([-28,-20,-12,-4,4,12,20,28]):
    p.append(rack("rackLo%d"%i,sx,11.5)); p.append(rack("rackRo%d"%i,sx,-11.5))
# Pallets lined along the aisle edge (still outside the driving corridor)
for i,sx in enumerate([-26,-18,-10,-2,6,14,22]):
    p.append(pallet("palL%d"%i,sx,6.0)); p.append(pallet("palR%d"%i,sx,-6.0))
# Barrels between rack rows
bcols=["0.85 0.15 0.1 1","0.1 0.35 0.8 1","0.2 0.6 0.2 1"]
for i,sx in enumerate([-17,-9,-1,7,15]):
    p.append(cyl("barL%d"%i,sx,9.3,0.45,0.45,0.9,cmat(bcols[i%3])))
    p.append(cyl("barR%d"%i,sx,-9.3,0.45,0.45,0.9,cmat(bcols[(i+1)%3])))
# Forklifts parked off to the side
p.append(forklift("fork1",-22,9.5,0.3))
p.append(forklift("fork2", 18,-9.5,3.0))
# Crate stacks in the corners
p.append(crate_stack("crate1",-39,14)); p.append(crate_stack("crate2",39,14))
p.append(crate_stack("crate3",-39,-14)); p.append(crate_stack("crate4",39,-14))
# Ceiling light fixtures (visual only)
for i,sx in enumerate([-28,-20,-12,-4,4,12,20,28]):
    p.append(box("fix%d"%i,sx,0,4.7,1.0,0.3,0.15,cmat("0.95 0.95 0.8 1"),col=False))
# Hazard lane lines down the aisle
yl=cmat("0.95 0.80 0.05 1")
p.append(box("laneL",0,2.0,0.02,62,0.16,0.02,yl,col=False))
p.append(box("laneR",0,-2.0,0.02,62,0.16,0.02,yl,col=False))
# Wall signage panels
p.append(box("signA",-HX+0.2,8,2.5,0.05,3,1.2,cmat("0.9 0.2 0.2 1"),col=False))
p.append(box("signB",-HX+0.2,-8,2.5,0.05,3,1.2,cmat("0.2 0.5 0.9 1"),col=False))

# ---- Busy-warehouse clutter: all placed at |y|>=5, well clear of the
# robot's tested main-path obstacle sequence (main path stays |y|<=3). ----
for i,(px,py,yaw) in enumerate([(-22,9.6,0.4),(-6,-9.6,1.0),(10,9.6,-0.3),(26,-9.6,0.8)]):
    p.append(pallet_jack("jack%d"%i, px, py, yaw))
for i,(cx,cy) in enumerate([(-14,-6.0),(-14,6.0),(14,-6.0),(14,6.0),(30,6.0)]):
    p.append(cone("cone%d"%i, cx, cy))
for i,(bx,by) in enumerate([(-24,13.5),(-8,13.5),(8,-13.5),(24,-13.5),(32,13.5)]):
    p.append(box_pile("pile%d"%i, bx, by))
# Extra background workers, off to the side (decorative only, not in the
# tested obstacle sequence -> won't affect navigation testing)
p.append(person("worker_1", -18.0,  9.5, 1.2))
p.append(person("worker_2",   2.0, -9.5, -1.2))
p.append(person("worker_3",  18.0,  9.5, 0.6))
p.append(person("worker_4",  -2.0, 13.5, 2.0))
# Cross-aisle markers: the racks already leave ~4m gaps every 8m (real
# warehouses use these as fire/access cross-aisles) -- flag a few clearly.
for gx in (-24, -8, 8, 24):
    p.append(cross_aisle_sign("crossaisle_%d"%(gx), gx, 7.5))
    p.append(cross_aisle_sign("crossaisle2_%d"%(gx), gx, -7.5))

# ---- JUNCTION at x = 0 (natural gap: no rack row is placed at x=0) ----
p.append(box("junction_lane_ns", 0, 0, 0.025, 0.16, 2*(HY+BAY_DEPTH)-1.0, 0.03, yl, col=False))   # N-S cross lane
p.append(box("junction_pad",     0, 0, 0.015, 3.0, 3.0, 0.02, cmat("0.35 0.38 0.42 1"), col=False))  # highlighted pad
p.append(box("junction_signL", -1.6, HY-1.0, 2.2, 0.08, 1.6, 1.0, cmat("0.95 0.75 0.05 1"), col=False))
p.append(box("junction_signR",  1.6,-HY+1.0, 2.2, 0.08, 1.6, 1.0, cmat("0.95 0.75 0.05 1"), col=False))


# ---- People + object obstacles: all AHEAD of the robot's spawn (x=-16),
# 6m lead before the first one, consistent 6m gaps, junction (x in [-3,3])
# kept clear, and a safe buffer before the goal. Two are placed dead-CENTER
# to force a genuine slow/avoid/reverse response, not just side-swerving. ----
p.append(obstacle("obs_1",  -10.0, -3.0, "0.95 0.45 0.05 1"))  # orange (-y)
p.append(person("person_1",  -4.0,  3.0, 0.0))                 # (+y)
# ---- junction zone x in [-3, 3] kept clear ----
p.append(obstacle("obs_2",    4.0,  0.0, "0.90 0.10 0.10 1"))  # red    CENTER (direct-path test)
p.append(person("person_2",  10.0, -3.0, 1.57))                # (-y)
p.append(obstacle("obs_3",   16.0,  3.0, "0.10 0.45 0.90 1"))  # blue   (+y)
p.append(obstacle("obs_4",   22.0,  0.0, "0.95 0.80 0.05 1"))  # yellow CENTER (direct-path test)
p.append(person("person_3",  28.0, -3.0, 0.0))                 # (-y)
p.append(obstacle("obs_5",   34.0,  3.0, "0.55 0.10 0.75 1"))  # purple (+y)


p.append('<model name="goal_marker"><static>true</static><pose>40 0 0.6 0 0 0</pose>'
         '<link name="link"><visual name="v"><geometry><cylinder><radius>0.4</radius>'
         '<length>1.2</length></cylinder></geometry>%s</visual></link></model>'%cmat("0.0 0.9 0.1 1"))

body="\n    ".join(p)
world=('<?xml version="1.0" ?>\n<sdf version="1.6">\n  <world name="warehouse">\n'
 '    <include><uri>model://sun</uri></include>\n'
 '    <include><uri>model://ground_plane</uri></include>\n'
 '    <light name="dir1" type="directional"><pose>0 0 12 0 0 0</pose><diffuse>0.9 0.9 0.9 1</diffuse>'
 '<specular>0.2 0.2 0.2 1</specular><direction>-0.3 0.2 -1</direction><cast_shadows>true</cast_shadows></light>\n'
 '    <light name="bay1" type="point"><pose>-12 0 8 0 0 0</pose><diffuse>0.7 0.7 0.7 1</diffuse>'
 '<attenuation><range>45</range><linear>0.03</linear><constant>0.3</constant></attenuation><cast_shadows>false</cast_shadows></light>\n'
 '    <light name="bay2" type="point"><pose>0 0 8 0 0 0</pose><diffuse>0.7 0.7 0.7 1</diffuse>'
 '<attenuation><range>45</range><linear>0.03</linear><constant>0.3</constant></attenuation><cast_shadows>false</cast_shadows></light>\n'
 '    <light name="bay3" type="point"><pose>12 0 8 0 0 0</pose><diffuse>0.7 0.7 0.7 1</diffuse>'
 '<attenuation><range>45</range><linear>0.03</linear><constant>0.3</constant></attenuation><cast_shadows>false</cast_shadows></light>\n'
 '    <scene><ambient>0.55 0.55 0.55 1</ambient><background>0.72 0.76 0.82 1</background><shadows>true</shadows></scene>\n'
 '    '+body+'\n'
 '    <physics name="dp" default="0" type="ode"><max_step_size>0.001</max_step_size>'
 '<real_time_factor>1.0</real_time_factor><real_time_update_rate>1000</real_time_update_rate></physics>\n'
 '  </world>\n</sdf>\n')
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"warehouse.world")
open(out,"w").write(world)
print("WROTE:",out,"(%d bytes)"%len(world))
