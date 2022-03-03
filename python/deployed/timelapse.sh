#! /bin/bash
echo "loading image capture.. please wait a while.."
echo

echo -ne '############\r'
sleep 2
echo -ne '########### \r'
sleep 2

echo -ne '##########  \r'
sleep 2
echo -ne '#########   \r'
sleep 1
echo -ne '########    \r'
sleep 1
echo -ne '#######     \r'
sleep 1
echo -ne '######      \r'
sleep 1
echo -ne '#####       \r'
sleep 1
echo -ne '####        \r'
sleep 1
echo -ne '##          \r'
sleep 1
echo -ne '#           \r'
sleep 1
echo -ne '            \r'


./report.py

echo
echo -ne 'Python finished!           \r'
sleep 55
