import os
import subprocess

def run_cmd(cmd):
    """
    Run a command while printing and returning the stdout and stderr
    """
    print('+ {}'.format(cmd))
    if isinstance(cmd, str):
        cmd = cmd.split()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print(output)
    print(err)
    return output, err

def run(args):
    input_dir = args.input_dir  # uses args.input_dir
    output_dir = args.output_dir
    output_dir = os.path.join(output_dir, 'ncclimo_climo_results')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    start_year = args.start_yrs
    end_year = args.end_yrs

    variables = ','.join(v for v in args.vars)
    case = args.case  # '20180129.DECKv1b_piControl.ne30_oEC.edison'

    cmd = 'ncclimo --vars={} --start={} --end={} --case={} --input={} --output={}'
    cmd = cmd.format(variables, start_year, end_year, case, input_dir, output_dir)
    run_cmd(cmd)
