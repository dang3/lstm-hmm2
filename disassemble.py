import sys
import subprocess
import os
import threading as thread

def main(args):
    exe_dir = args[1]
    output_dir = args[2]
    threads = []

    # Use multithreading to speed up disassembling, each thread handles a portion of files to be disassembled
    for count,folder_name in enumerate(os.listdir(exe_dir)):
        threadx = thread.Thread(target=process, args=("Thread " + str(count), exe_dir, folder_name, output_dir))
        threads.append(threadx)
        threadx.start()

    for threadx in threads:
        threadx.join()

    print("\n\n*****Done*****\n\n")

def process(thread_name, exe_dir, folder_name, output_dir): 
    file_directory = os.path.join(exe_dir, folder_name)

    for counter, file_name in enumerate(os.listdir(file_directory)):
        # Show progress
        if counter % 10 == 0:
            num_files = len(os.listdir(file_directory))
            print(thread_name + "- Iteration: " + str(counter) + " out of " + str(num_files))
            
        try:
            # Disassemble the file
            full_file_path = os.path.join(file_directory, file_name)

            # Isolate opcodes from objdump
            res1 = subprocess.Popen(["objdump", "-d", full_file_path], stdout=subprocess.PIPE)
            res2 = subprocess.Popen(["sed", '/[^\t]*\t[^\t]*\t/!d'], stdin=res1.stdout, stdout=subprocess.PIPE)
            res3 = subprocess.Popen(["cut", "-f", "3"], stdin=res2.stdout, stdout=subprocess.PIPE)
            res4 = subprocess.Popen(["sed", 's/ .*$//'], stdin=res3.stdout, stdout=subprocess.PIPE)
            res5 = subprocess.Popen(["sed", '/(bad)/d'], stdin=res4.stdout, stdout=subprocess.PIPE)
            
            out, err = res5.communicate()

            # Check if output file directory exists
            output_file_path = os.path.join(output_dir, folder_name, file_name) + ".txt"
            if not os.path.exists(output_dir + "/" + folder_name):
                os.makedirs(output_dir + "/" + folder_name)

            # Write to file
            with open(output_file_path, "wb") as file:
                file.write(out)
        except Exception as e:
            print(thread_name + "- error with file: " + file_name + ", skipping")
            print(thread_name + "- error details: " + str(e))


if __name__ == "__main__":
    main(sys.argv)