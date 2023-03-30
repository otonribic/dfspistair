'''
Add a spiral staircase according to a set of parameters to a Dark Forces' LEV file.
'''

import parsecl
import sys
import math

# Debug
# sys.argv = ['/C:245,76.5 /r:14,22 /A:90,180 /S:10 /FL:20,29 /CL:10,10']

# Auxiliaries

sectordef = '''#
SECTOR {0}
 NAME
 AMBIENT          31
 FLOOR TEXTURE    0  0.00  0.00 2
 FLOOR ALTITUDE   {1}
 CEILING TEXTURE  0  0.00  0.00 2
 CEILING ALTITUDE {2}
 SECOND ALTITUDE  0.00
 FLAGS            0 0 0
 LAYER            0
 VERTICES 4
'''
walldef = ''' WALLS 4
  WALL LEFT:  0 RIGHT:  1 MID: 0 0.00 0.00 0 TOP: 0 0.00 0.00 0 BOT: 0 0.00 0.00 0 SIGN: -1 0.00 0.00 ADJOIN: -1 MIRROR: -1 WALK: -1 FLAGS: 0 0 0 LIGHT: 0
  WALL LEFT:  1 RIGHT:  2 MID: 0 0.00 0.00 0 TOP: 0 0.00 0.00 0 BOT: 0 0.00 0.00 0 SIGN: -1 0.00 0.00 ADJOIN: -1 MIRROR: -1 WALK: -1 FLAGS: 0 0 0 LIGHT: 0
  WALL LEFT:  2 RIGHT:  3 MID: 0 0.00 0.00 0 TOP: 0 0.00 0.00 0 BOT: 0 0.00 0.00 0 SIGN: -1 0.00 0.00 ADJOIN: -1 MIRROR: -1 WALK: -1 FLAGS: 0 0 0 LIGHT: 0
  WALL LEFT:  3 RIGHT:  0 MID: 0 0.00 0.00 0 TOP: 0 0.00 0.00 0 BOT: 0 0.00 0.00 0 SIGN: -1 0.00 0.00 ADJOIN: -1 MIRROR: -1 WALK: -1 FLAGS: 0 0 0 LIGHT: 0
'''


def _csplit(string):
    '''Split a string 'x,y' to a tuple of floats (x:float, y:float)'''
    string = string.split(',')
    return float(string[0]), float(string[1])


# Main flow

print('DF Spiral Stair Generator')

if len(sys.argv) <= 1:
    # Help
    print('''Usage:

dfspistair filename /C:x,y /R:i,o /A:a,s /S:s /FL:f,l /CL:f,l

Arguments:
   filename  The name of the file (must be .LEV) [SECBASE.LEV]
   C         Center coordinates in DF X-Y system [0,0]
   R         Radii of stairs; inner and outer [8,16]
   A         Starting azimuth and the length of sweep (in degrees) [0,360]
   S         Number of steps in total [12]
   FL        Starting and ending step floor altitudes (can be same) [8,19]
   C         Starting and ending step ceiling altitudes (can be same) [0,11]

Example:
dfspistair SECBASE.LEV /C:245,76.5 /R:14,22 /A:90,180 /S:10 /FL:10,19 /CL:30,30

It appends the new sectors directly to the file, i.e. it doesn't make a copy so
please make sure the current user has the necessary permissions, and the LEV
file itself is not already in use and locked by another application. And have a
backup in case something doesn't work as expected!

Note that the altitude system (where positive values point downward) in DF
works opposite to the altitude system in WDFUSE, where it is reversed. This
utility applies DF altitudes, meaning the altitude of the ceilings should be
(as numbers) lower than the floors' altitudes. See /FL and /C defaults above.

By Fish (oton.ribic@bug.hr), 2023. Freeware, dedicated to the DF-21 community
of Dark Forces fans (www.df-21.net)''')
    sys.exit(0)

sys.argv = sys.argv[1:]  # Eliminate start command
# Process command line parameters
params = parsecl.parsecl(' '.join(sys.argv))
FILE = 'SECBASE.LEV'
if '' in params:
    params[''] = params[''].strip(' ')  # To avoid possibly space conundrums
    if params['']: FILE = params['']
