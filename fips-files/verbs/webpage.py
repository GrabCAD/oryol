"""fips verb to build the oryol samples webpage"""

import os
import yaml 
import shutil
import subprocess
import glob
from string import Template

from mod import log, util, project, emscripten, android
from tools import texexport

# what to build
BuildEmscripten = True
BuildWasm = True
ExportAssets = True
ExtensionSamples = True

# webpage template arguments
GitHubSamplesURL = 'https://github.com/floooh/oryol/tree/master/code/Samples/'
DocTitle = 'Oryol Core Samples'
Title = 'Oryol'
Subtitle = 'core samples'
# Separator = 'rainbow-separator'
# GameSeparator = 'game-rainbow-separator'
# BackgroundColor = '#19A3FF'     # this is the original bright blue 

Separator = 'simple-separator'
GameSeparator = 'simple-separator'
BackgroundColor = '#42A5F5'

# build configuration
EmscConfig  = 'webgl2-emsc-ninja-release'
WasmConfig  = 'webgl2-wasm-ninja-release'

#-------------------------------------------------------------------------------
def deploy_webpage(fips_dir, proj_dir, webpage_dir):
    """builds the final webpage under under fips-deploy/oryol-webpage"""
    ws_dir = util.get_workspace_dir(fips_dir)

    # load the websamples.yml file, should have been created during the last build
    with open(f'{webpage_dir}/websamples.yml', 'r') as f:
        samples = yaml.load(f.read())

    # create directories
    for platform in ['asmjs', 'wasm']:
        platform_dir = f'{webpage_dir}/{platform}'
        if not os.path.isdir(platform_dir) :
            os.makedirs(platform_dir)

    # link to the Extension Samples
    content = ''
    if ExtensionSamples:
        content = (
            '<div class="thumb">\n'
            + '  <div class="thumb-title">To Extension Samples...</div>\n'
        )
        content += '  <div class="img-frame"><a href="http://floooh.github.com/oryol-samples/index.html"><img class="image" src="ext_samples.jpg"></img></a></div>\n'
        content += '</div>\n'

    # build the thumbnail gallery
    for sample in samples:
        if sample['name'] != '__end__':
            log.info(f"> adding thumbnail for {sample['name']}")
            name    = sample['name']
            imgPath = sample['image']
            types   = sample['type']
            desc    = sample['desc']
            head, tail = os.path.split(imgPath)
            imgFileName = 'dummy.jpg' if tail == 'none' else tail
            content += '<div class="thumb">\n'
            content += f'  <div class="thumb-title">{name}</div>\n'
            content += f'  <div class="img-frame"><a href="asmjs/{name}.html"><img class="image" src="{imgFileName}" title="{desc}"></img></a></div>\n'
            content += '  <div class="thumb-bar">\n'
            content += '    <ul class="thumb-list">\n'
            if BuildEmscripten and 'emscripten' in types:
                content += f'      <li class="thumb-item"><a class="thumb-link" href="asmjs/{name}.html">asm.js</a></li>\n'
            if BuildWasm and 'emscripten' in types:
                content += f'      <li class="thumb-item"><a class="thumb-link" href="wasm/{name}.html">wasm</a></li>\n'
            content += '    </ul>\n'
            content += '  </div>\n'
            content += '</div>\n'

    # populate the html template, and write to the build directory
    with open(f'{proj_dir}/web/index.html', 'r') as f:
        templ = Template(f.read())
    html = templ.safe_substitute(doctitle=DocTitle, title=Title, subtitle=Subtitle, samples=content, separator=Separator)
    with open(f'{webpage_dir}/index.html', 'w') as f:
        f.write(html)

    # and the same with the CSS template
    with open(f'{proj_dir}/web/style.css', 'r') as f:
        templ = Template(f.read())
    css = templ.safe_substitute(background=BackgroundColor)
    with open(f'{webpage_dir}/style.css', 'w') as f:
        f.write(css)

    # copy other required files
    for name in ['dummy.jpg', 'emsc.js', 'wasm.js', 'about.html', 'favicon.png', 'ext_samples.jpg']:
        log.info(f'> copy file: {name}')
        shutil.copy(f'{proj_dir}/web/{name}', f'{webpage_dir}/{name}')

    # generate emscripten HTML pages
    if BuildEmscripten and emscripten.check_exists(fips_dir):
        emsc_deploy_dir = f'{ws_dir}/fips-deploy/oryol/{EmscConfig}'
        for sample in samples:
            name = sample['name']
            if name != '__end__' and 'emscripten' in sample['type']:
                log.info(f'> generate emscripten HTML page: {name}')
                for ext in ['js', 'html.mem']:
                    src_path = f'{emsc_deploy_dir}/{name}.{ext}'
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, f'{webpage_dir}/asmjs/')
                with open(f'{proj_dir}/web/emsc.html', 'r') as f:
                    templ = Template(f.read())
                src_url = GitHubSamplesURL + sample['src'];
                html = templ.safe_substitute(name=name, source=src_url, separator=GameSeparator)
                with open(f'{webpage_dir}/asmjs/{name}.html', 'w') as f:
                    f.write(html)

    # generate WebAssembly HTML pages
    if BuildWasm and emscripten.check_exists(fips_dir):
        wasm_deploy_dir = f'{ws_dir}/fips-deploy/oryol/{WasmConfig}'
        for sample in samples:
            name = sample['name']
            if name != '__end__' and 'emscripten' in sample['type']:
                log.info(f'> generate wasm HTML page: {name}')
                for ext in ['js', 'wasm.mappedGlobals']:
                    src_path = f'{wasm_deploy_dir}/{name}.{ext}'
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, f'{webpage_dir}/wasm/')
                for ext in ['html.mem', 'wasm']:
                    src_path = f'{wasm_deploy_dir}/{name}.{ext}'
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, f'{webpage_dir}/wasm/{name}.{ext}.txt')
                with open(f'{proj_dir}/web/wasm.html', 'r') as f:
                    templ = Template(f.read())
                src_url = GitHubSamplesURL + sample['src'];
                html = templ.safe_substitute(name=name, source=src_url, separator=GameSeparator)
                with open(f'{webpage_dir}/wasm/{name}.html', 'w') as f:
                    f.write(html)

    # copy the screenshots
    for sample in samples:
        if sample['name'] != '__end__':
            img_path = sample['image']
            head, tail = os.path.split(img_path)
            if tail != 'none':
                log.info(f'> copy screenshot: {tail}')
                shutil.copy(img_path, f'{webpage_dir}/{tail}')

