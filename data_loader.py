import os
from pathlib import Path
import operator

total_opcode_count = 0
opcode_covered = 0
opcode_not_covered = 0


'''
    ######################################################
    Gets all files in a directory - Used when number of 
    directories/files to look into isn't necessarily known
    ######################################################
'''
def get_list_of_files(dir):
    sub_dirs = os.listdir(dir)
    all_files_sub = list()

    for sub_dir in sub_dirs:
        full_path = os.path.join(dir, sub_dir)
        if os.path.isdir(full_path):
            all_files_sub = all_files_sub + get_list_of_files(full_path)
        else:
            all_files_sub.append(full_path)

    return all_files_sub

'''
    
    Counts the number of times each opcode appears, only look at the first x
    opcodes where x = max_opcode_sequence_length
'''
def get_opcode_to_frequency_map(files_looked, num_opcodes_to_use_per_family_per_family, max_opcode_sequence_length):
    opcodes_to_frequency_map = {}
    
    # Look through each family's files
    for family, files in files_looked.items():
        total_num_family_opcodes = 0

        # Look through each file
        file_index = 0
        while file_index < len(files):
            file = files[file_index]
            counter = 0

            with open(file, 'r') as f:
                opcodes = f.readlines()

            # Look at each opcode per file
            opcode_index = 0
            while opcode_index < len(opcodes) and counter <= max_opcode_sequence_length:
                opcode = opcodes[opcode_index].strip()

                if opcode in opcodes_to_frequency_map:
                    opcodes_to_frequency_map[opcode] += 1
                else:
                    opcodes_to_frequency_map[opcode] = 1

                counter += 1
                total_num_family_opcodes += 1
                opcode_index += 1

            file_index += 1

    return opcodes_to_frequency_map

def save_opcode_to_int(opcode_to_int_path, opcode_to_int_map, num_opcodes_to_use_per_family):
    with open(opcode_to_int_path, 'w') as file:
        file.write(str(num_opcodes_to_use_per_family) + "\n")

        for key, value in opcode_to_int_map.items():
            file.write(key + "\n")

# goes through list of all opcodes, find the most common ones and maps most common (the first 0 to num_unique_opcodes)
# opcodes with an int value, all other opcodes assigned a common number (lastKey)
def get_opcode_to_int_map(opcodes_to_frequency_map, num_unique_opcodes):
    sortedOpcodes = sorted(opcodes_to_frequency_map, key=opcodes_to_frequency_map.get, reverse=True)
    opcode_to_int_map = {}

    for i in range(num_unique_opcodes):
        key = sortedOpcodes[i]
        opcode_to_int_map[key] = i

    return opcode_to_int_map

# reads from the most common opcodes in file and creates
# opcode to int mapping
def read_opcode_to_int_file(opcode_to_int_path):
    opcode_to_int_map = {}
    num_opcodes_to_use_per_family = 0

    with open(opcode_to_int_path, 'r') as file:
        opcodes = file.readlines()

    # first line contains number of opcodes to use per family
    num_opcodes_to_use_per_family = opcodes[0].strip()

    for i, opcode in enumerate(opcodes[1:]):
        opcode = opcode.strip()
        opcode_to_int_map[opcode] = i

    return num_opcodes_to_use_per_family, opcode_to_int_map

'''
    ##########################################
    Converts each opcode in specified files to 
    integer based on opcode to integer mapping
    ##########################################
'''

def _getTrainData(family_files, opcode_to_int_map, max_opcode_sequence_length, num_opcodes_to_use_per_family, num_unique_opcodes):
    global total_opcode_count
    global opcode_covered
    global opcode_not_covered

    training_data = list()
    total_num_family_opcodes = 0
    file_index = 0

    while file_index < len(family_files):
        opcode_counter = 0
        file = family_files[file_index]

        with open(file, 'r') as f:
            file_opcodes = list()
            opcode = f.readline()

            while opcode and opcode_counter <= max_opcode_sequence_length:
                opcode = opcode.strip()
                total_opcode_count += 1

                if opcode in opcode_to_int_map:
                    opcode_value = opcode_to_int_map[opcode]
                    opcode_covered += 1
                else:
                    opcode_value = num_unique_opcodes
                    opcode_not_covered += 1
    
                file_opcodes.append(opcode_value)

                opcode = f.readline()
                opcode_counter += 1
                total_num_family_opcodes += 1

        if len(file_opcodes) > 0 and opcode_counter > 100:   # do not add empty lists or lists with small amounts of opcodes
            training_data.append(file_opcodes)

        file_index += 1

    print(len(training_data))
    return training_data

