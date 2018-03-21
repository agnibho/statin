'''
Copyright (c) 2018 Agnibho Mondal
All rights reserved

This file is part of Statin.

Statin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Statin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Statin.  If not, see <http://www.gnu.org/licenses/>.
'''

from datetime import datetime
from glob import glob
from os import path, unlink, makedirs
from shutil import copyfile, rmtree, copytree, ignore_patterns
from subprocess import run, PIPE
import argparse
import re
import tempfile

from statin.conf import *

# Global variables
conflist = {"timefmt": TIMEFMT, "sizefmt": SIZEFMT, "errmsg": ERRMSG}
varlist = {}
varlist["DATE_LOCAL"] = datetime.now().strftime(conflist["timefmt"])
varlist["DATE_GMT"] = datetime.utcnow().strftime(conflist["timefmt"])
openif = False
ifstatus = False
ifskip = False

# Start script
def main():
    global args
    global OUTPUT_DIR, PROCESS_PATT, MAX_RECURSION
    PROCESS_PATT = set(PROCESS_PATT)

    #Parse arguments
    parser = argparse.ArgumentParser(description="Generate static html files")
    verbo = parser.add_mutually_exclusive_group()
    verbo.add_argument("-q", "--quiet", help="suppress text output to console", action="store_true")
    verbo.add_argument("-v", "--verbose", help="verbose text output to console", action="store_true")
    parser.add_argument("-s", "--safe", help="disable python eval and cmd exec", action="store_true")
    parser.add_argument("-r", "--recursive", help="process files recursively", action="store_true")
    parser.add_argument("-l", "--level", help="maximum recursion level", type=int)
    parser.add_argument("-c", "--after", help="run command after processing file")
    parser.add_argument("-C", "--before", help="run command before processing file")
    parser.add_argument("-p", "--pattern", help="filename patterns to be processed", action="append")
    parser.add_argument("-o", "--output", help="specify the output directory")
    parser.add_argument("files", help="list of files to be processed", nargs="*")
    args = parser.parse_args()

    # Reassign variables from option
    if(args.level != None):
        MAX_RECURSION = args.level
    if(args.pattern != None):
        PROCESS_PATT = PROCESS_PATT.union(args.pattern)
    if(args.output != None):
        if(args.output[-1:] != "/"):
            args.output = args.output + "/"
        if(args.output[:2] != "./" and args.output[:1] != "/"):
            args.output = "./" + args.output
        OUTPUT_DIR = args.output

    # List all files to be processed
    filelist = []
    if(args.files):
        filelist = args.files
    else:
        for patt in PROCESS_PATT:
            filelist.extend(glob(patt))

    # Purge output directory and rebuild if specific filenames not supplied
    if(not args.files):
        rmtree(OUTPUT_DIR, True)
        copytree(".", OUTPUT_DIR, ignore=ignore_patterns(*PROCESS_PATT))
        if(not args.quiet):
            print("Contents copied to " + OUTPUT_DIR + "\n")
    else:
        makedirs(OUTPUT_DIR, exist_ok=True)

    # Send each file for processing
    for filename in filelist:
        if(not args.quiet):
            print("Processing '" + filename + "'")
        outfile = OUTPUT_DIR + path.splitext(path.basename(filename))[0] + ".html"
        temp = []
        fdir = path.dirname(path.realpath(filename))
        orig = filename

        # Run before-commands
        if(args.before):
            if(args.verbose):
                print("Running " + args.before)
            tf = tempfile.NamedTemporaryFile(delete = False)
            tf.close()
            copyfile(filename, tf.name)
            filename = tf.name
            try:
                with open(tf.name) as f:
                    p = run(args.before, shell = True, input = f.read(), stdout = PIPE, encoding = "utf-8")
                with open(tf.name, "w") as f:
                    if(p.returncode == 0):
                        f.write(p.stdout)
            except FileNotFoundError:
                if(not args.quiet):
                    print(args.before + ": command not recognized")
            except:
                if(args.verbose):
                    print(args.before + ": command failed")

        # Handle recursion
        if(args.recursive):
            if(not args.quiet):
                print("Creating temporary files")
            rlvl = 0
            temp.append(tempfile.NamedTemporaryFile(delete = False))
            temp[-1].close()
            temp.append(tempfile.NamedTemporaryFile(delete = False))
            temp[-1].close()
            copyfile(filename, temp[0].name)
            if(args.verbose):
                print("'" + filename + "' copied to '" + temp[0].name + "'")
            if(args.verbose):
                print("Processing '" + temp[0].name + "' to '" + temp[1].name + "'")
            while(rlvl < MAX_RECURSION and not process_file(temp[0].name, temp[1].name, directory = fdir, original = orig)):
                temp.append(tempfile.NamedTemporaryFile(delete = False))
                temp[-1].close()
                unlink(temp.pop(0).name)
                if(args.verbose):
                    print("Processing '" + temp[0].name + "' to '" + temp[1].name + "'")
                rlvl += 1
            if(not args.quiet and rlvl >= MAX_RECURSION):
                print("Maximum recursion level reached")
            copyfile(temp[0].name, outfile)
            if(not args.quiet):
                print("Output saved to '" + outfile + "'")
            if(not args.quiet):
                print("Cleaning up temporary files")
            for t in temp:
                unlink(t.name)
        # Simple processing
        else:
            process_file(filename, outfile, directory = fdir, original = orig)
            if(not args.quiet):
                print("Output saved to '" + outfile + "'")

        # Clean-up
        try:
            if(tf):
                unlink(tf.name)
        except:
            pass

        # Run after-commands
        if(args.after):
            if(args.verbose):
                print("Running " + args.after)
            try:
                with open(outfile) as f:
                    p = run(args.after, shell = True, input = f.read(), stdout = PIPE, encoding = "utf-8")
                with open(outfile, "w") as f:
                    if(p.returncode == 0):
                        f.write(p.stdout)
            except FileNotFoundError:
                if(not args.quiet):
                    print(args.after + ": command not recognized")
            except:
                if(args.verbose):
                    print(args.after + ": command failed")

