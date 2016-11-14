#!/usr/bin/env python
"""/
Python program to read coordinates from a file and handle them. Daniele Ongari 7/11/16

inputfilename          name of the input filename.inpformat
inputformat	       input format

natoms                 number of atoms
ntypes                 number of different atom types
ABC[012]               A B C in angstrom
abc[012]               alpha,beta,gamma in radians
cell(3x3)              unit cell matrix in angstrom


  atom[index]          atomic name
    an[index]          atomic number
   xyz[index][x,y,z]   cartesian coordinates in angstrom
 fract[index][x,y,z]   fractional coordinates
charge[index]          partial charge

"""

import string,sys
import numpy
import math
import subprocess

############################################################################# HELP 
if sys.argv[1]=='-h' or sys.argv[1]=='-help' or sys.argv[1]=='help':
        print
        print '####################################################################################'
	print '#  Python program to read coordinates from a file and handle them:'
	print '#'
	print '#  $ %s inputfile.xxx outputfile.yyy z' % (sys.argv[0])
	print '#  $ %s inputfile.xxx info'             % (sys.argv[0])  
	print '#'
	print '#  xxx=xyz(CELL),pdb,cssr,pwi,pwo    (next: cp2k-restart, xsf,gaussian, dcd+atoms)'
	print '#  yyy=cif,pdb,cssr,xyz(CELL),pwi,cp2k'
	print '#  z=f,l (for the first or the last coordinate in a dcd or pwo or axsf or log)'
	print '#  z=pbe, pbesol (pseudo for pwi output)'
        print '####################################################################################'
	print
	sys.exit()

############################################################################# STANDARD INFOS about the periodic table: atomic_ symbol/name/vdw/mass
from atomic_data import *         #import all the data stored in the file atom_data.py

atom_count=[0]*119 #anything assigned to 0, H_index=1, He_index=2, ...

############################################################################## INPUT

#reading input file: name and format
inputfilename = sys.argv[1].split(".")[0]
inputformat= sys.argv[1].split(".")[1]
file = open('./'+inputfilename+'.'+inputformat,'r')

if inputformat=='dcd':
	from pwtools import dcd
	cc,co = dcd.read_dcd_data('./'+inputfilename+'.'+inputformat, convang=False) #convang=True usefull to read LAMMPS data, because it converts angles from cosine to degree
	ABC=[ cc[-1][0], cc[-1][1], cc[-1][2] ]
	abc=[ math.acos(cc[-1][3]), math.acos(cc[-1][4]), math.acos(cc[-1][5]) ]
	cell=numpy.matrix([[                 ABC[0],                    0.0,                                                                           0.0],
			   [ABC[1]*math.cos(abc[2]),ABC[1]*math.sin(abc[2]),                                                                           0.0],
			   [ABC[2]*math.cos(abc[1]),ABC[2]*math.cos(abc[0]),math.sqrt(ABC[2]**2-(ABC[2]*math.cos(abc[1]))**2-(ABC[2]*math.cos(abc[0]))**2)]]) 
	xyz=co[-1]
	file.close()
	user_input = raw_input("Give me a file with the atoms: ")
	file = open(user_input,'r')
	natoms=int(file.readlines()[0].split()[0])
	atom=[]
	an=[]
	#xyz=[]
	charge=[]
	file = open(user_input,'r')
	for i in range(0,natoms):
		line = file.readlines()[i+2]
		data = line.split()
		atom.append(data[0])	
		#an.append(atomic_symbol.index(atom[i]))
                #atom_count[an[i]]+=1
		an.append(1)
                atom_count[an[i]]+=1
		#xyz.append([float(data[1]), float(data[2]), float(data[3])])
		charge.append(0.000)                                               #fix

#if inputformat=='pwo':
#	pwo2scf=subprocess.call("which pwo2xsf", shell=True)
#	if sys.argv[3]=="f":
#		subprocess.call(pwoscf+"--inicoor    "+sys.argv[1]" > "inputfilename".xsf", shell=True)
#	elif sys.argv[3]=="l":
#		subprocess.call(pwoscf+"--latestcoor "+sys.argv[1]" > "inputfilename".xsf", shell=True)
#	else:
#		print "********* use f for first and l for last coordinate*****"
#	file.close()
#	file = open('./'+inputfilename+'.xsf','r')
#	#now the xsf file still need to be processed
	

#if inputformat=='xsf' or inputformat=='pwo':

