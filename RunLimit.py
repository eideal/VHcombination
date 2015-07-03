# root -l -b -q runAsymptoticsCLs.C++"(\\"./results/ZH_SMH125GeV_2012_combined_ALLSYS_model.root\",\"combined\",\"ModelConfig\",\"asimovData\",\"asimovData_0\", \"conditionalGlobs_0\", \"nominalGlobs\")"

from ROOT import *
import os
import sys

gROOT.Reset()
gROOT.LoadMacro("AtlasStyle.C")
from ROOT import SetAtlasStyle
SetAtlasStyle()

make_csv = True
make_graph = True

lumi = 20.3

HiggsMasses = 	[
               	 '100',
               	 '105',
               	 '110',
               	 '115',
                 '120',
                 '125',
                 '130',
                 '135',
                 '140',
                 '145',
                 '150',
]

blinded = True

exc_limit = {}

for mass in HiggsMasses:
    configfile = "VH_" + mass + ".xml"

    #result = os.system("hist2workspace config/" + configfile + " > hist2workspace.log")
    result = os.system("hist2workspace " + configfile + " > hist2workspace.log")

    if result is not 0:
        print "ERROR: hist2workspace did not succeed for config xml: " + configfile
        sys.exit(1) 

    logfile = open("hist2workspace.log")
    workspacefile = None
    for line in logfile:
        if "Writing combined workspace" in line:
            workspacefile = line.split()[-1]
    if workspacefile is None:
        print "ERROR: couldn't locate workspace filename in hist2workspace logfile"
        sys.exit(2)
    else:
        print workspacefile

    observed = "asimovData"
    if not blinded:
        observed = "obsData"

    print """root -l -b -q runAsymptoticsCLs.C++"(\\"%s\\",\\"combined\\",\\"ModelConfig\\",\\"%s\\",\\"asimovData_0\\", \\"conditionalGlobs_0\\", \\"nominalGlobs\\")" > log_%s.out"""%(workspacefile, observed, configfile)

    os.system("""root -l -b -q runAsymptoticsCLs.C++"(\\"%s\\",\\"combined\\",\\"ModelConfig\\",\\"%s\\",\\"asimovData_0\\", \\"conditionalGlobs_0\\", \\"nominalGlobs\\")" > log_%s.out"""%(workspacefile, observed, configfile))

    exc_limit[mass] = {}
    for line in open("log_%s.out"%(configfile)):
        if 'Observed:' in line:
            exc_limit[mass]["Obs"] = float(line.split(':')[-1])
        elif "Median:" in line:
            exc_limit[mass]["Exp"] = float(line.split(':')[-1])
        elif "-1sigma" in line:
            exc_limit[mass]["sig1-"] = float(line.split(':')[-1])
        elif "+1sigma" in line:
            exc_limit[mass]["sig1+"] = float(line.split(':')[-1])
        elif "-2sigma" in line:
            exc_limit[mass]["sig2-"] = float(line.split(':')[-1])
        elif "+2sigma" in line:
            exc_limit[mass]["sig2+"] = float(line.split(':')[-1])

if make_csv:
    outFile = open('limit.csv', 'w')
    outFile.write(','.join(['mH', 'Obs', 'Exp', '-2', '-1', '+1', '+2']) + '\n')
    print '#######################'
    print '### Exc. Limit Res: ###'
    for mH in HiggsMasses:
        print '----------------------'
        print 'Higgs mass:  %s'%mH
        print 'Obs: %.3f' %exc_limit[mH]["Obs"]
        print 'Exp: %.3f' %exc_limit[mH]["Exp"]
        print '-1 Sigma: %.3f' %exc_limit[mH]["sig1-"]
        print '+1 Sigma: %.3f' %exc_limit[mH]["sig1+"]
        print '-2 Sigma: %.3f' %exc_limit[mH]["sig2-"]
        print '+2 Sigma: %.3f' %exc_limit[mH]["sig2+"]
        
        outFile.write(','.join([mH, str(exc_limit[mH]["Obs"]), str(exc_limit[mH]["Exp"]), str(exc_limit[mH]["sig2-"]), str(exc_limit[mH]["sig1-"]), str(exc_limit[mH]["sig1+"]), str(exc_limit[mH]["sig2+"])]) + '\n')

