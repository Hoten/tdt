import argparse
import datetime
import git
import json
import os
import pystache
import re
import subprocess
import sys

def run(quiet, git_dir, includes):
  args = locals()
  g = git.Git(git_dir)
  repo = git.Repo(git_dir)

  def generate_report(blame_results):
    return {
      'args': args,
      'commit': repo.head.commit.hexsha,
      'items': blame_results
    }

  def generate_html_view(report):
    template_path = os.path.join(os.path.dirname(__file__), '..', 'report.html.mustache')
    with open(template_path, 'r') as myfile:
      template = myfile.read()
      return pystache.render(template, report)

  def ls_files():
    return g.ls_files(['--', includes]).split("\n")

  def blame(file, regex):
    results = []
    lineno = 1
    for commit, lines in repo.blame('HEAD', file):
      for line in lines:
        if isinstance(line, bytes):
          continue

        if regex.match(line):
          results.append({
            'file': file,
            'lineno': lineno,
            'line': line.strip(),
            'commit': commit.hexsha,
            'commit_author': {
              'name': commit.author.name,
              'email': commit.author.email
            },
            'committed_date': commit.committed_date
          })
        lineno += 1

    return results

  regex = re.compile('.*TODO.*', re.IGNORECASE)
  files = ls_files()
  blame_results = []
  for file in files:
    blame_results.extend(blame(file, regex))

  report = generate_report(blame_results)
  with open('report.json', 'w') as file:
    file.write(json.dumps(report, indent=4, sort_keys=True))

  html = generate_html_view(report)
  with open('report.html', 'w') as file:
    file.write(html)

  if not quiet:
    for item in blame_results:
      timestamp = datetime.datetime.fromtimestamp(item['committed_date']).strftime('%Y-%m-%d')
      print(f'location: {item["file"]}:{item["lineno"]}')
      print(f'code: {item["line"]}')
      print(f'commit: {item["commit"]}')
      print(f'author: {item["commit_author"]["name"]} <{item["commit_author"]["email"]}>')
      print(f'committed date: {timestamp}')
      print()

  sys.exit(0 if len(blame_results) == 0 else 1)

def main():
  parser = argparse.ArgumentParser(description='Generate tech debt report')
  parser.add_argument('-q','--quiet', help='Supress output', action='store_true', default=False)
  parser.add_argument('-C','--git-dir', help='Root directory of git repo', default=os.getcwd())
  parser.add_argument('-i','--includes', nargs='+', help='Glob paths of files to process',
                      default=['**/*.rb', '**/*.php', '**/*.c', '**/*.cpp', '**/*.h', '**/*.hpp', '**/*.py', '**/*.groovy', '**/*.java', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx', '**/*.html', '**/*.twig'])
  args = vars(parser.parse_args())

  run(**args)

if __name__ == '__main__':
  main()
