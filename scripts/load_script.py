import sys
import os
import errno
import philologic

from philologic.LoadFilters import *
from philologic.PostFilters import *
from philologic.Parser import Parser
from philologic.ParserHelpers import *
from philologic.Loader import Loader, handle_command_line, setup_db_dir


dbname, files, workers, console_output, log, debug = handle_command_line(sys.argv)


##########################
## System Configuration ##
##########################

# Set the filesytem path to the root web directory for your PhiloLogic install.
database_root = None
# /var/www/html/philologic/ is conventional for linux,
# /Library/WebServer/Documents/philologic for Mac OS.
# Please follow the instructions in INSTALLING before use.

# Set the URL path to the same root directory for your philologic install.
url_root = None 
# http://localhost/philologic/ is appropriate if you don't have a DNS hostname.

if database_root is None or url_root is None:
    print >> sys.stderr, "Please configure the loader script before use.  See INSTALLING in your PhiloLogic distribution."
    exit()

template_dir = database_root + "_system_dir/_install_dir/"
# The load process will fail if you haven't set up the template_dir at the correct location.

# Define text objects for ranked relevancy: by default it's ['doc']. Disable by supplying empty list
default_object_level = 'doc' 

# Data tables to store.
tables = ['words', 'toms', 'pages']

# Define filters as a list of functions to call, either those in Loader or outside
filters = [normalize_unicode_raw_words,make_word_counts, generate_words_sorted,make_object_ancestors('doc', 'div1', 'div2', 'div3'), make_sorted_toms("doc","div1","div2","div3","para"),
           prev_next_obj,generate_pages, make_max_id]
post_filters = [word_frequencies,normalized_word_frequencies,metadata_frequencies,normalized_metadata_frequencies]

# Define text objects to generate plain text files for various machine learning tasks
plain_text_obj = []
if plain_text_obj:
    filters.extend([store_in_plain_text(*plaint_text_obj)])

extra_locals = {"db_url": url_root + dbname}

## Define which search reports to enable
## Note that this can still be configured in your database db_locals.py file
search_reports = ['concordance', 'kwic', 'collocation', 'time_series']
extra_locals['search_reports'] = search_reports
extra_locals['default_object_level'] = default_object_level

###########################
## Set-up database load ###
###########################

Philo_Types = ["doc","div" "para"] # every object type you'll be indexing.  pages don't count, yet.

XPaths =  [("doc","."),("div",".//div1"),("div",".//div2"),("div",".//div3"),("para",".//sp"),("page",".//pb")]         

Metadata_XPaths = [ # metadata per type.  '.' is in this case the base element for the type, as specified in XPaths above.
    # MUST MUST MUST BE SPECIFIED IN OUTER TO INNER ORDER--DOC FIRST, WORD LAST
    ("doc","./teiHeader//titleStmt/title","title"),
    ("doc","./teiHeader//titleStmt/author","author"),
    ("doc", "./text/front//docDate/@value", "date"),
    ("div","./head","head"),
    ("div",".@n","n"),
    ("div",".@id","id"),
    ("para", ".@who", "who"),
    ("page",".@n","n"),
    ("page",".@fac","img")
]

pseudo_empty_tags = ["milestone"]
suppress_tags = ["teiHeader",".//head"]
word_regex = r"([\w]+)"
punct_regex = r"([\.?!])"

token_regex = word_regex + "|" + punct_regex 

extra_locals["word_regex"] = word_regex
extra_locals["punct_regex"] = punct_regex

################################
## Don't edit unless you know ##
## what you're doing          ##
################################

os.environ["LC_ALL"] = "C" # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"
    
db_destination = database_root + dbname
data_destination = db_destination + "/data"
db_url = url_root + dbname

setup_db_dir(db_destination, template_dir)


####################
## Load the files ##
####################

l = Loader(data_destination,
           post_filters=post_filters,
           tables=tables,
           debug=debug)

l.add_files(files)
filenames = l.list_files()
load_metadata = [{"filename":f} for f in sorted(filenames)]
l.parse_files(workers,load_metadata)
l.merge_objects()
l.analyze()
l.make_tables()
l.finish(**extra_locals)

print "\nDone indexing."
print "Your database is viewable at " + db_url + "\n"