'''
    ###############################################################
    This function returns 2 items:
        1) Gets a frequency mapping between the a family and 
        the number of opcodes available to use for that particular 
        family.

        2) Gets all of the training data file paths for each family
    ###############################################################
'''
def find_most_common_families(data_dir, max_opcode_sequence_length, numFile=4):
    if numFile > 4:
        raise ValueError("The value of numFile cannot be greater than 4")

    most_common_families = {}
    files_looked = {}

    # Navigate through the numbered portions of malware data
    for family_portion in os.listdir(data_dir)[:numFile]:
        full_family_portion_path = os.path.join(data_dir, family_portion)
        
        # Navigate through the families within the numbered folders
        for family in os.listdir(full_family_portion_path):
            full_family_path = os.path.join(full_family_portion_path, family)
            family_opcode_count = 0
            files_in_family = []

            # Navigate through the files in the families
            for file in os.listdir(full_family_path):
                full_file_path = os.path.join(full_family_path, file)
                files_in_family.append(full_file_path)

                with open(full_file_path, 'r') as f:
                    opcodes = f.readlines()
                
                # Only count the first portion of opcodes specified by max_opcode_sequence_length
                if len(opcodes) > max_opcode_sequence_length:
                    family_opcode_count += max_opcode_sequence_length
                else:
                    family_opcode_count += len(opcodes)
            
            files_looked[family] = files_in_family
            # Add family with amount of usable opcodes to map
            most_common_families[family] = family_opcode_count

    most_common_families = {k: v for k, v in sorted(most_common_families.items(), key=lambda item: item[1], reverse=True)}

    print(most_common_families)
    
    return most_common_families, files_looked

# used once - find out how many winwebsec & zbot files to use
# in order to get roughly same number of opcodes
def countNumFilesToUse(data_dir, max_opcode_sequence_length):
    winwebsecData = list()
    zbotData = list()

    # get data for zbot
    zbotFiles = get_list_of_files(data_dir + "renos")
    numZbotOpcodes = 0
    numZbotFiles = 0

    for file in zbotFiles:
        with open(file, 'r') as f:
            opcodes = f.readlines()
            numOpcodes = len(opcodes)

        if numOpcodes >= max_opcode_sequence_length:
            numZbotOpcodes += max_opcode_sequence_length
        else:
            numZbotOpcodes += numOpcodes
        
        numZbotFiles += 1


'''
    ######################################################################
    The main function that is called by the Jupyter Notebooks to load data
    ######################################################################
'''
def getTrainData(data_dir, num_families_to_use, num_unique_opcodes, max_opcode_sequence_length, opcode_to_int_path):
    global total_opcode_count
    global opcode_covered
    global opcode_not_covered
    
    training_data = {}

    # Get the paths to the files used training
    print("Getting list of paths to training data")
    num_family_files = int(num_families_to_use/5)
    most_common_families, files_looked = find_most_common_families(data_dir, max_opcode_sequence_length, num_family_files)
    
    if Path(opcode_to_int_path).is_file():
        num_opcodes_to_use_per_family, opcode_to_int_map = read_opcode_to_int_file(opcode_to_int_path)
        num_opcodes_to_use_per_family = int(num_opcodes_to_use_per_family)
    else:
        # Find out how many opcodes to use per family
        print("Finding out how many opcodes to use per family...")
        keys = list(most_common_families.keys())
        num_opcodes_to_use_per_family = most_common_families[keys[-1]]
        print(num_opcodes_to_use_per_family)

        # Generate txt file containing number of opcodes to use per family and opcode to int mapping
        print("Generating opcode to int mapping...")
        opcodes_to_frequency_map = get_opcode_to_frequency_map(files_looked, num_opcodes_to_use_per_family, max_opcode_sequence_length)
        opcode_to_int_map = get_opcode_to_int_map(opcodes_to_frequency_map, num_unique_opcodes)
        save_opcode_to_int(opcode_to_int_path, opcode_to_int_map, num_opcodes_to_use_per_family)
        print("File saved, done.")

    for family_name, family_files in files_looked.items():
        print("Loading training data for {}".format(family_name))
        training_data[family_name] = _getTrainData(family_files, opcode_to_int_map, max_opcode_sequence_length, num_opcodes_to_use_per_family, num_unique_opcodes) 

    print("All training data loaded")

    print("total opcodes counted: {}".format(total_opcode_count))
    print("total covered: {}".format(opcode_covered))
    print("total not covered: {}".format(opcode_not_covered))
    print("{0}".format(opcode_covered/total_opcode_count))

    return training_data