#-------------------------------------------------------------------------------
def export_assets(fips_dir, proj_dir, webpage_dir):

    tex_srcdir = f'{proj_dir}/data'
    tex_dstdir = f'{webpage_dir}/data'
    texexport.configure(proj_dir, tex_srcdir, tex_dstdir)
    texexport.exportSampleTextures()
    for ext in ['txt']:
        for dataFile in glob.glob(f'{proj_dir}/data/*.{ext}'):
            shutil.copy(dataFile, f'{webpage_dir}/data/')

#-------------------------------------------------------------------------------
def build_deploy_webpage(fips_dir, proj_dir, rebuild):
    # if webpage dir exists, clear it first
    ws_dir = util.get_workspace_dir(fips_dir)
    webpage_dir = f'{ws_dir}/fips-deploy/oryol-webpage'
    if rebuild :
        if os.path.isdir(webpage_dir) :
            shutil.rmtree(webpage_dir)
    if not os.path.isdir(webpage_dir) :
        os.makedirs(webpage_dir)

    # compile samples
    if BuildEmscripten and emscripten.check_exists(fips_dir) :
        project.gen(fips_dir, proj_dir, EmscConfig)
        project.build(fips_dir, proj_dir, EmscConfig)
    if BuildWasm and emscripten.check_exists(fips_dir) :
        project.gen(fips_dir, proj_dir, WasmConfig)
        project.build(fips_dir, proj_dir, WasmConfig)

    # export sample assets
    if ExportAssets :
        export_assets(fips_dir, proj_dir, webpage_dir)

    # deploy the webpage
    deploy_webpage(fips_dir, proj_dir, webpage_dir)

    log.colored(log.GREEN, f'Generated Samples web page under {webpage_dir}.')

#-------------------------------------------------------------------------------
def serve_webpage(fips_dir, proj_dir):
    ws_dir = util.get_workspace_dir(fips_dir)
    webpage_dir = f'{ws_dir}/fips-deploy/oryol-webpage'
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
            build_deploy_webpage(fips_dir, proj_dir, False)
        elif args[0] == 'rebuild' :
            build_deploy_webpage(fips_dir, proj_dir, True)
        elif args[0] == 'serve' :
            serve_webpage(fips_dir, proj_dir)
        else:
            log.error(f"Invalid param '{args[0]}', expected 'build' or 'serve'")
    else:
        log.error("Param 'build' or 'serve' expected")

#-------------------------------------------------------------------------------
def help() :
    log.info(log.YELLOW +
             'fips webpage build\n' +
             'fips webpage rebuild\n' +
             'fips webpage serve\n' +
             log.DEF +
             '    build oryol samples webpage')

