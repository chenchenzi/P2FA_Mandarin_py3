#!/usr/bin/env python

""" Usage:
      align.py wavfile trsfile output_file
"""

import os
import sys
import wave
import codecs

def prep_wav(orig_wav, out_wav):
    f = wave.open(orig_wav, 'r')
    SR = f.getframerate()
    f.close()
    if (SR <> 16000):
        os.system("sox " + orig_wav + " -r 16000 " + out_wav + " polyphase")
    else:
        os.system("cp -f " + orig_wav + " " + out_wav)


def prep_mlf(trsfile, mlffile):

    f = codecs.open('./model/dict', 'r', 'utf-8')
    lines = f.readlines()
    f.close()
    dict = []
    for line in lines:
        dict.append(line.split()[0])
    
    f = codecs.open(trsfile, 'r', 'utf-8')
    lines = f.readlines()
    f.close()

    fw = codecs.open(mlffile, 'w', 'utf-8')
    fw.write('#!MLF!#\n')
    fw.write('"*/tmp.lab"\n')
    fw.write('sp\n')
    i = 0
    while (i < len(lines)):
        txt = lines[i].replace('\n', '')
        txt = txt.replace('{breath}', 'br').replace('{noise}', 'ns')
        txt = txt.replace('{laugh}', 'lg').replace('{laughter}', 'lg')
        txt = txt.replace('{cough}', 'cg').replace('{lipsmack}', 'ls')
        for pun in [',', '.', ':', ';', '!', '?', '"', '%', '-']:
            txt = txt.replace(pun,  '')
        for wrd in txt.split():
            if (wrd in dict):
                fw.write(wrd + '\n')
                fw.write('sp\n')
        i += 1
    fw.write('.\n')
    fw.close()


def TextGrid(infile1, infile2, outfile):
    
    f = codecs.open(infile1, 'r', 'utf-8')
    lines = f.readlines()
    f.close()
    
    f = codecs.open(infile2, 'r', 'utf-8')
    lines2 = f.readlines()
    f.close()
    words = []
    for line in lines2[2:-1]:
        if (line.strip() <> 'sp'):
            words.append(line.strip())
    words.reverse()

    fw = codecs.open(outfile, 'w', 'utf-8')
 
    j = 2
    phons = []
    wrds = []
    while (lines[j] <> '.\n'):
        ph = lines[j].split()[2]
        st = float(lines[j].split()[0])/10000000.0 + 0.0125
        en = float(lines[j].split()[1])/10000000.0 + 0.0125
        if (st <> en):
            phons.append([ph, st, en])

        if (len(lines[j].split()) == 5):
            wrd = lines[j].split()[4].replace('\n', '')
            st = float(lines[j].split()[0])/10000000.0 + 0.0125
            en = float(lines[j].split()[1])/10000000.0 + 0.0125
            if (st <> en):
                wrds.append([wrd, st])
        j += 1

    #write the phone interval tier
    fw.write('File type = "ooTextFile short"\n')
    fw.write('"TextGrid"\n')
    fw.write('\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][2]) + '\n')
    fw.write('<exists>\n')
    fw.write('2\n')
    fw.write('"IntervalTier"\n')
    fw.write('"phone"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(phons)) + '\n')
    for k in range(len(phons)):
        fw.write(str(phons[k][1]) + '\n')
        fw.write(str(phons[k][2]) + '\n')
        fw.write('"' + phons[k][0] + '"' + '\n')

    #write the word interval tier
    fw.write('"IntervalTier"\n')
    fw.write('"word"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(wrds)) + '\n')
    for k in range(len(wrds) - 1):
        fw.write(str(wrds[k][1]) + '\n')
        fw.write(str(wrds[k+1][1]) + '\n')
        if (wrds[k][0] == 'sp'):
                fw.write('"sp"\n')
        else:
            w = words.pop()
            fw.write('"' + w + '"\n')
    fw.write(str(wrds[-1][1]) + '\n')
    fw.write(str(phons[-1][2]) + '\n')
    if (wrds[-1][0] == 'sp'):
        fw.write('"sp"\n')
    else:
        w = words.pop()
        fw.write('"' + w + '"\n')

    if (len(words) <> 0):
        print words
        print '!!!words and phones are mismatched!!!'
    fw.close()

if __name__ == '__main__':

    try:
        wavfile = sys.argv[1]
        trsfile = sys.argv[2]
        outfile = sys.argv[3]
    except IndexError:
        print __doc__


    # create working directory
    os.system("rm -r -f ./tmp")
    os.system("mkdir ./tmp")
    
    #prepare wavefile
    prep_wav(wavfile, './tmp/tmp.wav')

    #prepare mlfile
    prep_mlf(trsfile, './tmp/tmp.mlf')

    #prepare scp files
    fw = open('./tmp/codetr.scp', 'w')
    fw.write('./tmp/tmp.wav ./tmp/tmp.plp\n')
    fw.close()
    fw = open('./tmp/test.scp', 'w')
    fw.write('./tmp/tmp.plp\n')
    fw.close()
    
    #call plp.sh and align.sh
    os.system('HCopy -T 1 -C ./model/16000/config -S ./tmp/codetr.scp')
    os.system('HVite -T 1 -a -m -I ./tmp/tmp.mlf -H ./model/16000/macros -H ./model/16000/hmmdefs  -S ./tmp/test.scp -i ./tmp/aligned.mlf -p 0.0 -s 5.0 ./model/dict ./model/monophones > ./tmp/aligned.results')
    os.path.split(trsfile)[1].split('.')[0] + '.TextGrid'

    TextGrid('./tmp/aligned.mlf', './tmp/tmp.mlf', outfile)