if make_graph:
    Obs  = TGraph(len(HiggsMasses))
    Exp  = TGraph(len(HiggsMasses))
    Exp1 = TGraphAsymmErrors(len(HiggsMasses))
    Exp2 = TGraphAsymmErrors(len(HiggsMasses))
    for i, mH in enumerate(HiggsMasses):
        m = float(mH)
        Obs.SetPoint(i,m,exc_limit[mH]['Obs'])
        Exp.SetPoint(i,m,exc_limit[mH]['Exp'])
        Exp1.SetPoint(i,m,exc_limit[mH]['Exp'])
        Exp2.SetPoint(i,m,exc_limit[mH]['Exp'])
        Exp1.SetPointError(i,0.,0.,(exc_limit[mH]['Exp']-exc_limit[mH]['sig1-']),(exc_limit[mH]['sig1+']-exc_limit[mH]['Exp']))
        Exp2.SetPointError(i,0.,0.,(exc_limit[mH]['Exp']-exc_limit[mH]['sig2-']),(exc_limit[mH]['sig2+']-exc_limit[mH]['Exp']))

    c = TCanvas("Test", "Test",600,600)
    c.SetBorderMode(0)
    leg = TLegend(0.59,0.75,0.92,0.94)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetLineColor(10)
    leg.SetShadowColor(kWhite)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    Obs.SetMarkerStyle(20)
    Exp1.SetLineColor(kBlue)
    Exp2.SetLineColor(kRed)
    Exp2.GetXaxis().SetTitle('m_{H} [GeV]')
    Exp2.GetYaxis().SetTitle('95% CL. limit on #sigma/#sigma_{H}^{SM}')
    Exp2.GetYaxis().SetTitleOffset(1.05)
    Exp2.GetYaxis().SetTitleSize(0.05)
    Exp2.GetXaxis().SetTitleOffset(1.05)
    Exp2.GetXaxis().SetTitleSize(0.05)

    Exp2.GetXaxis().SetRangeUser(100.,150.)
    Exp2.GetYaxis().SetRangeUser(0.,20.)
    Exp2.SetFillColor(kYellow)
    Exp2.SetLineColor(kBlack)
    Exp1.SetFillColor(kGreen)
    Exp.SetLineWidth(2)
    Exp.SetLineStyle(2)

    Exp2.Draw('ACE3')
    Exp1.Draw('sameCE3')
    Exp.Draw('sameC')
    if not blinded:
        Obs.Draw('sameLP')

    from ROOT import gPad
    gPad.RedrawAxis()

    if not blinded:
        leg.AddEntry(Obs, 'Observed CLs',"LP")
    leg.AddEntry(Exp, 'Expected CLs',"LP")
    leg.AddEntry(Exp1, '#pm 1#sigma',"F")
    leg.AddEntry(Exp2, '#pm 2#sigma',"F")
    leg.Draw()

    lumilatex = TLatex()
    lumilatex.SetNDC(true)
    lumilatex.SetTextAlign(12)
    lumilatex.SetTextSize(0.033)
    lumilatex.DrawLatex(0.19,0.85,"#sqrt{s} = 8 TeV,  #intLdt = %.1f fb^{-1}"%(lumi))
    lumilatex.DrawLatex(0.69,0.21, "#font[72]{ATLAS} Internal")
    lumilatex2 = TLatex()
    lumilatex2.SetNDC(true)
    lumilatex2.SetTextSize(0.04)
    lumilatex2.DrawLatex(0.19,0.9, "WH(#tau_{h}#tau_{h}) + ZH(#tau_{h}#tau_{h})")

    c.Update()
    c.SaveAs("ExclLimit.png")
