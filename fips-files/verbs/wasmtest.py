"""fips verb to build the oryol samples webpage"""

import os
import yaml 
import shutil
import subprocess
import glob
from distutils.dir_util import copy_tree
from string import Template

from mod import log, util, project, emscripten

BuildWasm = True
ExportAssets = True
Samples = [
    'InfiniteSpheres',
]

#-------------------------------------------------------------------------------
def copy_build_files(fips_dir, proj_dir, webpage_dir):
    # copy all files from the deploy dir to the webpage_dir
    ws_dir = util.get_workspace_dir(fips_dir)
    src_dir = f'{ws_dir}/fips-deploy/oryol/wasmasmjs-make-release'
    dst_dir = webpage_dir
    copy_tree(src_dir, dst_dir)
    shutil.copy(f'{proj_dir}/web/wasmsuite-readme.md', f'{dst_dir}/README.md')
    shutil.copy(f'{proj_dir}/LICENSE', f'{dst_dir}/LICENSE')

#-------------------------------------------------------------------------------
def export_assets(fips_dir, proj_dir, webpage_dir):
    data_src_dir = f'{proj_dir}/data'
    data_dst_dir = f'{webpage_dir}/data'
    if not os.path.exists(data_dst_dir) :
        os.makedirs(data_dst_dir)
    for ext in ['txt', 'dump']:
        for dataFile in glob.glob(f'{data_src_dir}/*.{ext}'):
            shutil.copy(dataFile, f'{data_dst_dir}/')

#-------------------------------------------------------------------------------
def build_deploy_webpage(fips_dir, proj_dir):
    # if webpage dir exists, clear it first
    ws_dir = util.get_workspace_dir(fips_dir)
    webpage_dir = f'{ws_dir}/fips-deploy/oryol-wasm-buildsuite'
    if not os.path.exists(webpage_dir) :
        os.makedirs(webpage_dir)
    config = 'wasmasmjs-make-release'
    project.clean(fips_dir, proj_dir, config)
    project.gen(fips_dir, proj_dir, config)
    for target in Samples :
        project.build(fips_dir, proj_dir, config, target)

    copy_build_files(fips_dir, proj_dir, webpage_dir)
    if ExportAssets :
        export_assets(fips_dir, proj_dir, webpage_dir)

    log.colored(log.GREEN, f'Done. ({webpage_dir})')

#-------------------------------------------------------------------------------
def serve_webpage(fips_dir, proj_dir):
    ws_dir = util.get_workspace_dir(fips_dir)
    webpage_dir = f'{ws_dir}/fips-deploy/oryol-wasm-buildsuite'
    p = util.get_host_platform()
    if p == 'osx':
        try:
            subprocess.call(
                f'open http://localhost:8000 ; python {fips_dir}/mod/httpserver.py',
                cwd=webpage_dir,
                shell=True,
            )
        except KeyboardInterrupt :
            pass
    elif p == 'win':
        try:
            subprocess.call(
                f'cmd /c start http://localhost:8000 && python {fips_dir}/mod/httpserver.py',
                cwd=webpage_dir,
                shell=True,
            )
        except KeyboardInterrupt:
            pass
    elif p == 'linux':
        try:
            subprocess.call(
                f'xdg-open http://localhost:8000; python {fips_dir}/mod/httpserver.py',
                cwd=webpage_dir,
                shell=True,
            )
        except KeyboardInterrupt:
            pass

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args):
    if len(args) > 0:
        if args[0] == 'build':
            build_deploy_webpage(fips_dir, proj_dir)
        elif args[0] == 'serve' :
            serve_webpage(fips_dir, proj_dir)
        else:
            log.error(f"Invalid param '{args[0]}', expected 'build' or 'serve'")
    else:
        log.error("Param 'build' or 'serve' expected")

#-------------------------------------------------------------------------------
def help() :
    log.info(log.YELLOW +
             'fips wasmtests build\n' +
             'fips wasmtests serve\n' +
             log.DEF +
             '    build WebAssembly build-suite samples (https://github.com/WebAssembly/build-suite)')

