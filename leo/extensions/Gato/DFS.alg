for v in Vertices:
    visited[v] = 0	
	
root = PickVertex()
visited[root] = 1	
S.Push(root)

while S.IsNotEmpty():
    v = S.Pop()
    for w in Neighborhood(v):
	if visited[w] == 0:
	    visited[w] = 1
	    S.Push(w)

