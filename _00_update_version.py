import sys

open("version.txt", "w").write(sys.argv[-1])

spec_replacement=str(open("_00_GUI.spec", "r").readlines()).replace(r'name=''\'_00_GUI\'''', r'name=''\'GUI_{}\''''.format(sys.argv[-1]))
open("_00_GUI.spec", "w").writelines(eval(spec_replacement))

spec_replacement=str(open("_00_GUI.spec", "r").readlines()).replace(r'dist/_00_CLI', r'dist/CLI_{}'.format(sys.argv[-1]))
open("_00_GUI.spec", "w").writelines(eval(spec_replacement))

spec_replacement=str(open("_00_CLI.spec", "r").readlines()).replace(r'name=''\'_00_CLI\'''', r'name=''\'CLI_{}\''''.format(sys.argv[-1]))
open("_00_CLI.spec", "w").writelines(eval(spec_replacement))