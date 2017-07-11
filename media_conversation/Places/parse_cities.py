cities = []

with open("700cities.txt", "r") as f:
    l = f.readlines()
    cities = [c.split("\t")[2] for c in l]
f.close()

with open("cities.txt", "w+") as f:
    for c in cities:
        print(c, file=f)
