#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 12:15:36 2018

@author: akanksha
"""

import argparse 
import numpy as np
import os
from collections import Counter
import subprocess 
import  itertools
import sys
import shutil
from collections import OrderedDict
import functools
import pandas as pd
import multiprocessing
import multiprocessing.pool
from HOME import HOME_functions as ho

from os.path import join

def remEmptyDir(mypath):
    for root, dirs, files in os.walk(mypath,topdown=False):
         for name in dirs:
             fname = join(root,name)
             if not os.listdir(fname): #to check wither the dir is empty
                 
                 os.removedirs(fname)
def main(c,nop, topass, args):
    package_path = os.path.dirname(os.path.abspath(__file__))
    classes = args.type
    numreps=topass['numreps']
    if True: 
        
        df_path=[]
        sample_name_temp=[]
        for i in range(len(topass['dictionary'])):
            
            val=[]
            count=0
            d_rep={}
            input_file1=list(topass['dictionary'].values())[i]
            sample_name1=list(topass['dictionary'].keys())[i]
            sample_name_temp.append(sample_name1)
            
            for j in input_file1:
                
                count=count+1
                c1=["chr", "pos", "strand", "type", "mc_rep"+str(count), "h_rep"+str(count)]
                
                d_rep[count]=pd.read_csv(j+'/'+c+'.tsv',header=None,names=c1,sep='\t')
                filter_col1 = [col for col in list(d_rep[count]) if col.startswith(('h'))]
                d_rep[count]=d_rep[count].loc[(d_rep[count][filter_col1]!=0).any(axis=1)]
            if args.Keepall: 
                val.append(functools.reduce(topass['mergeo'], list(d_rep.values()))) 
                df=functools.reduce(topass['merge'], val)
                df.pos=df.pos.astype(int)
                df.chr=df.chr.astype(str)
                df=ho.fill_na(df)   
            else:    
                val.append(functools.reduce(topass['merge'], list(d_rep.values())))            
                df=functools.reduce(topass['merge'], val)         
            preordered = ["chr", "pos", "strand", "type"]  
            new_cols = preordered + [co for co in df.columns if co not in preordered]
            df=df.reindex(columns=new_cols)   
            df=df.sort_values(['pos'])
            df.to_csv(args.outputpath+'/temp_HOME/'+sample_name1+"_format_{c}.txt".format(c=c),header=True, index=False,sep='\t')    
            df_path.append(args.outputpath+'/temp_HOME/'+sample_name1+"_format_{c}.txt".format(c=c))  
        dictionary_new = OrderedDict(list(zip(sample_name_temp,df_path)))
        result_list = list(map(OrderedDict, itertools.combinations(iter(list(dictionary_new.items())), 2)))
        if args.withrespectto is not None:
            result_list=[iii for iii in result_list if list(iii.keys())[0] in args.withrespectto] 

        for iii in result_list:
            
            input_file1= iii[list(iii.keys())[0]]
            input_file2=iii[list(iii.keys())[1]]
            
            if (len(input_file1)!=0 and len(input_file2)!=0):
                sample_name1=list(iii.keys())[0]
                sample_name2=list(iii.keys())[1]
                dfa=pd.read_csv(str(input_file1),sep='\t')
                dfb=pd.read_csv(str(input_file2),sep='\t')
                ra=dfa.shape[1]-4
                rb=dfb.shape[1]-4
        
                p_mc=3
                p_h=4
                for i in range(1,((ra)//2)+1):
                    
                    dfa.rename(columns={dfa.columns[i+p_mc]:"mc_cont_rep"+str(i)}, inplace = True)
                    dfa.rename(columns={dfa.columns[i+p_h]:"h_cont"+"_rep"+str(i)}, inplace = True)
                    p_mc=p_mc+1
                    p_h=p_h+1
                    
                p_mc=3
                p_h=4    
                for i in range(1,((rb)//2)+1):
                   
                    dfb.rename(columns={dfb.columns[i+p_mc]:"mc_case"+"_rep"+str(i)}, inplace = True)
                    dfb.rename(columns={dfb.columns[i+p_h]:"h_case"+"_rep"+str(i)}, inplace = True)
                    p_mc=p_mc+1
                    p_h=p_h+1
          
                df = pd.merge(dfa, dfb, how='inner', on=['chr','pos',"strand","type"])
                if len(df)>1:
                    df=df.sort_values(['pos'])
                    df1=ho.format_allc(df, classes)
                    
                    del(df) 
                    if len(df1)>5:
                        
                        if min(numreps)>1 and max(numreps)>1:
                            nop=min(nop,len(df1))
                            CHUNKSIZE = int(len(df1)//nop)
                            CHUNKSIZE_list=[CHUNKSIZE]*nop 
                            extra=(len(df1)%nop)
                            
                            if extra> 0:
                                
                                CHUNKSIZE_list[-1]=CHUNKSIZE_list[-1]+extra
                                
                            df_chunk=ho.chunker1(df1,CHUNKSIZE_list)
                            ttc=0
                            df_path=[]
                            
                            for i in df_chunk:
                                
                                ttc=ttc+1
                                i.to_csv(args.outputpath+'/temp_HOME'+'/chunks/'+sample_name1+"VS"+sample_name2+"_df_{c}_{ttc}.txt".format(c=c,ttc=ttc),header=True, index=False,sep='\t')    
                                df_path.append(args.outputpath+'/temp_HOME'+'/chunks/'+sample_name1+"VS"+sample_name2+"_df_{c}_{ttc}.txt".format(c=c,ttc=ttc))
                               
                            if nop>1:    
                                
                                pool = multiprocessing.Pool(processes=nop)
                                process = [pool.apply_async(ho.process_frame_withR, args=(dd,)) for dd in df_path]
                                pool.close()
                                pool.join()
                                
                                pool = multiprocessing.Pool(processes=nop)
                                process = [pool.apply_async(ho.pval_format_withrep, args=(dd,)) for dd in df_path]
                                pool.close()
                                pool.join()
                
                                output = [p.get() for p in process]
                                df3=pd.concat(output, ignore_index=True,axis=0)
                
                            else:
                
                                ho.process_frame_withR(df_path[0])
                                df3=ho.pval_format_withrep(df_path[0])
                            
                            smooth_exp_val=ho.smoothing(*df3.exp_val) 
                            
                            df3['smooth_val']=(smooth_exp_val-min(smooth_exp_val))/(max(smooth_exp_val)-min(smooth_exp_val))
                            df3=df3.fillna(0) 
                            
                        else:
                        
                            df3=ho.pval_cal_withoutrep(df1)
                        
                        #if classes.startswith("CG"):
                        if classes=="CGN":
                            #input_file_path=np.load(os.getcwd()+'/training_data/hist_data_CG.npy')
                            input_file_path=np.load(package_path+'/training_data/hist_data_CG.npy')
                            
                            #model_path=os.getcwd()+'/saved_model/CG/new/hist/'
                            model_path=package_path+'/saved_model/CG/new/hist/'
                            k=ho.norm_slidingwin_predict_CG(df3,input_file_path,model_path)
                            
                            len_cutoff=10
                            tr=args.pruncutoff
                            dmrs=ho.clustandtrim_CG(k,df3,args.scorecutoff,args.pruncutoff,args.mergedist,args.numcb,args.prunningC,len_cutoff)
                            
                            
                            if len(dmrs)>=1:
                                
                                dmrs_filtered=ho.filterdmr(dmrs,args.minlength,args.minc,args.delta)
                            else: 
                                    print(("No DMRs found for "+sample_name1+"_VS_"+sample_name2+"_{c}".format(c=c)))
                                    continue    
    #                          
                        else:
                            #input_file_path=np.load(os.getcwd()+'/training_data/hist_data_nonCG.npy')
                            input_file_path=np.load(package_path+'/training_data/hist_data_nonCG.npy')
                            #model_path=os.getcwd()+'/saved_model/nonCG/new/hist/'
                            model_path=package_path+'/saved_model/nonCG/new/hist/'
                            if (nop>1 and nop<len(df3)):
                                CHUNKSIZE = int(len(df3)/nop)
                                df_chunk=ho.chunker(df3,CHUNKSIZE)
                                pool = multiprocessing.Pool(processes=nop)
                                
                                process = [pool.apply_async(ho.norm_slidingwin_predict_nonCG, args=(dd,input_file_path,model_path)) for dd in df_chunk]
                                
                                pool.close()
                                pool.join()
                                output = [p.get() for p in process]
                                k=pd.concat(output, ignore_index=True,axis=0)
                            else:    
                                k=ho.norm_slidingwin_predict_nonCG_withoutchunk(df3,input_file_path,model_path)
                            
                            len_cutoff=2
                            k["meth_case"]=df3.meth_case
                            k["meth_cont"]=df3.meth_cont
                            k["meth_diff"]=df3.meth_diff
                            k["h_cont"]=df3.h_cont
                            k["h_case"]=df3.h_case
                            del(df3)
                            if (nop>1 and nop<len(k)):
                                CHUNKSIZE = int(len(k)//nop)
                                CHUNKSIZE_list=[CHUNKSIZE]*nop 
                                extra=(len(k)%nop)
                                
                                if extra> 0:
                                    CHUNKSIZE_list[-1]=CHUNKSIZE_list[-1]+extra
                                df_chunk=ho.chunker1(k,CHUNKSIZE_list)
                                
                                pool = multiprocessing.Pool(processes=nop)
                                process = [pool.apply_async(ho.clustandtrim_nonCG1, args=(dd,sc)) for dd in df_chunk]
                                pool.close()
                                pool.join()
                                output = [p.get() for p in process]
                                
                                pre_dmr=pd.concat(output, ignore_index=True,axis=0)
                                if len(pre_dmr)>=1:
                                    df_split=ho.splitlist(k,pre_dmr,nop,dis_thres)
                                else: 
                                        print(("No DMRs found for "+sample_name1+"_VS_"+sample_name2+"_{c}".format(c=c)))
                                        continue
                                
                                del(pre_dmr,k)
                                   
                                pool = multiprocessing.Pool(processes=nop)
                                process = [pool.apply_async(ho.clustandtrim_nonCG2, args=(ddd,dd,dis_thres,ncb,len_cutoff)) for dd,ddd in df_split]
                                pool.close()
                                pool.join()
                                output = [p.get() for p in process]
                                
                                dmrs=pd.concat(output, ignore_index=True,axis=0)
                            else:
                                pre_dmr=ho.clustandtrim_nonCG1(k,sc)
                                if len(pre_dmr)>=1:
                                    dmrs=ho.clustandtrim_nonCG2(k,pre_dmr,dis_thres,ncb,len_cutoff)
                                else: 
                                        print(("No DMRs found for "+sample_name1+"_VS_"+sample_name2+"_{c}".format(c=c)))
                                        continue
                            if len(dmrs)>=1:
                                
                                dmrs_filtered=ho.filterdmr_nonCG(dmrs,minlen,mc,d) 
                            else: 
                                    print(("No DMRs found for "+sample_name1+"_VS_"+sample_name2+"_{c}".format(c=c)))
                                    continue     
                            
                        
                        if len(dmrs_filtered)>=1: 
                            
                            dmr_final=pd.concat([df1.chr[0:len(dmrs_filtered)],dmrs_filtered],axis=1)
                            dmr_final['chr'] = dmr_final['chr'].astype(str)
                            dmr_final.to_csv(args.outputpath+'/HOME_pairwise_DMRs/'+sample_name1+"_VS_"+sample_name2+"/HOME_DMRs_{c}.txt".format(c=c),header=True, index=False,sep='\t')
                            print(("DMRs for "+sample_name1+"_VS_"+sample_name2+"_{c} done".format(c=c)))
                            
                        elif len(dmrs_filtered)<1: 
                            print(("No DMRs found for "+sample_name1+"_VS_"+sample_name2+"_{c}".format(c=c)))
                    else: 
                        print(("No DMRs found for "+sample_name1+"_VS_"+sample_name2+"_{c}".format(c=c)))
                else: 
                    print(("No DMRs found for {c} as no similar positions are observed in the files".format(c=c))) 
            else:
                print(("No DMRs found for {c} as file does not exit".format(c=c))) 
        return 
           
#main code

## Inputs from user  
def real_main():
    topass = dict()
    np.set_printoptions(threshold=np.inf,suppress=True,linewidth=np.inf,precision=3)
    parser = argparse.ArgumentParser(description='HOME -- HISTOGRAM Of METHYLATION',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i','--samplefilepath', help='path of the sample file with samplename and sample path TAB seperated', required=True)
    parser.add_argument('-t','--type', help='type of class', choices=["CGN","CHN"],required=True, type=str)
    parser.add_argument('-o','--outputpath', help='path where the DMRs will be saved', required=True)
    parser.add_argument('-sc','--scorecutoff',  help='min classifier score required to cluster the DMR',choices=np.round(np.linspace(0,1,20,endpoint=False),decimals=2), required=False, type=float,default=0.1)
    parser.add_argument('-p','--pruncutoff', help='prunning cutoff for boundaries', required=False,choices=np.round(np.arange(0,0.5,0.1),decimals=1), type=float,default=0.1)
    parser.add_argument('-ml','--minlength', help='minimum length of DMRs to be reported', required=False, type=int,default=50)
    parser.add_argument('-ncb','--numcb',  help='number of Cs required between DMRs to keep them seperate', required=False, type=int,default=5)
    parser.add_argument('-md','--mergedist',  help='distance between DMRs to merge', required=False, type=int,default=500)
    #parser.add_argument('-sin','--singlechrom',  help='parallel for single chromosomes',action='store_true',default=False)
    parser.add_argument('-npp','--numprocess', help='number of parallel processes for all chromosome', required=False, type=int,default=8)
    parser.add_argument('-mc','--minc', help='minimum number of C in a DMR to reported', required=False, type=int,default=3)
    parser.add_argument('-d','--delta', help='minimum average difference in methylation required', required=False, type=float,default=0.1)
    parser.add_argument('-prn','--prunningC', help='number of Cs required for prunning', required=False, type=int,default=3)
    parser.add_argument('-ns','--numsamples', help='number of samples to use for pairwise DMR calling', required=False, type=int)
    parser.add_argument('-sp','--startposition', help='start position of samples to use for pairwise DMR calling', required=False, type=int)
    parser.add_argument('-wrt','--withrespectto', help='samples to use for DMR calling for pairwise comparision with respect to specific samples', nargs='*',required=False, type=str)
    parser.add_argument('-Keepall','--Keepall',  help='Keep all cytosine positions present among replicates',action='store_true',default=False)
    
    
    ## Read the inputs and preprocess the files 
    o=parser.parse_args()
    classes=o.type
    if o.startposition is not None:
        
        sp=(o.startposition)-1
    else:
        
        sp=0
        
    if o.numsamples is not None:
        
        ns=o.numsamples
    else:
        
        ns=len(o.samplefilepath)
    #Keepall=o.Keepall     
    df_file=pd.read_csv(o.samplefilepath,header=None, sep='\t')
    samplenames=df_file.iloc[sp:sp+ns,0]
    samplenames.reset_index(drop=True,inplace=True)
    input_files=df_file.iloc[sp:sp+ns,1:]
    input_files.reset_index(drop=True,inplace=True)
    numreps=[len(input_files.iloc[x].dropna()) for x in range (len(input_files))]
    topass['numreps']=numreps
    
    input_files=[list(input_files.iloc[x].dropna()) for x in range (len(input_files))]
    
    k=-1
    cwd = os.getcwd()
    
    
    if not os.path.exists((o.outputpath+'/temp_HOME')):
                os.makedirs(o.outputpath+'/temp_HOME')
    else: 
        print(" Temp directory at output path already exist.... please clean up and rerun")
        #sys.exit()
                  
    input_files_mod=[]
    
    ## make output directory and store the input files per chromosome could be done in python but using awk as its faster 
    for i in input_files:
          temp_file=[]
          k=k+1
          for ii in range(len(i)):
         
              #if not os.path.exists((o.outputpath+'/temp_HOME'+'/'+samplenames[k]+'_rep'+str(ii+1))):
                if True:
                    if not os.path.exists((o.outputpath+'/temp_HOME'+'/'+samplenames[k]+'_rep'+str(ii+1))):
                        os.makedirs((o.outputpath+'/temp_HOME'+'/'+samplenames[k]+'_rep'+str(ii+1)))
                    os.chdir((o.outputpath+'/temp_HOME'+'/'+samplenames[k]+'_rep'+str(ii+1)))
                  
                    com='zcat -f '+i[ii]+ ' | '
                    if classes=="CGN":
                        com+=''' awk -v OFS='\t' '{if (substr($4,1,2)== "CG") {print $1"\t"$2"\t"$3"\t"$4"\t"$5"\t"$6 >> $1".tsv"}}'  '''
                    else:
                        com+=''' awk -v OFS='\t' '{if (substr($4,2,1)!= "G") {print $1"\t"$2"\t"$3"\t"$4"\t"$5"\t"$6 >> $1".tsv"}}'  '''


                    status=subprocess.call(com, shell=True)
                    
                    temp_file.append(os.getcwd())
                    os.chdir(cwd)
          input_files_mod.append(temp_file)        
    input_files=input_files_mod
    del(input_files_mod,temp_file)
    #s=[ os.path.splitext(os.path.basename(x))[0] for x in glob.glob(input_files[0][0]+'/*.tsv')]
    s=[f.split('.')[0] for dp, dn, filenames in os.walk(o.outputpath+'/temp_HOME') for f in filenames if os.path.splitext(f)[1] == '.tsv']
    s = Counter(s)
    coun_s=len(next(os.walk(o.outputpath+'/temp_HOME'))[1])
    s=[kv for kv, v in list(s.items()) if v == (coun_s)]
    os.chdir(cwd)  
    
      
    if not os.path.exists((o.outputpath+'/temp_HOME'+'/chunks')):
        os.makedirs(o.outputpath+'/temp_HOME'+'/chunks')
    else: 
        print(" Temp directory at output path already exist.... please clean up and rerun")
    if not os.path.exists((o.outputpath+'/HOME_pairwise_DMRs')):
        os.makedirs(o.outputpath+'/HOME_pairwise_DMRs') 

     
       
    sc=o.scorecutoff
    prn=o.prunningC
    tr=o.pruncutoff
    minlen=o.minlength
    
    dis_thres=o.mergedist
    ncb=o.numcb
    mc=o.minc
    d=o.delta
    #sin=o.singlechrom
    npp=o.numprocess
    nop=1
    #if sin==True:
    #    nop=npp
    #    npp=1
    #else: 
    #    nop=1
        
    
   #"handle any number of replicates as long as it is 2+ in all groups but cannot handle 1 replicate in 1 group and multiple in the other"
    if (min(numreps)==1 and max(numreps)>1):
        sys.exit('error: cannot handle 1 replicate in 1 group and more than 1 in other')
    
    pd.options.mode.chained_assignment = None
    mergeo = functools.partial(pd.merge, how='outer', on=['chr','pos',"strand","type"])  
    merge = functools.partial(pd.merge, how='inner', on=['chr','pos',"strand","type"])
    topass['mergeo']=mergeo
    topass['merge']=merge
    topass['dictionary'] = OrderedDict(list(zip(list(samplenames),list(input_files))))
    comb_samples=itertools.combinations(list(samplenames), 2)
    if o.withrespectto is not None:
        comb_samples=[coms for coms in comb_samples if coms[0] in o.withrespectto]
    for i in comb_samples:
        if not os.path.exists(o.outputpath+'/HOME_pairwise_DMRs/'+i[0]+"_VS_"+i[1]):
            os.makedirs(o.outputpath+'/HOME_pairwise_DMRs/'+i[0]+"_VS_"+i[1])
          
    if status==0:        
        print("Preparing the DMRs from HOME.....") 
        print("GOOD LUCK !") 


        if npp==1:  
                print('ha')
                for dx in s:
                   main(dx,nop,topass,o)
                shutil.rmtree(o.outputpath+'/temp_HOME', ignore_errors=True)
                print("Congratulations the DMRs are ready") 
                remEmptyDir(o.outputpath+'/HOME_DMRs/')
        elif npp>1:
                print('he')
                pool1= multiprocessing.Pool(processes=npp)
                process=[pool1.apply_async(main, args=(dx,nop,topass,o)) for dx in s]
                output = [p.get() for p in process]
                pool1.close()
                print("Congratulations the DMRs are ready")
                pool1.join()
                shutil.rmtree(o.outputpath+'/temp_HOME', ignore_errors=True)
                remEmptyDir(o.outputpath+'/HOME_DMRs/')
      





        #print 'npp',npp
        #print s
        #pool1= multiprocessing.Pool(processes=npp)
        #process=[pool1.apply_async(main, args=(dx,nop,topass,o)) for dx in s]
        #output = [p.get() for p in process]
        #pool1.close()
        #print("Congratulations the DMRs are ready")
        #pool1.join()
        #shutil.rmtree(o.outputpath+'/temp_HOME', ignore_errors=True)
        #remEmptyDir(o.outputpath+'/HOME_DMRs/')
 
