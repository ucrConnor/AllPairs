import argparse
import cProfile
import os
import re
import sys
import time

# Command line arguments
from math import inf

parser=argparse.ArgumentParser(description='Calculate the shortest path between all pairs of vertices in a graph')
parser.add_argument('--algorithm',default='a',\
    help='Algorithm: Select the algorithm to run, default is all. (a)ll, (b)ellman-ford only or (f)loyd-warshall only')
parser.add_argument('-v','--verbose',action='store_true')
parser.add_argument('--profile',action='store_true')
parser.add_argument('filename',metavar='<filename>',help='Input file containing graph')

graphRE=re.compile("(\\d+)\\s(\\d+)")
edgeRE=re.compile("(\\d+)\\s(\\d+)\\s(-?\\d+)")

vertices=[]
edges=[]
def shortest_path(G, s):
    d = []
    i = 0
    for i in range(len(vertices)):
        d.append(inf)
    d[s] = 0
    i = 0
    j = 0
    for k in range(len(vertices) - 1):
        for i in range(len(vertices) ):
            for j in range(len(vertices)):
                if  edges[i][j] != inf:
                    if d[j] > d[i] + int(edges[i][j]):
                        d[j] = d[i] + int(edges[i][j])


    for i in range(len(vertices) ):
        for j in range(len(vertices)):
             if  edges[i][j] != inf:
                if d[j] > d[i] + int(edges[i][j]):
                    return False
    return d

def BellmanFord(G):
    pathPairs=[]
    for i in vertices:
        val = shortest_path(G, i)
        if not val:
            return False
        pathPairs.append(val)

    # The pathPairs list will contain the 2D array of shortest paths between all pairs of vertices 
    # [[w(1,1),w(1,2),...]
    #  [w(2,1),w(2,2),...]
    #  [w(3,1),w(3,2),...]
    #   ...]
    return pathPairs

def FloydWarshall(G):

    length = len(vertices)
    #d = [[[0 for k in range(length + 1)] for j in range(length)] for i in range(length)]
    d = [[0 for j in range(length)] for i in range(length)]
    pathPairs = [[0 for j in range(length)] for i in range(length)]
    for i in range(length):
        for j in range(length):

            if i != j:
                if edges[i][j] != inf and edges[i][j]:
                   d[i][j] = int(edges[i][j])
                else:
                   d[i][j] = inf


    for k in range(1,length + 1):
        for i in range(length):
            for j in range(length):
                prev = d[i][j]
                take = d[i][k-1] + d[k-1][j]
                pathPairs[i][j] = min(prev,take)
        d = pathPairs

    # for i in range(length):
    #     pathPairs.append(list())
    #     for j in range(length):
    #         pathPairs[i].append(d[i][j][length])

    for i in range(length):
        if pathPairs[i][i] < 0:
            return False
    # The pathPairs list will contain the 2D array of shortest paths between all pairs of vertices 
    # [[w(1,1),w(1,2),...]
    #  [w(2,1),w(2,2),...]
    #  [w(3,1),w(3,2),...]
    #   ...]
    return pathPairs

def readFile(filename):
    global vertices
    global edges
    # File format:
    # <# vertices> <# edges>
    # <s> <t> <weight>
    # ...
    inFile=open(filename,'r')
    line1=inFile.readline()
    graphMatch=graphRE.match(line1)
    if not graphMatch:
        print(line1+" not properly formatted")
        quit(1)
    vertices=list(range(int(graphMatch.group(1))))
    edges=[]
    for i in range(len(vertices)):
        row=[]
        for j in range(len(vertices)):
            row.append(float("inf"))
        edges.append(row)
    for line in inFile.readlines():
        line = line.strip()
        edgeMatch=edgeRE.match(line)
        if edgeMatch:
            source=edgeMatch.group(1)
            sink=edgeMatch.group(2)
            if int(source) > len(vertices) or int(sink) > len(vertices):
                print("Attempting to insert an edge between "+source+" and "+sink+" in a graph with "+vertices+" vertices")
                quit(1)
            weight=edgeMatch.group(3)
            edges[int(source)-1][int(sink)-1]=weight
    G = (vertices,edges)
    return (vertices,edges)

def matrixEquality(a,b):
    if not a and not b:
        return True

    if len(a) == 0 or len(b) == 0 or len(a) != len(b):
        return False
    if len(a[0]) != len(b[0]):
        return False
    for i,row in enumerate(a):
        for j,value in enumerate(b):
            if a[i][j] != b[i][j]:
                return False
    return True


def main(filename,algorithm):
    profile1 = cProfile.Profile()
    profile2 = cProfile.Profile()

    G=readFile(filename)
    pathPairs = []
    # G is a tuple containing a list of the vertices, and a list of the edges
    # in the format ((source,sink),weight)
    if algorithm == 'b' or algorithm == 'B':
        if args.profile:
            profile1.enable()
            pathPairs = BellmanFord(G)
            profile1.print_stats()
            profile1.dump_stats()
            profile1.disable()
        else:
            pathPairs = BellmanFord(G)
    if algorithm == 'f' or algorithm == 'F':
        if args.profile:
            profile2.enable()
            pathPairs = FloydWarshall(G)
            profile2.print_stats()
            profile2.dump_stats()
            profile2.disable()
        else:
            pathPairs = FloydWarshall(G)
    if algorithm == 'a':
        print('running both')
        if args.profile:
            profile1.enable()
            pathPairsBellman = BellmanFord(G)
            profile1.print_stats()
            profile1.disable()

            profile2.enable()
            pathPairsFloyd = FloydWarshall(G)
            profile2.print_stats()
            profile2.disable()
        else:
            pathPairsBellman = BellmanFord(G)
            pathPairsFloyd = FloydWarshall(G)
        pathPairs = pathPairsBellman
        if not matrixEquality(pathPairsBellman,pathPairsFloyd):
            print('Floyd-Warshall and Bellman-Ford did not produce the same result')
    with open(os.path.splitext(filename)[0]+'_shortestPaths.txt','w') as f:
        if not pathPairs:
            f.write("False")
        else:
            for row in pathPairs:
                for weight in row:
                    f.write(str(weight)+' ')
                f.write('\n')

if __name__ == '__main__':
    args=parser.parse_args()
    main(args.filename,args.algorithm)