if inputformat=='pdb':
	while True:
		line = file.readline()
		if line.split()[0]=='CRYST1':
			break
	ABC=[float(line[06:15]),float(line[15:24]),float(line[24:33])]
	abc=[math.radians(float(line[33:40])),math.radians(float(line[40:47])),math.radians(float(line[47:54]))]
	#read atom[index]
        atom=[]
        an=[]
        xyz=[]
        charge=[]
	i=0
        while True:
         line = file.readline()
	 data = line.split()
	 if len(data)==0:           #if the file is finished stop  
		break 			
 	 elif data[0]=='END':        #if the file says "END" 
		break
	 else:		
                data = line.split()
                atom.append(data[2])
                an.append(atomic_symbol.index(atom[i]))
                atom_count[an[i]]+=1
		xyz.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
                charge.append(0.000)
		i=i+1	
	 natoms=i

if inputformat=='cssr':
	line = file.readline()
 	celltemp=line.split( )
	ABC=[float(celltemp[0]),float(celltemp[1]),float(celltemp[2])]
	line = file.readline()
 	celltemp=line.split( )
	abc=[math.radians(float(celltemp[0])),math.radians(float(celltemp[1])),math.radians(float( celltemp[2]))]
	line = file.readline()
        natoms=int(line.split( )[0])
        line = file.readline() 
        atom=[]
        an=[]
        fract=[]
        charge=[]
	i=0
	for i in range(0,natoms):
		line = file.readline()
		data = line.split( )
		atom.append(data[1])	
		an.append(atomic_symbol.index(atom[i]))
                atom_count[an[i]]+=1
		fract.append([float(data[2]), float(data[3]), float(data[4])])
		charge.append(0.000)

if inputformat=='xyz':
	#read number of atoms
	line = file.readline()
	natoms=int(line.split( )[0])

	#read cell in my way of writing it as a comment of xyz
	line = file.readline()
	celltemp=line.split( )
	#debug: celltemp=['cell:',1,2,3,4,5,6,7,8,9,10,11]

	if celltemp[0]=='CELL:' or celltemp[0]=='CELL':
		ABC=[float( celltemp[1]),float(celltemp[2]),float(celltemp[3])]
		abc=[math.radians(float(celltemp[4])),math.radians(float(celltemp[5])),math.radians(float( celltemp[6]))]

	elif celltemp[0]=='cell:' or celltemp[0]=='cell':
		cell=numpy.matrix([[float(celltemp[1]),float(celltemp[2]),float(celltemp[3])],
		                   [float(celltemp[4]),float(celltemp[5]),float(celltemp[6])],
		                   [float(celltemp[7]),float(celltemp[8]),float(celltemp[9])]])
	#read atom[index]
	atom=[]
	an=[]
	xyz=[]
	charge=[]
	for i in range(0,natoms):
		line = file.readline()
		data = line.split( )
		atom.append(data[0])	
		an.append(atomic_symbol.index(atom[i]))
                atom_count[an[i]]+=1
		xyz.append([float(data[1]), float(data[2]), float(data[3])])
		charge.append(0.000)

if inputformat=='pwo':
        #search for the last time the coordinates are printed and jump to that line
        lookup='CELL_PARAMETERS'             
        with file as myFile:
         for num, line in enumerate(myFile, 1):
           if lookup in line:
            coord_line=num
        file.close()
        file = open('./'+inputfilename+'.'+inputformat,'r')
        for i in range(0,coord_line):
	 skip = file.readline()
       
	#read cell 
	line = file.readline()
	celltempA=line.split( )
        line = file.readline()  
        celltempB=line.split( )
        line = file.readline()
        celltempC=line.split( )  
	cell=numpy.matrix([[float(celltempA[0]),float(celltempA[1]),float(celltempA[2])],
		           [float(celltempB[0]),float(celltempB[1]),float(celltempB[2])],
		           [float(celltempC[0]),float(celltempC[1]),float(celltempC[2])]])
        skip = file.readline().split()
        while len(skip)==0 or not skip[0]=='ATOMIC_POSITIONS':        
         skip = file.readline().split()

	#read atom[index]
	atom=[]
	an=[]
	xyz=[]
	charge=[]
        i=0
        while True:
         line = file.readline()
	 data = line.split()
	 if len(data)==0:           #if the file is finished stop  
		break 
	 else:
		atom.append(data[0])	
		an.append(atomic_symbol.index(atom[i]))
                atom_count[an[i]]+=1
		xyz.append([float(data[1]), float(data[2]), float(data[3])])
		charge.append(0.000)  
                i=i+1
        natoms=i

