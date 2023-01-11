from os import system

with open("deploy.sh", "r") as file:
    lines = file.readlines()
    env_line = None
    for line in lines:
        if (" env " in line) and ("--image" in line):
            env_line = line

    env_words = env_line.split()
    image_index = env_words.index("--image") + 1
    image_name = env_words[image_index]

system(f"docker build -t {image_name} .")
system(f"docker push {image_name}")

print(f"Image {image_name} published with success.")
while True:
    answer = input("\nRemove docker image from computer? (y or n)").strip().lower()
    if answer == "y":
        system(f"docker image rm {image_name}")
        print("Removed!")
        break
    elif answer == "n":
        break