# data_dir = "data\\"
# num_unique_opcodes = 30
# max_opcode_sequence_length = 2000
# opcode_to_int_path = "opcodeToInt.txt"
# num_families_to_use = 20

# training_data = getTrainData(data_dir, num_families_to_use, num_unique_opcodes, max_opcode_sequence_length, opcode_to_int_path)


def find_most_common_families1(data_dir, numFile=4):
    if numFile > 4:
        raise ValueError("The value of numFile cannot be greater than 4")
    
    num_family_files = int(num_families_to_use/5)
    training_data = {}
    most_common_families = {}
    vocabulary_file_dir = "vocabulary.txt"
    files_looked = {}

    # Navigate through the numbered portions of malware data
    for family_portion in os.listdir(data_dir)[:num_family_files]:
        full_family_portion_path = os.path.join(data_dir, family_portion)
        family_name = ""
        # Navigate through the families within the numbered folders
        for family in os.listdir(full_family_portion_path):
            full_family_path = os.path.join(full_family_portion_path, family)
            family_opcode_count = 0
            family_opcodes = []
            family_name = family

            # Navigate through the files in the families
            for file in os.listdir(full_family_path):
                full_file_path = os.path.join(full_family_path, file)
                files_in_family.append(full_file_path)

                with open(full_file_path, 'r') as f:
                    opcodes = f.readlines()
                
                # Only count the first portion of opcodes specified by max_opcode_sequence_length
                if len(opcodes) > max_opcode_sequence_length:
                    family_opcode_count += max_opcode_sequence_length
                else:
                    family_opcode_count += len(opcodes)
            
            files_looked[family] = files_in_family
            # Add family with amount of usable opcodes to map
            most_common_families[family] = family_opcode_count

    most_common_families = {k: v for k, v in sorted(most_common_families.items(), key=lambda item: item[1], reverse=True)}

    print(most_common_families)
    
    return most_common_families, files_looked


def getTrainData1(data_dir, num_families_to_use, max_opcode_sequence_length):
    num_family_files = int(num_families_to_use/5)
    training_data = {}
    vocabulary_file_dir = "vocabulary.txt"
    most_common_families = {}
    files_looked = {}

    # Navigate through the numbered portions of malware data
    for family_portion in os.listdir(data_dir)[:num_family_files]:
        full_family_portion_path = os.path.join(data_dir, family_portion)
        family_name = ""
        # Navigate through the families within the numbered folders
        for family in os.listdir(full_family_portion_path):
            full_family_path = os.path.join(full_family_portion_path, family)
            family_opcode_count = 0
            family_opcodes = []
            family_name = family
            # Navigate through the files in the families
            for file in os.listdir(full_family_path):
                full_file_path = os.path.join(full_family_path, file)
                opcodes_in_file = []

                with open(full_file_path, 'r') as f:
                    opcodes = f.readlines()

                cleaned_opcodes = []
                for opcode in opcodes:
                    cleaned_opcodes.append(opcode.strip())




                
                # Only count the first portion of opcodes specified by max_opcode_sequence_length
                if len(opcodes) < max_opcode_sequence_length:
                    opcodes_in_file = cleaned_opcodes
                else:
                    opcodes_in_file = cleaned_opcodes[:max_opcode_sequence_length]
            
            family_opcodes.append(opcodes_in_file)
        training_data[family_name] = family_opcodes

    return training_data

# data_dir = "data\\"
# num_families_to_use = 5
# max_opcode_sequence_length = 2000

# f = getTrainData1(data_dir, num_families_to_use, max_opcode_sequence_length)

# print(f)