if inputformat=='pwi':
        #search for the last time the coordinates are printed and jump to that line
        lookup='CELL_PARAMETERS'             
        with file as myFile:
         for num, line in enumerate(myFile, 1):
           if lookup in line:
            coord_line=num
        file.close()
        file = open('./'+inputfilename+'.'+inputformat,'r')
        for i in range(0,coord_line):
	 skip = file.readline()
       
	#read cell 
	line = file.readline()
	celltempA=line.split( )
        line = file.readline()  
        celltempB=line.split( )
        line = file.readline()
        celltempC=line.split( )  
	cell=numpy.matrix([[float(celltempA[0]),float(celltempA[1]),float(celltempA[2])],
		           [float(celltempB[0]),float(celltempB[1]),float(celltempB[2])],
		           [float(celltempC[0]),float(celltempC[1]),float(celltempC[2])]])
        skip = file.readline().split()
        while len(skip)==0 or not skip[0]=='ATOMIC_POSITIONS':        
         skip = file.readline().split()

	#read atom[index]
	atom=[]
	an=[]
	xyz=[]
	charge=[]
        i=0
        while True:
         line = file.readline()
	 data = line.split()
	 if len(data)==0:           #if the file is finished stop  
		break 
	 else:
		atom.append(data[0])	
		an.append(atomic_symbol.index(atom[i]))
                atom_count[an[i]]+=1
		xyz.append([float(data[1]), float(data[2]), float(data[3])])
		charge.append(0.000)  
                i=i+1
        natoms=i
############################################################################# DO SOMETHING
#check if xyz are really cartesian (angstrom) and if fract are really fractional coordinates.

if 'cell' in locals():   #make uc ABC+abc if it was read in cell
  print
  print " ...converting cell (matrix) to CELL (ABCabc)"
  ABC=[0]*3
  abc=[0]*3
  ABC[0]= math.sqrt(cell.item((0,0))*cell.item((0,0))+cell.item((0,1))*cell.item((0,1))+cell.item((0,2))*cell.item((0,2)) )
  ABC[1]= math.sqrt(cell.item((1,0))*cell.item((1,0))+cell.item((1,1))*cell.item((1,1))+cell.item((1,2))*cell.item((1,2)) )
  ABC[2]= math.sqrt(cell.item((2,0))*cell.item((2,0))+cell.item((2,1))*cell.item((2,1))+cell.item((2,2))*cell.item((2,2)) )
  abc[0]= math.acos( (cell.item((1,0))*cell.item((2,0))+cell.item((1,1))*cell.item((2,1))+cell.item((1,2))*cell.item((2,2)))/ABC[1]/ABC[2] ) #alpha=B^C
  abc[1]= math.acos( (cell.item((0,0))*cell.item((2,0))+cell.item((0,1))*cell.item((2,1))+cell.item((0,2))*cell.item((2,2)))/ABC[0]/ABC[2] ) #beta=A^C
  abc[2]= math.acos( (cell.item((0,0))*cell.item((1,0))+cell.item((0,1))*cell.item((1,1))+cell.item((0,2))*cell.item((1,2)))/ABC[0]/ABC[1] ) #gamma=A^B

elif 'ABC' in locals():  #make uc matrix if it was read in ABC+abc
  print
  print " ...converting CELL (ABCabc) to cell (matrix) "
  cell=numpy.matrix([[                ABC[0],                     0.0,                                                                           0.0],
		     [ABC[1]*math.cos(abc[2]),ABC[1]*math.sin(abc[2]),                                                                           0.0],
		     [ABC[2]*math.cos(abc[1]),ABC[2]*math.cos(abc[0]),math.sqrt(ABC[2]**2-(ABC[2]*math.cos(abc[1]))**2-(ABC[2]*math.cos(abc[0]))**2)]]) #check this part



if 'fract' in locals(): #convert in cartesian
  print
  print " ...converting fractional coordinates in cartesian"
  xyz=[] 
  for i in range(0,natoms):
	x=fract[i][0]*cell.item((0,0))+fract[i][1]*cell.item((1,0))+fract[i][2]*cell.item((2,0))
	y=fract[i][1]*cell.item((0,1))+fract[i][1]*cell.item((1,1))+fract[i][2]*cell.item((2,1))
	z=fract[i][2]*cell.item((0,2))+fract[i][1]*cell.item((1,2))+fract[i][2]*cell.item((2,2))
	xyz.append([x,y,z])
