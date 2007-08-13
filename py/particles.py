Particles_RemoveGroupWithGravity = """
mov   em0,x           
rot   (0;1),em2.0,a0      
mul   a0,em1.0,v         
rnd   -0.1,0.1,a
rot   v,a,v

indep

updateonly

mul   em3,dt,a0   
add   a0,v,v
mul   v,dt,a0         ; a0 = dx
add   x,a0,x          ; x = x + dx
"""


Particles_RemoveTokenProgram = """
; ---------------------
; setup particle

mov   em0,x           ; using source point

; randomize particle speed
;em4 = 50;60 initial speed
rnd   em4.0,em4.1,v.1 
neg   v.1,v.1
;em5 = -1;1 direction
rnd   -0.1,0.1,a
rot   v,a,v

; mark particle as independed
indep

; --------------------
; update code follow

updateonly 

mul   em4,dt,a0   
add   a0,v,v
mul   v,dt,a0         ; a0 = dx
;rnd   0.95,1.05,a     ;random direction change
;mul   a0,a,a0
add   x,a0,x          ; x = x + dx

; update particle transparency
;rnd   20,30,a 
;mul   a,dt,a
;add   trans,a,trans 
"""

Particles_RemoveTokenProgram1 = """
;!PSP,1.0

; $Id$
; Copyright (c) MoleStudio.com, 2003, Alexey Chen (hedgehog@molestudio.com)
; default particles program

; em0  source x,y
; em1  angle
; em2  trans
; em3  frno
; em4  speed
; em5  direct
; em6  area
; em7  scale
; em8  inc angle
; em9  inc trans
; em10 inc scale
; em11 gravity

; ---------------------
; setup particle

mov   em0,x           ; using source point
rnd   -1, 1, a        ; randomize direction
rot   (0;1),a,a0      ; 
rnd   em6.0,em6.1,a   ; randomize area
mul   a0,a,a0         ; 
add   x,a0,x          ; set particle x

; randomize particle attributes
rnd   em1.0,em1.1,angle 
rnd   em2.0,em2.1,trans
rnd   em3.0,em3.1,frno
rnd   em7.0,em7.1,scale

; randomize particle speed
rnd   em4.0,em4.1,v.1 
neg   v.1,v.1
rnd   em5.0,em5.1,a
rot   v,a,v

; mark particle as independed
indep

; --------------------
; update code follow

updateonly 

mul   (0;100),dt,a0
add   a0,v,v
mul   v,dt,a0         ; a0 = dx
add   x,a0,x          ; x = x + dx

; update particle attributes
rnd   em9.0,em9.1,a 
mul   a,dt,a
add   trans,a,trans 
;rnd   em10.0,em10.1,a ; no scale
;mul   a,dt,a
;add   scale,a,scale 
;rnd   em8.0,em8.1,a ; no rotation
;mul   a,dt,a
;add   angle,a,angle
"""
