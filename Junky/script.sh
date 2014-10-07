#!/bin/bash
echo "Enter your name: "
read name
echo "Your name is $name"
echo "Enter group: "
read group
echo "Your group is $group"
mkdir $name
cd $name
echo "" > $name.txt

javac -cp .:commons-io-2.4/commons-io-2.4.jar Junk.java MyFrame.java MyJPanel.java MyTailerListener.java Procedure.java & 
java -cp .:commons-io-2.4/commons-io-2.4.jar Junk $name $group
