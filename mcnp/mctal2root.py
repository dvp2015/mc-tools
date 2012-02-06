#! /usr/bin/python -W all

import sys, re, string
from array import array
from ROOT import ROOT, TFile, TH1F, TObjArray, THnSparseF

class Axis:
    name = None
    number = None
    boundaries = None

    def __init__(self, name, number):
#        del self.boundaries[:]
        self.boundaries = []
        self.name = name
        self.number = number

    def Print(self):
        """
        The printer
        """
        print "Axis", self.name, self.number
        if len(self.boundaries)<10:
            print "\tbins:", self.boundaries
        else:
            print "\tbins:", self.boundaries[0], '...', self.boundaries[-1]

    def hasTotalBin(self):
        """
        Checks whether the axis has Total Bin set
        """
        if number == len(self.boundaries):
            return False
        else:
            return True

    def getNbins(self, remove_zeros=True):
        """
        Return number of bins on the given axis
        """
        n = len(self.boundaries) # this takes into account NT (total bin) by removing it - in any case we can get it by TH1::Integral()

        # this is needed for Histogram():
        if remove_zeros and n == 0:
            n = 1
        return n

#    def getStrippedBoundaries(self):
#        """
#        Return boundaries without entries which have 0 or 1 entries
#        """
#        return filter(lambda item: item>1, self.boundaries)
        


class Tally:
    number = None
    title = None
    particle = None
    type = None     # tally type: 0=nondetector, 1=point detector; 2=ring; 3=FIP; 4=FIR; 5=FIC
    cells = None
    f  = None       # number of cell, surface or detector bins
    d  = None       # number of total / direct or flagged bins
# u is the number of user bins, including the total bin if there is one.
#   If there is a total bin, then 'ut' is used.
#   If there is cumulative binning, then 'uc' is used
# The same rules apply for the s, m, c, e, and t - lines
    u  = None
    s  = None       # segment or radiography s-axis bin
    m  = None       # multiplier bin
    c  = None       # cosine or radiography t-axis bin
    e  = None       # energy bin
    t  = None       # time bin

    axes = {}
    axes['f'] = None
    axes['d'] = None
    axes['u'] = None
    axes['s'] = None
    axes['m'] = None
    axes['c'] = None
    axes['e'] = None
    axes['t'] = None

    data = []
    errors = [] # errors are relative

    tfc_n   = None  # number of sets of tally fluctuation data
    tfc_jtf = []    # list of 8 numbers, the bin indexes of tally fluctuation chart bin
    tfc_data = []   # list of 4 numbers for each set of tally fluctuation chart data: nps, tally, error, figure of merit

    
    def __init__(self, number):
        self.number = number
#        for b in self.boundaries: del self.boundaries[b][:]
        del self.data[:]
        del self.errors[:]

    def Print(self, option=''):
        print "tally #%d:\t%s" % (self.number, self.title)
#        print "nbins", self.getNbins(), len(self.data)
        if option == 'title': return
#        self.Check()
        print "\tparticles:", self.particle
        print "\ttype:", self.type
        print "\tcells:", self.cells
        print "\tdimensions:", self.f, self.d, self.u, self.s, self.m, self.c, self.e, self.t
        print "\tnumber of dimensions:", self.getNdimensions()

        if self.d == 1:                                   # page 262
            print '\tthis is a cell or surface tally unless there is CF or SF card'
        elif self.d == 2:
            print '\tthis is a detector tally (unless thre is an ND card on the F5 tally)'

        for b in self.axes.keys():
            self.axes[b].Print()
        
#        print "\tData:", self.data
#        print "\tRelative Errors:", self.errors

#        print 2*(1+len(self.boundaries['e'])) * (1+len(self.boundaries['t'])), len(self.data)

    def getAxis(self, name):
        """
        Return axis with the given name
        """
        return self.axes[name]
#
#        if name in self.axes.keys:
#            return self.axes[name]
#        else:
#            print "ERROR in getAxis: no axis called", name
#            sys.exit(1)

    def getNonZeroAxes(self):
        """
        Return the list with non-zero axes
        """
# both 3 lines below give the same result:
#        while 0 in bins:  bins.remove(0)
#        bins = [x for x in bins if x]
#        bins = filter(lambda item: item>1, bins)
#        return vals
        return filter(lambda item: item.getNbins(False), self.axes.values())

    def getNbins(self):
        # Why don't just return len(self.data) ? - because it only works for 1D histos
        nbins = 1 #2  # !!! why 2? written on page 263, but still not clear Guess: value+error pairs?!!!
        for b in self.boundaries:
            l = len(self.boundaries[b])
            if l != 0: 
                nbins = nbins * (l+1)
        return nbins

    def getNdimensions(self):
        """
        Return number of non-empty dimensions of the tally (histogram)
        """
        n = 0
        for b in self.axes.keys():
            if len(self.axes[b].boundaries): n += 1
        return n
