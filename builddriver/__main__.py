import sys
import builddriver


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('command missing, exiting\n')
        sys.exit(1)

    cmd = " ".join(sys.argv[1:])
    sys.stderr.write('builddriver executing: \'{}\'\n'.format(cmd))
    ret = builddriver.execute(cmd)
    retcode = ret.returncode()
    if retcode == 0:
        msg = 'Compilation SUCCEED in {} seconds\n'
    else:
        msg = 'Compilation FAILED in {} seconds\n'
    sys.stderr.write(msg.format(ret.build_duration().total_seconds()))
    sys.stderr.write('Number of warnings: {}\n'.format(ret.warnings_no()))
    if ret.errors_no() > 0:
        sys.stderr.write('Number of errors: {}\n'.format(ret.errors_no()))
        error = list(ret.errors())[-1]
        sys.stderr.write('Last Error:\n  Message: \"{}\"\n'.format(error.message))
        sys.stderr.write('  Path: {}\n'.format(error.path))
        sys.stderr.write('  Line Number: {}\n'.format(error.lineno))
        sys.stderr.write('  Column: {}\n'.format(error.column))
        sys.stderr.write('For full log, please open: {}\n'.format(ret.tmp_name()))
        return retcode

    for warn in ret.warnings():
        print(warn)
    sys.stderr.write('For full log, please open: {}\n'.format(ret.tmp_name()))

    return retcode


if __name__ == "__main__":
    sys.exit(main() or 0)
