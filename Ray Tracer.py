#Thien Vu
#A ray tracer
#the import stuff
import math
import copy
import sys
import cmath
from tkinter import *


#calculates the ambient, diffuse, and specular lighting
#takes in surface normal, diffuse, specular, specularIndex, and point of intersection
def calcADS(N, Kd, Ks, specIndex, iPoint):
    # calc ambient lighting
    ambient = Ia * Kd
    L = calcUV(iPoint, lightSource)
    # crossprod of surface normal and lighting vector
    NdotL = N[0] * L[0] + N[1] * L[1] + N[2] * L[2]
    if NdotL < 0:
        NdotL = 0
    # calc defuse
    diffuse = Ip * Kd * NdotL
    # reflection vector
    R = reflectL(N, L)
    RdotV = R[0] * V[0] + R[1] * V[1] + R[2] * V[2]
    if RdotV < 0: RdotV = 0
    # calc specular
    specular = Ip * Ks * RdotV ** specIndex
    return [ambient, diffuse, specular]

#calculates the reflection vector for light
#normalizes in the function
def reflectL(N, L):
    R = []
    #normalize surface normal and lighting vector
    N = normalize(N)
    L = calcUV(N, lightSource)
    #le epic cosine trick
    twoCosPhi = 2  * (N[0]*L[0] + N[1]*L[1] + N[2]*L[2])
    #if phi < 90
    if twoCosPhi > 0:
        for i in range(3):
            R.append(N[i] - (L[i] / twoCosPhi))
    #if phi == 90
    elif twoCosPhi == 0:
        for i in range(3):
            R.append( -L[i])
    #if phi > 90
    else:
        for i in range(3):
            R.append( -N[i] + (L[i] / twoCosPhi))
    return normalize(R)

#calculates the reflection vector for traced ray
#normalizes in the function
def reflectT(N, T):
    R = []
    #normalize surface normal and lighting vector
    N = normalize(N)
    T = normalize(T)
    #le epic cosine trick
    twoCosPhi = 2 * (N[0]*-T[0] + N[1]*-T[1] + N[2]*-T[2])
    #if phi < 90
    if twoCosPhi > 0:
        for i in range(3):
            R.append(N[i] + (T[i] / twoCosPhi))
    # if phi == 90
    elif twoCosPhi == 0:
        for i in range(3):
            R.append(T[i])
    # if phi > 90
    else:
        for i in range(3):
            R.append(-N[i] - (T[i] / twoCosPhi))
    return normalize(R)

# turns colors into hexcodes
#takes intensities
def colorHexCode(intensity):
    hexString = str(hex(min(round(255 * intensity), 255)))
    if hexString[0] == "-":
        trimmedHexString = "00"
    else:
        trimmedHexString = hexString[2:]
        if len(trimmedHexString) == 1:
            trimmedHexString = "0" + trimmedHexString
    return trimmedHexString

# combines 3 hex color codes into one whole rgb code
def RGBColorHexCode(ambDiffSpec):
    rCode = colorHexCode(ambDiffSpec[0])
    gCode = colorHexCode(ambDiffSpec[1])
    bCode = colorHexCode(ambDiffSpec[2])
    colorString = "#" + rCode + gCode + bCode
    return colorString

#sphere class,
#has mathmatical representation and color stuff
class Sphere():
    #mathmatical sphere parameters
    center = [0,0,0]
    radius = 0
    #color of sphere
    localRGB = [0,0,0]
    #diffuse and speculars for illumination model
    Kd = 0
    Ks = 0
    specIndex = 0
    #weight of the color of sphere, color of its reflection, and color of its refraction
    weightL = 0
    weightRl = 0
    weightRr = 0
    #make a sphere instance
    def __init__(self, center, radius, localRGB, Kd, Ks, specIndex, weightL, weightRl, weightRr):
        self.center = center
        self.radius = radius
        self.localRGB = localRGB
        self.Kd = Kd
        self.Ks = Ks
        self.specIndex = specIndex
        self.weightL = weightL
        self.weightRl = weightRl
        self.weightRr = weightRr


    #check if a ray intersects with a sphere
    def intersect(self, sPoint, ray, currT):
        # a = i^2 + j^2 + k^2
        a = 0
        for i in range(3):
            a += ray[i] ** 2
        # b = 2 * i * (X1 - l) + 2 * j * (Y1 - m) + 2 * k * (Z1 - n)
        b = 0
        for i in range(3):
            b += 2 * ray[i] * (sPoint[i] - self.center[i])
        c = 0
        # c = l^2 + m^2 + n^2 + x1^2 + y1^2 + z1^2
        for i in range(3):
            c += self.center[i] ** 2
            c += sPoint[i] ** 2
        subc = 0
        # subc = 2 * (-l * X1 - m * Y1 - n * Z1) - r^2
        for i in range(3):
            subc += -self.center[i] * sPoint[i]
        subc *= 2
        c += subc - self.radius ** 2
        # calculate discriminant
        d = b ** 2 - 4 * a * c
        # if discriminant is less than 0, there is no intersection
        if d < 0:
            return sys.maxsize, 0
        # otherwise, there is atleast one intersection
        else:
            tOne = (-b + cmath.sqrt(d)) / (2 * a)
            tTwo = (-b - cmath.sqrt(d)) / (2 * a)
            # if there are two intersections, proceed with the one with the smaller t
            if tOne.imag == 0 and tTwo.imag == 0:
                t = min(tOne.real, tTwo.real)
            # else check for the real intersection
            elif tOne.imag == 0:
                t = tOne.real
            else:
                t = tTwo.real
            #check for rounding error or if there is a closer intersection already
            if t > currT or t < 0.001:
                return sys.maxsize, 0
            iPoint = []
            #make a point with them
            for i in range(3):
                iPoint.append(sPoint[i] + (ray[i] * t))
            if iPoint[2] < 0:
                return sys.maxsize, 0
            return t, iPoint

