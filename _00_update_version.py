import sys

open("version.txt", "w").write(sys.argv[-1])
spec_replacement=str(open("_00_GUI.spec", "r").readlines()).replace(r'name=''\'_00_GUI\'''', r'name=''\'{}\''''.format(sys.argv[-1]))
open("_00_GUI.spec", "w").writelines(eval(spec_replacement))