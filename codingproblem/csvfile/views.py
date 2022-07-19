# Import necessary packages
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Import database models
from .models import FileDescription

# Import packages to read csv files
import pandas as pd
import os


def index(request):
    return HttpResponse("csvfile")


# ================
# Units dictionary
# ================
units_dict = {"K":1e3,
              "M":1e6,
              "G":1e9}


# ================
# Search file view
# ================
def search_file(request):
    '''View that allows to search the content of the csv file. '''

    # Declare list of entries found by a query
    entry_list = []

    # Initialize the dictionary that will be passed to the HTML content
    context = initialize_html_dict()

    # Look for a potential request/query from a user
    if request.method == "POST":

        # Read a csv file
        if "read_file" in request.POST:
            context = read_file(request.POST["read_file"], context)

        # Search database by file name
        elif "searched_file_name" in request.POST:
            entry_list, context = \
                    search_name(request.POST["searched_file_name"], context)
            
        # Search database by file path
        elif "searched_file_path" in request.POST:
            entry_list, context = \
                    search_path(request.POST["searched_file_path"], context)

        # Search database by file extension
        elif "searched_file_extension" in request.POST:
            entry_list, context = \
                    search_extension(request.POST["searched_file_extension"], context)

        #  Search database by file size
        elif "searched_file_size" in request.POST:
            entry_list, context = \
                    search_size(request.POST["searched_file_size"], context)

    # Add the list of entries if any to the HTML dictionary
    context["entry_list"] = entry_list

    # Render the search file results
    return render(request, 'csvfile/search_file.html', context)


# ==========================
# Initialize HTML dictionary
# ==========================
def initialize_html_dict():

    '''

    Initialize and return the dictionary that will be passed 
    to the HTML content.

    '''

    # Declare the dictionarr
    context = {}

    # Add info on whether the database has entries
    if FileDescription.objects.count() == 0:
        context["read_warning"] = "Empty database. Please load data."
    else:
        context["read_warning"] = "Data loaded."

    # Return the dictionary
    return context


# =========
# Read file
# =========
def read_file(csv_file_path, context):

    '''

    Read csf file, add data to the database, and add warnings
    to the HTML dictionary.

    Arguments
    =========
        csv_file_path (str): Path to the csv file
        context (dict): HTML dictionary

    '''

    # Delete current database from previous csv file
    FileDescription.objects.all().delete()

    # If the csv file exists ..
    if os.path.isfile(csv_file_path):

        # Try to load data
        try:

            # Convert csv file into a Pandas DataFrame
            data = pd.read_csv(csv_file_path, sep=',')
            data = restructure_data(data)

            # For each row (entry) in the csv file ..
            for i_row in range(data.shape[0]):

                # Create an entry for the FileDescription object
                row = FileDescription(file_name = data["FileName"][i_row],
                                      file_path = data["FilePath"][i_row],
                                      file_extension = data["FileExtension"][i_row],
                                      size = data["Size"][i_row],
                                      uniform_size = data["UniformSize"][i_row])

                # Add entry to the Django database
                row.save()

            # Generate success message
            context["read_warning"] = "Data loaded from '"+csv_file_path+"'."

        # Generate error message if something went wrong during the reading
        except:
            context["read_warning"] = \
                "Error - The csv file '"+csv_file_path+"' has structure issues. No data loaded."

    # Generate error message if the csv file does not exist ..
    else:
        context["read_warning"] = \
            "Error - The csv file '"+csv_file_path+"' does not exist. No data loaded."

    # Return the updated HTML dictionary
    return context


# ===========
# Search name
# ===========
def search_name(searched, context):

    '''

    Filter the database based on the file name, and add warnings
    to the HTML dictionary.

    Arguments
    =========
        searched (str): String that should appear in the file name
        context (dict): HTML dictionary

    '''

    # Abord the search if necessary
    should_go, context = pre_query_check(searched, context)
    if not should_go:
        return [], context

    # Filter the database
    entry_list = FileDescription.objects.filter(file_name__contains=searched)

    # Generate query info
    context["query"] = format_query(len(entry_list), searched + " contained in FileName")

    # Return the results of the search
    return entry_list, context


# ===========
# Search path
# ===========
def search_path(searched, context):

    '''

    Filter the database based on the file path, and add warnings
    to the HTML dictionary.

    Arguments
    =========
        searched (str): String that should appear in the file path
        context (dict): HTML dictionary

    '''

    # Abord the search if necessary
    should_go, context = pre_query_check(searched, context)
    if not should_go:
        return [], context

    # Filter the database
    entry_list = FileDescription.objects.filter(file_path__contains=searched)

    # Generate query info
    context["query"] = format_query(len(entry_list), searched + " contained in FilePath")

    # Return the results of the search
    return entry_list, context


# ================
# Search extension
# ================
def search_extension(searched, context):

    '''

    Filter the database based on the file extension, and add warnings
    to the HTML dictionary.

    Arguments
    =========
        searched (str): String that should exactly match in the file extension
        context (dict): HTML dictionary

    '''

    # Abord the search if necessary
    should_go, context = pre_query_check(searched, context)
    if not should_go:
        return [], context

    # Remove "." from the searched extension if necessary
    if len(searched) > 0:
        if searched[0] == ".":
            searched = searched [1:]

    # Filter the database
    entry_list = FileDescription.objects.filter(file_extension=searched)

    # Generate query info
    context["query"] = format_query(len(entry_list), searched + " for FileExtension")

    # Return the results of the search
    return entry_list, context


