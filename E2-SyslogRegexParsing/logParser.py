import re
#Import File
file_path = "./logfile.txt"

pattern = r"Interface\s+?(\S+?):\s+?RX bytes:\s+?(\d+?)\s+?TX bytes:\s+?(\d+)"
# Interface\s+? <- Matches the string Interface and all tailing white spaces
# (\S+?): <- This Matches and Captures all of the follwing non-white space charaters until the : (Interface Name)
# \s+? <- Matches all of the white space after the : 
# RX bytes:\s+? <- Matches the string RX bytes and any trailing white spaces
# (\d+?) <- Matches and Captures all of the following digets (Could be \d+ but directions say to be non-greety)
# \s+?TX bytes:\s+? <- Matches white space followed by the string TX bytes and any trailing white spaces
# (\d+) <- This Matches and Captures the last digets cannot be non-greety because there is nothing left to match

print("") #Spacing
#Open and Search File
with open(file_path, "r") as file:
    for line in file:
        #Remove EOL charaters
        clean_line = line.rstrip("\r\n")
        match = re.search(pattern, line)
        if match:
            print(f"Interface: {match.group(1)}")
            print(f"RX Bytes:  {match.group(2)}")
            print(f"TX Bytes:  {match.group(3)}")
            print("") #Spacing
print("") #Spacing