#        return len(self.GetStrippedBoundaries())

    def GetStrippedBoundaries(self):
        """
        Return boundaries without entries which have 0 or 1 bins
        """
        return dict( (b, v) for b,v in self.boundaries.iteritems() if len(v)>0 )

    def Check(self):
        """
        Perform a simple check of the tally
        """
        if len(self.tfc_jtf) != 8:
            print 'length of tfc_jtf array is not 8 but', len(self.tfc_jtf)
            sys.exit(1)

        if len(self.tfc_data) != 4:
            print 'length of tfc_data array is not 4 but', len(self.tfc_data)
            sys.exit(1)

    def Histogram(self):
        """
        Histograms the current tally
        """
        print "->Histogram"
#        stripped_boundaries = self.GetStrippedBoundaries()

        # bins = []
        # for a in self.axes.values():
        #     print bins, a.boundaries
        #     if a.getNbins()>0:
        #         bins.extend(a.boundaries)

        # print "bins: ", bins

#        for a in self.getNonZeroAxes(): a.Print()

        non_zero_axes = self.getNonZeroAxes()
        dim = len(non_zero_axes)
        bins = []
        for a in non_zero_axes:
            bins.append(a.getNbins())
        print "dim, bins:", dim, bins

        hs = THnSparseF("f%d" % self.number, "", dim, array('i', bins));
        hs.Print()
        print hs.GetNdimensions()
        # set bin edges:
        for i,a in enumerate(non_zero_axes):
            edges = [0.0] + a.boundaries
            print "setting bin edges for ", a.name, edges
            hs.SetBinEdges(i, array('d', edges)) # !!! max edge is just +1 to the previous edge
            hs.GetAxis(i).SetTitle("%s" % a.name)

        coords = []

        gbin = 0
        for f in range(self.getAxis('f').getNbins()):
            for d in range(self.getAxis('d').getNbins()):
                for u in range(self.getAxis('u').getNbins()):
                    for s in range(self.getAxis('s').getNbins()):
                        for m in range(self.getAxis('m').getNbins()):
                            for c in range(self.getAxis('c').getNbins()):
                                for e in range(self.getAxis('e').getNbins()):
                                    for t in range(self.getAxis('t').getNbins()):
                                        print "global bin:", gbin
                                        val = self.data[gbin]
                                        err = self.errors[gbin]
                                        for a in non_zero_axes:
                                            if   a.name == 't': coords.append(t+1) # t+1 - checked
                                            elif a.name == 'e': coords.append(e+1)
                                            elif a.name == 'c': coords.append(c+1)
                                            elif a.name == 'm': coords.append(m+1)
                                            elif a.name == 's': coords.append(s+1)
                                            elif a.name == 'u': coords.append(u+1)
                                            elif a.name == 'd': coords.append(d+1)
                                            elif a.name == 'f': coords.append(f+1)
                                        print coords, gbin, val,err
                                        hs.SetBinContent(array('i', coords), val)
                                        hs.SetBinError(array('i', coords), err*val)
                                        del coords[:]
                                        gbin += 1

        return hs

#        hs.SetBinEdges(1, array('d', [0.0] + self.boundaries['e'] + [3000.0])) # !!! max energy set to 3000
#        # !!! first bin set to -0.1 since t-bins start from 0
#        hs.SetBinEdges(2, array('d', [-0.1] + self.boundaries['t'] + [sys.float_info.max])) # !!! max time set to MAX_FLOAT
#        print hs.GetAxis(2).GetNbins(), hs.GetAxis(2).GetBinLowEdge(1)




    def Histogram1D(self):
# old version - 1D histogram only
# f5 tallies work only with energy binnings !!!
#        print self.energy_bins
#        for i in range(len(self.energy_bins)):
#            if i>0:
#                if self.energy_bins[i] < self.energy_bins[i-1]:
#                    print i
        print "ndim:",self.getNdimensions()
        title = "" # ";energy [MeV]"
        if self.title: title = self.title + title
        if self.number % 10 == 4:
            nbins = self.getNbins()
#            print nbins, self.e[1]
            h = TH1F("f%d" % self.number, title, nbins-2, array('f', self.boundaries['e']))
            for i in range(nbins-1): # et-1 => skip the last bin with total over all energy value (see p. 139 - E Tally Energy)
                val = self.data[i]
                dx = h.GetBinLowEdge(i+1)-h.GetBinLowEdge(i) 
                val = val/dx # divide by the bin width
                h.SetBinContent(i, val)
                h.SetBinError(i, val*self.errors[i])
        elif self.number % 10 == 5:
            h = TH1F("f%d" % self.number, title, self.e[1], array('f', [0] + self.boundaries['e']))
            for i in range(self.e[1]):
                val = self.data[i] # !!! not normalized by the bin width !!! 
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, val*self.errors[i])
        elif self.number % 10 == 6: # energy deposit
            print "histogramming"
            nbins = len(self.data)
            print "nbins: ", nbins
            if self.getNbins()-1 == len(self.boundaries['f']): # region binning only
                