elif 'xyz' in locals(): #convert in fractionals
  print
  print " ...converting cartesian coordinates in fractional"
  from numpy.linalg import inv
  invcell=inv(cell)
  fract=[]
  for i in range(0,natoms):
	x=xyz[i][0]*invcell.item((0,0))+xyz[i][1]*invcell.item((1,0))+xyz[i][2]*invcell.item((2,0))
	y=xyz[i][1]*invcell.item((0,1))+xyz[i][1]*invcell.item((1,1))+xyz[i][2]*invcell.item((2,1))
	z=xyz[i][2]*invcell.item((0,2))+xyz[i][1]*invcell.item((1,2))+xyz[i][2]*invcell.item((2,2))
	fract.append([x,y,z])


#reading what to do
if sys.argv[2]=='info':
  justinfo=True
  outputformat='JUST INFO'
else:
  justinfo=False
  outputfilename = sys.argv[2].split(".")[0]
  outputformat= sys.argv[2].split(".")[1]

############################################################################## OUTPUT INFO
print
print "***************************************************"
print "  keep calm: I am converting %s to %s" % (inputformat, outputformat)
print "***************************************************"

ntypes=0
for i in range(1,len(atom_count)):
	if atom_count[i] != 0:
 		ntypes+=1
		print('{0:>5} {1:3} atoms'.format(atom_count[i],atomic_symbol[i]))

print " ---- --- ----- "
print('{0:>5} {1:3} atoms'.format(natoms,'tot'))
print
############################################################################## OUTPUT FILE

if justinfo:
  sys.exit("YOU JUST ASKED FOR INFO: not converting!")

ofile=open('./'+outputfilename+'.'+outputformat, 'w+')

#writing a CIF file
if outputformat=="cif":
	print >> ofile, "data_crystal"
	print >> ofile, " "
	print >> ofile, "_cell_length_a    %.3f" %ABC[0]
	print >> ofile, "_cell_length_b    %.3f" %ABC[1]
	print >> ofile, "_cell_length_c    %.3f" %ABC[2]
	print >> ofile, "_cell_angle_alpha %.3f" %math.degrees(abc[0])
	print >> ofile, "_cell_angle_beta  %.3f" %math.degrees(abc[1])
	print >> ofile, "_cell_angle_gamma %.3f" %math.degrees(abc[2])
	print >> ofile, " "
	print >> ofile, "_symmetry_space_group_name_Hall 'P 1'"
	print >> ofile, "_symmetry_space_group_name_H-M  'P 1'"
	print >> ofile, " "
	print >> ofile, "loop_"
	print >> ofile, "_symmetry_equiv_pos_as_xyz"
	print >> ofile, " 'x,y,z' "
	print >> ofile, " "
	print >> ofile, "loop_"
	print >> ofile, "_atom_site_label"
	print >> ofile, "_atom_site_type_symbol"
	print >> ofile, "_atom_site_fract_x"
	print >> ofile, "_atom_site_fract_y"
	print >> ofile, "_atom_site_fract_z"
	print >> ofile, "_atom_site_charge"
	for i in range(0,natoms):	
        	label=atom[i]    #removed: label=atom[i]+"_"+str(i+1)
		print >> ofile, ('{0:10} {1:5} {2:>9.3f} {3:>9.3f} {4:>9.3f} {5:>9.5f}'.format(label,  atom[i], fract[i][0], fract[i][1], fract[i][2], charge[i]))

#writing a PDB file
if outputformat=="pdb":
	print >> ofile, ('CRYST1{0:>9.3f}{1:>9.3f}{2:>9.3f}{3:>7.2f}{4:>7.2f}{5:>7.2f} P 1           1'.format( ABC[0],ABC[1],ABC[2],math.degrees(abc[0]),math.degrees(abc[1]),math.degrees(abc[2]) ))
	for i in range(0,natoms):
		print >> ofile, "%-6s%5d %4s%1s%3s %1s%4d%1s   %8.3f%8.3f%8.3f%6.2f%6.2f          %2s%2s" %("ATOM", i+1, atom[i],"", "XXX", "X", 1,"",fract[i][0],fract[i][1],fract[i][2],1.00, 0.00, atom[i], "")

