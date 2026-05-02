import random

BASE=["x","y","z","w"]

def mutate(S):
    m=random.randint(0,3)
    l=S.get("left","x")
    r=S.get("right","y")

    if m==0:
        return {"left":r,"right":l}
    if m==1:
        return {"left":l+l,"right":r}
    if m==2:
        return {"left":l,"right":r+r}
    return {"left":random.choice(BASE),"right":random.choice(BASE)}
