for v in Vertices:
    visited[v] = 0	
	
root = PickVertex()
visited[root] = 1	
Q.Append(root)

while Q.IsNotEmpty():
    v = Q.Top()
    for w in Neighborhood(v):
	if visited[w] == 0:
	    visited[w] = 1
	    Q.Append(w)
