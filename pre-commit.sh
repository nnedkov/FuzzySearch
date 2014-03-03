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
0 # (3) plot the graphs
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
	print "(3) plot the graphs\n"
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
# plot the graphs

function plot_graphs() {
	print "blue" "\n*** Starting to plot graphs ***"
	declare -a COLLECTIONS=("english_words" "inspire_authors" "imdb_actors_directors")
	for collection in ${COLLECTIONS[@]}; do
		slash="_"
		plotdata="average_pruning_capacity"
		print "dark_green" "\nPlotting graph: ./plots/$collection/$plotdata/$plotdata.png"
		gnuplot <<- EOF
			set terminal pdf monochrome solid font 'Helvetica,16' size 9cm,7cm
			set output "./plots/$collection/$plotdata/$collection$slash$plotdata.pdf"
			set xlabel "ED threshold"
			set ylabel "Average pruning\ncapacity"
			set xrange [0:4]
			set yrange [0:140]
			set ytics ("" 0, "20%%" 20, "40%%" 40, "60%%" 60, "80%%" 80, "100%%" 100, "" 120)
			set pointsize 1.6
			plot "./plots/$collection/$plotdata/$plotdata.txt" using 1:2:xtic(1) title "char-map filter" with linespoints lt 1 lc rgb "black" pt 5, \
			     "./plots/$collection/$plotdata/$plotdata.txt" using 1:3:xtic(1) title "position filter" with linespoints lt 2 lc rgb "black" pt 9
			quit
		EOF
		echo /home/nedko/Repositories/thesis.git/plots /home/nedko/Repositories/article.git/plots | xargs -n 1 cp ./plots/$collection/$plotdata/$collection$slash$plotdata.pdf
		plotdata="average_filter_performance_boost"
		print "dark_green" "Plotting graph: ./plots/$collection/$plotdata/$plotdata.png"
		gnuplot <<- EOF
			set terminal pdf monochrome solid font 'Helvetica,16' size 9cm,7cm
			set output "./plots/$collection/$plotdata/$collection$slash$plotdata.pdf"
			set xlabel "ED threshold"
			set ylabel "Average filter\nspeed-up"
			set format y '%2.0f%%'
			set yrange [0:120]
			set xtics ("" 0, "1" 1, "2" 2, "3" 3, "" 4)
			set ytics ("" 0, "20%%" 20, "40%%" 40, "60%%" 60, "80%%" 80, "100%%" 100, "" 120)
			set style fill solid 0.8 border -1
			set boxwidth 0.5 relative
			plot "./plots/$collection/$plotdata/$plotdata.txt" using 1:2 title "" with boxes lc rgb "royalblue"
			quit
		EOF
		echo /home/nedko/Repositories/thesis.git/plots /home/nedko/Repositories/article.git/plots | xargs -n 1 cp ./plots/$collection/$plotdata/$collection$slash$plotdata.pdf
		plotdata="average_overall_performance_boost"
		print "dark_green" "Plotting graph: ./plots/$collection/$plotdata/$plotdata.png"
		gnuplot <<- EOF
			set terminal pdf monochrome solid font 'Helvetica,16' size 9cm,7cm
			set output "./plots/$collection/$plotdata/$collection$slash$plotdata.pdf"
			set xlabel "ED threshold"
			set ylabel "Average overall\nspeed-up"
			set format y '%2.0f%%'
			set yrange [0:120]
			set xtics ("" 0, "1" 1, "2" 2, "3" 3, "" 4)
			set ytics ("" 0, "20%%" 20, "40%%" 40, "60%%" 60, "80%%" 80, "100%%" 100, "" 120)
			set style fill solid 0.8 border -1
			set boxwidth 0.5 relative
			plot "./plots/$collection/$plotdata/$plotdata.txt" using 1:2 title "" with boxes lc rgb "orange"
			quit
		EOF
		echo /home/nedko/Repositories/thesis.git/plots /home/nedko/Repositories/article.git/plots | xargs -n 1 cp ./plots/$collection/$plotdata/$collection$slash$plotdata.pdf
	done
	echo

# set terminal postscript
# set output '| ps2pdf - ./plots/$collection/$plotdata/$collection$slash$plotdata.pdf'

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