# ===========
# Search size
# ===========
def search_size(searched, context):

    '''

    Filter the database based on the file size, and add warnings
    to the HTML dictionary.

    Arguments
    =========
        searched (str): String that includes a conditon on the file size
        context (dict): HTML dictionary

    '''

    # Abord the search if necessary
    should_go, context = pre_query_check(searched, context)
    if not should_go:
        return [], context

    # Split searched string into [operator, uniform_digit]
    try:
        operator, uniform_digit = extract_operator(searched)

    # Exit function if something went wrong
    except:
        context["query"] = "Error - Query not formatted correctly."
        return [], context

    # Filter the database
    entry_list = apply_size_operator(operator, uniform_digit)

    # Generate query info
    context["query"] = format_query(len(entry_list), searched + " for FileExtension")

    # Return the results of the search
    return entry_list, context


# ===============
# Pre-query check
# ===============
def pre_query_check(searched, context):

    '''

    Check whether a database filter should be allowed to proceed, based
    on whether the database is empty or whether the search is valid. The
    function returns False if the filter should be avoid, along with the
    HTML dictionary to print warnings.

    Arguments
    =========
        searched (str): String representing the search from a user
        context (dict): HTML dictionary

    '''

    # Warning if the database if empty
    if FileDescription.objects.count() == 0:
        context["query"] = "Empty database."
        return False, context

    # Warning if the query is empty
    if searched == "":
        context["query"] = "Empty query."
        return False, context

    # Return True if nothing wrong was detected
    return True, context


# ============
# Format query
# ============
def format_query(nb_entry, query_str):

    '''

    Return the string to be printed in the query results section.

    Arguments
    =========
        nb_entry (int): Number of entries
        query_str (str): Description of the original query

    '''

    # Format entry string if more than 1 entries
    if nb_entry > 1:
        entry_str = str(nb_entry) + " entries"

    # Format entry string if 0 or 1 entry
    else:
        entry_str = str(nb_entry) + " entry"

    # Return the formatted query
    return entry_str + " found for (" + query_str + ")"


# =======================
# Restructure Pandas data
# =======================
def restructure_data(data):
    
    '''
    
    Loop over Pandas' DataFrame entries in order to remove
    file names from the file paths, uniform units for file
    sizes, and add file extention to DataFrame.
    
    Argument
    ========
        data (DataFrame): CSV file read using Pandas
    
    '''
    
    # Define the list of file extensions and uniform sizes
    file_extension_list = []
    uniform_size_list = []
    
    # For each row in the DataFrame ..
    for i_row in range(data.shape[0]):
        
        # Collect the file extension
        file_extension_list.append(data["FileName"][i_row].split(".")[-1])
        
        # Remove the file name from the file path
        data["FilePath"][i_row] = data["FilePath"][i_row].replace(data["FileName"][i_row],'')
        
        # Convert file size into bytes
        digit = data["Size"][i_row][:-1]
        units = data["Size"][i_row][-1].capitalize()
        uniform_size_list.append(float(digit) * units_dict[units])
        
    # Add file extensions and uniform sizes to the DataFramee
    data["FileExtension"] = file_extension_list
    data["UniformSize"] = uniform_size_list

    # Return the extended DataFrame
    return data


# ================
# Extract operator
# ================
def extract_operator(searched):

    '''

    Take an input query string and extract the operator and the
    uniform digit (e.g. > 2M should return ">", 2 000 000).

    Arguments
    =========
        searched (str): String that includes a conditon on the file size

    '''

    # Extract operator
    if "==" in searched:
        operator = "=="
    elif "<=" in searched:
        operator = "<="
    elif "<" in searched:
        operator = "<"
    elif ">=" in searched:
        operator = ">="
    elif ">" in searched:
        operator = ">"

    # Extract the digit and units
    digit_units = searched.split(operator)[-1]
    digit = float(digit_units[:-1])
    units = digit_units[-1].capitalize()

    # Uniform the units
    digit = digit * units_dict[units]

    # Return the extraction
    return operator, digit


# ===================
# Apply size operator
# ===================
def apply_size_operator(operator, digit):

    '''

    Filter the database based on an operation on the file size.

    Argument
    ========
    operator (str): Logic condition operator
    digit (float): Number to which size will be compared

    '''

    # Equal ==
    if operator == "==":
        return FileDescription.objects.filter(uniform_size=digit)

    # Less than <
    elif operator == "<":
        return FileDescription.objects.filter(uniform_size__lt=digit)

    # Less than or equal <=
    elif operator == "<=":
        return FileDescription.objects.filter(uniform_size__lte=digit)

    # Greater than >
    elif operator == ">":
        return FileDescription.objects.filter(uniform_size__gt=digit)

    # Greater than or equel >=
    elif operator == ">=":
        return FileDescription.objects.filter(uniform_size__gte=digit)

    # Safety net in case the operator is not recognized
    return []