# Process the file
def process_file(filename, outfile, directory, original):
    global args
    global openif, ifstatus, ifskip

    # Assign variable values
    no_directive = True

    try:
        varlist["DOCUMENT_URI"] = original
        varlist["DOCUMENT_NAME"] = path.basename(original)
        varlist["LAST_MODIFIED"] = datetime.fromtimestamp(path.getmtime(original)).strftime(conflist["timefmt"])
        with open(filename) as src, open(outfile, "w") as out:
            for line in src:
                line = re.split("(<!--#.+-->)", line)
                for item in line:
                    if(item.strip()):
                        if(item.strip()[:5] == "<!--#"):
                            no_directive = False
                            item = process_directive(item.strip()[5:][:-3].strip(), original = original, directory = directory)
                        if(not ifskip and (not openif or ifstatus)):
                            out.write(str(item))
        if(openif and not args.quiet):
            print("Error: Unexpected end of file reached. Expecting 'endif'.")
    except FileNotFoundError as e:
        if(not args.quiet):
            print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
    except IsADirectoryError as e:
        if(not args.quiet):
            print("Error: can't process directory '" + e.filename + "'. Please provide file names only.")

    return(no_directive)

# Process the directives
def process_directive(line, original, directory):
    global args
    global varlist, conflist
    global openif, ifstatus, ifskip

    if(args.verbose):
        print("  Processing directive : "+line)

    # Tokenize directives
    line = re.split('''\s(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)
    directive = line.pop(0);
    params = {}
    for pair in line:
        pair = re.split('''=(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', pair)
        params[pair[0]] = pair[1][1:-1]

    # Parse conditionals
    if(directive == "if"):
        openif = True
        try:
            ifstatus = (evaluate_expression(params["expr"]) == True)
        except KeyError:
            if(args.verbose):
                print("  Error: no expression to process")
            return(conflist["errmsg"])
        return("")
    elif(directive == "elif"):
        if(ifskip):
            return("")
        if(ifstatus):
            ifskip = True
        else:
            try:
                ifstatus = (evaluate_expression(params["expr"]) == True)
            except KeyError:
                if(args.verbose):
                    print("  Error: no expression to process")
                return(conflist["errmsg"])
        return("")
    elif(directive == "else"):
        if(ifskip):
            return("")
        ifskip = ifstatus
        ifstatus = not ifstatus
        return("")
    elif(directive == "endif"):
        openif = False
        ifskip = False
        return("")

    # Skip if conditional false
    if(ifskip or (openif and not ifstatus)):
        return("")

    # Parse directives
    if(directive == "include"):
        try:
            with open(params["virtual"]) as f:
                return(f.read())
        except KeyError:
            pass
        except FileNotFoundError as e:
            if(not args.quiet):
                print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
        try:
            with open(directory + "/" + params["file"]) as f:
                return(f.read())
        except KeyError:
            pass
        except FileNotFoundError as e:
            if(not args.quiet):
                print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
        if(args.verbose):
            print("  Error: no file to include")
        return(conflist["errmsg"])
    elif(directive == "exec"):
        if(args.safe):
            if(args.verbose):
                print("  Can't execute command in safe mode")
            return(conflist["errmsg"])
        try:
            return(run(params["cmd"], shell = True, stdout = PIPE, encoding = "utf-8").stdout)
        except KeyError:
            pass
        try:
            return(run(params["cgi"], shell = True, stdout = PIPE, encoding = "utf-8").stdout)
        except KeyError:
            pass
        if(args.verbose):
            print("  Error: no command to execute")
        return(conflist["errmsg"])
    elif(directive == "echo"):
        try:
            return(varlist[params["var"]])
        except KeyError:
            if(args.verbose):
                print("  Error: no variable to display")
            return(conflist["errmsg"])
    elif(directive == "config"):
        conflist.update(params)
        varlist["DATE_LOCAL"] = datetime.now().strftime(conflist["timefmt"])
        varlist["DATE_GMT"] = datetime.utcnow().strftime(conflist["timefmt"])
        varlist["LAST_MODIFIED"] = datetime.fromtimestamp(path.getmtime(original)).strftime(conflist["timefmt"])
    elif(directive == "flastmod"):
        try:
            return(datetime.fromtimestamp(path.getmtime(params["virtual"])).strftime(conflist["timefmt"]))
        except KeyError:
            pass
        except FileNotFoundError as e:
            if(not args.quiet):
                print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
                return(conflist["errmsg"])
        try:
            return(datetime.fromtimestamp(path.getmtime(directory + "/" + params["file"])).strftime(conflist["timefmt"]))
        except KeyError:
            pass
        except FileNotFoundError as e:
            if(not args.quiet):
                print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
                return(conflist["errmsg"])
        if(args.verbose):
            print("  Error: missing filename")
        return(conflist["errmsg"])
    elif(directive == "fsize"):
        idx = { "B":1, "KB":1024, "MB":1048576, "GB":1073741824, "TB":1099511627776, "b":1, "kb":1024, "mb":1048576, "gb":1073741824, "tb":1099511627776, "bytes":1, "kilobytes":1024, "megabytes":1048576, "gigabytes":1073741824, "terabytes":1099511627776 }
        if(conflist["sizefmt"] == "abbrev"):
            conflist["sizefmt"] = "kb"
        if(not conflist["sizefmt"] in idx):
            if(args.verbose):
                print("  Error: invalid size format")
            return(conflist["errmsg"])
        try:
            return("{0:.2f}".format(path.getsize(params["virtual"]) / idx[conflist["sizefmt"]]) + " " + conflist["sizefmt"])
        except KeyError:
            pass
        except FileNotFoundError as e:
            if(not args.quiet):
                print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
                return(conflist["errmsg"])
        try:
            return("{0:.2f}".format(path.getsize(directory + "/" + params["file"]) / idx[conflist["sizefmt"]]) + " " + conflist["sizefmt"])
        except KeyError:
            pass
        except FileNotFoundError as e:
            if(not args.quiet):
                print("Error: file '" + e.filename + "' could not be found. Please check if the file exists.")
                return(conflist["errmsg"])
        if(args.verbose):
            print("  Error: missing filename")
        return(conflist["errmsg"])
    elif(directive == "printenv"):
        return(varlist)
    elif(directive == "set"):
        try:
            varlist[params["var"]] = evaluate_expression(params["value"])
        except KeyError:
            if(args.verbose):
                print("  Error: missing variable or value")
            return(conflist["errmsg"])
    else:
        if(args.verbose):
            print("  Error: unrecognized directive")
        return(conflist["errmsg"])
    return("")

# Expression evaluation
def evaluate_expression(expr):
    global args
    expr = str(expr)
    if(args.safe):
        if(args.verbose):
            print("  Can't evaluate expression in safe mode")
        return(conflist["errmsg"])
    try:
        m=re.findall("\$\{*[^\}\s=><!+\-*/^%]+\}*", expr)
        for v in m:
            expr = expr.replace(v, str(varlist[v.replace("$", "").replace("{", "").replace("}", "")]))
    except Exception:
        pass
    expr = re.sub("([\w\s]+)", r"'\1'", expr)
    expr = re.sub("'([\d]+)'", r"\1", expr)
    try:
        return(eval(expr))
    except Exception:
        return(re.sub("'([\w\s]+)'", r"\1", expr))

if(__name__ == "__main__"):
    main()