#writing a CSSR file
if outputformat=="cssr":
   	print >> ofile, "                               %.3f  %.3f  %.3f"                    %(ABC[0],ABC[1],ABC[2])
	print >> ofile, "                %.3f   %.3f   %.3f   SPGR =  1 P 1         OPT = 1" %(math.degrees(abc[0]),math.degrees(abc[1]),math.degrees(abc[2]))
	print >> ofile, "%d   0"							     %(natoms)
	print >> ofile, "0 %s       : %s"                                                    %(inputfilename,inputfilename)
	for i in range(0,natoms):
		print >> ofile, "%4d %3s %8.3f %8.3f %8.3f    0  0  0  0  0  0  0  0  0.000"    %(i+1, atom[i], fract[i][0],fract[i][1],fract[i][2])
 
if outputformat=="xyz":
   	print >> ofile, "%d"   %(natoms)
	print >> ofile, "CELL: %.5f  %.5f  %.5f  %.3f  %.3f  %.3f  " %(ABC[0],ABC[1],ABC[2],math.degrees(abc[0]),math.degrees(abc[1]),math.degrees(abc[2]))
	for i in range(0,natoms):
		print >> ofile, "%3s %8.3f %8.3f %8.3f "  %(atom[i], xyz[i][0],xyz[i][1],xyz[i][2])

if outputformat=="pwi":
        if len(sys.argv)<4:
	   sys.exit("ERROR: You have to specify the pseudo in the input!")
   	print >> ofile, "ibrav = 0 "
    	print >> ofile, "nat   = %d " %(natoms)
    	print >> ofile, "ntyp  = %d " %(ntypes)
       	print >> ofile, " " 
   	print >> ofile, "ATOMIC_SPECIES " 
        for i in range(1,len(atom_count)):
	  if atom_count[i] != 0:
            	print >> ofile, "%3s %8.3f  %s" %(atomic_symbol[i],atomic_mass[i], atomic_pseudo[sys.argv[3]][i]) #add pseudo!
       	print >> ofile, " " 
   	print >> ofile, "CELL_PARAMETERS angstrom "    
	print >> ofile, "%8.5f %8.5f %8.5f"    %(cell.item((0,0)),cell.item((0,1)),cell.item((0,2)))
	print >> ofile, "%8.5f %8.5f %8.5f"    %(cell.item((1,0)),cell.item((1,1)),cell.item((1,2)))
	print >> ofile, "%8.5f %8.5f %8.5f"    %(cell.item((2,0)),cell.item((2,1)),cell.item((2,2)))
   	print >> ofile, " "
   	print >> ofile, "ATOMIC_POSITIONS angstrom "  
	for i in range(0,natoms):
		print >> ofile, "%3s %9.5f %9.5f %9.5f "  %(atom[i], xyz[i][0],xyz[i][1],xyz[i][2])
   	print >> ofile, " "
   	print >> ofile, "K_POINTS gamma "  

if outputformat=="cp2k":                          #tip: this section can be written in another file and added in the main with: @INCLUDE 'outputname.cp2k'
        print >> ofile, "  &SUBSYS"
        print >> ofile, "    &CELL"
        print >> ofile, "      PERIODIC XYZ"  
        print >> ofile, "      MULTIPLE_UNIT_CELL 1 1 1" 
        print >> ofile, "      SYMMETRY NONE"    
        print >> ofile, "      A [angstrom] %8.5f %8.5f %8.5f" %(cell.item((0,0)),cell.item((0,1)),cell.item((0,2)))
        print >> ofile, "      B [angstrom] %8.5f %8.5f %8.5f" %(cell.item((1,0)),cell.item((1,1)),cell.item((1,2)))
        print >> ofile, "      C [angstrom] %8.5f %8.5f %8.5f" %(cell.item((2,0)),cell.item((2,1)),cell.item((2,2)))
        print >> ofile, "    &END CELL"
        print >> ofile, " "
        print >> ofile, "    &COORD"
        print >> ofile, "      SCALED .FALSE." 
	for i in range(0,natoms):
		print >> ofile, "%3s %9.5f %9.5f %9.5f "  %(atom[i], xyz[i][0],xyz[i][1],xyz[i][2])
        print >> ofile, "    &END COORD"
        print >> ofile, " "
        for i in range(1,len(atom_count)):
	  if atom_count[i] != 0:
            print >> ofile, "    &KIND %3s" %(atomic_symbol[i]) 
            print >> ofile, "      BASIS_SET DZVP-MOLOPT-SR-GTH"
            print >> ofile, "      POTENTIAL GTH-PBE" 
            print >> ofile, "    &END KIND" 
            print >> ofile, " " 
        print >> ofile, "  &END SUBSYS"