#plane class(not the flying kind)
class Plane():
    #surface normal, essentially like a single polygon but cooler
    sNorm = [0,0,0]
    #point at which the plane is anchored to
    anchPoint = [0,0,0]
    #diffuse and specular
    Kd = 0
    Ks = 0
    specIndex = 0
    #weight of the color of plane, color of its reflection, and color of its refraction
    weightL = 0
    weightRl = 0
    weightRr = 0

    #make a da plane
    def __init__(self, sNorm, anchPoint, Kd, Ks, specIndex, weightL, weightRl):
        self.sNorm = normalize(sNorm)
        self.anchPoint = anchPoint
        self.Kd = Kd
        self.Ks = Ks
        self.specIndex = specIndex
        self.weightL = weightL
        self.weightRl = weightRl

    # check if a ray intersects with a plane
    def intersect(self, sPoint, ray, currT):
        D = 0
        # D = Aa + Bb + Cc
        for i in range(3):
            D += self.sNorm[i] * self.anchPoint[i]

        numer = 0
        # numerator = -(A*X1 + B*Y1 + C*Z1 - D)
        for i in range(3):
            numer += self.sNorm[i] * sPoint[i]
        numer -= D
        numer *= -1

        # denominator = A * i + B * j + C * k
        denom = 0
        for i in range(3):
            denom += self.sNorm[i] * ray[i]
        # t = numerator / denominator
        if denom == 0:
            return sys.maxsize, 0
        t = numer / denom
        if t > currT:
            return sys.maxsize, 0
        # if t is greater than 0 (really 0.001 cause rounding error) then it intersects with the plane
        if t > 0.001:
            #calc points of intersection
            iPoint = []
            for i in range(3):
                iPoint.append(sPoint[i] + ray[i] * t)
            #check if intersection point is farther away than view distance of plane
            if iPoint[2] > 2000 or iPoint[2] < 0:
                return sys.maxsize, 0
            return t, iPoint
        #if t <= 0 then theres no intersection
        else:
            return sys.maxsize, 0

    #gets the color
    #color is either red or white depending on location of intersection
    def getColor(self, iPoint):
        if iPoint[0] >= 0: cFlag = True
        else: cFlag = False
        if abs(iPoint[0]) % 400 > 200: cFlag = not cFlag
        if abs(iPoint[2]) % 400 > 200: cFlag = not cFlag
        if cFlag:
            return [1,0,0]
        else:
            return [1,1,1]

#calculates the unit vector, self explanatory
def calcUV(start, end):
    return normalize([end[0] - start[0], end[1] - start[1], end[2] - start[2]])


#normalizes vectors
#math thing
#take a vector, spit a vector
def normalize(vector):
    sumOfSquares = 0
    #get magnitude
    for i in range(len(vector)):
        sumOfSquares += vector[i]**2
    magnitude = math.sqrt(sumOfSquares)
    vect = []
    for i in range(len(vector)):
        vect.append(vector[i]/magnitude)
    return vect