#                h = TH1F("f%d" % self.number, title, nbins, array('f', self.boundaries['f']+ [self.boundaries['f'][len(self.boundaries['f'])-1]+1]))
                h = TH1F("f%d" % self.number, title + ";Cell", nbins, 0, nbins)
                print h.GetNbinsX()
                for i in range(nbins):
                    print i+1, h.GetBinCenter(i+1)
                    val = self.data[i] # !!! not normalized by the bin width !!! 
                    h.SetBinContent(i+1, val)
                    h.SetBinError(i+1, val*self.errors[i])
                    h.GetXaxis().SetBinLabel(i+1, "%d" % self.boundaries['f'][i])
            else:
                print "Error from Histogram: this binning not yet supported"
                exit(1)
        return h

def main():
    """
    mctal2root - MCTAL to ROOT converter
    Usage: mctal2root mctal [output.root]
    many features are not yet supported!
    """

    fname_in = sys.argv[1]
    fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print fname_out

    file_in = open(fname_in)
    
    kod = None               # name of the code, MCNPX
    ver = None               # code version
    probid = []              # date and time when the problem was run
    probid_date = None       # date from probid
    probid_time = None       # time from probid
    knod = None              # the dump number
    nps = None               # number of histories that were run
    rnr = None               # number of pseudorandom numbers that were used
    problem_title = None     # problem identification line
    ntal = None              # total number of tallies
    ntals = []               # array of tally numbers
    tally = None             # current tally

    is_vals = False          # True in the data/errors section

    histos = TObjArray()     # array of histograms

    for line in file_in.readlines():
        if kod is None:
            kod, ver, probid_date, probid_time, knod, nps, rnr = line.split()
            probid.append(probid_date)
            probid.append(probid_time)
#            print kod, ver, probid, knod, nps, rnr
            continue
        else:
            if problem_title is None and line[0] == " ":
                problem_title = line.strip()
                print problem_title
                continue

        words = line.split()

        if not ntal and words[0] == 'ntal':
            ntal = int(words[1])
            continue

        if ntal and not tally and words[0] != 'tally':
            for w in words:
                ntals.append(int(w))
            if ntal>1: print ntal, 'tallies:', ntals
            else: print ntal, 'tally:', ntals

        if words[0] == 'tally':
            if tally: 
                tally.Print()
#                histos.Add(tally.Histogram())
                if tally.number % 10 == 4 or tally.number == 5 or tally.number == 6 or tally.number == 15:
                    histos.Add(tally.Histogram())
#                elif tally.number == 125:
#                    tally.Print()
#                    histos.Add(tally.Histogram())
                del tally
            tally = Tally(int(words[1]))
            tally.particle = int(words[2])
            tally.type = int(words[3])
            if tally.number not in ntals:
                print 'tally %d is not in ntals' % tally.number
                print ntals
                return 1
            continue

        if not tally: continue

        if tally.axes['f'] and tally.axes['d']is None and line[0] == ' ':
            tally.cells = words
            for w in words:
                tally.boundaries['f'].append(float(w))

        if tally.axes['f'] is None and words[0] not in ['1', 'f']:
            tally.title = line.strip()
            print "tally.title:", tally.title
            

        if tally.axes['t'] and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
            for w in words: tally.axes['t'].boundaries.append(float(w))

        if tally.axes['e'] and tally.axes['t']is None and line[0] == ' ':
            for w in words: tally.axes['e'].boundaries.append(float(w))

        if tally.axes['u'] and tally.axes['s']is None and line[0] == ' ':
            for w in words: tally.axes['u'].boundaries.append(float(w))

        if   not tally.axes['f'] and re.search('^f', line[0]):        tally.axes['f'] = Axis(words[0], int(words[1]))
        elif not tally.axes['d'] and re.search('^d', line[0]):        tally.axes['d'] = Axis(words[0], int(words[1]))
        elif not tally.axes['u'] and re.search ("u[tc]?", line[0:1]): tally.axes['u'] = Axis(words[0], int(words[1]))
        elif not tally.axes['s'] and re.search('^s[tc]?', line[0:1]): tally.axes['s'] = Axis(words[0], int(words[1]))
        elif not tally.axes['m'] and re.search('^m[tc]?', line[0:1]): tally.axes['m'] = Axis(words[0], int(words[1]))
        elif not tally.axes['c'] and re.search('^c[tc]?', line[0:1]): tally.axes['c'] = Axis(words[0], int(words[1]))
        elif not tally.axes['e'] and re.search("^e[y]?",  line[0:1]): tally.axes['e'] = Axis(words[0], int(words[1]))
        elif not tally.axes['t'] and re.search("^t[tc]?", line[0:1]): tally.axes['t'] = Axis(words[0], int(words[1]))
        elif line[0:2] == 'tfc':
            tally.tfc_n = words[1]
            tally.tfc_jtf = words[2:]

        if tally.tfc_n and line[0] == ' ':
            tally.tfc_data = words

        if words[0] == 'vals':
            is_vals = True
            continue

        if is_vals:
            if line[0] == ' ':
                for iw, w in enumerate(words):
                    if not iw % 2: tally.data.append(float(w))
                    else: tally.errors.append(float(w))
            else:
                is_vals = False

    tally.Print()
    histos.Add(tally.Histogram())

    histos.Print()

    file_in.close()

    fout = TFile(fname_out, 'recreate')
    histos.Write()
    fout.Close()


if __name__ == '__main__':
    sys.exit(main())
