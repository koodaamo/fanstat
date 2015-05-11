# -*- encoding: utf-8 -*-
"""
fanstat - a command-line interface to build Fanstatic resources for web app use

Usage:
  fanstat list | libs | cont [<lib>...] [ --css | --js ]
  fanstat crossbar [<lib>...] [--prefix=<path>]
  fanstat html [--prefix=<path>] [--full] [<lib>...]

  list                List all packages for which resources exist
  libs                List all libraries
  cont                List contents of all libraries
  -c --css            List only css resources
  -j --js             Only js
  crossbar            Generate crossbar static config for libraries
  html                Generate HTML for JS & CSS inclusion
  -p --prefix=<path>  Set the URL path prefix for generated items
  -f --full           Link to full (uncompressed) files
  <lib>...            Limit to given library names (in dependency order)
  -h --help           Show this screen.
  -v --version        Show version.

"""

import sys, logging, string, json
from docopt import docopt
import pkg_resources
from fanstatic import get_library_registry


def run():

   args = docopt(__doc__, version='fanstat 1.2')
   if len(sys.argv) == 1:
      sys.exit(__doc__)

   if args["list"]:
      print "\nInstalled Python packages with Fanstatic libraries:\n"
      for ep in pkg_resources.iter_entry_points(group='fanstatic.libraries'):
         #print ep.name, ep.load()
         print ep.module_name


   if args["libs"]:
      print "\nResource libraries:\n"
      for k,v in get_library_registry().items():
         print k,  v.rootpath


   if args["cont"]:
      print "\nResources:\n"
      for k,v in get_library_registry().items():
         print k,  v.rootpath
         for r in v.known_resources:
            print r

   if args["html"]:
      print "\nHTML for inclusion on web page:"

      libnames = args["<lib>"]
      eps = [ep for ep in pkg_resources.iter_entry_points(group='fanstatic.libraries')]
      if libnames:
         selected = [ep for ep in eps if ep.name in libnames]
      else:
         selected = eps

      # generate list of <script> and <link> tags
      links = {"css":{}, "js":{}}
      for ep in selected:
         name = ep.name
         links["css"][name] = []
         links["js"][name] = []

         lib = ep.load()
         #module = ep.module_name,
         #root = lib.rootpath
         if args["--full"]:
            resources = [r for r in lib.known_resources if ".min." not in r]
         else:
            resources = [r for r in lib.known_resources if ".min." in r or ".css" in r]

         for res in resources:
            safename = name.replace("|","_")
            if res.endswith(".js"):
               prefix = args["--prefix"] or ""
               link = '<script type="text/javascript" src="%s"></script>' % (prefix + safename + "/" + res)
               links["js"][name].append(link)

            if res.endswith(".css"):
               prefix = args["--prefix"] or ""
               link = '<link type="text/css" href="%s" rel="stylesheet"/>' % (prefix + safename + "/" + res)
               links["css"][name].append(link)

      # print CSS link tags
      if links["css"]:
         print "\n<!-- CSS styles -->"
         for libname in libnames:
            if links["css"][libname]:
               print "\n".join(links["css"][libname])

      # print JS link tags
      if links["js"]:
         print "\n<!-- JavaScript scripts -->"
         for libname in libnames:
            if links["js"][libname]:
               print "\n".join(links["js"][libname])


   if args["crossbar"]:
      print "\nCrossbar resources configuration:\n"
      paths = {}
      for ep in pkg_resources.iter_entry_points(group='fanstatic.libraries'):
         name = args["--prefix"] + ep.name if  args["--prefix"] else ep.name
         lib = ep.load()
         paths[name.replace("|","_")] = {
            "type":"static",
            "package": ep.module_name,
            "resource": lib.rootpath
         }
      print json.dumps(paths, indent=3, separators=(',', ': '))


if __name__=="__main__":

   run()
