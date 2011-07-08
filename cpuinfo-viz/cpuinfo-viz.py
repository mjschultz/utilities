#!/usr/bin/env python
#
# Read in /proc/cpuinfo (or alternative file) and figure out the physical
# layout of the processors on the system.
# Provides visual mapping of processor ids to physical processors and
# threads.

import sys, re, math
import argparse
import pygtk, gtk

class SMThread:
    def __init__(self, id) :
        self.id = id

    def __repr__(self) :
        return 'SMThread(id={0})'.format(self.id)

class Core:
    def __init__(self, id) :
        self.id = id
        self.smts = {}
        self.is_smt = False

    def add_smt(self, smt) :
        self.smts[smt.id] = smt
        if len(self.smts) > 1 :
            self.is_smt = True

    def __repr__(self) :
        return 'Core(id={0}, smts={1})'.format(self.id, self.smts)

class Processor:
    def __init__(self, id) :
        self.id = id
        self.cores = {}
        self.siblings = -1
        self.core_count = -1
        self.smt_count = 0

    def add_core(self, core) :
        self.cores[core.id] = core

    def check_siblings(self, siblings) :
        if self.siblings == -1 :
            self.siblings = siblings
        if self.siblings != siblings :
            print 'error'

    def check_core_count(self, core_count) :
        if self.core_count == -1 :
            self.core_count = core_count
        if self.core_count != core_count :
            print 'error'

    def __repr__(self) :
        return 'Processor(id={0}, cores={1})'.format(self.id, self.cores)

class System:
    def __init__(self, cpuinfo) :
        self.cpuinfo = cpuinfo
        self.processors = {}
        self.smt_count = 0
        self.parse_cpuinfo()

    def parse_cpuinfo(self) :
        suffix = '\s*: (.*)'
        processor_re = re.compile('processor'+suffix)
        physical_id_re = re.compile('physical id'+suffix)
        siblings_re = re.compile('siblings'+suffix)
        core_id_re = re.compile('core id'+suffix)
        cpu_cores_re = re.compile('cpu cores'+suffix)
        f = open(self.cpuinfo, 'r')
        info = f.readlines()
        f.close()
        for line in info :
            match = physical_id_re.match(line)
            if match :
                proc_id = match.group(1)
                processor = self.processors.get(proc_id, Processor(proc_id))
                self.processors[proc_id] = processor

            match = core_id_re.match(line)
            if match :
                core_id = match.group(1)
                core = processor.cores.get(core_id, Core(core_id))
                core.add_smt(smt)
                processor.smt_count += 1
                self.smt_count += 1
                processor.add_core(core)

            match = processor_re.match(line)
            if match :
                smt = SMThread(match.group(1))

            match = siblings_re.match(line)
            if match :
                siblings = match.group(1)
                processor.check_siblings(siblings)

            match = cpu_cores_re.match(line)
            if match :
                core_count = match.group(1)
                processor.check_core_count(core_count)

    def __repr__(self) :
        output = 'System(smt_count={0}, processors={1})'
        return output.format(self.smt_count, self.processors)

class CPUViz :
    proc_width = 200
    proc_height = 200
    def __init__(self, system) :
        self.system = system
        self.nprocs = len(self.system.processors)
        self.proc_rows = int(math.sqrt(self.nprocs))
        self.proc_cols = self.nprocs / self.proc_rows

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('cpuinfo visualization')
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.set_border_width(10)

        self.area = gtk.DrawingArea()
        self.area.set_size_request(self.proc_width*self.proc_cols+1,
                                   self.proc_height*self.proc_rows+1)
        self.pango = self.area.create_pango_layout('')
        self.window.add(self.area)

        self.area.connect('expose-event', self.populate)
        self.area.show()
        self.window.show()

    def populate(self, area, event) :
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]

        for proc_id in self.system.processors :
            proc = self.system.processors[proc_id]
            x = self.proc_width * (int(proc_id) % self.proc_cols) + 2
            y = self.proc_height * (int(proc_id) / self.proc_cols) + 2
            self.area.window.draw_rectangle(self.gc, False, x, y,
                    self.proc_width-2, self.proc_height-2)
            self.pango.set_text('Processor {0}'.format(proc_id))
            self.area.window.draw_layout(self.gc, x+5,
                                         y+5, self.pango)
            ncores = len(proc.cores)
            core_rows = int(math.sqrt(ncores))
            core_cols = ncores / core_rows
            core_width = self.proc_width / core_cols - 2
            core_height = self.proc_height / core_rows - 12
            for core_id in proc.cores :
                core = proc.cores[core_id]
                core_x = x + core_width * (int(core_id) % core_cols) + 5
                core_y = y + (10 * core_rows)+ 10/core_rows
                core_y += core_height*(int(core_id)/core_cols)
                self.area.window.draw_rectangle(self.gc, False,
                        core_x, core_y,
                        core_width-8, core_height-16/core_rows)
                self.pango.set_text('Core {0}'.format(core_id))
                self.area.window.draw_layout(self.gc, core_x+2,
                                            core_y, self.pango)

                nsmts = len(core.smts)
                smt_pos_x = core_width / nsmts
                smt_width = 7
                smt_height = core_height - 50
                smt_top = 360*16
                smt_mid = 360*48
                smt_len = 360*32
                for (i, smt_id) in enumerate(core.smts) :
                    smt_x = core_x + smt_pos_x * i + 10
                    smt_y = core_y + 15
                    self.area.window.draw_arc(self.gc, False, smt_x, smt_y,
                            smt_width, smt_height/2, smt_top, smt_len)
                    self.area.window.draw_arc(self.gc, False, smt_x,
                            smt_y+smt_height/2,
                            smt_width, smt_height/2, smt_mid, smt_len)
                    self.pango.set_text('Id {0}'.format(smt_id))
                    self.area.window.draw_layout(self.gc, smt_x-5,
                                                smt_y+smt_height+2, self.pango)


    def main(self) :
        gtk.main()

def main(args) :
    parser = argparse.ArgumentParser()
    parser.add_argument('--viz', dest='display', action='store_const',
            const='viz', help='open a graphical display')
    parser.add_argument('--list', dest='display', action='store_const',
            const='list', help='print a listing of the system')
    parser.add_argument('cpuinfo', help='cpuinfo file to process')
    options = parser.parse_args(args)

    system = System(options.cpuinfo)

    if options.display == 'list' :
        for proc_id in sorted(system.processors, key=lambda x: int(x)) :
            proc = system.processors[proc_id]
            print 'Processor {0}:'.format(proc_id)
            for core_id in sorted(proc.cores, key=lambda x: int(x)) :
                core = proc.cores[core_id]
                print '\tCore {0}:'.format(core_id)
                for smt_id in sorted(core.smts, key=lambda x: int(x)) :
                    print '\t\tId {0}'.format(smt_id)
    elif options.display == 'viz' :
        viz = CPUViz(system)
        viz.main()
    else :
        parser.print_help()

if __name__ == '__main__' :
    main(sys.argv[1:])
