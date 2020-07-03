# adapted from Jiahong Yuan by Chenzi Xu in Dec 2019
# Use: python mlf2textgrid.py test.mlf
import tempfile
import codecs


def readAlignedMLF(mlffile, SR, wave_start):
    # This reads a MLF alignment output file with phone and word
    # alignments and returns a list of words, each word is a list containing
    # the word label followed by the phones, each phone is a tuple
    # (phone, start_time, end_time) with times in seconds.

    f = codecs.open(mlffile, 'r', 'utf-8')
    lines = [l.rstrip() for l in f.readlines()]
    f.close()

    if len(lines) < 3:
        raise ValueError("Alignment did not complete succesfully.")

    j = 2
    ret = []
    while (lines[j] != '.'):
        if (len(lines[j].split()) == 5):  # Is this the start of a word; do we have a word label?
            # Make a new word list in ret and put the word label at the beginning
            wrd = lines[j].split()[4]
            ret.append([wrd])

        # Append this phone to the latest word (sub-)list
        ph = lines[j].split()[2]
        if (SR == 11025):
            st = (float(lines[j].split()[0])/10000000.0 + 0.0125)*(11000.0/11025.0)
            en = (float(lines[j].split()[1])/10000000.0 + 0.0125)*(11000.0/11025.0)
        else:
            st = float(lines[j].split()[0])/10000000.0 + 0.0125
            en = float(lines[j].split()[1])/10000000.0 + 0.0125
        if st < en:
            ret[-1].append([ph, st+wave_start, en+wave_start])

        j += 1

    return ret


def writeTextGrid(outfile, word_alignments):
    # make the list of just phone alignments
    phons = []
    for wrd in word_alignments:
        phons.extend(wrd[1:])  # skip the word label

    # make the list of just word alignments
    # we're getting elements of the form:
    #   ["word label", ["phone1", start, end], ["phone2", start, end], ...]
    wrds = []
    for wrd in word_alignments:
        # If no phones make up this word, then it was an optional word
        # like a pause that wasn't actually realized.
        if len(wrd) == 1:
            continue
        # word label, first phone start time, last phone end time
        wrds.append([wrd[0], wrd[1][1], wrd[-1][2]])

    # write the phone interval tier
    fw = open(outfile, 'w', encoding='utf-8')
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

    # write the word interval tier
    fw.write('"IntervalTier"\n')
    fw.write('"word"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(wrds)) + '\n')
    for k in range(len(wrds) - 1):
        fw.write(str(wrds[k][1]) + '\n')
        fw.write(str(wrds[k+1][1]) + '\n')
        fw.write('"' + wrds[k][0] + '"' + '\n')

    fw.write(str(wrds[-1][1]) + '\n')
    fw.write(str(phons[-1][2]) + '\n')
    fw.write('"' + wrds[-1][0] + '"' + '\n')
    fw.close()


if __name__ == "__main__":
    # Load MLF file
    fname_in = './test1.mlf'
    fname_out = './test1mlf.TextGrid'
    # Default sampling rate
    SR = 11025.0
    wav_start = 0.0
    word_alignments = readAlignedMLF(fname_in, SR, wav_start)
    print(word_alignments)
    # Write file
    writeTextGrid(fname_out, word_alignments)
