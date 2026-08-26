import re
#Import File
file_path = "./show_ip_int_brief.txt"

#Title
print("\nActive Interfaces:")

#Open and Search File
with open(file_path, "r") as file:
    for line in file:
        #Remove EOL charaters
        clean_line = line.rstrip("\r\n")
        #File Line ends with UP  UP then print first word in line
        if re.search(r"\bup\s+up\s*$", clean_line):
            interface = clean_line.split()[0]
            print("     " + interface)
print("")