CENTER = 0, 0
if 'C' in params: CENTER = _csplit(params['C'])
RADII = 8, 16
if 'R' in params: RADII = _csplit(params['R'])
ANGLES = 0, 360
if 'A' in params: ANGLES = _csplit(params['A'])
STEPS = 12
if 'S' in params: STEPS = int(params['S'])
FLOORS = 0, 11
if 'FL' in params: FLOORS = _csplit(params['FL'])
CEILINGS = 8, 19
if 'CL' in params: CEILINGS = _csplit(params['CL'])

# Print the parameters
print(f'Adding stairs with the following parameters to {FILE}:')
print(f'Center (x,y): {CENTER[0]},{CENTER[1]}')
print(f'Inner radius: {RADII[0]}')
print(f'Outer radius: {RADII[1]}')
print(f'Starting azimuth: {ANGLES[0]}°')
print(f'Ending azimuth: {ANGLES[0]+ANGLES[1]}°')
print(f'Covered angle: {ANGLES[1]}°')
print(f'Number of steps: {STEPS}')
print(f'Floors spanning from: {FLOORS[0]} to {FLOORS[1]}')
print(f'Ceilings spanning from: {CEILINGS[0]} to {CEILINGS[1]}')

# File pomp
print('\nOpening file...')
file = open(FILE, 'r').readlines()
print(f'{len(file)} lines found')
# Counts
for i in range(len(file)):
    if file[i].strip(' ').startswith('NUMSECTORS'):
        # Some calculations on old and new sector count
        origsectors = int(file[i].rpartition(' ')[2])
        newsectors = origsectors + STEPS
        file[i] = f'NUMSECTORS {newsectors}\n'  # Update in the file
        break
print(f'Original number of sectors: {origsectors}')
print(f'New number of sectors: {newsectors}')

# Geometry preparations
print('Calculating geometry...')
# Calculate ladderline
stepangle = ANGLES[1] / STEPS
print(f'Individual step angle: {stepangle}°')
ladder = []  # Collector
for step in range(STEPS + 1):  # One more because the last step needs the endpoints
    pangle = (ANGLES[0] + step * stepangle) * math.pi / 180
    # Calculate points while rounding to 2 decimals like DF uses
    ip = round(CENTER[0] + math.cos(pangle) * RADII[0], 2), \
        round(CENTER[1] + math.sin(pangle) * RADII[0], 2)
    op = round(CENTER[0] + math.cos(pangle) * RADII[1], 2), \
        round(CENTER[1] + math.sin(pangle) * RADII[1], 2)
    # Finally append to the collector as a 2-item tuple
    ladder.append((ip, op))
# Altitudes steps
floorstep = (FLOORS[1] - FLOORS[0]) / (STEPS - 1)
ceilstep = (CEILINGS[1] - CEILINGS[0]) / (STEPS - 1)
print(f'Floor and ceiling step heights: {floorstep},{ceilstep}')

# Loop through steps
for step in range(STEPS):
    secnum = origsectors + step  # Ordinal of the sector in the file
    # Altitudes calculation
    flooralt = round(FLOORS[0] + floorstep * step, 2)
    ceilalt = round(CEILINGS[0] + ceilstep * step, 2)
    # Append header
    file.append(sectordef.format(secnum, flooralt, ceilalt))
    # Add vertices, fetching correct ladder rungs first
    lad1 = ladder[step]
    lad2 = ladder[step + 1]
    file.append(f'  X: {lad2[0][0]} Z: {lad2[0][1]}\n')
    file.append(f'  X: {lad2[1][0]} Z: {lad2[1][1]}\n')
    file.append(f'  X: {lad1[1][0]} Z: {lad1[1][1]}\n')
    file.append(f'  X: {lad1[0][0]} Z: {lad1[0][1]}\n')
    # Add walls
    file.append(walldef)

# Completed all geometry, reassemble the output file from the 'file' list
print('Finished geometry, writing to file')
outf = open(FILE, 'w')
outf.write(''.join(file))
outf.close()
print('All done')
