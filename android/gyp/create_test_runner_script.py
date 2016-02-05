#!/usr/bin/env python
#
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Creates a script to run an android test using build/android/test_runner.py.
"""

import argparse
import os
import sys

from util import build_utils

SCRIPT_TEMPLATE = """\
#!/usr/bin/env python
#
# This file was generated by build/android/gyp/create_test_runner_script.py

import os
import subprocess
import sys

def main():
  script_directory = os.path.dirname(__file__)

  def ResolvePath(path):
    \"\"\"Returns an absolute filepath given a path relative to this script.
    \"\"\"
    return os.path.abspath(os.path.join(script_directory, path))

  test_runner_path = ResolvePath('{test_runner_path}')
  test_runner_args = {test_runner_args}
  test_runner_path_args = {test_runner_path_args}
  for arg, path in sorted(test_runner_path_args.iteritems()):
    test_runner_args.extend([arg, ResolvePath(path)])

  test_runner_cmd = [test_runner_path] + test_runner_args + sys.argv[1:]
  print ' '.join(test_runner_cmd)
  return subprocess.call(test_runner_cmd)

if __name__ == '__main__':
  sys.exit(main())
"""

def main(args):
  parser = argparse.ArgumentParser()
  parser.add_argument('--script-output-path',
                      help='Output path for executable script.')
  parser.add_argument('--depfile',
                      help='Path to the depfile. This must be specified as '
                           "the action's first output.")
  # We need to intercept any test runner path arguments and make all
  # of the paths relative to the output script directory.
  group = parser.add_argument_group('Test runner path arguments.')
  group.add_argument('--output-directory')
  group.add_argument('--isolate-file-path')
  group.add_argument('--apk-under-test')
  group.add_argument('--test-apk')
  group.add_argument('--coverage-dir')
  args, test_runner_args = parser.parse_known_args(
      build_utils.ExpandFileArgs(args))

  def RelativizePathToScript(path):
    """Returns the path relative to the output script directory."""
    return os.path.relpath(path, os.path.dirname(args.script_output_path))

  test_runner_path = os.path.join(
      os.path.dirname(__file__), os.path.pardir, 'test_runner.py')
  test_runner_path = RelativizePathToScript(test_runner_path)

  test_runner_path_args = {}
  if args.output_directory:
    test_runner_path_args['--output-directory'] = RelativizePathToScript(
        args.output_directory)
  if args.isolate_file_path:
    test_runner_path_args['--isolate-file-path'] = RelativizePathToScript(
        args.isolate_file_path)
  if args.apk_under_test:
    test_runner_path_args['--apk-under-test'] = RelativizePathToScript(
        args.apk_under_test)
  if args.test_apk:
    test_runner_path_args['--test-apk'] = RelativizePathToScript(
        args.test_apk)
  if args.coverage_dir:
    test_runner_path_args['--coverage-dir'] = RelativizePathToScript(
        args.coverage_dir)

  with open(args.script_output_path, 'w') as script:
    script.write(SCRIPT_TEMPLATE.format(
        test_runner_path=str(test_runner_path),
        test_runner_args=str(test_runner_args),
        test_runner_path_args=str(test_runner_path_args)))

  os.chmod(args.script_output_path, 0750)

  if args.depfile:
    build_utils.WriteDepfile(
        args.depfile,
        build_utils.GetPythonDependencies())

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
