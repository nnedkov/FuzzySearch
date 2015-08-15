#!/bin/bash

#######################################
#   Filename: pre-commit.sh           #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013		      #
#######################################

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

declare -a FLAGS=(
1 # (1) show options
0 # (2) delete trailing whitespaces from modified files
0 # (3) run pychecker on modified files

### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###
)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

declare -A colors
colors["red"]="\e[0;31m"
colors["blue"]="\e[00;36m"
colors["dark_green"]="\e[00;32m"
colors["yellow"]="\e[01;33m"

function print() {
	if (( $# == 2 )); then
		echo -e "${colors[$1]}$2\e[00m"
	else
		echo -e $1
	fi
}


if (( $# > 0 )); then
	declare -a FLAGS=(0 0 0) ### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###
	for arg do
   		case $arg in
    		1)   ((FLAGS[0]=1));;
    		2)   ((FLAGS[1]=1));;
   		3)   ((FLAGS[2]=1));;

	        ### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###
   		esac
	done
fi

######################################################################################################
# show options

function show_options() {
	print "blue" "\n*** Showing options ***"
	print "(1) show options\n"
	print "(2) delete trailing whitespaces from modified files\n"
	print "(3) run pychecker on modified files\n"

	### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###
}

######################################################################################################
# delete trailing whitespaces from modified files

function delete_trail_whitespaces_modified_files() {
	print "blue" "\n*** Deleting trailing whitespaces from modified files ***"
	FILES=(`git status | awk '$1 == "modified:" { print head$2 }'`)
	for file in ${FILES[@]}; do
		print "dark_green" "Deleting trailing whitespaces from file: $file"
		sed -i '' -e's/[ \t]*$//' $file >& /dev/null
	done
	echo
}

######################################################################################################
# run pychecker on modified files

function check_modified_files() {
	print "blue" "\n*** Running pychecker on modified files ***"
	FILES=(`git status | awk '$1 == "modified:" { print head$2 }'`)
	for file in ${FILES[@]}; do
		print "dark_green" "\nPychecking modified file: $file\n"
		pychecker $file
	done
	echo
}

######################################################################################################

if (( FLAGS[0] == 1 )); then
	show_options
fi

if (( FLAGS[1] == 1 )); then
	delete_trail_whitespaces_modified_files
fi

if (( FLAGS[2] == 1 )); then
	check_modified_files
fi

### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###