#traces a ray from one point to another
def traceRay(sPoint, ray, depth, raySource, totalWRl):
    #end of trace
    if depth == 0:
        return [0,0,0]
    #get the closest point of intersection
    currT = sys.maxsize
    #for each object
    for obj in scene:
        #get the intersection distance and point of intersection
        t, iPoint = obj.intersect(sPoint, ray, currT)
        #if new intersection distance is closer than the current one
        #make it the new current one
        if t < currT:
            currT = t
            currObj = obj
            currIPoint = iPoint
    #if it has not intersected with anything, return skycolor
    if currT == sys.maxsize:
        return skyColor
    #check what type of object it is
    #then get the object surface normal at that point
    if isinstance(currObj, Sphere):
        c = currObj.localRGB
        objNorm = calcUV(currObj.center, currIPoint)
        raySource = "sphere"
    elif isinstance(currObj, Plane):
        c = currObj.getColor(currIPoint)
        objNorm = normalize(currObj.sNorm)
        raySource = "plane"
    # calculate the intensity
    ADS = calcADS(objNorm, currObj.Kd, currObj.Ks, currObj.specIndex, currIPoint)
    intsy = ADS[0] + ADS[1] + ADS[2]
    intsy *= 2
    #check if its in shadow
    if inShadow(currObj, currIPoint):
        #lower intensity if it is
        intsy *= 0.25
    #get color
    cL = [c[0]*intsy, c[1]*intsy, c[2]*intsy]
    #get weight of the color itself
    wL = currObj.weightL
    #get weight of reflection and multiply it by total reflection weight
    wRl = currObj.weightRl
    totalWRl *= wRl
    #if total reflection weight < 0.1, then stop tracing
    if totalWRl > 0.1:
        cRl = traceRay(currIPoint, reflectT(objNorm, ray), depth - 1, raySource, totalWRl)
    else:
        cRl = [0,0,0]
    cF = []
    #calc the points
    for i in range(3):
        cF.append(cL[i]*wL + cRl[i] * wRl)
    return cF

#checks for a shadow
#gets the point of intersection of the current object
def inShadow(currObj, iPoint):
    shadowRay = calcUV(iPoint, lightSource)
    #for each object that is not the current object
    for obj in scene:
        if obj != currObj:
            #check if there is an intersection
            t, throwaway = obj.intersect(iPoint, shadowRay, sys.maxsize)
            if t != sys.maxsize:
                return True
    return False

#average the color of pixels
#takes 4 pixel colors
def averageC(p1, p2, p3, p4):
    aP = []
    for i in range(3):
        aP.append((p1[i] + p2[i] + p3[i] + p4[i])/4)
    return aP


#renders an image pixel by pixel
def renderImage():
    pixelColors = [[0 for i in range(canvasHeight + 1)] for j in range(canvasWidth + 1)]
    top = round(canvasHeight / 2)
    bot = round(-canvasHeight / 2)
    left = round(-canvasWidth / 2)
    right = round(canvasWidth / 2)
    #get colors to supersamples
    #from top of screen to bottom of screen
    threads = []
    for y in range(top, bot - 1, -1):
        #from left of line to right of line
        for x in range(left, right + 1):
            pixelColors[right + x][top - y] = traceRay(cProj, calcUV(cProj, [x, y, 0]), 4, "camera", 1)
    #supersample for each pixel
    for y in range(canvasHeight):
        for x in range(canvasWidth):
            aPC = averageC(pixelColors[x][y], pixelColors[x+1][y], pixelColors[x][y+1], pixelColors[x+1][y+1])
            #use the supersampled pixel
            w.create_line(x, y, x+1, y, fill=RGBColorHexCode(aPC))

#canvas sizes
canvasWidth = 800
canvasHeight = 800
#distance of viewer
d = 500
#intensity of the ambient
Ia = 0.3
#intensity of the pointlight
Ip = 0.7
#position of the lightsource
lightSource = [500,500,0]
V = [0,0,-1]
V = normalize(V)
cProj = [0,0,-d]
skyColor = [135/255, 206/255, 235/255]
pYConst = -400


#a red, green, and blue sphere, and a plane
rS = Sphere([300,-100,350],200,[1,0.5,0.5],0.5,0.5,16,0.5,0.5,0)
gS = Sphere([-300,-200,500],100,[0.5,1,0.5],0.5,0.5,16,0.5,0.5,0)
bS = Sphere([-100,0,1100],350,[0.5,0.5,1],0.5,0.5,16,0.5,0.5,0)
p = Plane([0,1,0], [0,pYConst,0], 0.6, 0.4, 8, 0.6, 0.4)


scene = [rS, gS, bS, p]
root = Tk()
root.title("RAYS WHEN THEY NEED TO BE TRACED - CSC 470 - Assignment 5 - TV")
outerframe = Frame(root)
outerframe.pack()
w = Canvas(outerframe, width=canvasWidth, height=canvasHeight)
renderImage()
w.pack()
root.mainloop()
