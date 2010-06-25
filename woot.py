#!/usr/bin/env python
# Copyright (c) 2010, Michael J. Schultz
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * The names of its contributors may be used to endorse or promote
#       products derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL MICHAEL J. SCHULTZ BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

woot_index = 'http://www.woot.com/'
poll_period = 5

import sys, time, socket
import urllib, sgmllib

class WootParser(sgmllib.SGMLParser) :
    def __init__(self, verbose=0) :
        sgmllib.SGMLParser.__init__(self, verbose)
        self.in_element = {}
        self.information = {}
        # product, progress, price

    def get_information(self) :
        return self.information

    def handle_data(self, data) :
        if 'h2' in self.in_element and self.in_element['h2'] == True :
            self.information['product'] = data
        elif 'span' in self.in_element and self.in_element['span'] == True :
            self.information['price'] = data

    def start_h2(self, attr) :
        for (name, value) in attr :
            if name == 'class' and value == 'fn' :
                self.in_element['h2'] = True

    def end_h2(self) :
        self.in_element['h2'] = False

    def start_span(self, attr) :
        for (name, value) in attr :
            if name == 'class' and value == 'amount' :
                self.in_element['span'] = True

    def end_span(self) :
        self.in_element['span'] = False

    def start_div(self, attr) :
        has_progress = False
        for (name, value) in attr :
            if name == 'class' and value == 'wootOffProgressBarValue' :
                # this is the div with the progress bar
                has_progress = True
            if has_progress == True :
                if name == 'style' :
                    (css_property, css_value) = value.split(':')
                    self.information['progress'] = css_value

    def parse(self, s) :
        self.feed(s)
        self.close()

def parse_page() :
    try :
        page = urllib.urlopen(woot_index)
        contents = page.read()
        page.close()
    except socket.error :
        print 'error'
        return None

    parser = WootParser()
    parser.parse(contents)
    return parser.get_information()

products = {}

while True :
    information = parse_page()
    # Make sure we actually got some information
    if information != None :
        product = information['product']
        if product in products :
            if products[product]['progress'] != information['progress'] :
                products[product]['progress'] = information['progress']
                print 'Remaining:', information['progress'], '\r'
        else :
            products[product] = { 'time':time.time() }
            products[product]['progress'] = information['progress']
            print 'Product:', product
            print 'Price:', information['price']
            print 'Remaining:', information['progress'], '\r'

    # poll for a while
    sys.stdout.flush()
    time.sleep(poll_period)
