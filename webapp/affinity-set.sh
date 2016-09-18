NOW=0

sleep 10
for i in `ps ax | grep gunicorn | grep -v grep | sort -k1 -n | cut -c 1-5`
do
if [ $NOW -eq 0 ]
then
taskset -p -c 0 $i
NOW=1
else
taskset -p -c 1 $i
NOW=0
fi
done
