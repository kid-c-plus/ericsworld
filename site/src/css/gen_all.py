import os

outcss = [f"@import url({i});" for i in os.listdir() if i.endswith(".css") and not i == "all.css"]

with open("all.css", "w") as f:
    f.write("\n".join(outcss))
