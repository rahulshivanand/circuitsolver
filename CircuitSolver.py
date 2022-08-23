
from sys import argv

if len(argv) !=2:                                          #check if user has only given required inputs
    print('\nUsage: %s <inputfile>' %argv[0])
    exit()

CIRCUIT = '.circuit' 
END = '.end'       
AC = '.ac'  
AC1 = 'ac'
DC = 'dc'

try:
    with open(argv[1]) as f:                              #opening input file
        lines= f.readlines()                              #reading lines of the file into a list
        start=-1; end=-2
        for line in lines:
            if CIRCUIT == line[:len(CIRCUIT)]:            
                start= lines.index(line)                  #if line matches with .circuit, store line index in start
            
            elif END == line[:len(END)]:
                end= lines.index(line)                    #if line matches with .end, store line index in end
                break
        
        if start>=end:
            print('Invalid circuit definition')           #if .circuit comes after .end, tell the user the circuit is invalid
            exit(0)                                       #exit if true

        for i in lines:
            if i.split(" ")[0]== '.ac':
                w= complex(real=float(i.split(" ")[2]))
                w= 2*(3.14)*w
                break                                     #Get frequency from .ac line

        realLine = []
        tempLines = []
        for i in range(end, start, -1):
            tempLines = [lines[i]] + tempLines
        for i in tempLines:
            i = i.strip('\n')
            if CIRCUIT in i or END in i:
                continue
        
            else:
                temp = i.split('#')
                realLine = realLine + [temp[0]]
        for i in realLine:
            if i == '\n':
                realLine.remove('\n')                     #Remove comments and newline character
            
        
        
        
except IOError:
    print('Invalid file')                                 #Show invalid when an IOError occurs
    exit()    


first=[]
to=[]
value=[]
nam=[]
l=[]                                                      #Define lists to store each element of each line of netlist  

for j in range(len(realLine)):
    line= realLine[j]

    l= line.split()

    if l[3]== AC1:
        first= first + [l[1]]
        to= to + [l[2]]
        value= value + [l[4]]
        nam= nam+ [l[0]]

    elif l[3]== DC:
        first= first + [l[1]]
        to= to + [l[2]]
        value= value + [l[4]]
        nam= nam+ [l[0]]

    else:
        first= first + [l[1]]
        to= to + [l[2]]
        value= value + [l[3]]
        nam= nam+ [l[0]]                           #Store name,from node,to node,value in separate lists in order

GND= 'GND'
V= 'V'
C= 'C'
L= 'L'
R= 'R'

class resistor:
    def __init__(self,name,resistance,f,t):
        self.resistance= resistance
        self.name= name
        self.f=f
        self.t=t
        self.type= R

class voltage:
    def __init__(self,name,volt,f,t):
        self.volt= volt
        self.name= name
        self.f=f
        self.t=t
        self.type= V

class inductor:
    def __init__(self,name,inductance,f,t):
        self.inductance= inductance
        self.name= name
        self.f=f
        self.t=t
        self.type= L

class capacitor:
    def __init__(self,name,capacitance,f,t):
        self.capacitance= capacitance
        self.name= name
        self.f=f
        self.t=t
        self.type= C                                            #Define classes for each component and its attributes

        
m=0
for q in nam:   
    k= nam.index(q)        
    if q[0]== V:
        m=m+1
        nam[k]= voltage(nam[k],value[k],first[k],to[k])
    
    elif q[0]== R:
        nam[k]= resistor(nam[k],value[k],first[k],to[k])

    elif q[0]== L:   
        nam[k]= inductor(nam[k],value[k],first[k],to[k])

    elif q[0]== C:    
        nam[k]= capacitor(nam[k],value[k],first[k],to[k])             #Load each attribute into respective object

o=0
for s in first:
    if s!= GND:
        if int(s)>o:
            o= int(s)
e=0
for h in to:
    if h!= GND:
        if int(h)>e:
            e= int(h)

n= max(o,e)                                                          #determining max number of nodes

import numpy as np

A= np.zeros((n+m,n+m),complex);A
B= np.zeros((n+m),complex);B                                         #define zero matrices of appropriate orders

#Load values using Modified Nodal Analysis Concepts
d=0
for names in nam:

    if names.type== R:
        if names.f != GND and names.t != GND:
            A[int(names.f)-1][int(names.f)-1] += 1/float(names.resistance)
            A[int(names.f)-1][int(names.t)-1] -= 1/float(names.resistance)
            A[int(names.t)-1][int(names.f)-1] -= 1/float(names.resistance)
            A[int(names.t)-1][int(names.t)-1] += 1/float(names.resistance)
            
        elif names.f != GND and names.t == GND:
            A[int(names.f)-1][int(names.f)-1] += 1/float(names.resistance)

        elif names.f == GND and names.t != GND:    
            A[int(names.t)-1][int(names.t)-1] += 1/float(names.resistance)


    elif names.type== C:
        if names.f != GND and names.t != GND:
            A[int(names.f)-1][int(names.f)-1] += complex(imag=w*float(names.capacitance))
            A[int(names.t)-1][int(names.f)-1] -= complex(imag=w*float(names.capacitance))
            A[int(names.f)-1][int(names.t)-1] -= complex(imag=w*float(names.capacitance))
            A[int(names.t)-1][int(names.t)-1] += complex(imag=w*float(names.capacitance))
            
        elif names.f != GND and names.t == GND:
            A[int(names.f)-1][int(names.f)-1] += complex(imag=w*float(names.capacitance))

        elif names.f == GND and names.t != GND:    
            A[int(names.t)-1][int(names.t)-1] += complex(imag=w*float(names.capacitance))


    elif names.type== L:
        if names.f != GND and names.t != GND:
            A[int(names.f)-1][int(names.f)-1] += 1/(complex(imag=w*float(names.inductance)))
            A[int(names.t)-1][int(names.f)-1] -= 1/(complex(imag=w*float(names.inductance)))
            A[int(names.f)-1][int(names.t)-1] -= 1/(complex(imag=w*float(names.inductance)))
            A[int(names.t)-1][int(names.t)-1] += 1/(complex(imag=w*float(names.inductance)))
            
        elif names.f != GND and names.t == GND:
            A[int(names.f)-1][int(names.f)-1] += 1/(complex(imag=w*float(names.inductance)))

        elif names.f == GND and names.t != GND:    
            A[int(names.t)-1][int(names.t)-1] += 1/(complex(imag=w*float(names.inductance)))


    elif names.type== V:
        for p in range(1,n+1):
            if names.f != GND:
                if int(names.f) == p:
                    A[p-1][n+d] =1
                    A[n+d][p-1] =1
            if names.t !=GND:
                if int(names.t) == p:
                    A[p-1][n+d] =-1
                    A[n+d][p-1] =-1
         
        B[n+d]= names.volt
        d+=1                                                          

Y= np.linalg.solve(A,B);Y                                  #Solve matrices

print("V0=0",end='\n')
for r in range(n):
    print("V{}={}".format(r+1,Y[r]),end='\n')              #Print node voltages
for r in range(1,m+1):
    print("I{}={}".format(r,Y[r+n-1]),end='\n')            #Print unknown currents through voltage sources

    


