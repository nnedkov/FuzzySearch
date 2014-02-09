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
0 # (3) plot graphs
0 # (4) run pychecker on modified files

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
	declare -a FLAGS=(0 0 0 0) ### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###
	for arg do
   		case $arg in
    		1)   ((FLAGS[0]=1));;
    		2)   ((FLAGS[1]=1));;
   		3)   ((FLAGS[2]=1));;
		4)   ((FLAGS[3]=1));;

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
	print "(3) plot graphs\n"
	print "(4) run pychecker on modified files\n"

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
# run pychecker on modified files

function plot_graphs() {
	print "blue" "\n*** Starting to plot graphs ***"
	plotdata=length_clusters
	print "dark_green" "\nPlotting graph: plots/$plotdata.png"
	gnuplot <<- EOF
		set terminal png enhanced \
			font "/Library/Fonts/Verdana.ttf" 18  \
			size 2*350, 2*250
		set output "plots/$plotdata.png"
		set title "Length clusters of the string collection"
		set xlabel "Length clusters"
		set ylabel "Cluster size"
		set style fill solid 0.8 border -1
		set boxwidth 0.5 relative
		plot "plots/input/$plotdata.txt" using 1:2 title "" with boxes lc rgb "red"
		quit
	EOF

	declare -a THRESHOLDS=("5" "15" "25" "35" "45" "55")
	for threshold in ${THRESHOLDS[@]}; do
		plotdata="pruning_capacity_"
		print "dark_green" "Plotting graph: plots/$plotdata$threshold.png"
		gnuplot <<- EOF
			set terminal png enhanced \
				font "/Library/Fonts/Verdana.ttf" 18  \
				size 2*350, 2*250
			set output "plots/$plotdata$threshold.png"
			set xlabel "Query string length"
			set ylabel "Average pruning capacity"
			set format y '%2.0f%%'
			set yrange [60:100]
			plot "plots/input/$plotdata$threshold.txt" using 1:3:xtic(2) title "char-map filter" with linespoints, \
			     "plots/input/$plotdata$threshold.txt" using 1:4:xtic(2) title "position filter" with linespoints
			quit
		EOF
		plotdata="average_boost_"
		print "dark_green" "Plotting graph: plots/$plotdata$threshold.png"
		gnuplot <<- EOF
			set terminal png enhanced \
				font "/Library/Fonts/Verdana.ttf" 18 \
				size 2*350, 2*250
			set output "plots/$plotdata$threshold.png"
			set xlabel "Query string length"
			set ylabel "Average performance boost"
			set format y '%2.0f%%'
			set yrange [0:100]
			set style fill solid 0.8 border -1
			set boxwidth 0.5 relative
			plot "plots/input/$plotdata$threshold.txt" using 1:2 title "" with boxes lc rgb "blue"
			quit
		EOF
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
	plot_graphs
fi

if (( FLAGS[3] == 1 )); then
	check_modified_files
fi

### WHEN ADDING NEW FUNCTIONALITY TOUCH HERE ###

